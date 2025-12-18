"""
Project Generator - 專案內容生成器

Generates all project deliverables including source code, tests, configs, etc.
生成所有專案交付物，包括源代碼、測試、配置等。
"""

import logging
from typing import Dict, Any
from pathlib import Path

from .spec import ProjectSpec, ProjectType, Language
from .templates import TemplateEngine

logger = logging.getLogger(__name__)


class ProjectGenerator:
    """
    Generates complete project deliverables from specification.

    從規格生成完整的專案交付物。

    This class coordinates the generation of all project components:
    - Source code structure
    - Test suites
    - Docker configurations
    - Kubernetes manifests
    - CI/CD pipelines
    - Documentation

    本類協調生成所有專案組件。
    """

    def __init__(self, template_engine: TemplateEngine):
        """
        Initialize generator with template engine.

        Args:
            template_engine: Template engine for rendering files
        """
        self.template_engine = template_engine

    def generate(self, spec: ProjectSpec, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all project files.

        生成所有專案文件。

        Args:
            spec: Project specification
            context: Template rendering context

        Returns:
            Dict[str, str]: Map of file paths to file contents
        """
        logger.info(f"Generating project: {spec.name}")

        files = {}

        # Generate based on project type and language
        files.update(self._generate_project_structure(spec, context))
        files.update(self._generate_source_code(spec, context))

        if spec.deliverables.tests.unit:
            files.update(self._generate_tests(spec, context))

        if spec.deliverables.docker.multi_stage:
            files.update(self._generate_docker(spec, context))

        if spec.deliverables.kubernetes.deployment:
            files.update(self._generate_kubernetes(spec, context))

        if spec.deliverables.ci_cd.platform:
            files.update(self._generate_cicd(spec, context))

        files.update(self._generate_documentation(spec, context))
        files.update(self._generate_governance_docs(spec, context))

        logger.info(f"Generated {len(files)} files")
        return files

    def _generate_project_structure(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate basic project structure and config files."""
        files = {}

        # README.md
        files["README.md"] = self.template_engine.render(
            "common/README.md.j2",
            context
        )

        # .gitignore
        files[".gitignore"] = self.template_engine.render(
            f"{spec.language.value}/.gitignore.j2",
            context
        )

        # LICENSE
        files["LICENSE"] = self.template_engine.render(
            f"licenses/{spec.governance.license}.j2",
            context
        )

        # Language-specific config
        if spec.language == Language.PYTHON:
            files["pyproject.toml"] = self.template_engine.render(
                "python/pyproject.toml.j2",
                context
            )
            files["requirements.txt"] = self.template_engine.render(
                "python/requirements.txt.j2",
                context
            )

        elif spec.language == Language.TYPESCRIPT:
            files["package.json"] = self.template_engine.render(
                "typescript/package.json.j2",
                context
            )
            files["tsconfig.json"] = self.template_engine.render(
                "typescript/tsconfig.json.j2",
                context
            )

        elif spec.language == Language.GO:
            files["go.mod"] = self.template_engine.render(
                "go/go.mod.j2",
                context
            )

        return files

    def _generate_source_code(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate source code based on architecture pattern."""
        files = {}

        template_base = f"{spec.type.value}/{spec.language.value}-{spec.framework}"

        if spec.type == ProjectType.MICROSERVICE:
            files.update(self._generate_microservice_code(spec, context, template_base))
        elif spec.type == ProjectType.FRONTEND:
            files.update(self._generate_frontend_code(spec, context, template_base))
        elif spec.type == ProjectType.AI_AGENT:
            files.update(self._generate_ai_agent_code(spec, context, template_base))

        return files

    def _generate_microservice_code(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any],
        template_base: str
    ) -> Dict[str, str]:
        """Generate microservice source code."""
        files = {}
        pkg = context["package_name"]

        # Clean Architecture layers
        if spec.architecture.pattern.value == "clean-architecture":
            # Presentation layer
            files[f"src/{pkg}/api/routes.py"] = self.template_engine.render(
                f"{template_base}/api/routes.j2",
                context
            )
            files[f"src/{pkg}/api/dependencies.py"] = self.template_engine.render(
                f"{template_base}/api/dependencies.j2",
                context
            )

            # Application layer
            files[f"src/{pkg}/application/services.py"] = self.template_engine.render(
                f"{template_base}/application/services.j2",
                context
            )
            files[f"src/{pkg}/application/use_cases.py"] = self.template_engine.render(
                f"{template_base}/application/use_cases.j2",
                context
            )

            # Domain layer
            files[f"src/{pkg}/domain/models.py"] = self.template_engine.render(
                f"{template_base}/domain/models.j2",
                context
            )
            files[f"src/{pkg}/domain/repositories.py"] = self.template_engine.render(
                f"{template_base}/domain/repositories.j2",
                context
            )

            # Infrastructure layer
            if spec.features.database:
                files[f"src/{pkg}/infrastructure/database.py"] = self.template_engine.render(
                    f"{template_base}/infrastructure/database.j2",
                    context
                )

            if spec.features.cache:
                files[f"src/{pkg}/infrastructure/cache.py"] = self.template_engine.render(
                    f"{template_base}/infrastructure/cache.j2",
                    context
                )

            # Main entry point
            files[f"src/{pkg}/main.py"] = self.template_engine.render(
                f"{template_base}/main.j2",
                context
            )

        return files

    def _generate_frontend_code(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any],
        template_base: str
    ) -> Dict[str, str]:
        """Generate frontend source code."""
        files = {}

        # React/TypeScript structure
        if spec.framework in ["react", "nextjs"]:
            files["src/App.tsx"] = self.template_engine.render(
                f"{template_base}/App.tsx.j2",
                context
            )
            files["src/components/Button.tsx"] = self.template_engine.render(
                f"{template_base}/components/Button.tsx.j2",
                context
            )

        return files

    def _generate_ai_agent_code(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any],
        template_base: str
    ) -> Dict[str, str]:
        """Generate AI agent source code."""
        files = {}
        pkg = context["package_name"]

        files[f"src/{pkg}/agent.py"] = self.template_engine.render(
            f"{template_base}/agent.j2",
            context
        )
        files[f"src/{pkg}/tools.py"] = self.template_engine.render(
            f"{template_base}/tools.j2",
            context
        )

        return files

    def _generate_tests(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate test suites."""
        files = {}
        pkg = context["package_name"]

        if spec.language == Language.PYTHON:
            # pytest configuration
            files["pytest.ini"] = self.template_engine.render(
                "python/pytest.ini.j2",
                context
            )

            # Unit tests
            if spec.deliverables.tests.unit:
                files[f"tests/unit/test_{pkg}.py"] = self.template_engine.render(
                    "python/tests/test_unit.j2",
                    context
                )

            # Integration tests
            if spec.deliverables.tests.integration:
                files[f"tests/integration/test_api.py"] = self.template_engine.render(
                    "python/tests/test_integration.j2",
                    context
                )

        elif spec.language == Language.TYPESCRIPT:
            files["jest.config.js"] = self.template_engine.render(
                "typescript/jest.config.js.j2",
                context
            )
            files["tests/app.test.ts"] = self.template_engine.render(
                "typescript/tests/app.test.ts.j2",
                context
            )

        return files

    def _generate_docker(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Docker configuration."""
        files = {}

        files["Dockerfile"] = self.template_engine.render(
            f"docker/{spec.language.value}/Dockerfile.j2",
            context
        )

        files[".dockerignore"] = self.template_engine.render(
            "docker/.dockerignore.j2",
            context
        )

        files["docker-compose.yml"] = self.template_engine.render(
            "docker/docker-compose.yml.j2",
            context
        )

        return files

    def _generate_kubernetes(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Kubernetes manifests."""
        files = {}

        if spec.deliverables.kubernetes.deployment:
            files["k8s/deployment.yaml"] = self.template_engine.render(
                "k8s/deployment.yaml.j2",
                context
            )

        if spec.deliverables.kubernetes.service:
            files["k8s/service.yaml"] = self.template_engine.render(
                "k8s/service.yaml.j2",
                context
            )

        if spec.deliverables.kubernetes.ingress:
            files["k8s/ingress.yaml"] = self.template_engine.render(
                "k8s/ingress.yaml.j2",
                context
            )

        if spec.deliverables.kubernetes.hpa:
            files["k8s/hpa.yaml"] = self.template_engine.render(
                "k8s/hpa.yaml.j2",
                context
            )

        if spec.deliverables.kubernetes.network_policy:
            files["k8s/network-policy.yaml"] = self.template_engine.render(
                "k8s/network-policy.yaml.j2",
                context
            )

        return files

    def _generate_cicd(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate CI/CD pipeline configuration."""
        files = {}

        platform = spec.deliverables.ci_cd.platform

        if platform == "github-actions":
            files[".github/workflows/ci.yml"] = self.template_engine.render(
                "cicd/github-actions/ci.yml.j2",
                context
            )
            files[".github/workflows/cd.yml"] = self.template_engine.render(
                "cicd/github-actions/cd.yml.j2",
                context
            )

        elif platform == "gitlab-ci":
            files[".gitlab-ci.yml"] = self.template_engine.render(
                "cicd/gitlab-ci/gitlab-ci.yml.j2",
                context
            )

        elif platform == "drone":
            files[".drone.yml"] = self.template_engine.render(
                "cicd/drone/drone.yml.j2",
                context
            )

        return files

    def _generate_documentation(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate project documentation."""
        files = {}

        # API documentation
        if spec.features.api.rest:
            files["docs/api/openapi.yaml"] = self.template_engine.render(
                "docs/openapi.yaml.j2",
                context
            )

        # Architecture documentation
        files["docs/architecture/README.md"] = self.template_engine.render(
            "docs/architecture.md.j2",
            context
        )

        # Contributing guide
        if spec.deliverables.documentation.contributing:
            files["CONTRIBUTING.md"] = self.template_engine.render(
                "common/CONTRIBUTING.md.j2",
                context
            )

        return files

    def _generate_governance_docs(
        self,
        spec: ProjectSpec,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate governance and compliance documentation."""
        files = {}

        # SBOM
        if spec.governance.sbom:
            files["governance/SBOM.json"] = self.template_engine.render(
                "governance/sbom.json.j2",
                context
            )

        # Compliance declaration
        files["governance/COMPLIANCE.md"] = self.template_engine.render(
            "governance/compliance.md.j2",
            context
        )

        # Security policy
        files["SECURITY.md"] = self.template_engine.render(
            "common/SECURITY.md.j2",
            context
        )

        return files
