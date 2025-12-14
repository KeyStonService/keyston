"""
Project Specification - 專案規格定義

Defines the data structures for project specifications.
定義專案規格的數據結構。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ProjectType(Enum):
    """專案類型"""
    MICROSERVICE = "microservice"
    FRONTEND = "frontend"
    AI_AGENT = "ai-agent"
    DATA_PIPELINE = "data-pipeline"
    LIBRARY = "library"
    CLI_TOOL = "cli-tool"
    INFRASTRUCTURE = "infrastructure"


class Language(Enum):
    """支持的程式語言"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"


class ArchitecturePattern(Enum):
    """架構模式"""
    CLEAN_ARCHITECTURE = "clean-architecture"
    HEXAGONAL = "hexagonal"
    DDD = "domain-driven-design"
    LAYERED = "layered"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"


@dataclass
class APISpec:
    """API 規格"""
    rest: bool = True
    graphql: bool = False
    grpc: bool = False
    websocket: bool = False
    openapi_version: str = "3.1.0"


@dataclass
class DatabaseSpec:
    """資料庫規格"""
    type: str = "postgresql"  # postgresql, mysql, mongodb, redis, etc.
    orm: Optional[str] = None  # sqlalchemy, typeorm, gorm, etc.
    migrations: Optional[str] = None  # alembic, flyway, etc.
    connection_pool: bool = True


@dataclass
class CacheSpec:
    """快取規格"""
    type: str = "redis"  # redis, memcached, etc.
    serializer: str = "json"  # json, msgpack, pickle
    ttl_default: int = 3600


@dataclass
class MessagingSpec:
    """訊息系統規格"""
    type: str = "kafka"  # kafka, rabbitmq, nats, etc.
    topics: List[str] = field(default_factory=list)
    consumer_groups: List[str] = field(default_factory=list)


@dataclass
class ObservabilitySpec:
    """可觀測性規格"""
    logging: str = "structured"  # structured, json, plain
    log_level: str = "INFO"
    metrics: str = "prometheus"  # prometheus, statsd, datadog
    tracing: str = "opentelemetry"  # opentelemetry, jaeger, zipkin
    health_checks: bool = True


@dataclass
class TestSpec:
    """測試規格"""
    unit: bool = True
    integration: bool = True
    e2e: bool = False
    coverage_threshold: int = 80
    framework: Optional[str] = None  # pytest, jest, go test, etc.


@dataclass
class DockerSpec:
    """Docker 規格"""
    multi_stage: bool = True
    base_image: Optional[str] = None
    healthcheck: bool = True
    security_scan: bool = True


@dataclass
class KubernetesSpec:
    """Kubernetes 規格"""
    deployment: bool = True
    service: bool = True
    ingress: bool = False
    configmap: bool = True
    secret: bool = True
    hpa: bool = False  # Horizontal Pod Autoscaler
    network_policy: bool = True
    service_mesh: Optional[str] = None  # istio, linkerd, etc.


@dataclass
class CICDSpec:
    """CI/CD 規格"""
    platform: str = "github-actions"  # github-actions, gitlab-ci, drone, etc.
    stages: List[str] = field(default_factory=lambda: [
        "lint", "test", "build", "security-scan", "deploy"
    ])
    deployment_strategy: str = "rolling"  # rolling, blue-green, canary
    auto_deploy: bool = False


@dataclass
class DocumentationSpec:
    """文檔規格"""
    api_docs: str = "openapi"  # openapi, asyncapi, graphql-schema
    architecture: str = "c4-model"  # c4-model, uml, archimate
    readme: str = "comprehensive"  # minimal, standard, comprehensive
    changelog: bool = True
    contributing: bool = True


@dataclass
class FeatureSpec:
    """功能規格"""
    api: APISpec = field(default_factory=APISpec)
    database: Optional[DatabaseSpec] = None
    cache: Optional[CacheSpec] = None
    messaging: Optional[MessagingSpec] = None
    observability: ObservabilitySpec = field(default_factory=ObservabilitySpec)


@dataclass
class DeliverableSpec:
    """交付物規格"""
    source_code: bool = True
    tests: TestSpec = field(default_factory=TestSpec)
    docker: DockerSpec = field(default_factory=DockerSpec)
    kubernetes: KubernetesSpec = field(default_factory=KubernetesSpec)
    ci_cd: CICDSpec = field(default_factory=CICDSpec)
    documentation: DocumentationSpec = field(default_factory=DocumentationSpec)


@dataclass
class GovernanceSpec:
    """治理規格"""
    compliance: List[str] = field(default_factory=lambda: ["ISO-42001"])
    security_level: str = "high"  # low, medium, high, critical
    audit_trail: bool = True
    sbom: bool = True  # Software Bill of Materials
    provenance: str = "slsa-level-3"  # SLSA provenance level
    license: str = "MIT"


@dataclass
class ArchitectureSpec:
    """架構規格"""
    pattern: ArchitecturePattern = ArchitecturePattern.CLEAN_ARCHITECTURE
    layers: List[str] = field(default_factory=lambda: [
        "presentation", "application", "domain", "infrastructure"
    ])
    bounded_contexts: List[str] = field(default_factory=list)


@dataclass
class ProjectSpec:
    """
    Complete project specification.

    完整的專案規格定義，用於驅動 Project Factory 生成專案。

    Example:
        >>> spec = ProjectSpec(
        ...     name="user-service",
        ...     type=ProjectType.MICROSERVICE,
        ...     language=Language.PYTHON,
        ...     framework="fastapi",
        ...     description="User management microservice"
        ... )
        >>>
        >>> # 配置功能
        >>> spec.features.database = DatabaseSpec(
        ...     type="postgresql",
        ...     orm="sqlalchemy"
        ... )
        >>>
        >>> # 配置治理
        >>> spec.governance.compliance = ["ISO-42001", "SOC2"]
    """

    # 基本資訊 Basic Information
    name: str
    type: ProjectType
    language: Language
    framework: str
    description: str = ""
    version: str = "1.0.0"

    # 架構 Architecture
    architecture: ArchitectureSpec = field(default_factory=ArchitectureSpec)

    # 功能 Features
    features: FeatureSpec = field(default_factory=FeatureSpec)

    # 交付物 Deliverables
    deliverables: DeliverableSpec = field(default_factory=DeliverableSpec)

    # 治理 Governance
    governance: GovernanceSpec = field(default_factory=GovernanceSpec)

    # 自定義配置 Custom Configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert specification to dictionary.

        將規格轉換為字典格式。

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "name": self.name,
            "type": self.type.value,
            "language": self.language.value,
            "framework": self.framework,
            "description": self.description,
            "version": self.version,
            "architecture": {
                "pattern": self.architecture.pattern.value,
                "layers": self.architecture.layers,
                "bounded_contexts": self.architecture.bounded_contexts,
            },
            # Additional fields would be serialized here
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSpec':
        """
        Create specification from dictionary.

        從字典創建規格實例。

        Args:
            data: Dictionary containing specification data

        Returns:
            ProjectSpec: New specification instance
        """
        # Basic parsing - would be more comprehensive in real implementation
        return cls(
            name=data["name"],
            type=ProjectType(data["type"]),
            language=Language(data["language"]),
            framework=data["framework"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
        )

    def validate(self) -> List[str]:
        """
        Validate specification for completeness and correctness.

        驗證規格的完整性和正確性。

        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []

        # Validate name
        if not self.name or not self.name.replace('-', '').replace('_', '').isalnum():
            errors.append(f"Invalid project name: {self.name}")

        # Validate framework compatibility
        if self.language == Language.PYTHON and self.framework not in [
            "fastapi", "flask", "django", "starlette"
        ]:
            errors.append(f"Unsupported framework {self.framework} for {self.language.value}")

        # Validate coverage threshold
        if not 0 <= self.deliverables.tests.coverage_threshold <= 100:
            errors.append(f"Invalid coverage threshold: {self.deliverables.tests.coverage_threshold}")

        return errors
