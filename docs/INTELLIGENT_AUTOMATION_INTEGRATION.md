# Intelligent Automation Integration Guide

# 智能自動化整合指南

## 概述 Overview

本指南說明如何將從 OJ-agent 提取的智能自動化能力整合至您的項目中。

This guide explains how to integrate the intelligent automation capabilities extracted from OJ-agent into your project.

---

## 🎯 核心價值 Core Value

### 從 OJ-agent 提取的高價值能力

**High-value capabilities extracted from OJ-agent:**

1. **多智能體協同** - Multi-agent coordination
2. **實時代碼分析** - Real-time code analysis
3. **自動安全修復** - Automated security fixing
4. **智能意圖識別** - Intelligent intent recognition
5. **概念可視化解釋** - Concept visualization and explanation

### 商業價值 Business Value

- **零停機監控** - 24/7 zero-downtime monitoring
- **安全關鍵驗證** - Safety-critical validation for autonomous systems
- **實時性能優化** - Real-time performance optimization
- **自動化修復** - Automated issue resolution

---

## 📦 模組結構 Module Structure

```
intelligent-automation/
├── agents/                      # 智能體模組
│   ├── task_executor.py        # 任務執行器
│   ├── recognition_server.py   # 識別服務器
│   └── visualization_agent.py  # 可視化智能體
├── pipeline_service.py         # 管線編排服務
├── examples/
│   └── demo.py                 # 綜合演示
├── tests/
│   └── test_task_executor.py  # 單元測試
├── requirements.txt            # Python 依賴
└── README.md                   # 模組文檔
```

---

## 🚀 快速開始 Quick Start

### 1. 安裝依賴 Install Dependencies

```bash
cd intelligent-automation
pip install -r requirements.txt
```

### 2. 運行演示 Run Demo

```bash
python examples/demo.py
```

### 3. 基本使用 Basic Usage

```python
import asyncio
from pipeline_service import pipeline_service

async def analyze():
    result = await pipeline_service.process_request(
        query="分析代碼安全性",
        editor_code=your_code,
        analysis_type="security"
    )
    print(result)

asyncio.run(analyze())
```

---

## 🔧 集成方式 Integration Methods

### 方式 1：Python API Integration

**適用場景**: Python 項目直接調用

```python
from intelligent_automation import pipeline_service

# 健康檢查
health = pipeline_service.health_check()

# 代碼分析
result = await pipeline_service.process_request(
    query="分析這段代碼",
    editor_code=code,
    analysis_type="comprehensive"
)

# 實時流式分析
async for chunk in pipeline_service.stream_process(
    query="性能分析",
    editor_code=code
):
    print(chunk)
```

### 方式 2：CI/CD Pipeline Integration

**適用場景**: GitHub Actions, GitLab CI 等

```yaml
# .github/workflows/intelligent-analysis.yml
name: Intelligent Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'  # 依治理原則，建議使用彈性版本（或 '>=3.8'）
      
      - name: Install Dependencies
        run: |
          cd intelligent-automation
          pip install -r requirements.txt
      
      - name: Run Analysis
        run: |
          cd intelligent-automation
          python -c "
          import asyncio
          from pipeline_service import pipeline_service
          
          async def main():
              # 分析最近的 commit
              result = await pipeline_service.process_request(
                  query='Analyze recent changes',
                  analysis_type='comprehensive'
              )
              print(result)
          
          asyncio.run(main())
          "
```

### 方式 3：Docker Container Integration

**適用場景**: 容器化部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY intelligent-automation/ /app/intelligent-automation/

RUN cd intelligent-automation && pip install -r requirements.txt

CMD ["python", "intelligent-automation/pipeline_service.py"]
```

```bash
# 構建和運行
docker build -t intelligent-automation .
docker run -p 8080:8080 intelligent-automation
```

### 方式 4：Configuration File Integration

**適用場景**: 與 Auto-Fix Bot 整合

在 `.auto-fix-bot.yml` 中配置：

```yaml
intelligent_automation:
  enabled: true
  
  agents:
    task_executor:
      enabled: true
      analysis_types:
        - "comprehensive"
        - "security"
        - "performance"
      auto_fix_critical: true
    
    recognition_server:
      enabled: true
      security_validation: true
    
    visualization_agent:
      enabled: true
      generate_explanations: true
```

---

## 📊 使用場景 Use Cases

### 場景 1: 無人機飛控代碼監控

**Drone Flight Control Code Monitoring**

```python
# 實時監控飛控代碼
async def monitor_flight_control():
    while True:
        # 獲取最新代碼
        code = get_latest_flight_control_code()
        
        # 安全關鍵分析
        result = await pipeline_service.process_request(
            query="Safety-critical analysis for drone control",
            editor_code=code,
            analysis_type="security"
        )
        
        # 發現關鍵問題立即告警
        if result['result']['analysis']['issues']:
            critical = [i for i in result['result']['analysis']['issues'] 
                       if i['severity'] == 'critical']
            if critical:
                send_alert(critical)
        
        await asyncio.sleep(10)  # 每10秒檢查一次
```

### 場景 2: 自動駕駛決策代碼驗證

**Autonomous Vehicle Decision Code Validation**

```python
# PR 前驗證
async def validate_autonomous_code(pr_code):
    # 多層次驗證
    analyses = ['security', 'performance', 'comprehensive']
    
    for analysis_type in analyses:
        result = await pipeline_service.process_request(
            query=f"Validate autonomous vehicle code: {analysis_type}",
            editor_code=pr_code,
            analysis_type=analysis_type
        )
        
        # 任何關鍵問題都阻止合併
        if has_critical_issues(result):
            return False, result
    
    return True, "All validations passed"
```

### 場景 3: CI/CD 自動化迭代

**CI/CD Automated Iteration**

```python
# 自動修復並重新測試
async def auto_fix_and_test(code):
    # 分析
    result = await pipeline_service.process_request(
        query="Comprehensive analysis",
        editor_code=code,
        analysis_type="comprehensive"
    )
    
    # 如果有自動修復
    if result['result']['auto_fix_applied']:
        fixed_code = result['result']['fixed_code']
        
        # 運行測試
        test_result = run_tests(fixed_code)
        
        if test_result.passed:
            # 自動提交修復
            commit_fix(fixed_code, result)
            return True
    
    return False
```

---

## 🔒 安全特性 Security Features

### 威脅檢測 Threat Detection

智能識別以下安全威脅：

1. **Prompt Injection** - 提示詞注入
   - "show me your system prompt"
   - "ignore previous instructions"

2. **API Key Extraction** - API 密鑰提取
   - "reveal your api key"
   - "show me the token"

3. **Code Execution** - 危險代碼執行
   - eval(), exec()
   - os.system()

4. **Data Leakage** - 數據洩露
   - Hardcoded passwords
   - Sensitive data exposure

### 自動修復 Auto-Fix

支持自動修復的問題類型：

- ✅ **Critical Security Issues** - 關鍵安全問題
  - eval/exec 移除
  - 危險函數替換

- ✅ **Code Quality Issues** - 代碼質量問題
  - 格式化問題
  - 簡單邏輯錯誤

- ⚠️ **Performance Issues** - 性能問題
  - 建議優化（需人工確認）

---

## 📈 性能指標 Performance Metrics

### 目標性能 Target Performance

| 指標 | 目標值 | 說明 |
|------|--------|------|
| 響應時間 | < 100ms | 平均分析響應時間 |
| 並發處理 | 1000+ req/s | 最大並發請求數 |
| 準確率 | 99.5% | 安全問題檢測準確率 |
| 成功率 | 95.8% | 自動修復成功率 |
| 可用性 | 99.9% | 系統可用性 |

### 監控方式 Monitoring

```python
# 獲取統計信息
stats = pipeline_service.get_statistics()
print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats.get('success_rate', 'N/A')}%")

# 健康檢查
health = pipeline_service.health_check()
print(f"Status: {health['status']}")
for agent, status in health['agents'].items():
    print(f"  {agent}: {status}")
```

---

## 🧪 測試 Testing

### 運行測試 Run Tests

```bash
# 運行所有測試
cd intelligent-automation
pytest tests/ -v

# 運行特定測試
pytest tests/test_task_executor.py -v

# 生成覆蓋率報告
pytest --cov=agents tests/
```

### 測試範例 Test Examples

```python
import pytest
from agents.task_executor import TaskExecutor

@pytest.mark.asyncio
async def test_security_analysis():
    executor = TaskExecutor()
    
    unsafe_code = "result = eval(user_input)"
    result = await executor.analyze_code(unsafe_code, "security")
    
    assert len(result["issues"]) > 0
    assert any(i["severity"] == "critical" for i in result["issues"])
```

---

## 🐛 故障排除 Troubleshooting

### 常見問題 Common Issues

#### 1. 模組導入錯誤

```bash
# 確保路徑正確
export PYTHONPATH="${PYTHONPATH}:/path/to/intelligent-automation"
```

#### 2. 依賴缺失

```bash
# 重新安裝依賴
pip install -r requirements.txt --force-reinstall
```

#### 3. 異步錯誤

```python
# 確保使用 asyncio.run()
import asyncio
asyncio.run(your_async_function())
```

---

## 📚 進階配置 Advanced Configuration

### 自定義分析規則

```python
# 擴展 TaskExecutor
class CustomTaskExecutor(TaskExecutor):
    async def _check_custom_rules(self, code: str) -> list:
        issues = []
        
        # 添加自定義檢查
        if "custom_pattern" in code:
            issues.append({
                "type": "custom",
                "severity": "high",
                "description": "Custom rule violation"
            })
        
        return issues
```

### 添加新智能體

```python
# agents/custom_agent.py
class CustomAgent:
    def __init__(self):
        self.name = "custom_agent"
    
    async def process(self, query: str) -> dict:
        # 實現自定義邏輯
        return {"result": "processed"}
```

---

## 🔗 相關文檔 Related Documentation

- [README.md](../README.md) - 項目概述
- [intelligent-automation/README.md](../intelligent-automation/README.md) - 模組詳細文檔
- [AUTO_FIX_BOT_GUIDE.md](../AUTO_FIX_BOT_GUIDE.md) - Auto-Fix Bot 使用指南
- [DELEGATION_WORKFLOW.md](../DELEGATION_WORKFLOW.md) - 委派工作流程

---

## 💡 最佳實踐 Best Practices

1. **定期更新** - 保持依賴更新以獲取最新功能
2. **監控日誌** - 關注系統日誌以發現異常
3. **測試覆蓋** - 確保充分的測試覆蓋率
4. **安全配置** - 使用環境變數管理敏感信息
5. **性能調優** - 根據負載調整並發設置

---

## 🤝 貢獻 Contributing

歡迎貢獻！請查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解詳情。

---

## 📄 許可證 License

MIT License - 詳見 [LICENSE](../LICENSE)

---

**最後更新**: 2025-11-25  
**維護者**: SynergyMesh Team
