# autonomous

## 目錄職責

此目錄為 MachineNativeOps 的**自主系統框架**，包含智能代理、11 骨架架構實現、自動化部署等自主運維能力。

## 子目錄說明

| 子目錄 | 職責 | 關鍵內容 |
|--------|------|----------|
| `agents/` | 智能代理系統 | SynergyMesh Core、多代理協同、Pipeline 編排 |
| `core/` | 自主系統核心 | 核心抽象與共用邏輯 |
| `infrastructure/` | 11 骨架架構實現 | 架構穩定性、API 治理、測試兼容、安全觀測等 |
| `deployment/` | 自動化部署 | Docker、K8s、即時執行管道 |

## 詳細說明

### agents/

智能自動化模組，提供多代理 AI 系統：

- `coordinator-agent.py` - 協調器代理
- `autopilot-agent.py` - 自動駕駛代理
- `deployment-agent.py` - 部署代理
- `base-agent.py` - 基礎代理類
- `synergymesh_core/` - SynergyMesh 核心系統
- `pipeline_service.py` - Pipeline 服務

### infrastructure/

11 個架構骨架的實現代碼：

| 骨架 | 技術棧 | 用途 |
|------|--------|------|
| architecture-stability | C++ + ROS 2 | 100Hz 控制迴圈、IMU 融合、PID 控制 |
| testing-compatibility | Python + YAML | 自動化測試、跨版本兼容 |
| security-observability | Go | 分散式日誌、安全監控、追蹤 |
| identity-tenancy | - | 身份管理、多租戶 |
| cost-management | - | 成本監控與優化 |
| performance-reliability | - | 性能優化、可靠性保障 |
| knowledge-base | - | 知識庫管理 |
| nucleus-orchestrator | - | 核心編排器 |

### deployment/

自動化部署配置：

- `docker/` - Docker 配置
- `k8s/` / `kubernetes/` - Kubernetes 配置
- `instant_execution_pipeline.py` - 即時執行管道

### core/

自主系統的核心抽象（目前為骨架）

## 設計原則

1. **完全自主化**：「無人機、無人駕駛、自動化迭代升遷」的高階架構
2. **多代理協同**：代理間透過 SynergyMesh 協調網格通信
3. **11 骨架分離**：每個骨架專注單一職責，可獨立部署

## 與其他目錄的關係

- **src/core/**：使用核心的 AI 決策引擎和編排器
- **src/automation/**：與自動化引擎協同工作
- **archive/unmanned-engineer-ceo/**：對應的架構指南（已歸檔）
