# Automation Pipelines - 自動化管線

## Overview / 概覽

This directory contains reusable automation pipelines for SynergyMesh, including
the AI-powered Instant Execution Pipeline.

本目錄包含 SynergyMesh 的可重用自動化管線，包括 AI 驅動的即時執行管線。

---

## 📦 Available Pipelines / 可用管線

### 1. Instant Execution Pipeline ⭐

**File:** `instant_execution_pipeline.py`

**Purpose:** AI-powered 3-stage instant execution for zero-touch deployment

**Key Features:**

- ✅ Stage 1: AI Analysis (< 5s)
- ✅ Stage 2: Synthetic Validation (< 30s)
- ✅ Stage 3: Automated Deployment (< 30min)
- ✅ 97% accuracy target
- ✅ Self-healing capabilities
- ✅ Rollback support

**Quick Start:**

```bash
# Complete pipeline (dry-run)
./scripts/run-instant-execution.sh --dry-run

# Run specific stage
python3 automation/pipelines/instant_execution_pipeline.py stage --stage 1

# With configuration
python3 automation/pipelines/instant_execution_pipeline.py run \
  --namespace synergymesh-system \
  --output results.json
```

**Documentation:** See
[INSTANT_EXECUTION_INTEGRATION_MAP.md](../../docs/INSTANT_EXECUTION_INTEGRATION_MAP.md)

---

## 🏗️ Pipeline Architecture / 管線架構

```
automation/pipelines/
│
├── __init__.py                        # Package initialization
├── README.md                          # This file
└── instant_execution_pipeline.py     # Main instant execution pipeline
```

---

## 🔧 Creating Custom Pipelines / 創建自訂管線

### Template Structure

```python
#!/usr/bin/env python3
"""
Custom Pipeline - 自訂管線
"""

import asyncio
from typing import Dict, Any

class CustomPipeline:
    """Your custom pipeline"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def run_pipeline(self) -> Dict[str, Any]:
        """Execute pipeline"""
        # Your logic here
        pass

async def main():
    pipeline = CustomPipeline({})
    result = await pipeline.run_pipeline()
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📚 Integration / 整合

### With Automation Launcher

```python
# automation_launcher.py
from automation.pipelines import InstantExecutionPipeline, PipelineContext

# Create pipeline
context = PipelineContext(namespace="synergymesh-system")
pipeline = InstantExecutionPipeline(context)

# Run
result = await pipeline.run_pipeline()
```

### With CI/CD

```yaml
# .github/workflows/deploy.yml
- name: Run Instant Execution Pipeline
  run: |
    ./scripts/run-instant-execution.sh \
      --namespace production \
      --output pipeline-results.json
```

---

## 📊 Performance Metrics / 效能指標

| Pipeline          | Stage 1 | Stage 2 | Stage 3 | Total   |
| ----------------- | ------- | ------- | ------- | ------- |
| Instant Execution | < 5s    | < 30s   | < 30min | < 31min |

---

## 🔗 Related Documentation / 相關文件

- [Integration Map](../../docs/INSTANT_EXECUTION_INTEGRATION_MAP.md) - Complete
  architecture
- [AI Governance Engine](../../tools/ai/governance_engine.py) - AI decision
  making
- [Validation Engine](../../tools/automation/engines/baseline_validation_engine.py) -
  Resource validation
- [Test Framework](../../tests/automation/test_framework_patterns.py) - Testing
  patterns
- [Deployment Script](../../scripts/k8s/deploy-baselines.sh) - K8s deployment

---

## 🚀 Quick Links / 快速連結

- **Configuration:** `config/instant-execution-pipeline.yaml`
- **Quick Start:** `scripts/run-instant-execution.sh`
- **Main Pipeline:** `instant_execution_pipeline.py`

---

## 📄 License

See: [LICENSE](../../LICENSE)
