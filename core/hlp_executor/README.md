# HLP Executor Core Plugin

## 🎯 Overview

The **Hard Logic Plugin (HLP) Executor Core** is an enterprise-grade async DAG
orchestration engine designed for mission-critical workflow execution with
advanced recovery capabilities.

## 🌟 Key Features

### 1. Async DAG Orchestration

- **Topological Sorting**: Intelligent dependency resolution (planned)
- **Risk-Weighted Scheduling**: Prioritize based on risk assessment (planned)
- **Parallel Execution**: Maximize throughput with concurrent task execution
- **Dynamic Dependency Resolution**: Real-time graph updates (planned)

### 2. Partial Rollback Management

Three-level granularity for precise recovery:

- **Phase Level**: Rollback entire execution phases
- **Plan-Unit Level**: Rollback specific plan components
- **Artifact Level**: Rollback individual artifacts

### 3. State Machine Orchestration

7-state transition flow with recovery:

```
PENDING → RUNNING → COMPLETED
         ↓         ↓
      PAUSED → RESUMED
         ↓
      FAILED → RECOVERING → RECOVERED/FAILED
```

### 4. Dynamic Retry Policies

- **Exponential Backoff**: Progressive delay increases
- **Jitter**: Prevent thundering herd
- **Risk-Adaptive**: Adjust retry strategy based on risk level

### 5. Quantum Backend Integration

- Graceful degradation to classical mode
- Optional quantum scheduler support
- Automatic fallback mechanisms

## 📦 Installation

The HLP Executor is deployed as part of the SynergyMesh platform.

### Kubernetes Deployment

```bash
# Deploy HLP Executor
kubectl apply -f infrastructure/kubernetes/deployments/hlp-executor-core.yaml

# Deploy RBAC
kubectl apply -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml

# Verify deployment
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core
```

## 🔧 Configuration

### Environment Variables

| Variable                   | Description               | Default           |
| -------------------------- | ------------------------- | ----------------- |
| `ENVIRONMENT`              | Deployment environment    | `production`      |
| `LOG_LEVEL`                | Logging level             | `INFO`            |
| `LOG_FORMAT`               | Log format                | `json`            |
| `STATE_STORE`              | State persistence backend | `kubernetes-etcd` |
| `PARTIAL_ROLLBACK_ENABLED` | Enable partial rollback   | `true`            |
| `QUANTUM_ENABLED`          | Enable quantum backend    | `false`           |
| `QUANTUM_FALLBACK_MODE`    | Fallback mode             | `classical`       |

## 🔌 API Endpoints

### HTTP (Port 8080)

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /health/startup` - Startup probe
- `POST /execute` - Execute DAG workflow
- `POST /rollback` - Trigger partial rollback
- `GET /status/{execution_id}` - Get execution status

### gRPC (Port 50051)

- `ExecuteDAG` - Execute workflow with streaming updates
- `GetExecutionStatus` - Get real-time status
- `TriggerRollback` - Initiate rollback operation

### Metrics (Port 9090)

- Prometheus-compatible metrics endpoint
- Custom metrics for DAG execution
- SLO tracking metrics

## 📊 Performance SLOs

| Metric                         | Target  |
| ------------------------------ | ------- |
| DAG Parse Latency (P95)        | < 120ms |
| State Transition Latency (P90) | < 50ms  |
| Recovery Time Objective (RTO)  | < 30s   |
| Service Availability           | 99.9%   |

## 🔒 Security

### SLSA Level 3 Compliance

- Build provenance attestation
- Sigstore signature verification
- Supply chain security

### Security Features

- Non-root container execution
- Read-only root filesystem
- Network policies enforced
- Secret management via Kubernetes

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  HLP Executor Core                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ DAG Parser  │→ │ State Machine│→ │ Executor     │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↓          │
│  ┌─────────────────────────────────────────────────┐  │
│  │         Partial Rollback Manager                │  │
│  └─────────────────────────────────────────────────┘  │
│         ↓                                              │
│  ┌─────────────┐  ┌──────────────┐                    │
│  │ Retry Policy│  │ State Store  │                    │
│  └─────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## 📚 Documentation

### Related Documents

- [Plugin Registry](../../../governance/24-registry/plugins/hlp-executor-core.yaml)
- [Deployment Manifest](../../../infrastructure/kubernetes/deployments/hlp-executor-core.yaml)
- [RBAC Configuration](../../../infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml)
- [HLP Executor Action Plan](../../../docs/refactor_playbooks/03_refactor/HLP_EXECUTOR_CORE_ACTION_PLAN.md)

### Architecture Documentation

- [State Machine JSON Schema](../../../governance/31-schemas/state-machine.schema.json)
- [Checkpoint Strategy](../../../docs/architecture/CHECKPOINT_STRATEGY.md)
- [Recovery Mode](../../../docs/architecture/RECOVERY_MODE.md)

### Operations

- [Error Handling Runbook](../../../docs/operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md)
- [Emergency Procedures](../../../docs/operations/runbooks/HLP_EXECUTOR_EMERGENCY.md)
- [SLO Documentation](../../../docs/operations/slo/HLP_EXECUTOR_SLO.md)

## 🔄 Development Status

| Feature                | Status     | Version |
| ---------------------- | ---------- | ------- |
| Core DAG Engine        | 📋 Planned | 1.0.0   |
| State Machine          | 📋 Planned | 1.0.0   |
| Partial Rollback       | 📋 Planned | 1.0.0   |
| Retry Policies         | 📋 Planned | 1.0.0   |
| Quantum Integration    | 📋 Planned | 1.0.0   |
| Kubernetes Deployment  | ✅ Ready   | 1.0.0   |
| RBAC Configuration     | ✅ Ready   | 1.0.0   |
| Monitoring Integration | ✅ Ready   | 1.0.0   |

## 🚀 Next Steps

### P0 (Immediate)

- [ ] Implement core DAG execution engine
- [ ] Implement state machine transitions
- [ ] Implement partial rollback logic
- [ ] Create unit tests

### P1 (Short-term)

- [ ] Implement retry policies
- [ ] Integrate with monitoring
- [ ] Create integration tests
- [ ] Performance benchmarking

### P2 (Long-term)

- [ ] Quantum backend integration
- [ ] Advanced scheduling algorithms
- [ ] ML-based optimization
- [ ] Multi-cluster support

## 📞 Support

For issues, questions, or contributions:

- **Issue Tracker**: GitHub Issues
- **Documentation**: `/docs`
- **Team**: SynergyMesh Platform Team

## 📄 License

MIT License - See LICENSE file for details

---

**Version**: 0.1.0  
**Status**: Planning & Infrastructure Setup  
**Last Updated**: 2025-12-10
