"""
Governance Validator - 治理驗證器

Validates generated projects against governance standards.
根據治理標準驗證生成的專案。
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import yaml
import re

if TYPE_CHECKING:
    from .factory import GeneratedProject

logger = logging.getLogger(__name__)


class ValidationResult:
    """
    Result of governance validation.

    治理驗證結果。
    """

    def __init__(self):
        self.checks: Dict[str, Dict[str, Any]] = {}
        self.overall_status: str = "PENDING"

    def add_check(
        self,
        check_name: str,
        status: str,
        details: str,
        **extra_data
    ) -> None:
        """Add validation check result."""
        self.checks[check_name] = {
            "status": status,
            "details": details,
            **extra_data
        }

    def finalize(self) -> None:
        """Compute overall validation status."""
        if not self.checks:
            self.overall_status = "NO_CHECKS"
            return

        statuses = [check["status"] for check in self.checks.values()]

        if all(s == "PASSED" for s in statuses):
            self.overall_status = "PASSED"
        elif any(s == "FAILED" for s in statuses):
            self.overall_status = "FAILED"
        elif any(s == "WARNING" for s in statuses):
            self.overall_status = "WARNING"
        else:
            self.overall_status = "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_status": self.overall_status,
            "checks": self.checks,
        }


class GovernanceValidator:
    """
    Validates projects against SynergyMesh governance standards.

    根據 SynergyMesh 治理標準驗證專案。

    Performs validation against:
    - Language policy
    - Security standards
    - Architecture constraints
    - CI/CD requirements
    - Compliance standards
    """

    def __init__(self, governance_config_path: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            governance_config_path: Path to governance configuration
        """
        self.governance_config_path = governance_config_path
        self.governance_config = self._load_governance_config()

    def _load_governance_config(self) -> Dict[str, Any]:
        """Load governance configuration."""
        if not self.governance_config_path or not self.governance_config_path.exists():
            logger.warning("Governance config not found, using defaults")
            return self._get_default_config()

        try:
            with open(self.governance_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load governance config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default governance configuration."""
        return {
            "principles": {
                "machine_first": {"description": "Machine as primary reader"},
                "semantic_consistency": {"description": "Standardized semantics"},
                "modularity": {"description": "Independent, composable modules"},
                "auditability": {"description": "Complete audit trail"},
                "automation": {"description": "Native CI/CD support"},
            },
            "execution": {
                "instant_standard": {
                    "understanding_time": "< 1s",
                    "execution_time": "2-3 minutes",
                    "repair_time": "< 45s",
                },
            },
        }

    def validate(self, project: 'GeneratedProject') -> Dict[str, Any]:
        """
        Validate project against all governance standards.

        驗證專案是否符合所有治理標準。

        Args:
            project: Generated project to validate

        Returns:
            Dict containing validation results
        """
        logger.info(f"Validating project: {project.spec.name}")

        result = ValidationResult()

        # Run all validation checks
        self._check_language_policy(project, result)
        self._check_security_standards(project, result)
        self._check_architecture_constraints(project, result)
        self._check_cicd_standards(project, result)
        self._check_compliance_requirements(project, result)

        result.finalize()

        logger.info(f"Validation complete: {result.overall_status}")
        return result.to_dict()

    def _check_language_policy(
        self,
        project: 'GeneratedProject',
        result: ValidationResult
    ) -> None:
        """Check language policy compliance."""
        spec = project.spec

        # Check if language is allowed
        forbidden_languages = ["php", "perl"]  # From language-policy.yaml

        if spec.language.value.lower() in forbidden_languages:
            result.add_check(
                "language_policy",
                "FAILED",
                f"Language {spec.language.value} is forbidden by policy"
            )
            return

        # Check version requirements
        version_requirements = {
            "python": ">=3.11",
            "typescript": ">=5.0",
            "go": ">=1.21",
        }

        required_version = version_requirements.get(spec.language.value)
        if required_version:
            details = f"Language {spec.language.value} requires version {required_version}"
        else:
            details = "All language constraints satisfied"

        result.add_check(
            "language_policy",
            "PASSED",
            details
        )

    def _check_security_standards(
        self,
        project: 'GeneratedProject',
        result: ValidationResult
    ) -> None:
        """Check security standards compliance."""
        spec = project.spec
        files = project.files

        issues = []

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api[_-]?key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
        ]

        for file_path, content in files.items():
            if file_path.endswith(('.py', '.ts', '.js', '.go')):
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Potential secret in {file_path}")

        # Check Dockerfile security
        if 'Dockerfile' in files:
            dockerfile = files['Dockerfile']
            if 'USER root' in dockerfile:
                issues.append("Dockerfile runs as root (security risk)")

        if issues:
            result.add_check(
                "security",
                "WARNING",
                f"Security issues found: {', '.join(issues)}"
            )
        else:
            result.add_check(
                "security",
                "PASSED",
                "No security issues found"
            )

    def _check_architecture_constraints(
        self,
        project: 'GeneratedProject',
        result: ValidationResult
    ) -> None:
        """Check architecture constraints from ai-constitution.yaml."""
        spec = project.spec

        # Check if architecture pattern is correctly implemented
        if spec.architecture.pattern.value == "clean-architecture":
            expected_layers = {"presentation", "application", "domain", "infrastructure"}
            actual_layers = set(spec.architecture.layers)

            if not expected_layers.issubset(actual_layers):
                missing = expected_layers - actual_layers
                result.add_check(
                    "architecture",
                    "WARNING",
                    f"Clean architecture missing layers: {missing}"
                )
            else:
                result.add_check(
                    "architecture",
                    "PASSED",
                    f"{spec.architecture.pattern.value} correctly implemented"
                )
        else:
            result.add_check(
                "architecture",
                "PASSED",
                f"Architecture pattern: {spec.architecture.pattern.value}"
            )

    def _check_cicd_standards(
        self,
        project: 'GeneratedProject',
        result: ValidationResult
    ) -> None:
        """Check CI/CD standards compliance."""
        spec = project.spec
        files = project.files

        required_stages = {"lint", "test", "build"}
        actual_stages = set(spec.deliverables.ci_cd.stages)

        if not required_stages.issubset(actual_stages):
            missing = required_stages - actual_stages
            result.add_check(
                "ci_cd",
                "WARNING",
                f"Missing CI/CD stages: {missing}"
            )
        else:
            # Check if CI/CD file exists
            ci_files = [
                ".github/workflows/ci.yml",
                ".gitlab-ci.yml",
                ".drone.yml"
            ]

            has_ci_file = any(f in files for f in ci_files)

            if has_ci_file:
                result.add_check(
                    "ci_cd",
                    "PASSED",
                    f"All CI/CD stages configured for {spec.deliverables.ci_cd.platform}"
                )
            else:
                result.add_check(
                    "ci_cd",
                    "WARNING",
                    "CI/CD configured but pipeline file not generated"
                )

    def _check_compliance_requirements(
        self,
        project: 'GeneratedProject',
        result: ValidationResult
    ) -> None:
        """Check compliance requirements."""
        spec = project.spec
        files = project.files

        compliance_artifacts = []

        # Check for SBOM
        if spec.governance.sbom and "governance/SBOM.json" in files:
            compliance_artifacts.append("SBOM")

        # Check for compliance documentation
        if "governance/COMPLIANCE.md" in files:
            compliance_artifacts.append("Compliance declaration")

        # Check for security policy
        if "SECURITY.md" in files:
            compliance_artifacts.append("Security policy")

        if compliance_artifacts:
            result.add_check(
                "compliance",
                "PASSED",
                f"Compliance requirements met: {', '.join(compliance_artifacts)}",
                compliance_standards=spec.governance.compliance,
                artifacts=compliance_artifacts
            )
        else:
            result.add_check(
                "compliance",
                "WARNING",
                "Missing compliance documentation"
            )
