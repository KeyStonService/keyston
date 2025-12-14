# Evolution Orchestrator - Integration Guide

## 📖 Overview

The **Evolution Orchestrator** is an AI-powered automated evolution planning engine that reads the system's evolution state and generates prioritized, actionable refactor plans.

**Location**: `automation/intelligent/synergymesh_core/evolution_orchestrator.py`

## 🎯 Core Capabilities

1. **Auto-Read Evolution State**: Automatically loads `knowledge/evolution-state.yaml`
2. **Constraint Validation**: Applies constraints from `config/system-evolution.yaml` and `config/ai-constitution.yaml`
3. **Priority Generation**: Creates P0-P3 prioritized action lists based on objective scores
4. **Plan Export**: Outputs executable markdown plans to `docs/evolution/CURRENT_ACTION_PLAN.md`
5. **Ecosystem Integration**: Works with `ecosystem_orchestrator.py` as EVOLUTION_ENGINE subsystem

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Evolution Orchestrator (P1)                      │
│   automation/intelligent/synergymesh_core/               │
│         evolution_orchestrator.py                        │
└──────────────────┬──────────────────────────────────────┘
                   │
    ┌──────────────┴───────────────┐
    │                              │
    ▼                              ▼
┌───────────────┐          ┌──────────────────┐
│  Input Files  │          │   Output Files   │
├───────────────┤          ├──────────────────┤
│ evolution-    │          │ CURRENT_ACTION_  │
│ state.yaml    │ ────────▶│ PLAN.md          │
│               │          │                  │
│ system-       │          │ (Prioritized     │
│ evolution.yaml│          │  refactor tasks) │
│               │          │                  │
│ ai-           │          │                  │
│ constitution. │          │                  │
│ yaml          │          │                  │
└───────────────┘          └──────────────────┘
```

## 🚀 Quick Start

### Method 1: Standalone CLI

```bash
cd /path/to/Unmanned-Island

# Generate evolution action plan
python3 automation/intelligent/synergymesh_core/evolution_orchestrator.py

# Check output
cat docs/evolution/CURRENT_ACTION_PLAN.md
```

### Method 2: Python API

```python
from automation.intelligent.synergymesh_core import EvolutionOrchestrator

# Initialize
orchestrator = EvolutionOrchestrator()

# Generate plan
plan = orchestrator.generate_action_plan()

# Access plan details
print(f"Current Score: {plan.current_score}/100")
print(f"Actions: {len(plan.actions)}")

# Export to markdown
orchestrator.export_plan_to_markdown(plan)
```

### Method 3: Async Integration (Recommended)

```python
import asyncio
from automation.intelligent.synergymesh_core import EvolutionOrchestrator

async def run_orchestration():
    orchestrator = EvolutionOrchestrator()
    plan = await orchestrator.orchestrate()
    return plan

# Run
plan = asyncio.run(run_orchestration())
```

## 📋 Action Plan Structure

Generated plans follow this structure:

```markdown
# 🤖 System Evolution Action Plan

生成時間: 2025-12-07T07:09:41
基於狀態: 2025-12-07T06:56:04.535641Z
計畫 ID: plan-20251207-070941

## 📊 當前狀態
- 目前分數: **81.25/100**
- 目標分數: **100.0/100**
- 待執行動作: **3** 個
- 預估時程: **2.5 hours**

## 🔒 演化約束
- 不得自動修改 core/autonomous 中 safety-critical 邏輯。
- 不得破壞 architecture skeletons 的邊界...
- ...

## P0: P0 Critical
**1 個動作**

### [PENDING] 修復 Semgrep 高風險問題 (當前: 2 個問題)
- **Action ID**: `security-high-severity`
- **Objective**: security
- **Cluster**: core
- **Expected Improvement**: +15.0 points
- **Playbook**: `docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md`
- **Constraints**: ✅ Checked

**執行步驟:**
```bash
# Review security issues in governance/semgrep-report.json
# Create security refactor playbooks for affected clusters
# Apply fixes following playbook guidelines
```
```

## 🔄 Integration with Ecosystem Orchestrator

The Evolution Orchestrator can be registered as a subsystem:

```python
from automation.intelligent.synergymesh_core import (
    EcosystemOrchestrator,
    EvolutionOrchestrator,
    SubsystemType
)

# Initialize ecosystem
ecosystem = EcosystemOrchestrator()

# Register evolution orchestrator as subsystem
evolution_orch = EvolutionOrchestrator()

async def handle_evolution_request(message):
    """Handler for evolution orchestration requests"""
    plan = await evolution_orch.orchestrate()
    return {
        "plan_id": plan.plan_id,
        "actions_count": len(plan.actions),
        "current_score": plan.current_score,
        "target_score": plan.target_score
    }

# Register with ecosystem
await ecosystem.register_subsystem(
    subsystem_id="evolution-orchestrator-1",
    name="Evolution Orchestrator",
    subsystem_type=SubsystemType.EVOLUTION_ENGINE,
    capabilities=["plan_generation", "constraint_validation"],
    handler=handle_evolution_request
)
```

## 🎨 Customization

### Adding New Objective Handlers

Edit `generate_actions_for_objective()` in `evolution_orchestrator.py`:

```python
def generate_actions_for_objective(self, objective: dict[str, Any]) -> list[RefactorAction]:
    # ... existing code ...
    
    # Add new objective type
    elif obj_id == "test-coverage" and score < 100:
        action = RefactorAction(
            action_id=f"{obj_id}-increase-coverage",
            priority=ActionPriority.P1_HIGH,
            objective_id=obj_id,
            cluster="all",
            description=f"提升測試覆蓋率至 {objective['target']}%",
            commands=[
                "pytest --cov=. --cov-report=html",
                "# Review coverage report",
                "# Add tests for uncovered modules"
            ],
            expected_improvement=100 - score
        )
        actions.append(action)
```

### Custom Constraint Checks

Add constraint validation in `check_constraints()`:

```python
def check_constraints(self, action: RefactorAction) -> tuple[bool, list[str]]:
    violations = []
    
    for constraint in self.constraints:
        # Add custom constraint check
        if "no-external-api" in constraint:
            if "API" in action.description or "http" in action.description.lower():
                violations.append(f"External API constraint violated")
    
    return len(violations) == 0, violations
```

## 📊 Output Files

### CURRENT_ACTION_PLAN.md

**Location**: `docs/evolution/CURRENT_ACTION_PLAN.md`

**Purpose**: Human-readable action plan with prioritized tasks

**Updated**: Every time orchestrator runs

**Format**: Markdown with P0-P3 sections, constraints, and executable commands

## 🔐 Constraint Validation

The orchestrator validates all actions against:

1. **System Evolution Constraints** (`config/system-evolution.yaml`)
   - Safety-critical code protection
   - Architecture boundary enforcement
   - Language policy compliance

2. **AI Constitution** (`config/ai-constitution.yaml`)
   - Fundamental laws (non-harm, obedience with limits)
   - Operational rules
   - Adaptive guidelines

**Validation Process**:
```python
is_valid, violations = orchestrator.check_constraints(action)
if not is_valid:
    action.status = ActionStatus.BLOCKED
    logger.warning(f"Action blocked: {violations}")
```

## 🔄 Workflow Integration

### CI/CD Integration

Add to `.github/workflows/system-evolution.yml`:

```yaml
- name: Generate Evolution Plan
  run: |
    python3 automation/intelligent/synergymesh_core/evolution_orchestrator.py
    
- name: Commit Evolution Plan
  run: |
    git add docs/evolution/CURRENT_ACTION_PLAN.md
    git commit -m "chore(evolution): update action plan"
    git push
```

### Scheduled Execution

Add cron job for daily planning:

```yaml
on:
  schedule:
    - cron: "0 18 * * *"  # Daily at 18:00 UTC
```

## 📈 Metrics & Monitoring

Track orchestrator performance:

```python
# Duration tracking
start = datetime.now()
plan = orchestrator.generate_action_plan()
duration = (datetime.now() - start).total_seconds()

# Plan quality metrics
print(f"Actions generated: {len(plan.actions)}")
print(f"Expected improvement: {plan.target_score - plan.current_score}")
print(f"Estimated duration: {plan.estimated_duration}")
print(f"Blocked actions: {sum(1 for a in plan.actions if a.status == ActionStatus.BLOCKED)}")
```

## 🐛 Troubleshooting

### Issue: "Evolution state not found"

**Solution**: Ensure evolution report is generated first:
```bash
python3 tools/evolution/generate_evolution_report.py
```

### Issue: "All actions blocked by constraints"

**Solution**: Review and adjust constraints in `config/system-evolution.yaml`

### Issue: "No actions generated (score = 100)"

**Expected**: System is already at target state. No actions needed.

## 🔮 Future Enhancements (P2)

1. **AI API Integration**:
   - Connect to OpenAI/Anthropic for enhanced planning
   - Use LLM to generate context-aware refactor strategies
   
2. **Metric Expansion**:
   - Test coverage tracking
   - CI success rate monitoring
   - Technical debt scoring
   - Dependency health checks

3. **Auto-Execution**:
   - Safe auto-apply for P3/P2 actions
   - Human approval workflow for P0/P1
   - Rollback mechanism

4. **Learning Loop**:
   - Track action effectiveness
   - Improve priority algorithms based on outcomes
   - Adaptive constraint tuning

## 📚 Related Documentation

- [`docs/evolution/README.md`](./README.md) - Evolution subsystem overview
- [`docs/evolution/orchestrator-prompt-template.md`](./orchestrator-prompt-template.md) - AI prompt template
- [`config/system-evolution.yaml`](../../config/system-evolution.yaml) - Evolution configuration
- [`config/ai-constitution.yaml`](../../config/ai-constitution.yaml) - AI behavior constraints

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-07  
**Maintainer**: SynergyMesh Team
