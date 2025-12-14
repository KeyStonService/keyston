# Agent Governance Quick Start Guide

> **⚡ INSTANT Execution Enabled**  
> Deployment Time: < 30 seconds | Human Intervention: 0

## 🎯 Overview

This guide provides step-by-step instructions for launching the SynergyMesh agent governance framework and deploying the unmanned-island-agent with full compliance and automation.

## 📋 Prerequisites

- Git repository cloned
- Python 3.10+ installed
- Node.js 18+ installed
- Access to repository root

## 🚀 Quick Start (< 30 seconds)

### Option 1: INSTANT Deployment Script

```bash
# Navigate to repository root
cd /path/to/SynergyMesh

# Run INSTANT deployment
./governance/deploy-instant.sh
```

**Expected Output:**
```
✅ DEPLOYMENT COMPLETE - 部署完成
⏱️  Total Time: 0-2s
✅ INSTANT Standard: PASSED (< 3 minutes)
📊 Human Interventions: 0
🚀 Governance Framework: PRODUCTION READY
```

### Option 2: Manual Validation

```bash
# 1. Validate governance structure
ls -la governance/30-agents/

# 2. Check agent registration
cat governance/30-agents/registry/agent-catalog.yaml | grep unmanned-island-agent

# 3. Verify YAML syntax
python3 -c "import yaml; yaml.safe_load(open('governance/30-agents/framework.yaml'))"

# 4. Check agent definition
cat .github/agents/my-agent.agent.md
```

## 📊 Verify Deployment

### 1. Check Agent Status

```yaml
# File: governance/30-agents/registry/agent-catalog.yaml
agents:
  - agent_id: "unmanned-island-agent"
    status: "active"
    lifecycle:
      stage: "production"
```

### 2. Verify Compliance

```bash
# ISO/IEC 42001
cat governance/30-agents/compliance/iso-42001.yaml

# RBAC Policies
cat governance/30-agents/permissions/rbac-policies.yaml

# Health Checks
cat governance/30-agents/monitoring/health-checks.yaml
```

### 3. Test Integration

```bash
# Check policy integration
ls governance/10-policy/

# Check contract registry
ls governance/60-contracts/

# Check audit system
ls governance/70-audit/

# Check feedback loop
ls governance/80-feedback/
```

## 🔧 Configuration

### Agent Catalog

Location: `governance/30-agents/registry/agent-catalog.yaml`

```yaml
agents:
  - agent_id: "unmanned-island-agent"
    name: "Unmanned Island Agent"
    version: "2.0.0"
    status: "active"
    capabilities:
      - intelligent_automation
      - platform_integration
      - autonomous_operation
      - governance_compliance
```

### RBAC Policies

Location: `governance/30-agents/permissions/rbac-policies.yaml`

```yaml
agent_assignments:
  unmanned-island-agent:
    roles:
      - "agent_autonomous"
    custom_permissions:
      - "governance:validate"
```

### Health Monitoring

Location: `governance/30-agents/monitoring/health-checks.yaml`

```yaml
agents:
  unmanned-island-agent:
    enabled: true
    liveness:
      - name: "agent_responsive"
        endpoint: "/health"
        interval: 30s
```

## 📈 Monitoring & Observability

### Health Dashboard

```bash
# View agent health status
# (Requires Grafana/Prometheus setup)
open http://localhost:3000/d/agent-health
```

### Metrics Endpoints

```yaml
# Prometheus metrics
endpoint: "/metrics"
port: 9090

# Health check
endpoint: "/health"
method: GET
expected: 200 OK
```

### Log Locations

```yaml
audit_logs: "governance/70-audit/logs/"
health_logs: "governance/30-agents/monitoring/logs/"
performance_logs: "governance/30-agents/monitoring/metrics/"
```

## 🔄 Continuous Evolution

### Automatic Triggers

The agent evolves automatically based on:

1. **Performance Degradation**
   - Response time > 100ms
   - Error rate > 5%
   - Success rate < 95%

2. **Data Drift**
   - Statistical threshold: 5%
   - Check interval: 1 hour

3. **Feedback Threshold**
   - User satisfaction < 3.5/5
   - Automation success < 90%

### Manual Triggers

```bash
# Trigger retraining
# (Requires approval from governance team)
curl -X POST http://localhost:8080/agents/unmanned-island-agent/retrain

# Update configuration
# (Requires approval for production)
curl -X PUT http://localhost:8080/agents/unmanned-island-agent/config \
  -H "Content-Type: application/json" \
  -d @new-config.json
```

## 🛡️ Security & Compliance

### Compliance Standards

- ✅ ISO/IEC 42001:2023 - AI Management System
- ✅ NIST AI RMF - Trustworthiness Framework
- ✅ AI Behavior Contract - SynergyMesh Internal Standard

### Security Controls

```yaml
# Least Privilege (RBAC)
role: "agent_autonomous"
permissions: "minimal_required"

# Audit Logging
retention: "90 days"
completeness: "100%"

# Resource Limits
memory: "2GB"
cpu: "1 core"
network: "50 Mbps"
```

## 🔗 Integration Points

### Governance Layers

```yaml
10-policy:    Policy as Code Framework
20-intent:    Intent-based Orchestration
30-agents:    AI Agent Governance (THIS LAYER)
60-contracts: Contract Registry
70-audit:     Audit & Traceability
80-feedback:  Closed-Loop Feedback
```

### Data Flow

```
User Request
    ↓
10-policy (Validate)
    ↓
20-intent (Orchestrate)
    ↓
30-agents (Execute)
    ↓
60-contracts (Verify)
    ↓
70-audit (Log)
    ↓
80-feedback (Analyze)
    ↓
10-policy (Optimize)
```

## 📝 Common Tasks

### Add New Agent

1. Create agent definition in `.github/agents/`
2. Register in `governance/30-agents/registry/agent-catalog.yaml`
3. Configure RBAC in `governance/30-agents/permissions/rbac-policies.yaml`
4. Set up health checks in `governance/30-agents/monitoring/health-checks.yaml`
5. Run deployment script

### Update Agent Configuration

1. Edit `governance/30-agents/registry/agent-catalog.yaml`
2. Validate YAML syntax
3. Run deployment script
4. Verify health checks

### Investigate Issues

```bash
# Check agent status
cat governance/30-agents/registry/agent-catalog.yaml | grep -A 20 unmanned-island-agent

# View health check results
cat governance/30-agents/monitoring/health-checks.yaml

# Review audit logs
ls -l governance/70-audit/logs/

# Check recent evolution events
cat governance/30-agents/lifecycle/continuous-evolution.yaml
```

## 🆘 Troubleshooting

### Agent Not Registered

```bash
# Verify agent catalog
cat governance/30-agents/registry/agent-catalog.yaml | grep agent_id

# Re-run deployment
./governance/deploy-instant.sh
```

### Permission Denied

```bash
# Check RBAC configuration
cat governance/30-agents/permissions/rbac-policies.yaml

# Verify role assignment
grep -A 10 "unmanned-island-agent" governance/30-agents/permissions/rbac-policies.yaml
```

### Health Check Failed

```bash
# View health check configuration
cat governance/30-agents/monitoring/health-checks.yaml

# Check agent dependencies
cat governance/30-agents/registry/dependency-map.yaml
```

## 📚 Additional Resources

- **AI Behavior Contract:** `.github/AI-BEHAVIOR-CONTRACT.md`
- **Technical Guidelines:** `.github/copilot-instructions.md`
- **Code Standards:** `.github/island-ai-instructions.md`
- **Governance Framework:** `governance/30-agents/README.md`
- **Integration Architecture:** `governance/GOVERNANCE_INTEGRATION_ARCHITECTURE.md`

## 🎉 Success Criteria

After successful deployment, you should have:

- ✅ Agent registered in catalog
- ✅ RBAC policies configured
- ✅ Health monitoring enabled
- ✅ Compliance frameworks active
- ✅ Integration with governance layers
- ✅ Continuous evolution hooks enabled
- ✅ Zero human intervention required
- ✅ Deployment time < 30 seconds

---

**Status:** 🟢 PRODUCTION_READY  
**Deployment Time:** < 30 seconds  
**Human Intervention:** 0  
**Automation Level:** 100%

**Last Updated:** 2025-12-11
