"""
Execution Isolator

Provides isolated execution environments for analysis:
- Container/Kubernetes Job based isolation
- Destroyed after execution completes
- Network restrictions (egress deny by default)
- Resource limits

CRITICAL: Never run external code without isolation!
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """Isolation levels for execution environments"""
    STANDARD = "standard"       # Container with standard restrictions
    HIGH = "high"              # Additional network isolation
    MAXIMUM = "maximum"        # Completely air-gapped


class NetworkPolicy(Enum):
    """Network egress policies"""
    DENY_ALL = "deny_all"                 # No network access
    ALLOW_INTERNAL = "allow_internal"     # Only internal services
    ALLOW_SPECIFIC = "allow_specific"     # Allowlist specific domains
    ALLOW_ALL = "allow_all"              # Unrestricted (dangerous!)


@dataclass
class IsolationPolicy:
    """
    Policy defining isolation requirements

    Defines how strictly to isolate the execution environment.
    """
    # Isolation level
    level: IsolationLevel = IsolationLevel.STANDARD

    # Network policy
    network_policy: NetworkPolicy = NetworkPolicy.DENY_ALL
    allowed_egress: list[str] = field(default_factory=list)  # Allowlist if ALLOW_SPECIFIC

    # Resource limits
    cpu_limit: str = "1"                    # CPU cores (e.g., "0.5", "1", "2")
    memory_limit: str = "512Mi"             # Memory limit
    ephemeral_storage_limit: str = "1Gi"    # Disk space

    # Timeouts
    execution_timeout_seconds: int = 300    # Max execution time
    setup_timeout_seconds: int = 60         # Container startup timeout

    # Capabilities
    drop_all_capabilities: bool = True      # Drop Linux capabilities
    read_only_root_fs: bool = True         # Read-only filesystem
    run_as_non_root: bool = True           # Run as non-root user
    user_id: int = 1000                    # UID to run as

    # Filesystem
    allowed_volume_mounts: list[str] = field(default_factory=list)
    temp_dir_size_limit: str = "100Mi"

    # Security context
    seccomp_profile: str = "RuntimeDefault"
    apparmor_profile: str | None = None


@dataclass
class ExecutionSpec:
    """
    Specification for an isolated execution

    Defines what to run and how.
    """
    id: UUID = field(default_factory=uuid4)

    # Tenant isolation
    org_id: UUID = field(default_factory=uuid4)
    run_id: UUID | None = None

    # Container image
    image: str = ""                         # Worker image to use
    image_pull_secret: str | None = None

    # Command
    command: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    working_dir: str = "/workspace"

    # Environment
    env_vars: dict[str, str] = field(default_factory=dict)
    secret_refs: list[str] = field(default_factory=list)  # Secrets to inject

    # Input
    input_source: str = ""                  # Git URL or artifact location
    input_ref: str = ""                     # Git ref or version

    # Policy
    isolation_policy: IsolationPolicy = field(default_factory=IsolationPolicy)

    # Labels (for tracking)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """
    Result of an isolated execution
    """
    id: UUID = field(default_factory=uuid4)
    spec_id: UUID = field(default_factory=uuid4)

    # Status
    success: bool = False
    exit_code: int = -1
    error: str | None = None

    # Output
    stdout: str = ""
    stderr: str = ""
    output_artifacts: list[str] = field(default_factory=list)  # Paths to output files

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    # Resource usage
    cpu_usage_seconds: float | None = None
    memory_peak_bytes: int | None = None
    network_egress_bytes: int | None = None

    # Execution details
    container_id: str | None = None
    pod_name: str | None = None
    node_name: str | None = None


class ContainerRuntime(Protocol):
    """Interface for container runtime operations"""

    async def create_container(
        self,
        spec: ExecutionSpec,
    ) -> str:
        """Create a container, return container ID"""
        ...

    async def start_container(
        self,
        container_id: str,
    ) -> None:
        """Start a container"""
        ...

    async def wait_for_container(
        self,
        container_id: str,
        timeout: int,
    ) -> int:
        """Wait for container to complete, return exit code"""
        ...

    async def get_logs(
        self,
        container_id: str,
    ) -> tuple[str, str]:
        """Get container logs (stdout, stderr)"""
        ...

    async def destroy_container(
        self,
        container_id: str,
    ) -> None:
        """Destroy container and cleanup"""
        ...

    async def get_resource_usage(
        self,
        container_id: str,
    ) -> dict[str, Any]:
        """Get resource usage statistics"""
        ...


class KubernetesClient(Protocol):
    """Interface for Kubernetes operations"""

    async def create_job(
        self,
        namespace: str,
        job_spec: dict[str, Any],
    ) -> str:
        """Create a Kubernetes Job, return job name"""
        ...

    async def wait_for_job(
        self,
        namespace: str,
        job_name: str,
        timeout: int,
    ) -> bool:
        """Wait for job completion, return success status"""
        ...

    async def get_pod_logs(
        self,
        namespace: str,
        pod_name: str,
    ) -> str:
        """Get pod logs"""
        ...

    async def delete_job(
        self,
        namespace: str,
        job_name: str,
    ) -> None:
        """Delete job and associated pods"""
        ...

    async def get_job_status(
        self,
        namespace: str,
        job_name: str,
    ) -> dict[str, Any]:
        """Get job status"""
        ...


@dataclass
class ExecutionIsolator:
    """
    Execution Isolator

    Runs analysis in isolated environments (containers or K8s Jobs).
    Environments are destroyed after execution.
    """

    # Runtime backends
    container_runtime: ContainerRuntime | None = None
    kubernetes_client: KubernetesClient | None = None

    # Configuration
    default_namespace: str = "mno-workers"
    default_image: str = "mno/worker:latest"
    image_pull_policy: str = "IfNotPresent"

    # Cleanup
    cleanup_on_complete: bool = True
    cleanup_on_failure: bool = True

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        spec: ExecutionSpec,
    ) -> ExecutionResult:
        """
        Execute in an isolated environment

        The environment is destroyed after execution completes.
        """
        result = ExecutionResult(spec_id=spec.id)
        result.started_at = datetime.utcnow()

        try:
            if self.kubernetes_client:
                result = await self._execute_kubernetes(spec, result)
            elif self.container_runtime:
                result = await self._execute_container(spec, result)
            else:
                raise ValueError("No execution runtime configured")

            result.success = result.exit_code == 0

        except TimeoutError:
            result.error = "Execution timed out"
            result.exit_code = 124  # Standard timeout exit code

        except Exception as e:
            logger.exception(f"Execution failed: {e}")
            result.error = str(e)
            result.exit_code = 1

        finally:
            result.completed_at = datetime.utcnow()
            if result.started_at:
                result.duration_seconds = (
                    result.completed_at - result.started_at
                ).total_seconds()

        logger.info(
            f"Execution completed: spec={spec.id} "
            f"success={result.success} "
            f"exit_code={result.exit_code} "
            f"duration={result.duration_seconds:.2f}s"
        )

        return result

    async def _execute_container(
        self,
        spec: ExecutionSpec,
        result: ExecutionResult,
    ) -> ExecutionResult:
        """Execute using container runtime (Docker)"""
        container_id = None

        try:
            # Create container
            container_id = await self.container_runtime.create_container(spec)
            result.container_id = container_id

            # Start and wait
            await self.container_runtime.start_container(container_id)

            exit_code = await asyncio.wait_for(
                self.container_runtime.wait_for_container(
                    container_id,
                    spec.isolation_policy.execution_timeout_seconds,
                ),
                timeout=spec.isolation_policy.execution_timeout_seconds + 10,
            )

            result.exit_code = exit_code

            # Get logs
            stdout, stderr = await self.container_runtime.get_logs(container_id)
            result.stdout = stdout
            result.stderr = stderr

            # Get resource usage
            usage = await self.container_runtime.get_resource_usage(container_id)
            result.cpu_usage_seconds = usage.get("cpu_seconds")
            result.memory_peak_bytes = usage.get("memory_peak_bytes")

        finally:
            # Always cleanup
            if container_id and (
                self.cleanup_on_complete
                or (not result.success and self.cleanup_on_failure)
            ):
                try:
                    await self.container_runtime.destroy_container(container_id)
                except Exception as e:
                    logger.warning(f"Failed to cleanup container: {e}")

        return result

    async def _execute_kubernetes(
        self,
        spec: ExecutionSpec,
        result: ExecutionResult,
    ) -> ExecutionResult:
        """Execute using Kubernetes Job"""
        job_name = f"mno-run-{spec.id.hex[:8]}"
        namespace = self.default_namespace

        try:
            # Build job spec
            job_spec = self._build_k8s_job_spec(spec, job_name)

            # Create job
            await self.kubernetes_client.create_job(namespace, job_spec)
            result.pod_name = job_name  # Pod name will include job name

            # Wait for completion
            success = await asyncio.wait_for(
                self.kubernetes_client.wait_for_job(
                    namespace,
                    job_name,
                    spec.isolation_policy.execution_timeout_seconds,
                ),
                timeout=spec.isolation_policy.execution_timeout_seconds + 30,
            )

            result.exit_code = 0 if success else 1

            # Get logs
            logs = await self.kubernetes_client.get_pod_logs(namespace, job_name)
            result.stdout = logs

            # Get job status
            status = await self.kubernetes_client.get_job_status(namespace, job_name)
            result.node_name = status.get("node_name")

        finally:
            # Cleanup
            if self.cleanup_on_complete or (not result.success and self.cleanup_on_failure):
                try:
                    await self.kubernetes_client.delete_job(namespace, job_name)
                except Exception as e:
                    logger.warning(f"Failed to cleanup job: {e}")

        return result

    def _build_k8s_job_spec(
        self,
        spec: ExecutionSpec,
        job_name: str,
    ) -> dict[str, Any]:
        """Build Kubernetes Job specification"""
        policy = spec.isolation_policy

        # Security context
        security_context = {
            "runAsNonRoot": policy.run_as_non_root,
            "runAsUser": policy.user_id,
            "readOnlyRootFilesystem": policy.read_only_root_fs,
        }

        if policy.drop_all_capabilities:
            security_context["capabilities"] = {"drop": ["ALL"]}

        if policy.seccomp_profile:
            security_context["seccompProfile"] = {
                "type": policy.seccomp_profile,
            }

        # Resource limits
        resources = {
            "limits": {
                "cpu": policy.cpu_limit,
                "memory": policy.memory_limit,
                "ephemeral-storage": policy.ephemeral_storage_limit,
            },
            "requests": {
                "cpu": "100m",
                "memory": "128Mi",
            },
        }

        # Environment variables
        env = [
            {"name": k, "value": v}
            for k, v in spec.env_vars.items()
        ]

        # Add secret references
        for secret_ref in spec.secret_refs:
            env.append({
                "name": secret_ref.upper(),
                "valueFrom": {
                    "secretKeyRef": {
                        "name": secret_ref,
                        "key": "value",
                    },
                },
            })

        # Build job spec
        job_spec = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": job_name,
                "labels": {
                    "app": "mno-worker",
                    "org-id": str(spec.org_id),
                    "run-id": str(spec.run_id) if spec.run_id else "",
                    **spec.labels,
                },
            },
            "spec": {
                "backoffLimit": 0,  # No retries
                "activeDeadlineSeconds": policy.execution_timeout_seconds,
                "ttlSecondsAfterFinished": 3600,  # Cleanup after 1 hour
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "mno-worker",
                        },
                    },
                    "spec": {
                        "restartPolicy": "Never",
                        "automountServiceAccountToken": False,
                        "securityContext": {
                            "runAsNonRoot": policy.run_as_non_root,
                            "fsGroup": policy.user_id,
                        },
                        "containers": [{
                            "name": "worker",
                            "image": spec.image or self.default_image,
                            "imagePullPolicy": self.image_pull_policy,
                            "command": spec.command if spec.command else None,
                            "args": spec.args if spec.args else None,
                            "workingDir": spec.working_dir,
                            "env": env,
                            "resources": resources,
                            "securityContext": security_context,
                            "volumeMounts": [
                                {
                                    "name": "workspace",
                                    "mountPath": "/workspace",
                                },
                                {
                                    "name": "tmp",
                                    "mountPath": "/tmp",
                                },
                            ],
                        }],
                        "volumes": [
                            {
                                "name": "workspace",
                                "emptyDir": {
                                    "sizeLimit": policy.ephemeral_storage_limit,
                                },
                            },
                            {
                                "name": "tmp",
                                "emptyDir": {
                                    "sizeLimit": policy.temp_dir_size_limit,
                                },
                            },
                        ],
                    },
                },
            },
        }

        # Add network policy annotation if needed
        if policy.network_policy == NetworkPolicy.DENY_ALL:
            job_spec["spec"]["template"]["metadata"]["annotations"] = {
                "mno.io/network-policy": "deny-all",
            }

        # Add image pull secret if specified
        if spec.image_pull_secret:
            job_spec["spec"]["template"]["spec"]["imagePullSecrets"] = [
                {"name": spec.image_pull_secret},
            ]

        return job_spec

    # ------------------------------------------------------------------
    # Network Policy Management
    # ------------------------------------------------------------------

    def _build_network_policy(
        self,
        policy: IsolationPolicy,
        labels: dict[str, str],
    ) -> dict[str, Any]:
        """Build Kubernetes NetworkPolicy for isolation"""
        if policy.network_policy == NetworkPolicy.DENY_ALL:
            return {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": f"deny-egress-{labels.get('run-id', 'default')}",
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": labels,
                    },
                    "policyTypes": ["Egress"],
                    "egress": [],  # Empty = deny all
                },
            }

        elif policy.network_policy == NetworkPolicy.ALLOW_SPECIFIC:
            egress_rules = []
            for domain in policy.allowed_egress:
                # In practice, you'd resolve domains or use external DNS
                egress_rules.append({
                    "to": [{"ipBlock": {"cidr": domain}}]
                    if "/" in domain
                    else [],
                    "ports": [
                        {"protocol": "TCP", "port": 443},
                        {"protocol": "TCP", "port": 80},
                    ],
                })

            return {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": f"allow-specific-{labels.get('run-id', 'default')}",
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": labels,
                    },
                    "policyTypes": ["Egress"],
                    "egress": egress_rules,
                },
            }

        return None
