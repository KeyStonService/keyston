# core/architecture-stability 集成劇本（Integration Playbook）

- **Cluster ID**: `core/architecture-stability`
- **對應解構劇本**: `docs/refactor_playbooks/01_deconstruction/core/core__architecture_deconstruction.md`
- **對應重構劇本**: `docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md`
- **設計日期**: 2025-12-07
- **狀態**: ✅ 設計完成

---

## 1. 架構願景與目標

### 1.1 整體目標

基於解構分析的發現，本集成方案旨在：

1. **語言純度提升**
   - Python (69%) + TypeScript (27%) → **Python (70%) + TypeScript (30%)**
   - JavaScript 檔案 7 → **0**
   - 型別註解覆蓋率 50% → **85%+**

2. **架構清晰化**
   - 頂層散落檔案 11 個 → **組織到功能子目錄**
   - 明確定義公開 API 邊界
   - 打破循環依賴

3. **品質指標達標**
   - 測試覆蓋率: 55% → **80%**
   - 平均複雜度: 8.5 → **≤ 8.0**
   - Semgrep HIGH: 0 → **保持 0**

4. **可維護性提升**
   - 模組職責明確
   - 文件完整覆蓋
   - 降低變更成本

### 1.2 設計原則

遵循以下核心原則：

1. **Single Responsibility Principle (SRP)**
   - 每個模組/類別只有一個變更理由
   - 明確的職責邊界

2. **Dependency Inversion Principle (DIP)**
   - 高層模組不依賴低層模組，都依賴抽象
   - 引入 `core/interfaces/` 作為契約層

3. **Interface Segregation Principle (ISP)**
   - 客戶端不應依賴它不需要的介面
   - 小而專注的介面定義

4. **Open/Closed Principle (OCP)**
   - 對擴展開放，對修改封閉
   - 透過策略模式、外掛機制實現

5. **Layered Architecture**
   - 明確的層次結構
   - 單向依賴流

---

## 2. 新架構設計

### 2.1 目標目錄結構

```text
core/
├─ README.md                              # Core 引擎總覽
├─ __init__.py                            # 公開 API 定義
│
├─ interfaces/                            # 共享契約層 (新增)
│  ├─ __init__.py
│  ├─ service_interface.py                # 服務介面
│  ├─ processor_interface.py              # 處理器介面
│  ├─ runtime_interface.py                # Runtime 介面
│  └─ safety_interface.py                 # 安全機制介面
│
├─ ai_engines/                            # AI 引擎集合 (重組)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ decision/                           # 決策引擎
│  │  ├─ __init__.py
│  │  ├─ engine.py                        # 從 ai_decision_engine.py 遷移
│  │  ├─ strategies/
│  │  └─ tests/
│  ├─ context_understanding/              # 上下文理解
│  │  ├─ __init__.py
│  │  ├─ engine.py                        # 從 context_understanding_engine.py 遷移
│  │  └─ tests/
│  └─ hallucination_detection/            # 幻覺偵測
│     ├─ __init__.py
│     ├─ detector.py                      # 從 hallucination_detector.py 遷移
│     └─ tests/
│
├─ governance/                            # 治理子系統 (重組)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ hub.py                              # 從 auto_governance_hub.py 遷移
│  ├─ trust_engine.py                     # 從 autonomous_trust_engine.py 遷移
│  └─ tests/
│
├─ quality_assurance/                     # 品質保證 (重組)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ bug_detector.py                     # 從 auto_bug_detector.py 遷移
│  └─ tests/
│
├─ unified_integration/                   # 統一整合層 (保留，改進)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ cognitive_processor.py              # 重構降低複雜度
│  ├─ service_registry.py                 # 重構降低複雜度
│  ├─ configuration/                      # 配置子模組 (新增)
│  │  ├─ __init__.py
│  │  ├─ manager.py                       # 從 configuration_manager.py 遷移
│  │  ├─ optimizer.py                     # 從 configuration_optimizer.py 遷移
│  │  └─ work_manager.py                  # 從 work_configuration_manager.py 遷移
│  ├─ orchestration/                      # 編排子模組 (新增)
│  │  ├─ __init__.py
│  │  ├─ orchestrator.py                  # 從 system_orchestrator.py 遷移
│  │  └─ execution_system.py              # 從 deep_execution_system.py 遷移
│  ├─ integration_hub.py                  # 保留
│  ├─ cli_bridge.py                       # 保留
│  └─ tests/
│
├─ island_ai_runtime/                     # Island AI Runtime (保留，改進)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ runtime.py                          # 重構降低複雜度
│  ├─ agent_framework.py                  # 依賴 interfaces/
│  ├─ knowledge_engine.py
│  ├─ model_gateway.py
│  ├─ tool_executor.py
│  ├─ session_memory.py
│  ├─ safety_constitution.py
│  └─ tests/
│
├─ safety_mechanisms/                     # 安全機制 (保留，微調)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ circuit_breaker.py                  # 保留
│  ├─ emergency_stop.py                   # 保留
│  ├─ rollback_system.py                  # 保留
│  ├─ anomaly_detector.py                 # 保留
│  ├─ escalation_ladder.py                # 保留
│  ├─ safety_net.py                       # 保留
│  └─ tests/
│
├─ slsa_provenance/                       # SLSA 溯源 (保留)
│  ├─ __init__.py
│  ├─ README.md
│  ├─ provenance_generator.py
│  ├─ attestation_manager.py
│  ├─ signature_verifier.py
│  ├─ artifact_verifier.py
│  └─ tests/
│
├─ contract_service/                      # 合約服務 (保留)
│  └─ contracts-L1/
│     └─ contracts/
│        └─ src/
│
└─ advisory-database/                     # Advisory DB (JS→TS 遷移)
   ├─ README.md
   └─ src/
      ├─ index.ts                         # 從 .js 遷移
      ├─ types/
      ├─ utils.ts                         # 從 .js 遷移
      ├─ parser.ts                        # 從 .js 遷移
      └─ tests/
```

### 2.2 變更摘要

| 類型 | 變更項目 | 影響範圍 |
|------|----------|----------|
| 🆕 新增 | `core/interfaces/` | 全域 |
| 🆕 新增 | `core/ai_engines/` (3 子模組) | AI 功能 |
| 🆕 新增 | `core/governance/` | 治理功能 |
| 🆕 新增 | `core/quality_assurance/` | QA 功能 |
| 📦 重組 | `unified_integration/` → 子模組化 | 配置、編排 |
| 🔧 改進 | `island_ai_runtime/` → 依賴 interfaces | Runtime |
| ✅ 保留 | `safety_mechanisms/`, `slsa_provenance/` | 安全、溯源 |
| 🔄 遷移 | `advisory-database/src/*.js` → `.ts` | Advisory DB |

---

## 3. 組件對照與轉換映射

### 3.1 頂層檔案遷移映射

| 舊位置 | 新位置 | 變更類型 |
|--------|--------|----------|
| `core/ai_decision_engine.py` | `core/ai_engines/decision/engine.py` | 移動 + 重構 |
| `core/context_understanding_engine.py` | `core/ai_engines/context_understanding/engine.py` | 移動 + 重構 |
| `core/hallucination_detector.py` | `core/ai_engines/hallucination_detection/detector.py` | 移動 + 重構 |
| `core/auto_governance_hub.py` | `core/governance/hub.py` | 移動 + 重構 |
| `core/autonomous_trust_engine.py` | `core/governance/trust_engine.py` | 移動 + 重構 |
| `core/auto_bug_detector.py` | `core/quality_assurance/bug_detector.py` | 移動 + 重構 |

### 3.2 unified_integration/ 內部重組

| 舊檔案 | 新位置 | 理由 |
|--------|--------|------|
| `configuration_manager.py` | `configuration/manager.py` | 配置相關集中 |
| `configuration_optimizer.py` | `configuration/optimizer.py` | 配置相關集中 |
| `work_configuration_manager.py` | `configuration/work_manager.py` | 配置相關集中 |
| `system_orchestrator.py` | `orchestration/orchestrator.py` | 編排相關集中 |
| `deep_execution_system.py` | `orchestration/execution_system.py` | 編排相關集中 |

### 3.3 Import 路徑變更

**Before (舊)**:
```python
# 外部服務直接 import 內部實作
from core.ai_decision_engine import DecisionEngine
from core.unified_integration.cognitive_processor import CognitiveProcessor
from core.island_ai_runtime.runtime import Runtime
```

**After (新)**:
```python
# 透過公開 API import
from core import DecisionEngine, CognitiveProcessor, Runtime
# 或
from core.ai_engines.decision import DecisionEngine
from core.unified_integration import CognitiveProcessor
from core.island_ai_runtime import Runtime
```

**Shim Layer (過渡期)**:
```python
# core/ai_decision_engine.py (保留作為 shim)
import warnings
from core.ai_engines.decision import DecisionEngine

warnings.warn(
    "core.ai_decision_engine is deprecated. "
    "Use core.ai_engines.decision instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['DecisionEngine']
```

---

## 4. API 邊界與介面定義

### 4.1 公開 API 層級

#### Level 1: 頂層公開 API (`core/__init__.py`)

```python
"""
Unmanned Island Core Engine

Public API for core system components.
"""

# AI Engines
from core.ai_engines.decision import DecisionEngine
from core.ai_engines.context_understanding import ContextEngine
from core.ai_engines.hallucination_detection import HallucinationDetector

# Unified Integration
from core.unified_integration import (
    CognitiveProcessor,
    ServiceRegistry,
    IntegrationHub,
)

# Runtime
from core.island_ai_runtime import Runtime, AgentFramework

# Safety & Governance
from core.safety_mechanisms import CircuitBreaker, EmergencyStop
from core.governance import GovernanceHub, TrustEngine

# SLSA Provenance
from core.slsa_provenance import ProvenanceGenerator, AttestationManager

__all__ = [
    # AI Engines
    'DecisionEngine',
    'ContextEngine',
    'HallucinationDetector',
    # Unified Integration
    'CognitiveProcessor',
    'ServiceRegistry',
    'IntegrationHub',
    # Runtime
    'Runtime',
    'AgentFramework',
    # Safety & Governance
    'CircuitBreaker',
    'EmergencyStop',
    'GovernanceHub',
    'TrustEngine',
    # SLSA
    'ProvenanceGenerator',
    'AttestationManager',
]

__version__ = '3.0.0'
```

#### Level 2: 子模組公開 API

**`core/ai_engines/__init__.py`**:
```python
"""AI Engines Module"""

from core.ai_engines.decision import DecisionEngine
from core.ai_engines.context_understanding import ContextEngine
from core.ai_engines.hallucination_detection import HallucinationDetector

__all__ = ['DecisionEngine', 'ContextEngine', 'HallucinationDetector']
```

**`core/unified_integration/__init__.py`**:
```python
"""Unified Integration Layer"""

from core.unified_integration.cognitive_processor import CognitiveProcessor
from core.unified_integration.service_registry import ServiceRegistry
from core.unified_integration.integration_hub import IntegrationHub

# Configuration is internal, not exposed at top level
from core.unified_integration.configuration import ConfigurationManager

__all__ = [
    'CognitiveProcessor',
    'ServiceRegistry',
    'IntegrationHub',
    'ConfigurationManager',  # Expose for advanced users
]
```

### 4.2 介面契約層 (`core/interfaces/`)

#### `core/interfaces/service_interface.py`

```python
"""Service Interface Definitions"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ServiceMetadata:
    """Service metadata."""
    name: str
    version: str
    health_status: str
    dependencies: List[str]


class IService(ABC):
    """Base service interface."""
    
    @abstractmethod
    def start(self) -> None:
        """Start the service."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the service."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check service health."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> ServiceMetadata:
        """Get service metadata."""
        pass


class IServiceRegistry(ABC):
    """Service registry interface."""
    
    @abstractmethod
    def register(self, service: IService) -> None:
        """Register a service."""
        pass
    
    @abstractmethod
    def unregister(self, service_name: str) -> None:
        """Unregister a service."""
        pass
    
    @abstractmethod
    def discover(self, service_name: str) -> Optional[IService]:
        """Discover a service by name."""
        pass
    
    @abstractmethod
    def list_services(self) -> List[ServiceMetadata]:
        """List all registered services."""
        pass
```

#### `core/interfaces/processor_interface.py`

```python
"""Processor Interface Definitions"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ProcessingContext:
    """Processing context."""
    input_data: Dict[str, Any]
    metadata: Dict[str, Any]
    trace_id: str


@dataclass
class ProcessingResult:
    """Processing result."""
    output_data: Dict[str, Any]
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None


class IProcessor(ABC):
    """Base processor interface."""
    
    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingResult:
        """Process input and return result."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        pass


class ICognitiveProcessor(IProcessor):
    """Cognitive processor with four layers."""
    
    @abstractmethod
    def perceive(self, input_data: Dict[str, Any]) -> Any:
        """Perception layer."""
        pass
    
    @abstractmethod
    def reason(self, perceived_data: Any) -> Any:
        """Reasoning layer."""
        pass
    
    @abstractmethod
    def execute(self, reasoned_data: Any) -> Any:
        """Execution layer."""
        pass
    
    @abstractmethod
    def prove(self, executed_data: Any) -> ProcessingResult:
        """Proof layer."""
        pass
```

#### `core/interfaces/runtime_interface.py`

```python
"""Runtime Interface Definitions"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IRuntime(ABC):
    """Runtime interface."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize runtime."""
        pass
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Any:
        """Execute a task."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown runtime."""
        pass


class IAgentFramework(ABC):
    """Agent framework interface."""
    
    @abstractmethod
    def create_agent(self, agent_config: Dict[str, Any]) -> Any:
        """Create an agent."""
        pass
    
    @abstractmethod
    def run_agent(self, agent_id: str, input_data: Any) -> Any:
        """Run an agent."""
        pass
```

### 4.3 API 版本化策略

**版本規則**:
- **Major (3.x.x)**: Breaking changes
- **Minor (x.1.x)**: New features, backward compatible
- **Patch (x.x.1)**: Bug fixes, backward compatible

**Deprecation Policy**:
1. 在版本 N 標記為 `@deprecated`
2. 在版本 N+1 發出 `DeprecationWarning`
3. 在版本 N+2 移除

**範例**:
```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead. "
        "Will be removed in version 3.2.0.",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

---

## 5. 依賴關係與約束

### 5.1 依賴方向圖

```text
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│            (services/agents, apps/web, automation/)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     core/__init__.py                         │
│                     (Public API Layer)                       │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┬───────┘
    │         │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼         ▼
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
│ AI  │  │Unified│ │Runtime│ │Safety│ │SLSA │  │Govern│
│Engines│ │Integ. │ │       │ │Mech. │ │Prov.│  │-ance│
└──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
   │        │        │        │        │        │
   └────────┴────────┴────────┴────────┴────────┘
                      │
                      ▼
             ┌────────────────┐
             │ core/interfaces/│
             │ (Contract Layer)│
             └────────────────┘
                      │
                      ▼
             ┌────────────────┐
             │ infrastructure/ │
             │ shared/utils/   │
             └────────────────┘
```

### 5.2 允許與禁止的依賴

根據 `config/system-module-map.yaml`:

```yaml
architecture_constraints:
  allowed_dependencies:
    - "core/*"              # Core 內部可互相依賴
    - "infrastructure/*"    # 可依賴基礎設施
    - "shared/utils/*"      # 可依賴共用工具
  
  banned_dependencies:
    - "apps/**"             # 不可依賴應用層
    - "services/**"         # 不可依賴服務層
    - "automation/**"       # 不可依賴自動化層
  
  dependency_direction: "downstream_only"
```

### 5.3 打破循環依賴

**問題**: `unified_integration` ↔ `island_ai_runtime`

**解決方案**: 引入 `core/interfaces/`

**Before**:
```python
# unified_integration/cognitive_processor.py
from core.island_ai_runtime.runtime import Runtime  # 依賴 runtime

# island_ai_runtime/agent_framework.py
from core.unified_integration.service_registry import ServiceRegistry  # 依賴回去
```

**After**:
```python
# core/interfaces/runtime_interface.py
class IRuntime(ABC):
    @abstractmethod
    def execute(self, task): ...

# core/interfaces/service_interface.py
class IServiceRegistry(ABC):
    @abstractmethod
    def discover(self, name): ...

# unified_integration/cognitive_processor.py
from core.interfaces.runtime_interface import IRuntime  # 依賴介面

# island_ai_runtime/agent_framework.py
from core.interfaces.service_interface import IServiceRegistry  # 依賴介面

# island_ai_runtime/runtime.py
from core.interfaces.runtime_interface import IRuntime

class Runtime(IRuntime):  # 實作介面
    def execute(self, task):
        ...

# unified_integration/service_registry.py
from core.interfaces.service_interface import IServiceRegistry

class ServiceRegistry(IServiceRegistry):  # 實作介面
    def discover(self, name):
        ...
```

**結果**: 打破循環，兩個模組都依賴 `interfaces/`，但不互相依賴。

---

## 6. 遷移策略與階段規劃

### 6.1 遷移階段

#### Phase A: 基礎建設 (Week 1)

**目標**: 建立新架構的骨架

**任務**:
1. 建立新目錄結構
   ```bash
   mkdir -p core/{interfaces,ai_engines,governance,quality_assurance}
   mkdir -p core/unified_integration/{configuration,orchestration}
   ```

2. 建立介面定義 (`core/interfaces/*.py`)
   - `service_interface.py`
   - `processor_interface.py`
   - `runtime_interface.py`
   - `safety_interface.py`

3. 更新 `core/__init__.py` (暫時保持空，後續填充)

4. 建立各子模組的 `README.md`

**驗收**:
- [ ] 所有新目錄建立完成
- [ ] 介面定義完成並通過 mypy 檢查
- [ ] README 覆蓋所有子模組

#### Phase B: 頂層檔案遷移 (Week 2)

**目標**: 遷移 11 個頂層 Python 檔案

**遷移順序** (按依賴關係):

1. **First Wave (無依賴)**:
   - `auto_bug_detector.py` → `quality_assurance/bug_detector.py`

2. **Second Wave (少量依賴)**:
   - `hallucination_detector.py` → `ai_engines/hallucination_detection/detector.py`
   - `context_understanding_engine.py` → `ai_engines/context_understanding/engine.py`

3. **Third Wave (中等依賴)**:
   - `ai_decision_engine.py` → `ai_engines/decision/engine.py`
   - `autonomous_trust_engine.py` → `governance/trust_engine.py`
   - `auto_governance_hub.py` → `governance/hub.py`

4. **每個檔案遷移流程**:
   ```bash
   # 1. 複製到新位置
   cp core/ai_decision_engine.py core/ai_engines/decision/engine.py
   
   # 2. 更新 import 路徑
   sed -i 's/from core\./from core.ai_engines.decision./g' core/ai_engines/decision/engine.py
   
   # 3. 新增型別註解
   # (手動編輯)
   
   # 4. 在舊位置建立 shim
   echo "import warnings\nfrom core.ai_engines.decision import *" > core/ai_decision_engine.py
   
   # 5. 執行測試
   pytest core/ai_engines/decision/tests/
   
   # 6. 確認無問題後，標記舊檔案為 deprecated
   ```

**驗收**:
- [ ] 所有檔案遷移完成
- [ ] Shim layer 正常運作
- [ ] 測試覆蓋率 ≥ 70%
- [ ] CI/CD 通過

#### Phase C: unified_integration 重組 (Week 2)

**目標**: 重組 `unified_integration/` 內部結構

**任務**:
1. 建立 `configuration/` 子模組
   - 移動 `configuration_manager.py`
   - 移動 `configuration_optimizer.py`
   - 移動 `work_configuration_manager.py`
   - 建立統一的 `__init__.py`

2. 建立 `orchestration/` 子模組
   - 移動 `system_orchestrator.py`
   - 移動 `deep_execution_system.py`

3. 重構 `cognitive_processor.py`
   - 降低複雜度 (18 → ≤ 15)
   - 實作 `ICognitiveProcessor` 介面

4. 重構 `service_registry.py`
   - 降低複雜度 (16 → ≤ 15)
   - 實作 `IServiceRegistry` 介面

**驗收**:
- [ ] 子模組建立完成
- [ ] 複雜度達標
- [ ] 介面實作完成
- [ ] 測試通過

#### Phase D: Runtime 改進 (Week 3)

**目標**: `island_ai_runtime/` 依賴介面而非實作

**任務**:
1. 更新 `runtime.py`
   - 實作 `IRuntime` 介面
   - 降低複雜度 (17 → ≤ 15)

2. 更新 `agent_framework.py`
   - 依賴 `IServiceRegistry` 而非 `ServiceRegistry`
   - 實作 `IAgentFramework` 介面

3. 補充單元測試
   - 目標覆蓋率: 75%

**驗收**:
- [ ] 介面實作完成
- [ ] 循環依賴已打破
- [ ] 測試覆蓋率 ≥ 75%

#### Phase E: TypeScript 遷移 (Week 3)

**目標**: JavaScript → TypeScript

**任務**:
1. 遷移 `advisory-database/src/*.js` (7 個檔案)
   ```bash
   for file in core/advisory-database/src/*.js; do
     mv "$file" "${file%.js}.ts"
   done
   ```

2. 新增型別定義
   - 建立 `types/` 目錄
   - 定義介面與類型

3. 配置 TypeScript
   - 更新 `tsconfig.json`
   - 設定嚴格模式

4. 單元測試
   - Jest 測試覆蓋率 > 80%

**驗收**:
- [ ] 所有 .js 檔案遷移為 .ts
- [ ] TypeScript 編譯通過 (`tsc --noEmit`)
- [ ] 測試覆蓋率 > 80%

#### Phase F: 公開 API 定義 (Week 4)

**目標**: 明確公開 API 邊界

**任務**:
1. 填充 `core/__init__.py`
   - Export 主要類別/函式
   - 設定版本號

2. 更新所有子模組 `__init__.py`
   - 明確 `__all__`

3. 掃描並更新下游使用者
   ```bash
   grep -r "from core\\.ai_decision_engine" services/
   # 提供遷移建議
   ```

4. 文件生成
   - 使用 Sphinx 生成 API 文檔
   - 部署到內部文件網站

**驗收**:
- [ ] `core/__init__.py` 完成
- [ ] API 文檔生成
- [ ] 下游服務遷移指南完成

#### Phase G: 驗證與監控 (Week 4)

**目標**: 確保品質指標達標

**任務**:
1. 執行完整測試套件
   ```bash
   pytest core/ --cov=core --cov-report=html
   ```

2. 執行語言治理掃描
   ```bash
   npm run governance:check
   ```

3. 執行 Semgrep 掃描
   ```bash
   semgrep --config auto core/
   ```

4. 執行複雜度分析
   ```bash
   radon cc core/ -a -nb
   ```

5. 部署到 staging 環境
   - 執行整合測試
   - 監控效能指標

**驗收**:
- [ ] 測試覆蓋率 ≥ 80%
- [ ] 語言違規 = 0
- [ ] Semgrep HIGH = 0
- [ ] 平均複雜度 ≤ 8.0
- [ ] Staging 環境穩定運行 48 小時

### 6.2 回滾策略

每個 Phase 都應設定回滾點：

```bash
# Phase A 完成後
git tag phase-a-complete
git push origin phase-a-complete

# 如需回滾
git reset --hard phase-a-complete
git push --force-with-lease
```

**Feature Flag 控制**:

```python
# core/__init__.py
import os

USE_NEW_STRUCTURE = os.getenv('ENABLE_NEW_CORE_STRUCTURE', 'true').lower() == 'true'

if USE_NEW_STRUCTURE:
    from core.ai_engines.decision import DecisionEngine
else:
    from core.ai_decision_engine import DecisionEngine  # Legacy
```

### 6.3 風險緩解

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|----------|
| 遺漏 import 更新 | MEDIUM | HIGH | 自動掃描工具 + 回歸測試 |
| 測試覆蓋不足 | MEDIUM | MEDIUM | 要求最低覆蓋率 70% |
| 循環依賴未完全打破 | LOW | HIGH | 依賴分析工具 (`tools/dependency-graph.py`) |
| 效能下降 | LOW | MEDIUM | Staging 效能測試 + 監控 |
| 下游服務中斷 | MEDIUM | HIGH | Feature flag + 漸進式部署 |

---

## 7. API 契約與相容性

### 7.1 向後相容性保證

**保證內容**:

1. **Major 版本內相容** (3.x.x)
   - 公開 API 不破壞性變更
   - Deprecation warnings 提前 2 個版本
   - 保留舊 import 路徑 (shim layer)

2. **Minor 版本新增功能**
   - 不影響現有 API
   - 新功能透過新模組/函式提供

3. **Patch 版本僅 bug 修復**
   - 不變更 API 簽名
   - 不變更行為（除非是 bug）

### 7.2 破壞性變更清單

本次重構的破壞性變更（需要 Major 版本提升到 3.0.0）:

| 變更 | 影響 | 遷移指南 |
|------|------|----------|
| Import 路徑變更 | HIGH | 使用新路徑或 shim |
| 介面新增抽象方法 | MEDIUM | 實作新方法或使用預設實作 |
| 配置格式變更 | LOW | 提供轉換工具 |

**遷移範例**:

```python
# Before (v2.x)
from core.ai_decision_engine import DecisionEngine

engine = DecisionEngine()
result = engine.decide(input_data)

# After (v3.0 - Recommended)
from core import DecisionEngine

engine = DecisionEngine()
result = engine.decide(input_data)

# After (v3.0 - Legacy shim, with deprecation warning)
from core.ai_decision_engine import DecisionEngine  # DeprecationWarning

engine = DecisionEngine()
result = engine.decide(input_data)
```

### 7.3 測試覆蓋相容性

**契約測試**:

```python
# tests/contract/test_api_compatibility.py

def test_legacy_import_paths_work():
    """確保舊 import 路徑仍可用（有 deprecation warning）"""
    import warnings
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from core.ai_decision_engine import DecisionEngine
        
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message).lower()

def test_new_import_paths_work():
    """確保新 import 路徑正常工作"""
    from core import DecisionEngine
    from core.ai_engines.decision import DecisionEngine as DE
    
    assert DecisionEngine is DE

def test_api_signature_unchanged():
    """確保公開 API 簽名未變更"""
    from core import DecisionEngine
    
    engine = DecisionEngine()
    
    # 檢查方法存在
    assert hasattr(engine, 'decide')
    assert hasattr(engine, 'initialize')
    
    # 檢查簽名
    import inspect
    sig = inspect.signature(engine.decide)
    params = list(sig.parameters.keys())
    assert 'input_data' in params
```

---

## 8. 驗證與成功標準

### 8.1 品質指標

| 指標 | 當前值 | 目標值 | 驗證方式 |
|------|--------|--------|----------|
| 測試覆蓋率 | 55% | ≥ 80% | `pytest --cov` |
| 語言違規 | 7 (JS) | 0 | `npm run governance:check` |
| Semgrep HIGH | 0 | 0 | `semgrep --config auto` |
| 平均複雜度 | 8.5 | ≤ 8.0 | `radon cc -a` |
| Hotspot 檔案數 | 10 | ≤ 5 | `hotspot.json` analysis |
| 文件覆蓋率 | 45% | ≥ 80% | Docstring 檢查 |

### 8.2 架構合規性

**檢查清單**:

- [ ] 無循環依賴 (`tools/dependency-graph.py --check-cycles`)
- [ ] 依賴方向正確 (core → infrastructure, NOT core → services)
- [ ] 公開 API 明確定義 (`core/__init__.py` 完整)
- [ ] 介面實作完整 (所有主要類別實作對應介面)
- [ ] 目錄結構符合設計 (對照 Section 2.1)

### 8.3 整合測試

**測試場景**:

1. **AI 決策流程**
   ```python
   def test_ai_decision_flow():
       engine = DecisionEngine()
       context = ContextEngine()
       detector = HallucinationDetector()
       
       # 完整流程
       ctx = context.understand(input_text)
       decision = engine.decide(ctx)
       validated = detector.validate(decision)
       
       assert validated.is_valid
   ```

2. **服務註冊與發現**
   ```python
   def test_service_registry_flow():
       registry = ServiceRegistry()
       service = MockService()
       
       registry.register(service)
       discovered = registry.discover(service.name)
       
       assert discovered is not None
       assert discovered.health_check()
   ```

3. **安全機制觸發**
   ```python
   def test_circuit_breaker_flow():
       breaker = CircuitBreaker(threshold=3)
       
       # 模擬失敗
       for _ in range(3):
           breaker.record_failure()
       
       assert breaker.state == 'OPEN'
       
       # 應該拒絕請求
       with pytest.raises(CircuitBreakerOpenError):
           breaker.call(lambda: None)
   ```

### 8.4 效能基準

**關鍵指標**:

| 操作 | 當前 (v2.x) | 目標 (v3.0) | 允許範圍 |
|------|-------------|-------------|----------|
| AI 決策延遲 (p50) | 150ms | ≤ 160ms | +10% |
| AI 決策延遲 (p99) | 500ms | ≤ 550ms | +10% |
| 服務註冊時間 | 10ms | ≤ 12ms | +20% |
| 記憶體使用 (idle) | 200MB | ≤ 220MB | +10% |
| 記憶體使用 (load) | 800MB | ≤ 880MB | +10% |

**測試方法**:

```bash
# 使用 pytest-benchmark
pytest tests/performance/ --benchmark-only

# 記憶體分析
python -m memory_profiler tests/performance/test_memory.py
```

---

## 9. 文件與知識傳遞

### 9.1 文件更新清單

- [ ] `core/README.md` - Core 引擎總覽
- [ ] `core/ai_engines/README.md` - AI 引擎使用指南
- [ ] `core/governance/README.md` - 治理系統說明
- [ ] `core/unified_integration/README.md` - 整合層架構
- [ ] `core/island_ai_runtime/README.md` - Runtime 使用指南
- [ ] `docs/api/core-v3.md` - API 參考文檔
- [ ] `docs/migration/v2-to-v3.md` - 遷移指南

### 9.2 遷移指南範本

**`docs/migration/v2-to-v3.md`**:

```markdown
# Core v2 → v3 遷移指南

## 快速遷移

### Import 路徑變更

| v2 | v3 | 狀態 |
|----|----|----|
| `from core.ai_decision_engine import DecisionEngine` | `from core import DecisionEngine` | ⚠️ 舊路徑 deprecated |
| `from core.unified_integration.cognitive_processor import CognitiveProcessor` | `from core import CognitiveProcessor` | ⚠️ 舊路徑 deprecated |

### 使用統一 API

**推薦方式**:
\`\`\`python
from core import DecisionEngine, ContextEngine, CognitiveProcessor

engine = DecisionEngine()
\`\`\`

**過渡方式** (有 deprecation warning):
\`\`\`python
from core.ai_decision_engine import DecisionEngine  # 仍可用，但會警告

engine = DecisionEngine()
\`\`\`

## 進階配置

### 介面導向程式設計

v3 引入介面層，建議依賴介面而非實作:

\`\`\`python
from core.interfaces.processor_interface import ICognitiveProcessor

def my_function(processor: ICognitiveProcessor):
    result = processor.process(context)
    return result
\`\`\`

## 常見問題

### Q: 舊程式碼是否需要立即修改？

A: 不需要。v3 保留了 shim layer，舊程式碼仍可運行，但會收到 deprecation warning。
建議在方便時遷移到新 API。

### Q: 如何知道我的程式碼是否需要更新？

A: 執行測試，檢查是否有 DeprecationWarning。使用 `pytest -W error::DeprecationWarning` 
將 warning 視為錯誤。

### Q: 新架構的效能如何？

A: 效能影響在 ±10% 範圍內。詳見效能基準測試報告。
\`\`\`

### 9.3 內部培訓計畫

**Week 1**: 架構概覽
- 新目錄結構介紹
- 介面層概念
- 遷移策略說明

**Week 2**: 實戰工作坊
- Live coding: 遷移一個舊模組
- Q&A session
- Hands-on practice

**Week 3**: 持續支援
- Office hours
- Slack 支援頻道
- 文件反饋收集

---

## 10. 與重構劇本的對齊

### 10.1 Refactor Playbook 依賴

本 Integration 設計完成後，`03_refactor/core/core__architecture_refactor.md` 應包含：

1. **具體執行步驟** (基於本設計的 Section 6)
2. **Proposer/Critic 工作流程** (驗證是否符合本設計)
3. **質量度量追蹤** (對照本設計的 Section 8)
4. **驗收標準** (參考本設計的 Section 8.1)

### 10.2 關鍵決策點

**已決策**:

1. ✅ **Contract Service 位置**: 保留在 `core/contract_service/`
   - 理由: 合約服務是 core 功能的一部分

2. ✅ **頂層檔案分組**: AI engines / Governance / QA
   - 理由: 功能明確，易於理解

3. ✅ **介面層設計**: 引入 `core/interfaces/`
   - 理由: 打破循環依賴，提高可測試性

**待決策** (在 Refactor 階段):

- [ ] 配置格式是否需要版本化？
- [ ] 是否需要 API Gateway 統一入口？
- [ ] 監控指標的採集方式？

---

## 11. 風險評估與應對

### 11.1 技術風險

| 風險 | 可能性 | 影響 | 應對措施 |
|------|--------|------|----------|
| Import 路徑遺漏更新 | 中 | 高 | 自動掃描 + 回歸測試 |
| 介面設計不當 | 低 | 中 | 設計評審 + 原型驗證 |
| 效能下降 | 低 | 中 | Staging 效能測試 |
| 測試覆蓋不足 | 中 | 中 | 強制最低覆蓋率 |

### 11.2 組織風險

| 風險 | 可能性 | 影響 | 應對措施 |
|------|--------|------|----------|
| 下游團隊不配合遷移 | 中 | 高 | Shim layer + 長期支援 |
| 文件不足導致混亂 | 中 | 中 | 詳細文檔 + 培訓 |
| 資源不足 | 低 | 高 | 分階段執行 + 優先級管理 |

### 11.3 應急預案

**場景 1: Staging 測試失敗**
- 行動: 暫停部署，回滾到上一個穩定版本
- 分析: 識別失敗原因
- 修復: 在 feature branch 修復後重新測試

**場景 2: Production 效能問題**
- 行動: 啟用 Feature Flag 回切到舊架構
- 監控: 收集詳細效能資料
- 優化: 針對瓶頸進行優化

**場景 3: 下游服務大量報錯**
- 行動: 發布緊急修復版本 (shim 改進)
- 溝通: 通知所有團隊並提供遷移支援
- 改進: 更新遷移指南

---

**完成日期**: 2025-12-07  
**審核狀態**: ✅ 設計完成，待評審  
**下一步**: 執行 Phase A (基礎建設)

---

*此集成劇本定義了 core/architecture-stability cluster 重構的目標架構與遷移路徑，為 Refactor 階段提供具體指導。*
