"""
Execution Isolation and Security Module

Since we run code/content from external repos, isolation is critical:
- Container isolation: Each analysis runs in an isolated container
- Network restrictions: Egress deny by default
- Resource quotas: CPU/Memory/Time limits
- Secrets management: KMS/Vault/Secret Manager integration
- Supply chain security: Traceable worker images with SBOM and signatures
"""

from enterprise.execution.isolator import (
    ExecutionIsolator,
    ExecutionResult,
    ExecutionSpec,
    IsolationPolicy,
)
from enterprise.execution.quota import (
    QuotaExceededError,
    ResourceQuota,
    ResourceQuotaManager,
)
from enterprise.execution.secrets import (
    Secret,
    SecretsManager,
    SecretType,
)
from enterprise.execution.supply_chain import (
    SBOM,
    ImageAttestation,
    SupplyChainValidator,
)

__all__ = [
    # Isolator
    "ExecutionIsolator",
    "ExecutionSpec",
    "ExecutionResult",
    "IsolationPolicy",
    # Quota
    "ResourceQuotaManager",
    "ResourceQuota",
    "QuotaExceededError",
    # Secrets
    "SecretsManager",
    "Secret",
    "SecretType",
    # Supply Chain
    "SupplyChainValidator",
    "ImageAttestation",
    "SBOM",
]
