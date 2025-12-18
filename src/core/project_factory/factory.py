"""
Project Factory - 專案生成工廠核心

Core factory for generating complete projects with governance compliance.
核心工廠，生成符合治理標準的完整專案。
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .spec import ProjectSpec
from .generator import ProjectGenerator
from .validator import GovernanceValidator
from .templates import TemplateEngine

logger = logging.getLogger(__name__)


class GeneratedProject:
    """
    Represents a generated project with all deliverables.

    表示生成的專案及其所有交付物。

    Attributes:
        spec: Original project specification
        root_path: Root directory of generated project
        files: Dictionary of generated files {path: content}
        validation_result: Governance validation result
        metadata: Generation metadata
    """

    def __init__(
        self,
        spec: ProjectSpec,
        root_path: Path,
        files: Dict[str, str],
        metadata: Dict[str, Any]
    ):
        self.spec = spec
        self.root_path = root_path
        self.files = files
        self.validation_result: Optional[Dict[str, Any]] = None
        self.metadata = metadata

    def export(self, output_path: Optional[Path] = None) -> Path:
        """
        Export generated project to filesystem.

        將生成的專案導出到文件系統。

        Args:
            output_path: Target directory (uses self.root_path if not specified)

        Returns:
            Path: Path where project was exported

        Example:
            >>> project = factory.generate(spec)
            >>> project.export(Path("./projects/my-service"))
        """
        target = output_path or self.root_path

        logger.info(f"Exporting project to: {target}")

        # Create directory structure
        target.mkdir(parents=True, exist_ok=True)

        # Write all files
        for file_path, content in self.files.items():
            full_path = target / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.debug(f"Created: {file_path}")

        # Write metadata
        metadata_path = target / ".project-factory-metadata.json"
        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"✅ Project exported successfully: {target}")
        return target

    def validate_governance(self) -> Dict[str, Any]:
        """
        Validate project against governance standards.

        根據治理標準驗證專案。

        Returns:
            Dict containing validation results
        """
        if self.validation_result is None:
            validator = GovernanceValidator()
            self.validation_result = validator.validate(self)

        return self.validation_result

    def get_summary(self) -> str:
        """
        Get human-readable summary of generated project.

        獲取生成專案的可讀摘要。

        Returns:
            str: Formatted summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"  Generated Project: {self.spec.name}")
        lines.append("=" * 60)
        lines.append(f"Type: {self.spec.type.value}")
        lines.append(f"Language: {self.spec.language.value}")
        lines.append(f"Framework: {self.spec.framework}")
        lines.append(f"Files generated: {len(self.files)}")
        lines.append(f"Root path: {self.root_path}")
        lines.append("")

        if self.validation_result:
            status = self.validation_result.get("overall_status", "UNKNOWN")
            lines.append(f"Governance validation: {status}")

        lines.append("=" * 60)
        return "\n".join(lines)


class ProjectFactory:
    """
    Central factory for generating complete projects.

    核心工廠，用於生成完整專案。

    The factory orchestrates the entire generation process:
    1. Validate specification
    2. Select appropriate templates
    3. Generate all deliverables
    4. Validate against governance
    5. Export project

    工廠編排整個生成流程：
    1. 驗證規格
    2. 選擇合適的模板
    3. 生成所有交付物
    4. 根據治理標準驗證
    5. 導出專案

    Example:
        >>> from core.project_factory import ProjectFactory, ProjectSpec
        >>> from core.project_factory.spec import ProjectType, Language
        >>>
        >>> # Create specification
        >>> spec = ProjectSpec(
        ...     name="user-service",
        ...     type=ProjectType.MICROSERVICE,
        ...     language=Language.PYTHON,
        ...     framework="fastapi"
        ... )
        >>>
        >>> # Generate project
        >>> factory = ProjectFactory()
        >>> project = factory.generate(spec)
        >>>
        >>> # Validate and export
        >>> validation = project.validate_governance()
        >>> if validation["overall_status"] == "PASSED":
        ...     project.export(Path("./projects/user-service"))
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        governance_config: Optional[Path] = None
    ):
        """
        Initialize Project Factory.

        初始化專案工廠。

        Args:
            template_dir: Directory containing project templates
            governance_config: Path to governance configuration
        """
        self.template_dir = template_dir or self._get_default_template_dir()
        self.governance_config = governance_config or self._get_default_governance_config()

        self.template_engine = TemplateEngine(self.template_dir)
        self.generator = ProjectGenerator(self.template_engine)
        self.validator = GovernanceValidator(self.governance_config)

        logger.info("ProjectFactory initialized")

    def _get_default_template_dir(self) -> Path:
        """Get default template directory."""
        return Path(__file__).parent / "templates"

    def _get_default_governance_config(self) -> Path:
        """Get default governance configuration path."""
        return Path(__file__).parents[2] / "governance" / "governance.yaml"

    def generate(
        self,
        spec: ProjectSpec,
        output_path: Optional[Path] = None,
        validate: bool = True
    ) -> GeneratedProject:
        """
        Generate complete project from specification.

        從規格生成完整專案。

        Args:
            spec: Project specification
            output_path: Target directory for project
            validate: Whether to validate against governance (default: True)

        Returns:
            GeneratedProject: Generated project with all deliverables

        Raises:
            ValueError: If specification is invalid
            RuntimeError: If generation fails

        Example:
            >>> spec = ProjectSpec(
            ...     name="payment-service",
            ...     type=ProjectType.MICROSERVICE,
            ...     language=Language.GO,
            ...     framework="gin"
            ... )
            >>>
            >>> factory = ProjectFactory()
            >>> project = factory.generate(spec, Path("./projects/payment-service"))
            >>> print(project.get_summary())
        """
        logger.info(f"Starting project generation: {spec.name}")

        # Step 1: Validate specification
        logger.info("Step 1/5: Validating specification...")
        errors = spec.validate()
        if errors:
            raise ValueError(f"Invalid specification: {'; '.join(errors)}")

        # Step 2: Prepare generation context
        logger.info("Step 2/5: Preparing generation context...")
        context = self._prepare_context(spec)

        # Step 3: Generate all deliverables
        logger.info("Step 3/5: Generating deliverables...")
        files = self.generator.generate(spec, context)

        # Step 4: Create project instance
        logger.info("Step 4/5: Creating project instance...")
        project = GeneratedProject(
            spec=spec,
            root_path=output_path or Path(f"./{spec.name}"),
            files=files,
            metadata=self._create_metadata(spec, context)
        )

        # Step 5: Validate governance (if requested)
        if validate:
            logger.info("Step 5/5: Validating governance compliance...")
            validation_result = project.validate_governance()

            if validation_result["overall_status"] != "PASSED":
                logger.warning("Governance validation issues found:")
                for check, result in validation_result["checks"].items():
                    if result["status"] != "PASSED":
                        logger.warning(f"  - {check}: {result['details']}")
        else:
            logger.info("Step 5/5: Skipped (validation disabled)")

        logger.info(f"✅ Project generation completed: {spec.name}")
        return project

    def _prepare_context(self, spec: ProjectSpec) -> Dict[str, Any]:
        """
        Prepare template context from specification.

        從規格準備模板上下文。

        Args:
            spec: Project specification

        Returns:
            Dict containing all template variables
        """
        return {
            # Basic info
            "project_name": spec.name,
            "project_type": spec.type.value,
            "language": spec.language.value,
            "framework": spec.framework,
            "description": spec.description,
            "version": spec.version,

            # Package names (sanitized for code)
            "package_name": spec.name.replace("-", "_"),
            "module_name": spec.name.replace("-", "_"),

            # Architecture
            "architecture_pattern": spec.architecture.pattern.value,
            "layers": spec.architecture.layers,

            # Features
            "has_database": spec.features.database is not None,
            "has_cache": spec.features.cache is not None,
            "has_messaging": spec.features.messaging is not None,

            # Deliverables
            "needs_docker": spec.deliverables.docker.multi_stage,
            "needs_k8s": spec.deliverables.kubernetes.deployment,
            "needs_ci_cd": spec.deliverables.ci_cd.platform is not None,

            # Governance
            "compliance_standards": spec.governance.compliance,
            "security_level": spec.governance.security_level,
            "license": spec.governance.license,

            # Generation metadata
            "generated_at": datetime.utcnow().isoformat(),
            "generator_version": "1.0.0",
        }

    def _create_metadata(self, spec: ProjectSpec, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create generation metadata.

        創建生成元數據。

        Args:
            spec: Project specification
            context: Generation context

        Returns:
            Dict containing metadata
        """
        return {
            "generated_at": context["generated_at"],
            "generator_version": context["generator_version"],
            "spec": spec.to_dict(),
            "deliverables": {
                "source_code": spec.deliverables.source_code,
                "tests": {
                    "unit": spec.deliverables.tests.unit,
                    "integration": spec.deliverables.tests.integration,
                    "e2e": spec.deliverables.tests.e2e,
                },
                "docker": spec.deliverables.docker.multi_stage,
                "kubernetes": spec.deliverables.kubernetes.deployment,
                "ci_cd": spec.deliverables.ci_cd.platform,
            },
            "governance": {
                "compliance": spec.governance.compliance,
                "validation_performed": True,
            }
        }

    def list_templates(self) -> Dict[str, list]:
        """
        List available project templates.

        列出可用的專案模板。

        Returns:
            Dict mapping project types to available templates
        """
        return self.template_engine.list_templates()

    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific template.

        獲取特定模板的資訊。

        Args:
            template_name: Name of template

        Returns:
            Dict containing template information, or None if not found
        """
        return self.template_engine.get_template_info(template_name)
