# Architecture Optimization Dashboard

## 📊 Overview

The Architecture Optimization Dashboard provides real-time visibility into the
Unmanned Island System's global health metrics, optimization progress, and
governance compliance. It serves as the primary interface for the Architecture
Reasoner agent and human reviewers to monitor system-wide quality.

---

## 🎯 Objective Functions (目標函數)

### Definition

The dashboard tracks **optimization toward ideal state** across multiple
dimensions. Each objective function defines:

- **Current State**: Measured from live system
- **Ideal State**: Theoretical optimum based on architecture principles
- **Gap**: Distance from ideal (what remains to be improved)
- **Trend**: Movement direction over time

### Core Objective Functions

#### 1. Language Stack Convergence（語言堆疊收斂）

**Objective**: Minimize language diversity while maintaining necessary
polyglotism

```yaml
objective_function:
  name: "language_stack_convergence"
  formula: "1 - (actual_language_diversity / baseline_diversity)"

  ideal_state:
    primary_languages: ["TypeScript"]
    secondary_languages: ["Python", "Go", "C++", "Rust"]
    language_count: 5
    distribution:
      TypeScript: 70%
      Python: 15%
      Go: 5%
      C++: 5%
      Rust: 5%
    forbidden_count: 0

  current_state:
    actual_languages: ["TypeScript", "JavaScript", "Python", "Go", "C++", "Rust", "Shell", "PHP"]
    language_count: 8
    distribution:
      TypeScript: 45%
      JavaScript: 25%
      Python: 12%
      Go: 6%
      C++: 4%
      Rust: 3%
      Shell: 4%
      PHP: 1%
    forbidden_count: 1  # PHP

  gap_analysis:
    excess_languages: ["JavaScript", "Shell", "PHP"]
    missing_distribution:
      TypeScript: "Need +25% (from 45% to 70%)"
      Python: "Need +3% (from 12% to 15%)"
    convergence_score: 0.625  # 62.5% toward ideal

  improvement_targets:
    P0: "Remove PHP (1% of codebase) → +5% convergence"
    P1: "Migrate 15% of JavaScript to TypeScript → +15% convergence"
    P2: "Migrate remaining JavaScript → +10% convergence"
    P2: "Consolidate Shell scripts → +5% convergence"
```

**Visualization**:

```
Current Language Distribution:
TypeScript ████████████████████████ 45%
JavaScript ██████████████ 25%
Python     ███████ 12%
Go         ███ 6%
C++        ██ 4%
Shell      ██ 4%
Rust       █ 3%
PHP        ▌ 1%

Target Distribution:
TypeScript ████████████████████████████████████ 70%
Python     █████████ 15%
Go         ██ 5%
C++        ██ 5%
Rust       ██ 5%

Gap: 37.5% | Trend: ↗ Improving (+5% last 30 days)
```

#### 2. Architecture Compliance Score（架構合規分數）

**Objective**: Zero architecture violations (perfect layering)

```yaml
objective_function:
  name: 'architecture_compliance'
  formula: '1 - (violation_count / total_possible_violations)'

  ideal_state:
    reverse_dependencies: 0
    circular_dependencies: 0
    skeleton_violations: 0
    forbidden_patterns: 0
    compliance_score: 1.0 # 100%

  current_state:
    reverse_dependencies: 3 # apps → core violations
    circular_dependencies: 1 # core modules circular
    skeleton_violations: 2 # architecture-stability rules
    forbidden_patterns: 0
    compliance_score: 0.88 # 88%

  gap_analysis:
    total_violations: 6
    by_severity:
      CRITICAL: 3 # reverse dependencies
      HIGH: 1 # circular dependency
      MEDIUM: 2 # skeleton violations
    by_module:
      'apps/web': 2 violations
      'core/unified_integration': 2 violations
      'core/mind_matrix': 1 violation
      'services/gateway': 1 violation

  improvement_targets:
    P0: 'Fix 3 reverse dependencies → +50% compliance'
    P1: 'Break circular dependency → +17% compliance'
    P2: 'Fix skeleton violations → +33% compliance'
```

**Visualization**:

```
Architecture Health:
┌─────────────────────────────────────┐
│ Overall Compliance: 88% ████████▊   │
├─────────────────────────────────────┤
│ Layering (core→services→apps)       │
│   ✅ Core Dependencies: 100%        │
│   ⚠️  Apps Dependencies: 75%        │
│   ❌ Reverse Deps: 3 violations     │
├─────────────────────────────────────┤
│ Skeleton Compliance                 │
│   ✅ api-governance: 100%           │
│   ⚠️  architecture-stability: 90%   │
│   ✅ security-observability: 100%   │
└─────────────────────────────────────┘

Target: 100% | Gap: 12% | Trend: ↗ (+3% last 14 days)
```

#### 3. Security Posture Index（安全態勢指數）

**Objective**: Zero HIGH findings, minimal MEDIUM findings

```yaml
objective_function:
  name: 'security_posture'
  formula: '1 - (weighted_findings / max_weighted_score)'
  weights:
    HIGH: 100
    MEDIUM: 10
    LOW: 1

  ideal_state:
    semgrep_high: 0
    semgrep_medium: 0
    semgrep_low: 0
    codeql_high: 0
    codeql_medium: 0
    security_score: 1.0

  current_state:
    semgrep_high: 3
    semgrep_medium: 8
    semgrep_low: 15
    codeql_high: 0
    codeql_medium: 2
    weighted_score: 315 # (3*100 + 8*10 + 15*1 + 2*10)
    security_score: 0.685 # 68.5%

  gap_analysis:
    critical_gap: '3 HIGH findings blocking 100% score'
    medium_gap: '10 MEDIUM findings'
    acceptable_risk: '15 LOW findings (within tolerance)'

  improvement_targets:
    P0: 'Fix 3 HIGH findings → +30% security score'
    P1: 'Fix 5 critical MEDIUM findings → +5% score'
    P2: 'Fix remaining MEDIUM → +5% score'
```

#### 4. Refactor Progress Index（重構進度指數）

**Objective**: All clusters reach target state defined in playbooks

```yaml
objective_function:
  name: 'refactor_progress'
  formula: 'completed_items / total_planned_items'

  ideal_state:
    all_clusters_complete: true
    p0_completion: 100%
    p1_completion: 100%
    p2_completion: 100%

  current_state:
    total_clusters: 12
    completed_clusters: 3
    in_progress_clusters: 5
    not_started_clusters: 4

    p0_items:
      total: 45
      completed: 38
      completion: 84.4%

    p1_items:
      total: 78
      completed: 22
      completion: 28.2%

    p2_items:
      total: 134
      completed: 8
      completion: 6.0%

  gap_analysis:
    immediate_blockers: '7 P0 items remaining'
    estimated_completion:
      P0: '2 days'
      P1: '3 weeks'
      P2: '8 weeks'

  by_cluster:
    'core/architecture-stability':
      status: IN_PROGRESS
      p0: '100% (12/12)'
      p1: '60% (6/10)'
      p2: '10% (2/20)'

    'services/gateway':
      status: NOT_STARTED
      p0: '0% (0/5)'
      p1: '0% (0/8)'
      p2: '0% (0/15)'
```

#### 5. Test Coverage Momentum（測試覆蓋率動量）

**Objective**: Maintain or improve test coverage across all modules

```yaml
objective_function:
  name: 'test_coverage_momentum'
  formula: 'current_coverage - baseline_coverage'

  ideal_state:
    system_coverage: 85%
    no_module_below: 75%
    trend: 'increasing'

  current_state:
    system_coverage: 76.3%
    modules:
      'core/': 82.1%
      'services/': 74.8%
      'apps/': 68.2%
      'automation/': 79.5%

  gap_analysis:
    system_gap: '-8.7% from ideal'
    critical_modules:
      'apps/web': '68.2% (needs +6.8%)'
      'services/gateway': '72.1% (needs +2.9%)'

  trend_analysis:
    last_7_days: '+0.3%'
    last_30_days: '+1.2%'
    last_90_days: '-0.5%'
    momentum: 'SHORT_TERM_POSITIVE'
```

#### 6. Cyclomatic Complexity Trend（圈複雜度趨勢）

**Objective**: Reduce average complexity toward target thresholds

```yaml
objective_function:
  name: 'complexity_reduction'
  formula: '(baseline_complexity - current_complexity) / baseline_complexity'

  ideal_state:
    system_avg_complexity: 10
    no_function_above: 15
    no_file_above: 20

  current_state:
    system_avg_complexity: 13.2
    hotspot_functions: 23 # above 15
    hotspot_files: 8 # avg above 20

    by_module:
      'core/': 14.8
      'services/': 12.1
      'apps/': 11.9
      'automation/': 16.3

  gap_analysis:
    avg_gap: '+3.2 (24% above ideal)'
    critical_hotspots:
      - file: 'core/unified_integration/processor.ts'
        avg_complexity: 28.5
        worst_function: 45

  improvement_targets:
    P0: 'Refactor 5 worst functions → -1.2 avg complexity'
    P1: 'Break down hotspot files → -1.5 avg complexity'
    P2: 'Systematic simplification → -0.5 avg complexity'
```

---

## 📈 Optimization Gap Report（優化 vs 現實差距報告）

### Report Structure

Generated daily, provides comprehensive gap analysis across all dimensions:

```markdown
# System Optimization Gap Report

**Generated**: 2025-12-06 22:00:00 UTC **Reporting Period**: Last 30 days

## Executive Summary

| Dimension               | Current | Ideal | Gap   | Trend   | Status       |
| ----------------------- | ------- | ----- | ----- | ------- | ------------ |
| Language Convergence    | 62.5%   | 100%  | 37.5% | ↗ +5%   | 🟡 IMPROVING |
| Architecture Compliance | 88%     | 100%  | 12%   | ↗ +3%   | 🟡 IMPROVING |
| Security Posture        | 68.5%   | 100%  | 31.5% | → 0%    | 🟠 STAGNANT  |
| Refactor Progress       | 38.4%   | 100%  | 61.6% | ↗ +8%   | 🟢 ON_TRACK  |
| Test Coverage           | 76.3%   | 85%   | 8.7%  | ↗ +1.2% | 🟢 ON_TRACK  |
| Complexity Reduction    | 13.2    | 10.0  | 24%   | ↘ -0.3  | 🔴 WORSENING |

**Overall System Health**: 🟡 71.6% toward ideal state

## Critical Gaps (Blocking 100% Health)

### 1. Security - 3 HIGH Severity Findings (Priority: P0)

**Impact**: Blocks production readiness **Affected Modules**:
core/unified_integration (2), services/gateway (1) **Remediation**:

- `SEMGREP-001`: SQL injection risk in `core/unified_integration/db.ts:45`
- `SEMGREP-002`: Unsafe deserialization in `core/unified_integration/api.ts:128`
- `SEMGREP-003`: Missing authentication check in `services/gateway/router.ts:89`

**Estimated Fix Time**: 16 hours **Blocking**: Phase 3 completion, production
deployment

### 2. Architecture - 3 Reverse Dependencies (Priority: P0)

**Impact**: Violates layering principles, increases coupling **Violations**:

1. `apps/web/src/utils/core-helpers.ts` → imports `core/unified_integration`
2. `apps/web/src/services/processor.ts` → imports `core/mind_matrix`
3. `services/mcp/client.ts` → imports `core/safety_mechanisms` (should go
   through API)

**Remediation Plan**:

- Create `services/api/core-facade.ts` for apps to use
- Move `core-helpers.ts` logic to services layer
- Update imports in 23 files

**Estimated Fix Time**: 3 days **Blocking**: Architecture certification,
modularity goals

### 3. Language - 1 Forbidden Language (PHP, 1%) (Priority: P0)

**Impact**: Violates language policy, security risk **Files**:

- `automation/legacy/backup-script.php` (127 lines)

**Remediation**: Rewrite in Python, estimated 4 hours **Blocking**: Language
governance compliance

## Moderate Gaps (Impact Quality Metrics)

### Cyclomatic Complexity Worsening (-0.3 trend)

**Root Cause**: New feature additions without refactoring **Hotspots**:

- `core/unified_integration/processor.ts` (avg 28.5, 8 functions > 20)
- `automation/autonomous/controller.cpp` (avg 24.1, 12 functions > 20)

**Recommended Action**: Schedule P1 refactoring sprints

### Test Coverage Stagnant in Apps (68.2%)

**Gap from Target**: -6.8% **Missing Coverage**:

- `apps/web/src/components/` (42% coverage)
- `apps/web/src/utils/` (55% coverage)

**Recommended Action**: Implement test-first policy for new features

## Progress Toward Ideal State

**Modules at Ideal State**: 2/12 (17%)

- ✅ `infrastructure/kubernetes` (100% compliant)
- ✅ `governance/schemas` (100% compliant)

**Modules Close to Ideal (>90%)**: 3/12 (25%)

- 🟢 `automation/autonomous` (94%)
- 🟢 `core/safety_mechanisms` (92%)
- 🟢 `services/mcp` (91%)

**Modules Needing Attention (<70%)**: 4/12 (33%)

- 🔴 `apps/web` (62%)
- 🔴 `services/gateway` (68%)
- 🟠 `core/unified_integration` (69%)
- 🟠 `tools/` (64%)

## Projected Timeline to Ideal State

**Current Velocity**: +2.3% system health per week

**Projected Milestones**:

- 80% Health: 4 weeks (2025-01-03)
- 90% Health: 9 weeks (2025-02-07)
- 95% Health: 14 weeks (2025-03-14)
- 100% Health: 18+ weeks (requires sustained effort)

**Risk Factors**:

- New feature development may slow refactoring
- Security findings may increase before decreasing
- Team capacity constraints

## Recommendations

1. **P0 Focus**: Complete security fixes this sprint (blocks everything)
2. **P0 Focus**: Resolve architecture violations next sprint
3. **P1 Action**: Implement complexity gates in CI
4. **P1 Action**: Mandatory test coverage for new code
5. **P2 Action**: Schedule monthly refactoring sprints
```

---

## 🎛️ Dashboard Interface Specification

### Main Dashboard View

**URL**: `http://localhost:3000/architecture/dashboard`

**Layout**:

```
┌────────────────────────────────────────────────────────────────┐
│  🏝️ Unmanned Island System - Architecture Dashboard            │
│  Last Updated: 2025-12-06 22:00:00 UTC | Refresh: Auto (30s)   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  System Health: 71.6% ████████████████████▌                    │
│  Status: 🟡 IMPROVING | Trend: ↗ +2.3%/week                   │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│  Objective Functions                                            │
│  ┌──────────────────────────┬──────────────────────────────┐  │
│  │ Language Convergence     │ Architecture Compliance      │  │
│  │ 62.5% ████████████▌      │ 88% ██████████████████▊      │  │
│  │ Gap: 37.5% | ↗ +5%       │ Gap: 12% | ↗ +3%             │  │
│  └──────────────────────────┴──────────────────────────────┘  │
│  ┌──────────────────────────┬──────────────────────────────┐  │
│  │ Security Posture         │ Refactor Progress            │  │
│  │ 68.5% ████████████████▌  │ 38.4% ████████▌              │  │
│  │ Gap: 31.5% | → 0%        │ Gap: 61.6% | ↗ +8%           │  │
│  └──────────────────────────┴──────────────────────────────┘  │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│  🚨 Critical Alerts (3)                                         │
│  ❌ 3 HIGH severity security findings (BLOCKING)               │
│  ⚠️  3 architecture violations (P0)                            │
│  ⚠️  Cyclomatic complexity trending worse (-0.3)              │
│                                                                 │
│  [View Details] [Generate Report] [Historical Data]            │
└────────────────────────────────────────────────────────────────┘
```

### Module Detail View

**URL**: `http://localhost:3000/architecture/module/{module-id}`

Shows per-module metrics, violations, and optimization path.

### Historical Trends View

**URL**: `http://localhost:3000/architecture/trends`

Time-series graphs for all objective functions over 7/30/90 days.

---

## 📡 API Endpoints

### GET /api/architecture/health

Returns current system health summary:

```json
{
  "timestamp": "2025-12-06T22:00:00Z",
  "overall_health": 0.716,
  "status": "IMPROVING",
  "trend": {
    "value": 0.023,
    "unit": "per_week",
    "direction": "up"
  },
  "objective_functions": [
    {
      "name": "language_convergence",
      "current": 0.625,
      "ideal": 1.0,
      "gap": 0.375,
      "trend": 0.05,
      "status": "IMPROVING"
    },
    ...
  ],
  "critical_alerts": 3,
  "blocking_issues": [
    {
      "type": "security",
      "severity": "HIGH",
      "count": 3,
      "blocking": ["production_deployment", "phase_3_completion"]
    }
  ]
}
```

### GET /api/architecture/gap-report

Returns comprehensive optimization gap analysis (markdown or JSON).

### GET /api/architecture/metrics/{metric-name}

Returns historical data for specific metric.

### POST /api/architecture/decision

Submit architecture decision for evaluation by Architecture Reasoner.

---

## 🔔 Alerting Rules

### Critical Alerts (Immediate Action Required)

```yaml
alerts:
  - id: 'ARCH-001'
    name: 'HIGH Security Finding Detected'
    condition: 'semgrep_high_count > 0 OR codeql_high_count > 0'
    severity: CRITICAL
    action:
      - 'Block all merges'
      - 'Notify: @security-team, @architecture-team'
      - 'Create incident ticket'
    sla: '4 hours to resolution'

  - id: 'ARCH-002'
    name: 'Architecture Violation Introduced'
    condition: 'architecture_violations > baseline'
    severity: HIGH
    action:
      - 'Reject PR'
      - 'Notify: proposer, @architecture-team'
      - 'Require Architecture Reasoner approval'
    sla: 'Same day resolution'

  - id: 'ARCH-003'
    name: 'Forbidden Language Detected'
    condition: 'forbidden_language_file_count > 0'
    severity: HIGH
    action:
      - 'Block PR merge'
      - 'Notify: @language-governance-team'
      - 'Require immediate remediation plan'
    sla: '24 hours to removal'
```

### Warning Alerts (Attention Needed)

```yaml
alerts:
  - id: 'ARCH-004'
    name: 'Test Coverage Declining'
    condition: 'test_coverage_delta < -2.0'
    severity: MEDIUM
    action:
      - 'Warn reviewers in PR'
      - 'Require justification or additional tests'

  - id: 'ARCH-005'
    name: 'Complexity Increasing'
    condition: 'complexity_trend > 0 for 7 days'
    severity: MEDIUM
    action:
      - 'Notify: @tech-lead'
      - 'Schedule refactoring review'
      - 'Enable complexity gates'
```

---

## 🔧 Implementation Guide

### For Dashboard Developers

1. **Data Sources**:
   - `config/system-module-map.yaml` - Constraints and targets
   - `reports/language-governance/` - Language metrics
   - `reports/security-scans/` - Semgrep, CodeQL results
   - `reports/test-coverage/` - Coverage data
   - `reports/complexity/` - Cyclomatic complexity metrics
   - `docs/refactor_playbooks/03_refactor/index.yaml` - Refactor progress

2. **Update Frequency**:
   - Real-time: Security findings, architecture violations
   - Hourly: Language governance, test coverage
   - Daily: Complexity metrics, refactor progress
   - Weekly: Trend analysis, gap reports

3. **Storage**:
   - Time-series database (InfluxDB, TimescaleDB) for metrics
   - Document store (MongoDB) for gap reports
   - Cache (Redis) for dashboard queries

### For Architecture Reasoner Integration

The dashboard provides input data for Architecture Reasoner decisions:

```python
# Pseudo-code
def get_architecture_reasoner_context():
    return {
        "current_metrics": dashboard_api.get("/api/architecture/health"),
        "gap_analysis": dashboard_api.get("/api/architecture/gap-report"),
        "active_alerts": dashboard_api.get("/api/architecture/alerts"),
        "historical_trends": dashboard_api.get("/api/architecture/trends"),
        "module_states": dashboard_api.get("/api/architecture/modules")
    }

# Architecture Reasoner uses this context for decisions
decision = architecture_reasoner.evaluate_proposal(
    proposal=refactor_playbook,
    context=get_architecture_reasoner_context()
)
```

---

## 📚 References

- **Architecture Reasoner**: `services/agents/architecture-reasoner/README.md`
- **AI Behavior Contract**: `.github/AI-BEHAVIOR-CONTRACT.md` (Section 9)
- **Refactor Playbook Template**:
  `docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md`
- **System Module Map**: `config/system-module-map.yaml`

---

**Maintainer**: SynergyMesh Admin Team  
**Last Updated**: 2025-12-06  
**Version**: 1.0.0
