"""
Architecture Configuration (架構配置)

Defines the recommended technology stack for SynergyMesh:
- Python 3.11+ for AI/ML core (80% of AI agents use Python)
- TypeScript for system orchestration and UI
- Hybrid architecture for optimal performance

Reference: Python supports 80% of AI agent implementations [4]
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LanguageType(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


class ArchitectureLayer(Enum):
    """System architecture layers"""
    AI_CORE = "ai_core"                    # AI/ML core (Python)
    ORCHESTRATION = "orchestration"         # System orchestration (TypeScript)
    INTEGRATION = "integration"             # External integrations
    PRESENTATION = "presentation"           # UI layer
    DATA = "data"                          # Data layer
    INFRASTRUCTURE = "infrastructure"       # Infrastructure layer


class FrameworkCategory(Enum):
    """Framework categories"""
    AI_AGENT = "ai_agent"
    ML_LIBRARY = "ml_library"
    WEB_FRAMEWORK = "web_framework"
    DATABASE = "database"
    MESSAGING = "messaging"
    MONITORING = "monitoring"
    TESTING = "testing"


@dataclass
class LanguageConfig:
    """Configuration for a programming language
    
    語言配置：定義每種編程語言的使用場景和最佳實踐
    """
    name: str
    version: str
    language_type: LanguageType
    primary_use_cases: list[str]
    strengths: list[str]
    weaknesses: list[str]
    adoption_rate: float  # 0-100%
    ecosystem_maturity: str  # "emerging", "mature", "established"

    def is_suitable_for(self, use_case: str) -> bool:
        """Check if language is suitable for a use case"""
        return use_case.lower() in [uc.lower() for uc in self.primary_use_cases]


@dataclass
class FrameworkConfig:
    """Configuration for a framework
    
    框架配置：定義框架的特性、用途和整合方式
    """
    id: str
    name: str
    version: str
    category: FrameworkCategory
    language: LanguageType
    description: str
    features: list[str]
    use_cases: list[str]
    dependencies: list[str]
    integration_complexity: str  # "low", "medium", "high"
    documentation_url: str
    is_recommended: bool = True

    def get_install_command(self) -> str:
        """Get installation command for the framework"""
        if self.language == LanguageType.PYTHON:
            return f"pip install {self.name.lower().replace(' ', '-')}"
        elif self.language in [LanguageType.TYPESCRIPT, LanguageType.JAVASCRIPT]:
            return f"npm install {self.name.lower().replace(' ', '-')}"
        return f"# Install {self.name} manually"


@dataclass
class LayerConfig:
    """Configuration for an architecture layer
    
    層級配置：定義每個架構層的職責和技術選擇
    """
    layer: ArchitectureLayer
    primary_language: LanguageType
    secondary_languages: list[LanguageType]
    frameworks: list[str]
    responsibilities: list[str]
    communication_protocols: list[str]
    scaling_strategy: str


@dataclass
class TechStackConfig:
    """Complete technology stack configuration
    
    完整技術棧配置：SynergyMesh 專案的推薦技術棧
    
    核心原則：
    1. Python 用於 AI/ML 核心（80% AI 代理採用）
    2. TypeScript 用於系統編排和 UI
    3. 混合架構實現最佳效能
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "SynergyMesh Tech Stack"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)

    # Language configurations
    languages: dict[str, LanguageConfig] = field(default_factory=dict)

    # Framework configurations
    frameworks: dict[str, FrameworkConfig] = field(default_factory=dict)

    # Layer configurations
    layers: dict[str, LayerConfig] = field(default_factory=dict)

    # Architecture metadata
    architecture_type: str = "hybrid"
    primary_pattern: str = "microservices"
    communication_pattern: str = "event-driven"

    def get_frameworks_for_layer(self, layer: ArchitectureLayer) -> list[FrameworkConfig]:
        """Get all frameworks recommended for a specific layer"""
        if layer.value not in self.layers:
            return []
        layer_config = self.layers[layer.value]
        return [
            self.frameworks[fw_id]
            for fw_id in layer_config.frameworks
            if fw_id in self.frameworks
        ]

    def get_frameworks_by_category(self, category: FrameworkCategory) -> list[FrameworkConfig]:
        """Get all frameworks in a specific category"""
        return [
            fw for fw in self.frameworks.values()
            if fw.category == category
        ]

    def validate(self) -> dict[str, Any]:
        """Validate the tech stack configuration"""
        issues = []
        warnings = []

        # Check for required layers
        required_layers = [ArchitectureLayer.AI_CORE, ArchitectureLayer.ORCHESTRATION]
        for layer in required_layers:
            if layer.value not in self.layers:
                issues.append(f"Missing required layer: {layer.value}")

        # Check for Python in AI core
        if ArchitectureLayer.AI_CORE.value in self.layers:
            ai_layer = self.layers[ArchitectureLayer.AI_CORE.value]
            if ai_layer.primary_language != LanguageType.PYTHON:
                warnings.append(
                    "AI core layer should use Python (80% of AI agents use Python)"
                )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


def get_recommended_stack() -> TechStackConfig:
    """Get the recommended technology stack for SynergyMesh
    
    推薦技術棧：基於研究資料的最佳實踐
    
    參考：
    - Python dominates with 51% adoption for AI [4]
    - LangChain, CrewAI, AutoGen for multi-agent [2][7]
    - TypeScript for type-safe orchestration
    """
    config = TechStackConfig()

    # Configure languages
    config.languages = {
        "python": LanguageConfig(
            name="Python",
            version="3.11+",
            language_type=LanguageType.PYTHON,
            primary_use_cases=[
                "AI/ML development",
                "Data processing",
                "Agent implementation",
                "Model training",
                "Predictive analytics"
            ],
            strengths=[
                "Rich AI/ML ecosystem",
                "Easy to learn and use",
                "Extensive library support",
                "Strong community",
                "80% AI agent adoption"
            ],
            weaknesses=[
                "Slower execution than compiled languages",
                "GIL limitations for threading",
                "Memory consumption"
            ],
            adoption_rate=51.0,
            ecosystem_maturity="established"
        ),
        "typescript": LanguageConfig(
            name="TypeScript",
            version="5.0+",
            language_type=LanguageType.TYPESCRIPT,
            primary_use_cases=[
                "System orchestration",
                "API development",
                "Frontend development",
                "MCP server integration",
                "Real-time processing"
            ],
            strengths=[
                "Type safety",
                "Excellent async handling",
                "Unified frontend/backend",
                "Strong tooling",
                "Modern language features"
            ],
            weaknesses=[
                "Compilation step required",
                "Complex type system",
                "Smaller AI ecosystem"
            ],
            adoption_rate=30.0,
            ecosystem_maturity="mature"
        )
    }

    # Configure frameworks
    config.frameworks = {
        # AI Agent Frameworks (Python)
        "langchain": FrameworkConfig(
            id="langchain",
            name="LangChain",
            version="0.1.0+",
            category=FrameworkCategory.AI_AGENT,
            language=LanguageType.PYTHON,
            description="Framework for developing applications powered by language models",
            features=[
                "LLM abstraction",
                "Chain composition",
                "Agent creation",
                "Tool integration",
                "Memory management",
                "Prompt templates"
            ],
            use_cases=[
                "Conversational AI",
                "Document Q&A",
                "Code generation",
                "Task automation"
            ],
            dependencies=["openai", "tiktoken", "pydantic"],
            integration_complexity="medium",
            documentation_url="https://python.langchain.com/docs/",
            is_recommended=True
        ),
        "crewai": FrameworkConfig(
            id="crewai",
            name="CrewAI",
            version="0.28.0+",
            category=FrameworkCategory.AI_AGENT,
            language=LanguageType.PYTHON,
            description="Framework for orchestrating role-playing AI agents",
            features=[
                "Role-based agents",
                "Task delegation",
                "Crew management",
                "Process orchestration",
                "Inter-agent communication"
            ],
            use_cases=[
                "Multi-agent collaboration",
                "Complex task automation",
                "Team simulation",
                "Workflow automation"
            ],
            dependencies=["langchain", "openai"],
            integration_complexity="medium",
            documentation_url="https://docs.crewai.com/",
            is_recommended=True
        ),
        "autogen": FrameworkConfig(
            id="autogen",
            name="Microsoft AutoGen",
            version="0.2.0+",
            category=FrameworkCategory.AI_AGENT,
            language=LanguageType.PYTHON,
            description="Framework for building multi-agent conversational systems",
            features=[
                "Conversable agents",
                "Human-in-the-loop",
                "Code execution",
                "Group chat",
                "Customizable agents"
            ],
            use_cases=[
                "Software development",
                "Research automation",
                "Complex problem solving",
                "Enterprise workflows"
            ],
            dependencies=["openai", "docker"],
            integration_complexity="high",
            documentation_url="https://microsoft.github.io/autogen/",
            is_recommended=True
        ),
        "langgraph": FrameworkConfig(
            id="langgraph",
            name="LangGraph",
            version="0.0.1+",
            category=FrameworkCategory.AI_AGENT,
            language=LanguageType.PYTHON,
            description="Library for building stateful, multi-actor applications with LLMs",
            features=[
                "State machine",
                "Cyclic workflows",
                "Persistence",
                "Human-in-the-loop",
                "Streaming"
            ],
            use_cases=[
                "Complex workflows",
                "Stateful agents",
                "Multi-step reasoning",
                "Iterative processes"
            ],
            dependencies=["langchain"],
            integration_complexity="medium",
            documentation_url="https://langchain-ai.github.io/langgraph/",
            is_recommended=True
        ),
        # ML Libraries (Python)
        "pytorch": FrameworkConfig(
            id="pytorch",
            name="PyTorch",
            version="2.0+",
            category=FrameworkCategory.ML_LIBRARY,
            language=LanguageType.PYTHON,
            description="Open source machine learning framework",
            features=[
                "Dynamic computation graphs",
                "GPU acceleration",
                "Automatic differentiation",
                "Model hub",
                "Distributed training"
            ],
            use_cases=[
                "Deep learning",
                "Model training",
                "Computer vision",
                "NLP"
            ],
            dependencies=["numpy"],
            integration_complexity="medium",
            documentation_url="https://pytorch.org/docs/",
            is_recommended=True
        ),
        "transformers": FrameworkConfig(
            id="transformers",
            name="Hugging Face Transformers",
            version="4.30+",
            category=FrameworkCategory.ML_LIBRARY,
            language=LanguageType.PYTHON,
            description="State-of-the-art machine learning for PyTorch, TensorFlow, JAX",
            features=[
                "Pre-trained models",
                "Model hub",
                "Fine-tuning",
                "Inference optimization",
                "Pipeline API"
            ],
            use_cases=[
                "NLP tasks",
                "Text generation",
                "Embeddings",
                "Sentiment analysis"
            ],
            dependencies=["pytorch", "tokenizers"],
            integration_complexity="low",
            documentation_url="https://huggingface.co/docs/transformers/",
            is_recommended=True
        ),
        # Web Frameworks
        "fastapi": FrameworkConfig(
            id="fastapi",
            name="FastAPI",
            version="0.100+",
            category=FrameworkCategory.WEB_FRAMEWORK,
            language=LanguageType.PYTHON,
            description="Modern, fast web framework for building APIs with Python",
            features=[
                "Async support",
                "OpenAPI docs",
                "Type hints",
                "Dependency injection",
                "WebSocket support"
            ],
            use_cases=[
                "REST APIs",
                "ML model serving",
                "Microservices",
                "Real-time apps"
            ],
            dependencies=["starlette", "pydantic"],
            integration_complexity="low",
            documentation_url="https://fastapi.tiangolo.com/",
            is_recommended=True
        ),
        "express": FrameworkConfig(
            id="express",
            name="Express.js",
            version="4.18+",
            category=FrameworkCategory.WEB_FRAMEWORK,
            language=LanguageType.TYPESCRIPT,
            description="Fast, unopinionated, minimalist web framework for Node.js",
            features=[
                "Middleware support",
                "Routing",
                "Template engines",
                "Static files",
                "Error handling"
            ],
            use_cases=[
                "REST APIs",
                "Web applications",
                "Microservices",
                "Real-time apps"
            ],
            dependencies=["node"],
            integration_complexity="low",
            documentation_url="https://expressjs.com/",
            is_recommended=True
        )
    }

    # Configure layers
    config.layers = {
        ArchitectureLayer.AI_CORE.value: LayerConfig(
            layer=ArchitectureLayer.AI_CORE,
            primary_language=LanguageType.PYTHON,
            secondary_languages=[],
            frameworks=["langchain", "crewai", "autogen", "langgraph", "pytorch", "transformers"],
            responsibilities=[
                "AI agent implementation",
                "ML model training and inference",
                "Decision making algorithms",
                "Natural language processing",
                "Predictive analytics"
            ],
            communication_protocols=["gRPC", "REST", "WebSocket"],
            scaling_strategy="horizontal_pod_autoscaling"
        ),
        ArchitectureLayer.ORCHESTRATION.value: LayerConfig(
            layer=ArchitectureLayer.ORCHESTRATION,
            primary_language=LanguageType.TYPESCRIPT,
            secondary_languages=[LanguageType.PYTHON],
            frameworks=["express", "fastapi"],
            responsibilities=[
                "System coordination",
                "Task scheduling",
                "Event processing",
                "API gateway",
                "Service mesh management"
            ],
            communication_protocols=["REST", "WebSocket", "gRPC"],
            scaling_strategy="kubernetes_hpa"
        ),
        ArchitectureLayer.INTEGRATION.value: LayerConfig(
            layer=ArchitectureLayer.INTEGRATION,
            primary_language=LanguageType.TYPESCRIPT,
            secondary_languages=[LanguageType.PYTHON],
            frameworks=["express"],
            responsibilities=[
                "External system integration",
                "Database connections",
                "Cloud provider interfaces",
                "MCP server integration",
                "Third-party API adapters"
            ],
            communication_protocols=["REST", "GraphQL", "gRPC"],
            scaling_strategy="connection_pooling"
        ),
        ArchitectureLayer.DATA.value: LayerConfig(
            layer=ArchitectureLayer.DATA,
            primary_language=LanguageType.PYTHON,
            secondary_languages=[LanguageType.TYPESCRIPT],
            frameworks=["pytorch", "transformers"],
            responsibilities=[
                "Data processing",
                "ETL pipelines",
                "Feature engineering",
                "Data validation",
                "Storage management"
            ],
            communication_protocols=["REST", "gRPC", "Kafka"],
            scaling_strategy="data_partitioning"
        )
    }

    return config


# Convenience function to get stack summary
def get_stack_summary() -> dict[str, Any]:
    """Get a summary of the recommended tech stack
    
    獲取技術棧摘要
    """
    stack = get_recommended_stack()

    return {
        "name": stack.name,
        "version": stack.version,
        "architecture_type": stack.architecture_type,
        "primary_languages": {
            "ai_core": "Python 3.11+",
            "orchestration": "TypeScript 5.0+"
        },
        "key_frameworks": {
            "ai_agents": ["LangChain", "CrewAI", "AutoGen", "LangGraph"],
            "ml_libraries": ["PyTorch", "Transformers"],
            "web_frameworks": ["FastAPI", "Express.js"]
        },
        "validation": stack.validate()
    }
