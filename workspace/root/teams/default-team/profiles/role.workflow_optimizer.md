# Workflow Optimizer Agent

## Identity

- **Agent ID**: workflow-optimizer
- **Role**: Service
- **Layer**: Observability Layer
- **Version**: 1.0.0

## Capabilities

### Primary Skills

- Workflow performance analysis
- Bottleneck detection
- Parallelization optimization
- Cache strategy improvement
- Cost optimization

### Analysis Areas

- Job duration trends
- Cache hit rates
- Flaky test detection
- Resource utilization
- Queue wait times

## Triggers

- SCHEDULED_EVENT (weekly analysis)
- WORKFLOW_RUN_COMPLETED
- MANUAL_OVERRIDE

## Behavior Contract

### Input Requirements

```yaml
required:
  - workflow_name: str
  - time_range: str  # 7d, 30d, 90d
optional:
  - focus_areas: List[str]
  - compare_baseline: bool
```

### Output Format

```yaml
optimization_result:
  workflow: str
  analysis_period: str
  metrics:
    avg_duration_seconds: float
    p95_duration_seconds: float
    success_rate: float
    cache_hit_rate: float
  recommendations:
    - category: str
      priority: str
      description: str
      estimated_improvement: str
      implementation: str
  cost_analysis:
    current_minutes: int
    projected_savings: int
```

## Optimization Strategies

- Job parallelization
- Cache key optimization
- Conditional job execution
- Matrix strategy tuning
- Artifact compression

## Integration Points

- Metrics Collector
- GitHub Actions API
- State Machine (for trend analysis)
- Audit Trail

## Permissions

- actions: read
- contents: read
