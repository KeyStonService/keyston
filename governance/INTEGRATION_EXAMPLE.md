# Integration Example: Self-Healing Service Deployment

This example demonstrates how the layered governance framework coordinates to
deploy and manage a self-healing service.

## Scenario

Deploy a high-availability web service with automatic recovery capabilities.

## Flow

### 1. Intent Definition (20-intent)

User submits high-level intent:

```yaml
intent:
  id: 'DEPLOY-WEB-001'
  type: 'deployment'
  description: '部署高可用性 Web 服務，保證 99.9% 可用性'

  requirements:
    availability: '99.9%'
    performance:
      latency_p95: '<100ms'
      throughput: '>1000 req/s'
    scalability:
      min_instances: 3
      max_instances: 10

  constraints:
    budget: '$500/month'
    region: ['us-west', 'us-east']
```

### 2. Policy Validation (10-policy)

Intent is validated against governance policies:

```yaml
validation:
  policies_checked:
    - security-policies.yaml
    - compliance-policies.yaml
    - architecture-policies.yaml

  results:
    - policy: 'SEC-AUTH-001'
      status: 'passed'
      message: 'Authentication configured'

    - policy: 'SEC-ENC-001'
      status: 'passed'
      message: 'TLS 1.3 enabled'

    - policy: 'COMP-BUDGET-001'
      status: 'passed'
      message: 'Within budget constraints'
```

### 3. Semantic Translation (20-intent)

Intent is translated to technical actions:

```yaml
translation:
  actions:
    - action: 'create_load_balancer'
      config:
        type: 'application'
        scheme: 'internet-facing'

    - action: 'deploy_instances'
      config:
        count: 3
        instance_type: 't3.medium'
        availability_zones: ['us-west-2a', 'us-west-2b', 'us-west-2c']

    - action: 'configure_auto_scaling'
      config:
        min: 3
        max: 10
        target_cpu: 70

    - action: 'setup_health_checks'
      config:
        interval: 30
        timeout: 5
        healthy_threshold: 2
        unhealthy_threshold: 3

    - action: 'enable_self_healing'
      config:
        recovery_policy:
          strategy: 'restart'
          max_attempts: 3
          timeout_seconds: 60
```

### 4. Contract Verification (60-contracts)

Verify all required contracts:

```yaml
contract_verification:
  contracts_required:
    - contract.self-healing.v1
    - contract.monitoring.v1
    - contract.automation.v1

  verification_results:
    - contract: 'contract.self-healing.v1'
      status: 'verified'
      version: '1.0.0'
      compatible: true
```

### 5. Agent Coordination (30-agents)

Deploy and configure agents:

```yaml
agent_deployment:
  agents:
    - agent_id: 'monitoring-agent-001'
      type: 'monitoring'
      version: '2.1.0'
      permissions:
        - 'read:metrics'
        - 'write:health_status'

    - agent_id: 'self-healing-agent-001'
      type: 'self-healing'
      version: '1.5.0'
      permissions:
        - 'read:health_status'
        - 'execute:recovery'
        - 'write:audit_logs'

    - agent_id: 'scaling-agent-001'
      type: 'auto-scaling'
      version: '1.3.0'
      permissions:
        - 'read:metrics'
        - 'execute:scale_operations'
```

### 6. Automation Execution (39-automation)

Execute deployment workflow:

```yaml
execution:
  workflow_id: 'deploy-web-service-001'

  steps:
    - step: 'provision_infrastructure'
      status: 'completed'
      duration_seconds: 120

    - step: 'deploy_application'
      status: 'completed'
      duration_seconds: 180

    - step: 'configure_monitoring'
      status: 'completed'
      duration_seconds: 30

    - step: 'enable_self_healing'
      status: 'completed'
      duration_seconds: 15

  total_duration_seconds: 345
  status: 'success'
```

### 7. Audit Logging (70-audit)

All actions are logged:

```yaml
audit_trail:
  trace_id: 'trace-deploy-web-001'

  events:
    - event_id: 'evt-001'
      timestamp: '2025-12-11T14:00:00Z'
      actor: 'user@example.com'
      action: 'submit_intent'
      resource: 'DEPLOY-WEB-001'
      outcome: 'success'

    - event_id: 'evt-002'
      timestamp: '2025-12-11T14:00:05Z'
      actor: 'policy-engine'
      action: 'validate_policies'
      resource: 'DEPLOY-WEB-001'
      outcome: 'success'

    - event_id: 'evt-003'
      timestamp: '2025-12-11T14:00:10Z'
      actor: 'intent-orchestrator'
      action: 'translate_intent'
      resource: 'DEPLOY-WEB-001'
      outcome: 'success'

    # ... more events
```

### 8. Monitoring & Self-Healing (40-self-healing)

Service is now monitored and auto-healing:

```yaml
monitoring:
  component_id: 'web-service-001'
  health_status: 'healthy'

  metrics:
    availability: 99.95
    latency_p95: 85
    throughput: 1250
    error_rate: 0.01

  self_healing_config:
    enabled: true
    recovery_policy:
      strategy: 'restart'
      max_attempts: 3
      timeout_seconds: 60

    triggers:
      - condition: "health_status == 'failed'"
        action: 'restart_instance'

      - condition: 'error_rate > 5%'
        action: 'restart_service'

      - condition: 'latency_p95 > 200ms'
        action: 'scale_out'
```

### 9. Feedback Collection (80-feedback)

System collects performance data:

```yaml
feedback:
  period: '7 days'

  metrics_collected:
    deployment:
      success_rate: 98.5
      average_deployment_time: 345

    availability:
      achieved: 99.95
      target: 99.9
      delta: +0.05

    performance:
      latency_p95: 85
      target: 100
      delta: -15

    self_healing:
      recovery_attempts: 12
      successful_recoveries: 11
      success_rate: 91.7

  analysis:
    strengths:
      - 'Exceeded availability target'
      - 'Performance better than expected'
      - 'Self-healing working effectively'

    improvements:
      - '1 recovery failure needs investigation'
      - 'Consider adding buffer instances for peak load'
```

### 10. Optimization Recommendations (80-feedback)

AI generates optimization suggestions:

```yaml
recommendations:
  - recommendation_id: 'OPT-001'
    type: 'capacity_optimization'
    description: 'Add 1 buffer instance to handle peak load'
    expected_benefit:
      availability_improvement: '+0.02%'
      cost_increase: '+$50/month'
    priority: 'medium'
    approval_required: true

  - recommendation_id: 'OPT-002'
    type: 'self_healing_improvement'
    description: 'Investigate failed recovery attempt'
    expected_benefit:
      self_healing_success_rate: '+5%'
      cost: '0'
    priority: 'high'
    approval_required: false
```

## Integration Points

```
User Intent → 20-intent → 10-policy → 60-contracts → 30-agents → 39-automation
                ↓            ↓            ↓              ↓            ↓
             70-audit ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
                ↓
          80-feedback → Optimization → Back to 10-policy (closed loop)
```

## Benefits Demonstrated

1. **Policy Compliance**: Automatic validation against security and compliance
   policies
2. **Intent-Driven**: High-level business intent translated to technical actions
3. **Contract Safety**: Interface contracts ensure compatibility
4. **Agent Governance**: AI agents deployed with proper permissions and
   monitoring
5. **Automation**: Deployment fully automated with minimal human intervention
6. **Auditability**: Complete audit trail for compliance and debugging
7. **Self-Healing**: Automatic recovery from failures
8. **Continuous Optimization**: AI-driven recommendations for improvement
9. **Closed-Loop**: Feedback drives policy and configuration refinement

## Time to Value

- **Intent to Deployment**: ~6 minutes
- **Recovery Time**: ~60 seconds
- **Optimization Cycle**: 7 days

## Success Metrics

- Deployment Success Rate: 98.5%
- Availability: 99.95% (target: 99.9%)
- Self-Healing Success: 91.7%
- Policy Compliance: 100%
- Audit Coverage: 100%
