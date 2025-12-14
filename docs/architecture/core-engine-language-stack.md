# 🧠 Core Engine（SynergyMesh 核心）語言堆疊說明

## 1. Layer 1 — Core Engine 概覽

Core Engine 由三個語言層組成：

- **TypeScript**：控制平面（Control Plane）
  - 流程協調、服務註冊表、事件流、API 入口、MCP/CLI 整合
- **Python**：認知與推理平面（Cognitive Plane）
  - 模型調用、規劃器、重構建議、決策演算法
- **C++（可選）**：性能與即時控制平面（Performance Plane）
  - 高頻邏輯、實時控制、底層橋接

## 2. 語言分工規則

### TypeScript（必須放的東西）

- **服務註冊表與 discovery**
  - `core/unified_integration/service_registry.ts`
  - 服務健康監控、依賴解析、動態發現
- **任務排程與 workflow orchestration**
  - `core/unified_integration/system_orchestrator.ts`
  - 工作流管理、任務調度、狀態機控制
- **MCP / HTTP / gRPC API 入口**
  - `core/contract_service/contracts-L1/contracts/src/`
  - RESTful API、gRPC 端點、MCP 協議實現
- **Policy decision wiring（決策結果的 apply，不是演算法本身）**
  - `core/unified_integration/configuration_manager.ts`
  - 策略執行、配置應用、結果同步
- **與前端 / Admin CLI 的對接**
  - `core/unified_integration/integration_hub.ts`
  - 消息路由、事件發布訂閱、CLI 命令處理
- **生命週期管理**
  - `core/unified_integration/lifecycle_systems.ts`
  - 服務啟動、停止、重啟、健康檢查
- **安全機制與熔斷器**
  - `core/safety_mechanisms/`
  - 斷路器、限流、回滾策略、緊急停止
- **SLSA 溯源流程控制**
  - `core/slsa_provenance/`
  - 簽名流程、證明鏈管理、驗證協調

### Python（必須放的東西）

- **LLM 調用邏輯**
  - `core/ai_decision_engine.py`
  - `core/context_understanding_engine.py`
  - OpenAI、Anthropic、本地模型調用
- **語言治理分析（parser、打分、建議）**
  - `core/auto_governance_hub.py`
  - 代碼掃描、違規檢測、合規性評分
- **AI Refactor Playbook 生成器**
  - `tools/generate-refactor-playbook.py`
  - 重構計畫生成、優先級排序、依賴分析
- **Auto-Fix PR 建議生成（不含 Git 操作）**
  - `core/auto_bug_detector.py`
  - 缺陷檢測、修復建議、補丁生成
- **認知處理器（Cognitive Processor）**
  - `core/unified_integration/cognitive_processor.py`
  - 感知層、推理層、執行層、證明層
- **幻覺偵測與驗證**
  - `core/hallucination_detector.py`
  - LLM 輸出驗證、一致性檢查、信心評分
- **知識圖譜處理**
  - `core/knowledge_processing/`
  - 實體提取、關係抽取、本體構建
- **自主信任引擎**
  - `core/autonomous_trust_engine.py`
  - 信任評估、風險評分、治理驗證

### C++（只有必要才用）

- **與無人機 / 自主系統 / 低延遲系統的即時控制邏輯**
  - `automation/autonomous/architecture-stability/` （C++ 實現）
  - 飛行控制、感測器融合、實時路徑規劃
- **必須 10ms 內完成的硬邏輯**
  - 高頻控制迴路、實時數據處理
- **必須有：**
  - **TS API 封裝**：透過 gRPC 或 HTTP 提供 TypeScript 接口
  - **或 Python binding**：使用 pybind11 或 ctypes 提供 Python 綁定

> **重要原則：** C++ 代碼不應直接被 `core/` 以外的模組調用，必須通過 TypeScript 或 Python 的抽象層。

## 3. Core Engine 目錄與語言對應

```text
core/
  ├── unified_integration/           # TypeScript：整合層，所有 request 先來這裡
  │   ├── unified_controller.ts      # 系統啟動器、階段協調
  │   ├── integration_hub.ts         # 消息路由、事件發布訂閱
  │   ├── system_orchestrator.ts     # 工作流管理、任務調度
  │   ├── configuration_manager.ts   # 配置管理、密鑰管理
  │   ├── service_registry.ts        # 服務發現、健康監控、依賴解析
  │   ├── cognitive_processor.py     # Python：認知處理器（推理邏輯）
  │   └── configuration_optimizer.py # Python：配置優化建議
  │
  ├── mind_matrix/                   # TS + Py：心智矩陣（TS orchestration，Py reasoning）
  │   ├── executive_system.ts        # TypeScript：執行控制器
  │   ├── multi_agent_hypergraph.py  # Python：多代理超圖推理
  │   └── cognitive_stack.py         # Python：認知堆疊
  │
  ├── contract_service/              # TypeScript：合約服務
  │   └── contracts-L1/contracts/
  │       ├── src/controllers/       # REST API 控制器
  │       ├── src/middleware/        # 中間件（驗證、日誌、限流）
  │       └── src/services/          # 業務邏輯服務
  │
  ├── safety_mechanisms/             # TypeScript：斷路器、熔斷、回滾策略
  │   ├── circuit_breaker.ts
  │   ├── emergency_stop.ts
  │   └── rollback_system.ts
  │
  ├── slsa_provenance/               # TypeScript：簽名與證明流程
  │   ├── provenance_manager.ts
  │   ├── signature_service.ts
  │   └── attestation_builder.ts
  │
  ├── ai_decision_engine.py          # Python：AI 決策引擎
  ├── context_understanding_engine.py # Python：上下文理解
  ├── hallucination_detector.py      # Python：幻覺偵測
  ├── auto_governance_hub.py         # Python：自動治理中心
  ├── auto_bug_detector.py           # Python：自動缺陷偵測
  ├── autonomous_trust_engine.py     # Python：自主信任引擎
  │
  ├── knowledge_processing/          # Python：知識圖譜處理
  │   ├── triple_extractor.py        # 實體與關係提取
  │   ├── ontology_builder.py        # 本體構建
  │   └── entity_resolver.py         # 實體解析與去重
  │
  └── native_adapters/               # C++：必要時的原生橋接層（透過 TS/Py wrapper 使用）
      ├── realtime_controller.cpp    # 實時控制邏輯
      ├── sensor_fusion.cpp          # 感測器融合
      └── bindings/
          ├── python_bindings.cpp    # pybind11 綁定
          └── typescript_grpc.proto  # gRPC 接口定義
```

## 4. 禁止與 Anti-Pattern

### ❌ 不允許在 TypeScript 內實作複雜 ML/AI 演算法

**錯誤示例：**
```typescript
// ❌ 不要在 TypeScript 裡實現複雜的 ML 邏輯
function trainNeuralNetwork(data: number[][]): Model {
  // 複雜的梯度下降、反向傳播...
}
```

**正確做法：**
```typescript
// ✅ 應該抽象為「調用 Python 模組」
async function trainModel(data: number[][]): Promise<Model> {
  return await pythonService.call('train_neural_network', { data });
}
```

### ❌ 不允許在 Python 內直接控制 core/ 內部部署 / 基礎設施

**錯誤示例：**
```python
# ❌ 不要在 Python 裡直接操作基礎設施
def deploy_to_kubernetes(manifest: dict):
    # 直接調用 kubectl、修改配置...
```

**正確做法：**
```python
# ✅ 應交由 TS orchestration 模組執行
async def request_deployment(manifest: dict):
    await orchestrator_api.post('/deploy', manifest)
```

### ❌ 不允許直接從 apps/ 或 services/ 呼叫 C++ 函式庫

**錯誤示例：**
```typescript
// ❌ 不要直接從應用層調用 C++ 模組
import { realtimeController } from 'core/native_adapters/realtime_controller.cpp';
```

**正確做法：**
```typescript
// ✅ 必須透過 core/native_adapters 提供的 API 使用
import { NativeAdapter } from 'core/native_adapters';
const controller = new NativeAdapter('realtime_controller');
await controller.executeCommand({ ... });
```

## 5. 語言間通訊協議

### TypeScript ↔ Python

**方法 1：HTTPS/REST API（推薦用於異步任務）**
```typescript
// TypeScript 調用 Python 服務（使用 TLS 加密）
const response = await fetch('https://python-service:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${serviceToken}`,  // 服務間認證
  },
  body: JSON.stringify({ code: sourceCode })
});
```

**方法 2：gRPC with TLS（推薦用於高性能同步調用）**
```typescript
// TypeScript gRPC 客戶端（使用 TLS 和雙向認證）
import * as grpc from '@grpc/grpc-js';
import * as fs from 'fs';

const tlsCredentials = grpc.credentials.createSsl(
  fs.readFileSync('ca-cert.pem'),      // CA 證書
  fs.readFileSync('client-key.pem'),   // 客戶端私鑰
  fs.readFileSync('client-cert.pem')   // 客戶端證書
);

const client = new AnalysisServiceClient(
  'python-service:50051',
  tlsCredentials
);
const result = await client.analyzeCode({ code: sourceCode });
```

**方法 3：MCP 協議（推薦用於 Agent 間通訊）**
```typescript
// 使用 MCP 協議與 Python Agent 通訊（透過 TLS）
const mcpClient = new MCPClient('python-cognitive-agent', {
  secure: true,
  tlsOptions: {
    ca: fs.readFileSync('ca-cert.pem'),
    cert: fs.readFileSync('client-cert.pem'),
    key: fs.readFileSync('client-key.pem'),
  }
});
const response = await mcpClient.sendMessage({
  action: 'reasoning',
  context: { ... }
});
```

### TypeScript/Python ↔ C++

**方法：gRPC + Protocol Buffers with TLS**
```protobuf
// realtime_controller.proto
service RealtimeController {
  rpc ExecuteControl(ControlRequest) returns (ControlResponse);
}
```

```typescript
// TypeScript 調用 C++ 服務（使用 TLS 雙向認證）
import * as grpc from '@grpc/grpc-js';
import * as fs from 'fs';

const tlsCredentials = grpc.credentials.createSsl(
  fs.readFileSync('ca-cert.pem'),
  fs.readFileSync('client-key.pem'),
  fs.readFileSync('client-cert.pem')
);

const grpcClient = new RealtimeControllerClient(
  'cpp-service:50052',
  tlsCredentials
);
const result = await grpcClient.executeControl({ commands: [...] });
```

```python
# Python 調用 C++ 服務（使用 TLS 雙向認證）
import grpc
import realtime_controller_pb2_grpc as rt_grpc

# 載入 TLS 憑證
with open('ca-cert.pem', 'rb') as f:
    ca_cert = f.read()
with open('client-cert.pem', 'rb') as f:
    client_cert = f.read()
with open('client-key.pem', 'rb') as f:
    client_key = f.read()

# 創建 TLS 憑證
credentials = grpc.ssl_channel_credentials(
    root_certificates=ca_cert,
    private_key=client_key,
    certificate_chain=client_cert
)

# 使用安全通道
channel = grpc.secure_channel('cpp-service:50052', credentials)
stub = rt_grpc.RealtimeControllerStub(channel)
result = stub.ExecuteControl(control_request)
```

> **🔒 安全注意事項：**
> - 所有服務間通訊必須使用 TLS/SSL 加密
> - 實施雙向 TLS（mTLS）進行服務身份驗證
> - 定期輪換證書和密鑰
> - 在生產環境中使用受信任的 CA 簽發的證書
> - 將憑證存儲在安全的密鑰管理系統（如 Kubernetes Secrets、HashiCorp Vault）
> - 開發環境可使用自簽名證書，但必須妥善管理

## 6. 開發與測試指南

### TypeScript 開發規範

- **嚴格模式：** 所有 TypeScript 文件必須啟用 `strict: true`
- **明確返回類型：** 所有函數必須明確聲明返回類型
- **使用 Zod：** 所有外部輸入必須使用 Zod 進行驗證
- **錯誤處理：** 使用 Result 類型或明確的 try-catch

```typescript
// ✅ 良好的 TypeScript 實踐
export async function processRequest(
  input: RequestSchema
): Promise<Result<Response, Error>> {
  const validated = requestSchema.safeParse(input);
  if (!validated.success) {
    return { ok: false, error: new ValidationError(validated.error) };
  }
  // 處理邏輯...
  return { ok: true, value: response };
}
```

### Python 開發規範

- **類型註解：** 使用 Python 3.10+ 的類型提示
- **異步優先：** AI/ML 調用應使用 `async/await`
- **依賴管理：** 使用 `uv` 或 `poetry` 管理依賴
- **錯誤處理：** 使用明確的異常類型

```python
# ✅ 良好的 Python 實踐
async def analyze_code(code: str) -> AnalysisResult:
    """分析代碼並返回結果"""
    try:
        result = await llm_service.analyze(code)
        return AnalysisResult(
            score=result.score,
            issues=result.issues,
            confidence=result.confidence
        )
    except LLMServiceError as e:
        logger.error(f"LLM analysis failed: {e}")
        raise AnalysisError(f"Failed to analyze code: {e}") from e
```

### C++ 開發規範

- **現代 C++：** 使用 C++17 或更新版本
- **內存安全：** 優先使用智能指針（`std::unique_ptr`, `std::shared_ptr`）
- **必須提供綁定：** 所有 C++ 模組必須提供 Python 或 TypeScript 綁定
- **文檔完整：** 所有公開 API 必須有詳細文檔

## 7. 測試策略

### TypeScript 測試

```typescript
// core/unified_integration/__tests__/service_registry.test.ts
import { ServiceRegistry } from '../service_registry';

describe('ServiceRegistry', () => {
  it('should register and discover services', async () => {
    const registry = new ServiceRegistry();
    await registry.register({
      id: 'test-service',
      name: 'Test Service',
      endpoint: 'http://localhost:3000'
    });
    
    const discovered = await registry.discover('test-service');
    expect(discovered).toBeDefined();
    expect(discovered.name).toBe('Test Service');
  });
});
```

### Python 測試

```python
# core/tests/test_ai_decision_engine.py
import pytest
from core.ai_decision_engine import AIDecisionEngine

@pytest.mark.asyncio
async def test_decision_making():
    """測試 AI 決策引擎"""
    engine = AIDecisionEngine()
    decision = await engine.make_decision(context={
        'issue_type': 'security',
        'severity': 'high'
    })
    
    assert decision is not None
    assert decision.action in ['approve', 'reject', 'escalate']
    assert decision.confidence >= 0.7
```

## 8. 未來擴展

若新增語言（例如 Rust），必須先更新：

1. **此文件** - 添加新語言的使用場景與規範
2. **`config/system-module-map.yaml`** - 在 `modules.core-engine.languages` 中聲明
3. **`governance/rules/language-policy.yml`** - 在 `allowed_languages` 中添加
4. **文檔** - 更新 `docs/architecture/language-stack.md`

### 示例：添加 Rust 支持

```yaml
# config/system-module-map.yaml
modules:
  core-engine:
    languages:
      primary:
        - "TypeScript"
      secondary:
        - "Python"
        - "C++"
        - "Rust"  # 新增
    rules:
      can_use:
        - "Rust"  # 用於性能關鍵的安全模組
```

## 9. 架構決策記錄（ADR）

### ADR-001: 為何 Core Engine 使用 TypeScript + Python

**背景：**
Core Engine 需要同時處理高階編排和 AI 推理。

**決策：**
- TypeScript 負責控制流程、服務協調、API 層
- Python 負責 AI/ML、數據分析、認知處理

**理由：**
1. TypeScript 提供類型安全和優秀的異步支持
2. Python 擁有最豐富的 AI/ML 生態系統
3. 兩者通過 HTTP/gRPC/MCP 良好協作
4. 降低團隊認知負擔（前端也用 TS）

**後果：**
- 需要維護兩種語言的開發環境
- 需要清晰的語言邊界定義
- 需要標準化的通訊協議

### ADR-002: C++ 僅用於性能關鍵路徑

**背景：**
某些場景需要低延遲、高性能計算。

**決策：**
C++ 僅用於以下場景：
- 實時控制（< 10ms 響應）
- 感測器融合
- 高頻數據處理

**理由：**
1. C++ 提供最佳性能和內存控制
2. 避免過度使用增加維護成本
3. 通過抽象層保護上層代碼

**後果：**
- 所有 C++ 模組必須提供綁定
- 增加了額外的接口層開銷
- 需要專門的 C++ 開發者維護

## 10. 監控與可觀測性

### TypeScript 服務監控

```typescript
// 使用 OpenTelemetry 進行追蹤
import { trace, SpanStatusCode } from '@opentelemetry/api';

const tracer = trace.getTracer('core-engine');

export async function orchestrateWorkflow(workflow: Workflow) {
  const span = tracer.startSpan('orchestrate_workflow');
  try {
    // 執行工作流...
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    throw error;
  } finally {
    span.end();
  }
}
```

### Python 服務監控

```python
# 使用 structlog 進行結構化日誌
import time
import structlog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from your_llm_service import LLMService  # 替換為實際的 LLM 服務導入

logger = structlog.get_logger()

async def analyze_with_llm(prompt: str, llm: 'LLMService') -> str:
    """使用 LLM 分析並記錄性能
    
    Args:
        prompt: 要分析的提示文本
        llm: LLM 服務實例（例如 OpenAI、Anthropic 等）
    """
    logger.info("llm_analysis_started", prompt_length=len(prompt))
    
    start_time = time.time()
    result = await llm.complete(prompt)
    duration = time.time() - start_time
    
    logger.info("llm_analysis_completed", 
                duration_ms=duration * 1000,
                tokens=result.token_count)
    
    return result.text
```

## 11. 總結

Core Engine 的語言策略設計旨在：

1. **清晰分工**：TypeScript 管控制、Python 管認知、C++ 管性能
2. **降低複雜度**：避免語言混亂導致的維護困難
3. **支持擴展**：通過標準協議和抽象層支持未來擴展
4. **提升品質**：明確的規範和測試策略保證代碼質量

**核心原則：**
- ✅ 在正確的層使用正確的語言
- ✅ 通過清晰的 API 邊界通訊
- ✅ 優先使用現有生態系統
- ✅ 避免過早優化

---

## 參考文件

- [Language Stack Overview](./language-stack.md) - 全系統語言堆疊
- [Language Governance](./language-governance.md) - 語言治理策略
- [System Module Map](../../config/system-module-map.yaml) - 模組映射配置
- [Island AI Instructions](../../.github/island-ai-instructions.md) - 開發規範

---

**文件版本：** v1.0  
**最後更新：** 2025-12-07  
**維護者：** Core Engine Team  
**審核者：** Architecture Committee
