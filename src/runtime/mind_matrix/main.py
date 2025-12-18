# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Mind Matrix Main Module
#                    心智矩陣主模組 - 可運行且相容現有系統
# ═══════════════════════════════════════════════════════════════════════════════
"""
MindMatrix main module.

可運行且相容現有系統的強化版本，含 schema 驗證與啟動自檢。
This module provides a runnable and backward-compatible enhanced version
with schema validation and boot-time self-checks.
"""

import sys
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


# ------------ Pydantic Schemas (嚴格 Schema 驗證) ------------


class ExecutiveRole(BaseModel):
    """
    執行長角色定義 (Executive Role Definition).

    Defines the structure for executive-level roles in the system.
    """

    id: str
    title: str
    kind: str
    mission: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)


class ToolPipeline(BaseModel):
    """
    工具管線定義 (Tool Pipeline Definition).

    Defines the eight-stage tool pipeline.
    """

    stages: list[str]


class YamlValidationPipeline(BaseModel):
    """
    YAML 驗證管線定義 (YAML Validation Pipeline Definition).

    Defines the seven-stage YAML validation pipeline.
    """

    stages: list[str]


class CognitiveStackItem(BaseModel):
    """
    認知棧層級項目 (Cognitive Stack Item).

    Defines a single layer in the cognitive stack.
    """

    id: str
    name: str
    responsibilities: list[str] = Field(default_factory=list)


class ExecutiveLayer(BaseModel):
    """
    執行層定義 (Executive Layer Definition).

    Defines the executive layer including roles and cognitive stack.
    """

    version: str
    roles: list[ExecutiveRole] = Field(default_factory=list)
    cognitive_stack: list[CognitiveStackItem] = Field(default_factory=list)


class AgentDefinition(BaseModel):
    """
    代理定義 (Agent Definition).

    Defines a single agent in the multi-agent hypergraph.
    """

    name: str
    kind: str


class CoordinationMechanisms(BaseModel):
    """
    協調機制定義 (Coordination Mechanisms Definition).

    Defines the coordination mechanisms for the multi-agent hypergraph.
    """

    mechanisms: list[str] = Field(default_factory=list)


class MultiAgentHypergraph(BaseModel):
    """
    多代理超圖定義 (Multi-Agent Hypergraph Definition).

    Defines the multi-agent hypergraph structure.
    """

    agents: list[AgentDefinition] = Field(default_factory=list)
    coordination: CoordinationMechanisms = Field(default_factory=CoordinationMechanisms)


class SLSAEvidence(BaseModel):
    """
    SLSA 證據配置 (SLSA Evidence Configuration).

    Defines SLSA evidence production and storage settings.
    """

    produce: bool = True
    store: str = "immutable_audit_log"


class SLSAConfig(BaseModel):
    """
    SLSA 配置 (SLSA Configuration).

    Defines SLSA compliance level and evidence settings.
    """

    level: str = "L3"
    evidence: SLSAEvidence = Field(default_factory=SLSAEvidence)


class MindMatrixModel(BaseModel):
    """
    心智矩陣模型 (Mind Matrix Model).

    The root model for the mind matrix configuration with strict validation.
    """

    version: str
    governance_principles: list[str]
    executive_layer: ExecutiveLayer
    multi_agent_hypergraph: MultiAgentHypergraph
    tool_pipeline: ToolPipeline
    yaml_validation_pipeline: YamlValidationPipeline
    slsa: SLSAConfig = Field(default_factory=SLSAConfig)


# ------------ Core Wrapper (核心包裝器) ------------


class MindMatrix:
    """
    心智矩陣核心類別 (Mind Matrix Core Class).

    讀取 topology config，並以 Pydantic 進行嚴格 schema 驗證。
    相容：保持現有 main.py 的使用方式不變。

    Reads topology config and performs strict schema validation with Pydantic.
    Maintains backward compatibility with existing usage patterns.
    """

    def __init__(self, topology_config: dict[str, Any]) -> None:
        """
        初始化心智矩陣 (Initialize Mind Matrix).

        Args:
            topology_config: The topology configuration dictionary.

        Raises:
            ValidationError: When the schema validation fails.
        """
        self.raw = topology_config
        self.config = topology_config.get("mind_matrix", {})
        # schema 驗證：缺失或類型錯誤會拋出 ValidationError
        try:
            self.model = MindMatrixModel(**self.config)
        except ValidationError as e:
            print("[FATAL] mind_matrix schema 驗證失敗：", file=sys.stderr)
            print(e.json(), file=sys.stderr)
            raise

    # -------- Helpers（輔助方法） --------

    def get_executive_roles(self) -> list[ExecutiveRole]:
        """
        取得所有執行長角色 (Get all executive roles).

        Returns:
            List of ExecutiveRole objects.
        """
        return self.model.executive_layer.roles

    def get_ceo_mission(self, ceo_id: str = "synergymesh.ceo") -> Optional[list[str]]:
        """
        取得特定執行長的使命 (Get mission for a specific executive).

        Args:
            ceo_id: The ID of the executive role to look up.

        Returns:
            List of mission statements, or None if not found.
        """
        for role in self.model.executive_layer.roles:
            if role.id == ceo_id:
                return role.mission
        return None

    def get_cognitive_stack(self) -> list[CognitiveStackItem]:
        """
        取得認知棧層級 (Get cognitive stack layers).

        Returns:
            List of CognitiveStackItem objects.
        """
        return self.model.executive_layer.cognitive_stack

    def get_tool_pipeline_stages(self) -> list[str]:
        """
        取得工具管線的八階段 (Get eight stages of tool pipeline).

        Returns:
            List of stage names.
        """
        return self.model.tool_pipeline.stages

    def get_yaml_validation_stages(self) -> list[str]:
        """
        取得 YAML 驗證的七階段 (Get seven stages of YAML validation).

        Returns:
            List of validation stage names.
        """
        return self.model.yaml_validation_pipeline.stages

    def get_governance_principles(self) -> list[str]:
        """
        取得治理原則 (Get governance principles).

        Returns:
            List of governance principles.
        """
        return self.model.governance_principles

    def get_agents(self) -> list[AgentDefinition]:
        """
        取得所有代理定義 (Get all agent definitions).

        Returns:
            List of AgentDefinition objects.
        """
        return self.model.multi_agent_hypergraph.agents

    def get_coordination_mechanisms(self) -> list[str]:
        """
        取得協調機制 (Get coordination mechanisms).

        Returns:
            List of coordination mechanism names.
        """
        return self.model.multi_agent_hypergraph.coordination.mechanisms

    def get_slsa_level(self) -> str:
        """
        取得 SLSA 等級 (Get SLSA level).

        Returns:
            SLSA compliance level string.
        """
        return self.model.slsa.level

    # -------- Bootstrap（啟動方法） --------

    @classmethod
    def bootstrap(cls, config_path: Optional[str] = None) -> "MindMatrix":
        """
        啟動時載入拓撲，進行輕量自檢 (Bootstrap and perform self-check).

        - 工具管線八階段
        - YAML 驗證管線七階段
        並輸出執行長摘要，便於人工校驗。

        Args:
            config_path: Optional path to the topology config file.
                         Defaults to "config/topology-mind-matrix.yaml".

        Returns:
            Initialized MindMatrix instance.

        Raises:
            AssertionError: When self-checks fail.
            FileNotFoundError: When config file is not found.
        """
        if config_path is None:
            # Try to find config relative to current directory or module location
            possible_paths = [
                Path("config/topology-mind-matrix.yaml"),
                Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml",
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
            else:
                config_path = "config/topology-mind-matrix.yaml"

        with open(config_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)

        mm = cls(topology)

        # 啟動自檢（強相容檢查）
        tool_stages = mm.get_tool_pipeline_stages()
        yaml_stages = mm.get_yaml_validation_stages()

        assert len(tool_stages) == 8, f"工具管線必須為八階段，目前有 {len(tool_stages)} 階段"
        assert len(yaml_stages) == 7, f"YAML 驗證管線必須為七階段，目前有 {len(yaml_stages)} 階段"

        print("✅ MindMatrix 啟動自檢通過：八階段工具管線、七階段 YAML 驗證")

        # 輸出角色摘要（相容現有使用者習慣）
        for role in mm.get_executive_roles():
            print(f"🎯 {role.title} ({role.id}) | 領域: {', '.join(role.domains)}")
            if role.id == "synergymesh.ceo":
                print(f"   使命: {', '.join(role.mission)}")

        return mm


if __name__ == "__main__":
    # 默認：啟動自檢
    mm = MindMatrix.bootstrap()

    # 可選：執行長全自動一次
    try:
        # Try relative import first, then absolute
        try:
            from runtime.mind_matrix.executive_auto import ExecutiveAutoController
        except ImportError:
            from executive_auto import ExecutiveAutoController

        controller = ExecutiveAutoController()
        report = controller.run_once()
        print(f"🚀 Autonomous Executive 完成一次閉環，審計事件數：{len(report['audit'])}")
    except ImportError as ex:
        print(f"[WARN] 自動執行長模組未載入：{ex}")
    except Exception as ex:
        print(f"[WARN] 自動執行長未啟動：{ex}")
