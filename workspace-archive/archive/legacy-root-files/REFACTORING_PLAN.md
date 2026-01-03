# MachineNativeOps 重构计划：命名规范与结构治理

## 目标

统一 v1-python-drones 和 v2-multi-islands 的代码，整合到新的 MachineNativeOps 架构中，建立统一的命名规范和结构治理。

---

## 第一阶段：代码整合方案

### 1.1 Drone 系统整合 (v1-python-drones)

**源目录**: `archive/legacy/v1-python-drones/`

**目标映射**:

```
archive/legacy/v1-python-drones/
├── drones/base_drone.py              → src/autonomous/agents/base-agent.py
├── drones/coordinator_drone.py       → src/autonomous/agents/coordinator-agent.py
├── drones/autopilot_drone.py         → src/autonomous/agents/autopilot-agent.py
├── drones/deployment_drone.py        → src/autonomous/agents/deployment-agent.py
├── config/drone_config.py            → src/autonomous/agents/config/agent-config.py
└── utils/helpers.py                  → src/autonomous/agents/utils.py
```

**类名映射**:

- `BaseDrone` → `BaseAgent`
- `CoordinatorDrone` → `CoordinatorAgent`
- `AutopilotDrone` → `AutopilotAgent`
- `DeploymentDrone` → `DeploymentAgent`
- `DroneStatus` → `AgentStatus`

**方法映射**:

- `start()` → `start()` (保持不变)
- `stop()` → `stop()` (保持不变)
- `execute()` → `execute()` (保持不变)

---

### 1.2 Island 系统整合 (v2-multi-islands)

**源目录**: `archive/legacy/v2-multi-islands/`

**目标映射**:

```
archive/legacy/v2-multi-islands/
├── islands/base_island.py            → src/bridges/language-islands/base-island.py
├── islands/python_island.py          → src/bridges/language-islands/python-island.py
├── islands/rust_island.py            → src/bridges/language-islands/rust-island.py
├── islands/go_island.py              → src/bridges/language-islands/go-island.py
├── islands/typescript_island.py      → src/bridges/language-islands/typescript-island.py
├── islands/java_island.py            → src/bridges/language-islands/java-island.py
├── orchestrator/island_orchestrator.py → src/core/orchestrators/language-island-orchestrator.py
├── bridges/language_bridge.py        → (已存在，需要集成)
├── config/island_config.py           → src/bridges/language-islands/config/island-config.py
└── utils/helpers.py                  → src/bridges/language-islands/utils.py
```

**类名映射**:

- `BaseIsland` → `BaseIsland` (保持不变)
- `PythonIsland` → `PythonIsland` (保持不变)
- `RustIsland` → `RustIsland` (保持不变)
- `GoIsland` → `GoIsland` (保持不变)
- `TypeScriptIsland` → `TypeScriptIsland` (保持不变)
- `JavaIsland` → `JavaIsland` (保持不变)
- `IslandOrchestrator` → `LanguageIslandOrchestrator`
- `IslandStatus` → `IslandStatus` (保持不变)

---

### 1.3 统一 Orchestrator

**新文件**: `src/core/orchestrators/synergy-mesh-orchestrator.py`

**功能**:

- 统一协调 Agents 和 Islands
- 提供统一的执行接口
- 管理资源和生命周期
- 提供监控和报告

**类定义**:

```python
class SynergyMeshOrchestrator:
    - register_agent(agent: BaseAgent)
    - register_island(island: BaseIsland)
    - execute_all() -> Dict[str, ExecutionResult]
    - execute_agent(agent_name: str) -> ExecutionResult
    - execute_island(island_name: str) -> ExecutionResult
    - get_status() -> SystemStatus
```

---

## 第二阶段：命名规范统一

### 2.1 目录命名规范

**规则**: kebab-case (小写，用连字符分隔)

**示例**:

- ✓ `src/autonomous/agents/`
- ✓ `src/bridges/language-islands/`
- ✓ `src/core/orchestrators/`
- ✗ `src/autonomous/Agents/`
- ✗ `src/autonomous/agents_legacy/`

### 2.2 文件命名规范

**规则**: kebab-case for all filenames

**Python 文件**:

- ✓ `base-agent.py`
- ✓ `coordinator-agent.py`
- ✓ `auto-upgrade-env.py`
- ✗ `base_agent.py`
- ✗ `baseAgent.py`

### 2.3 Python 类命名规范

**规则**: PascalCase

**示例**:

- ✓ `class BaseAgent:`
- ✓ `class CoordinatorAgent:`
- ✓ `class LanguageIslandOrchestrator:`
- ✗ `class base_agent:`
- ✗ `class BaseagentImpl:`

### 2.4 Python 函数/方法命名规范

**规则**: snake_case

**示例**:

- ✓ `def start_agent():`
- ✓ `def execute_deployment():`
- ✓ `def get_status():`
- ✗ `def startAgent():`
- ✗ `def START_AGENT():`

### 2.5 Python 常量命名规范

**规则**: UPPER_SNAKE_CASE

**示例**:

- ✓ `AGENT_STATUS_RUNNING = "running"`
- ✓ `DEFAULT_TIMEOUT = 30`
- ✓ `SUPPORTED_ISLANDS = ["python", "rust", "go"]`
- ✗ `agent_status_running = "running"`

### 2.6 导入和模块引用

**文件路径**: kebab-case
**类名**: PascalCase
**函数**: snake_case

**示例**:

```python
# ✓ 正确
from src.autonomous.agents.base_agent import BaseAgent
from src.bridges.language_islands.config.island_config import IslandConfig
from src.core.orchestrators.synergy_mesh_orchestrator import SynergyMeshOrchestrator

# ✗ 错误
from src.autonomous.Agents.BaseAgent import BaseAgent
from src.autonomous.agents.base_agent import base_agent
```

---

## 第三阶段：文档和配置清理

### 3.1 修复大小写冲突

**待修复的目录**:

1. `docs/GOVERNANCE/` → 迁移到 `governance/29-docs/`
2. `docs/ARCHITECTURE/` → 保留 `docs/architecture/` (小写)
3. `docs/AGENTS/` → 保留 `docs/agents/` (小写)
4. 删除所有 UPPERCASE 变体

### 3.2 删除重复的遗留代码

**待删除**:

1. `archive/v1-python-drones/` (重复，保留 `archive/legacy/v1-python-drones/`)
2. `archive/v2-multi-islands/` (重复，保留 `archive/legacy/v2-multi-islands/`)

---

## 第四阶段：验证和测试

### 4.1 命名规范验证

**工具**: `tools/governance/python/validate_naming.py`

**检查项**:

- [ ] 所有目录使用 kebab-case
- [ ] 所有 Python 文件使用 kebab-case
- [ ] 所有 Python 类使用 PascalCase
- [ ] 所有 Python 函数使用 snake_case
- [ ] 所有常量使用 UPPER_SNAKE_CASE
- [ ] 导入语句正确引用

### 4.2 功能测试

**测试框架**: pytest

**测试套件**:

- [ ] Agent 系统测试
- [ ] Island 系统测试
- [ ] SynergyMeshOrchestrator 测试
- [ ] 导入和依赖关系测试

### 4.3 集成测试

**验证**:

- [ ] 所有 Agent 可以正常启动
- [ ] 所有 Island 可以正常激活
- [ ] Orchestrator 可以协调所有组件
- [ ] 日志输出正确

---

## 执行步骤

### Step 1: 准备工作

- [ ] 创建新分支 `claude/refactor-naming-standards`
- [ ] 备份现有代码

### Step 2: 创建目标目录结构

- [ ] 创建 `src/autonomous/agents/` 子目录
- [ ] 创建 `src/bridges/language-islands/` 目录
- [ ] 创建 `src/core/orchestrators/` 目录

### Step 3: 复制和重命名代码

- [ ] 复制 v1-python-drones 到新位置，重命名文件和类
- [ ] 复制 v2-multi-islands 到新位置，重命名文件和类
- [ ] 更新所有导入语句

### Step 4: 创建统一 Orchestrator

- [ ] 编写 SynergyMeshOrchestrator
- [ ] 集成 Agent 和 Island 系统
- [ ] 编写单元测试

### Step 5: 清理和验证

- [ ] 修复文档结构大小写
- [ ] 删除重复的遗留代码
- [ ] 运行验证工具
- [ ] 运行完整测试套件

### Step 6: 提交和推送

- [ ] 提交所有更改
- [ ] 推送到分支
- [ ] 准备 Pull Request

---

## 预期结果

1. **统一的架构**: 所有代码遵循 MachineNativeOps 命名和结构规范
2. **可维护性**: 清晰的目录结构和命名规范
3. **可扩展性**: 易于添加新的 Agent 和 Island
4. **文档化**: 完整的重构文档和规范说明

---

## 版本信息

- **项目**: MachineNativeOps
- **重构版本**: v1.0
- **创建日期**: 2025-12-18
- **状态**: 计划阶段
