# Orchestrator Agent

## 概述

編排器代理 (Orchestrator Agent) 是整個自動化系統的指揮中心，負責協調各個代理的工作，管理工作流程，並確保整個系統高效運行。

## 功能特性

### 1. 工作流編排

- **任務調度**: 智能分配任務給各個代理
- **依賴管理**: 處理任務之間的依賴關係
- **並行執行**: 優化並行任務執行
- **錯誤處理**: 統一的錯誤處理和恢復

### 2. 代理協調

- **Code Analyzer**: 觸發代碼分析
- **Vulnerability Detector**: 啟動安全掃描
- **Auto Repair**: 執行自動修復
- **狀態同步**: 保持所有代理狀態一致

### 3. 決策引擎

- **優先級排序**: 基於業務規則排序任務
- **資源分配**: 智能分配計算資源
- **策略選擇**: 根據情況選擇最佳策略
- **風險評估**: 評估操作風險

## 架構設計

```
orchestrator/
├── src/
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── scheduler.py
│   │   └── coordinator.py
│   ├── workflows/
│   │   ├── analysis_workflow.py
│   │   ├── repair_workflow.py
│   │   └── validation_workflow.py
│   ├── engines/
│   │   ├── decision_engine.py
│   │   └── priority_engine.py
│   ├── models/
│   │   ├── task.py
│   │   ├── workflow.py
│   │   └── result.py
│   └── engine.py
├── config/
│   ├── orchestrator.yaml
│   ├── workflows/
│   └── policies/
├── tests/
└── README.md
```

## 工作流類型

### 1. 分析工作流

```yaml
# analysis_workflow.yaml
name: "Code Analysis Workflow"
version: "1.0.0"
trigger:
  - on: push
  - on: pull_request
  - on: schedule
    cron: "0 2 * * *"

steps:
  - id: checkout
    agent: git
    action: checkout
  
  - id: analyze
    agent: code-analyzer
    action: analyze
    params:
      scan_type: full
      parallel: true
    depends_on: [checkout]
  
  - id: detect_vulnerabilities
    agent: vulnerability-detector
    action: scan
    params:
      severity_threshold: HIGH
    depends_on: [analyze]
  
  - id: generate_report
    agent: reporter
    action: generate
    params:
      format: [json, html, pdf]
    depends_on: [analyze, detect_vulnerabilities]

on_failure:
  - notify: [slack, email]
  - create_issue: true
```

### 2. 修復工作流

```yaml
# repair_workflow.yaml
name: "Auto Repair Workflow"
version: "1.0.0"
trigger:
  - on: analysis_complete
    condition: "critical_issues > 0"

steps:
  - id: prioritize
    agent: orchestrator
    action: prioritize_issues
  
  - id: repair
    agent: auto-repair
    action: repair_batch
    params:
      auto_apply: false
      strategy: rule_based
    depends_on: [prioritize]
  
  - id: validate
    agent: validator
    action: validate_repairs
    params:
      run_tests: true
      security_scan: true
    depends_on: [repair]
  
  - id: create_pr
    agent: git
    action: create_pull_request
    params:
      title: "🤖 Auto-fix: {issue_count} issues"
      reviewers: [security-team, tech-lead]
    depends_on: [validate]
    condition: "validation.passed"

on_success:
  - notify: [github]
  - update_metrics: true
```

### 3. 持續監控工作流

```yaml
# monitoring_workflow.yaml
name: "Continuous Monitoring Workflow"
version: "1.0.0"
trigger:
  - on: schedule
    cron: "*/15 * * * *"  # 每 15 分鐘

steps:
  - id: health_check
    agent: monitor
    action: check_health
  
  - id: collect_metrics
    agent: monitor
    action: collect_metrics
    depends_on: [health_check]
  
  - id: analyze_trends
    agent: analyzer
    action: analyze_trends
    params:
      window: 24h
    depends_on: [collect_metrics]
  
  - id: alert_if_needed
    agent: alerter
    action: check_thresholds
    params:
      thresholds:
        error_rate: 0.05
        response_time: 200ms
    depends_on: [analyze_trends]

on_failure:
  - escalate: true
  - page: on-call
```

## 使用方式

### 基本用法

```python
from orchestrator import Orchestrator

# 初始化編排器
orchestrator = Orchestrator(config_path="config/orchestrator.yaml")

# 執行工作流
result = await orchestrator.run_workflow(
    workflow_name="analysis_workflow",
    params={
        "repository": "owner/repo",
        "branch": "main"
    }
)

# 檢查結果
if result.success:
    print(f"Workflow completed: {result.summary}")
else:
    print(f"Workflow failed: {result.error}")
```

### 高級用法

```python
# 註冊自定義工作流
orchestrator.register_workflow(
    name="custom_workflow",
    definition=workflow_definition
)

# 動態調整優先級
orchestrator.set_priority(
    task_id="task-123",
    priority=1
)

# 暫停和恢復工作流
orchestrator.pause_workflow("workflow-456")
orchestrator.resume_workflow("workflow-456")

# 監控工作流狀態
status = orchestrator.get_workflow_status("workflow-789")
```

## 配置範例

```yaml
# orchestrator.yaml
enabled: true
max_concurrent_workflows: 10
max_tasks_per_workflow: 50

scheduler:
  type: priority_queue
  max_workers: 16
  timeout: 3600

agents:
  code-analyzer:
    enabled: true
    max_instances: 4
    endpoint: "http://code-analyzer:8001"
  
  vulnerability-detector:
    enabled: true
    max_instances: 2
    endpoint: "http://vuln-detector:8002"
  
  auto-repair:
    enabled: true
    max_instances: 4
    endpoint: "http://auto-repair:8003"

policies:
  auto_approval:
    enabled: false
    conditions:
      - severity: LOW
      - test_coverage: "> 0.9"
  
  escalation:
    enabled: true
    thresholds:
      critical_issues: 1
      high_issues: 5
      workflow_failures: 3

notifications:
  slack:
    enabled: true
    webhook: "${SLACK_WEBHOOK}"
  
  email:
    enabled: true
    recipients: ["platform@synergymesh.com"]
  
  github:
    enabled: true
    create_issues: true
```

## 決策引擎

### 優先級算法

```python
class PriorityEngine:
    """優先級決策引擎"""
    
    def calculate_priority(self, task: Task) -> int:
        """
        計算任務優先級
        
        優先級因素：
        1. 嚴重程度 (40%)
        2. 業務影響 (30%)
        3. 修復難度 (20%)
        4. 時間緊急度 (10%)
        """
        severity_score = self._severity_score(task.severity)
        impact_score = self._impact_score(task.impact)
        difficulty_score = self._difficulty_score(task.difficulty)
        urgency_score = self._urgency_score(task.created_at)
        
        priority = (
            severity_score * 0.4 +
            impact_score * 0.3 +
            difficulty_score * 0.2 +
            urgency_score * 0.1
        )
        
        return int(priority * 100)
    
    def _severity_score(self, severity: str) -> float:
        """嚴重程度評分"""
        scores = {
            "CRITICAL": 1.0,
            "HIGH": 0.7,
            "MEDIUM": 0.4,
            "LOW": 0.2
        }
        return scores.get(severity, 0.0)
```

### 資源分配

```python
class ResourceAllocator:
    """資源分配器"""
    
    def allocate_resources(
        self,
        tasks: List[Task],
        available_workers: int
    ) -> Dict[str, int]:
        """
        智能分配資源
        
        策略：
        1. 高優先級任務優先
        2. 平衡各類型任務
        3. 考慮任務依賴
        """
        allocation = {}
        
        # 按優先級排序
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.priority,
            reverse=True
        )
        
        # 分配 workers
        remaining_workers = available_workers
        for task in sorted_tasks:
            if remaining_workers <= 0:
                break
            
            required = task.estimated_workers
            allocated = min(required, remaining_workers)
            
            allocation[task.id] = allocated
            remaining_workers -= allocated
        
        return allocation
```

## 監控與可觀測性

### 指標收集

```python
class MetricsCollector:
    """指標收集器"""
    
    def collect_metrics(self) -> Dict[str, Any]:
        """收集系統指標"""
        return {
            "workflows": {
                "total": self.count_workflows(),
                "active": self.count_active_workflows(),
                "completed": self.count_completed_workflows(),
                "failed": self.count_failed_workflows()
            },
            "tasks": {
                "queued": self.count_queued_tasks(),
                "running": self.count_running_tasks(),
                "completed": self.count_completed_tasks()
            },
            "agents": {
                "code_analyzer": self.get_agent_status("code-analyzer"),
                "vulnerability_detector": self.get_agent_status("vulnerability-detector"),
                "auto_repair": self.get_agent_status("auto-repair")
            },
            "performance": {
                "avg_workflow_duration": self.avg_workflow_duration(),
                "avg_task_duration": self.avg_task_duration(),
                "throughput": self.calculate_throughput()
            }
        }
```

### 健康檢查

```python
async def health_check() -> HealthStatus:
    """系統健康檢查"""
    
    status = HealthStatus()
    
    # 檢查各個代理
    for agent_name, agent in agents.items():
        try:
            response = await agent.ping()
            status.agents[agent_name] = "healthy"
        except Exception as e:
            status.agents[agent_name] = "unhealthy"
            status.errors.append(f"{agent_name}: {e}")
    
    # 檢查數據庫連接
    try:
        await db.execute("SELECT 1")
        status.database = "healthy"
    except Exception as e:
        status.database = "unhealthy"
        status.errors.append(f"Database: {e}")
    
    # 檢查消息隊列
    try:
        await queue.ping()
        status.queue = "healthy"
    except Exception as e:
        status.queue = "unhealthy"
        status.errors.append(f"Queue: {e}")
    
    status.overall = "healthy" if not status.errors else "unhealthy"
    
    return status
```

## 錯誤處理

### 重試策略

```python
class RetryStrategy:
    """重試策略"""
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff: str = "exponential"
    ):
        self.max_retries = max_retries
        self.backoff = backoff
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """執行函數，失敗時重試"""
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # 計算等待時間
                wait_time = self._calculate_wait_time(attempt)
                await asyncio.sleep(wait_time)
    
    def _calculate_wait_time(self, attempt: int) -> float:
        """計算退避時間"""
        if self.backoff == "exponential":
            return 2 ** attempt
        elif self.backoff == "linear":
            return attempt + 1
        else:
            return 1.0
```

## 性能優化

### 並行執行

```python
async def execute_parallel_tasks(tasks: List[Task]) -> List[Result]:
    """並行執行任務"""
    
    # 分析任務依賴
    dependency_graph = build_dependency_graph(tasks)
    
    # 拓撲排序
    sorted_tasks = topological_sort(dependency_graph)
    
    # 按層級並行執行
    results = []
    for level in sorted_tasks:
        level_results = await asyncio.gather(*[
            execute_task(task) for task in level
        ])
        results.extend(level_results)
    
    return results
```

## CI/CD 整合

```yaml
# .github/workflows/orchestrator.yml
name: Orchestrator

on:
  push:
  pull_request:
  schedule:
    - cron: '0 */6 * * *'

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Orchestrator
        run: |
          python agent/orchestrator/src/engine.py \
            --workflow analysis_workflow \
            --params repo=${{ github.repository }}
```

## 最佳實務

1. **工作流設計**: 保持工作流簡單、可重用
2. **錯誤處理**: 實施完善的錯誤處理和恢復機制
3. **監控**: 持續監控系統健康和性能
4. **文檔**: 維護清晰的工作流文檔

## 性能指標

- **工作流吞吐量**: 100-500 workflows/hour
- **任務調度延遲**: < 1 秒
- **系統可用性**: > 99.9%
- **錯誤恢復時間**: < 5 分鐘

## 授權

MIT License
