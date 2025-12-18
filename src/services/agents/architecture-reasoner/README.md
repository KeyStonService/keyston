# Architecture Reasoner Agent

## 🎯 Purpose

The Architecture Reasoner is a specialized AI agent responsible for **global optimization reasoning** across the Unmanned Island System. It ensures that all architecture changes, refactoring proposals, and language governance decisions are evaluated from a system-wide perspective before local implementation.

## 🏗️ Role in Agent Hierarchy

```text
Unmanned Island System Agent Architecture
│
├── 🌐 Architecture Reasoner (Global Layer)
│   ├── Role: System-wide optimization and constraint validation
│   ├── Scope: Cross-module, cross-domain analysis
│   ├── Authority: CAN VETO proposals that violate global constraints
│   └── Outputs: Global Optimization Views, Architecture Decisions
│
├── 🔧 Local Refactor Agents (Execution Layer)
│   ├── Role: Module-specific refactoring execution
│   ├── Scope: Single module/cluster operations
│   ├── Authority: MUST get approval from Architecture Reasoner
│   └── Outputs: Concrete code changes, test updates
│
└── 🤖 Orchestrator (Coordination Layer)
    ├── Role: Workflow management and agent coordination
    ├── Scope: Process execution, gate enforcement
    ├── Authority: Routes tasks between agents
    └── Outputs: Status reports, execution logs
```

## 📋 Responsibilities

### Primary Responsibilities

1. **Global Constraint Validation**
   - Validate all proposed changes against system-wide hard constraints
   - Ensure architecture layering (core → services → apps) is maintained
   - Verify no forbidden languages are introduced
   - Check skeleton rule compliance

2. **Cross-Module Impact Analysis**
   - Analyze how local changes affect system-wide metrics
   - Identify cascading dependencies and ripple effects
   - Predict impacts on global optimization targets
   - Detect problem-shifting patterns

3. **Architecture Decision Making**
   - Approve/reject refactor proposals based on global impact
   - Suggest alternative approaches that better serve global goals
   - Resolve conflicts between module-local optimizations
   - Define new architectural patterns when needed

4. **Metric Optimization**
   - Track system-wide metrics (language violations, security findings, architecture compliance)
   - Define optimization targets for each Phase (0-5)
   - Monitor progress toward global goals
   - Report deviations and suggest corrections

### Secondary Responsibilities

- Maintain system architecture documentation
- Update `config/system-module-map.yaml` constraints
- Review and approve skeleton rule changes
- Provide guidance to local refactor agents
- Generate architecture health reports

## 🔄 Integration with Phase 0–5

The Architecture Reasoner's involvement varies by phase:

### Phase 0: Inventory & Discovery

- **Reasoning Weight**: 🔴 HIGH
- **Focus**: Establish global baseline metrics
- **Activities**:
  - Analyze complete system state
  - Identify all modules and their relationships
  - Create dependency graphs
  - Document current language distribution
  - Catalogue all architecture violations

### Phase 1: Governance Baseline

- **Reasoning Weight**: 🔴 HIGH
- **Focus**: Define optimization targets and constraints
- **Activities**:
  - Set system-wide quality thresholds
  - Define hard constraints for all modules
  - Establish architecture layering rules
  - Identify forbidden patterns and anti-patterns
  - Create global optimization roadmap

### Phase 2: Refactor Planning

- **Reasoning Weight**: 🟠 CRITICAL
- **Focus**: Design global optimization strategy
- **Activities**:
  - Review all refactor proposals for global consistency
  - Ensure proposals don't conflict with each other
  - Sequence refactors to minimize disruption
  - Validate that local plans sum to global improvement
  - Approve P0/P1/P2 prioritization

### Phase 3: Safe Execution

- **Reasoning Weight**: 🟡 MEDIUM
- **Focus**: Implement with continuous metric validation
- **Activities**:
  - Monitor execution against global constraints
  - Detect early signs of constraint violations
  - Approve/reject PR changes based on global impact
  - Provide real-time guidance to implementers
  - Trigger rollbacks if global metrics degrade

### Phase 4: Consolidation

- **Reasoning Weight**: 🟢 LOW
- **Focus**: Verify global metrics improved as planned
- **Activities**:
  - Compare final state against targets
  - Validate all hard constraints still hold
  - Document lessons learned
  - Update baseline for next iteration
  - Certify phase completion

### Phase 5: Continuous Governance

- **Reasoning Weight**: 🟡 MEDIUM
- **Focus**: Monitor for regression against global targets
- **Activities**:
  - Continuous metric monitoring
  - Detect new violations immediately
  - Trigger alerts when thresholds are breached
  - Recommend preventive actions
  - Maintain architecture health dashboard

## 🛠️ Operational Model

### Input Requirements

The Architecture Reasoner requires these inputs for any decision:

```yaml
required_inputs:
  system_state:
    - config/system-module-map.yaml (complete, current version)
    - docs/refactor_playbooks/03_refactor/index.yaml (cluster states)
    - Language governance reports (latest)
    - Dependency graphs (auto-generated)
    - Security scan results (Semgrep, CodeQL)
    - Test coverage reports
    
  proposed_change:
    - Refactor playbook or proposal document
    - Affected modules and files
    - Expected local improvements
    - Risk assessment
    
  historical_context:
    - Previous architecture decisions
    - Past violation patterns
    - Migration history
    - Team capacity and velocity
```

### Output Format

All Architecture Reasoner decisions follow this format:

```yaml
decision:
  proposal_id: "{{PROPOSAL_ID}}"
  decision: APPROVED | REJECTED | CONDITIONAL_APPROVAL
  timestamp: "{{ISO_8601_TIMESTAMP}}"
  
global_optimization_view:
  optimization_targets:
    - metric: "Language violations"
      impact: "-8 (moves toward target)"
    - metric: "Semgrep HIGH"
      impact: "-3 (achieves target)"
    - metric: "Architecture compliance"
      impact: "+1 (improvement)"
      
  hard_constraints_check:
    - constraint: "No apps → core dependencies"
      status: PASS
    - constraint: "Semgrep HIGH = 0"
      status: PASS
    - constraint: "Test coverage ≥ baseline - 2%"
      status: PASS
      
  global_impact_assessment:
    positive: ["Language violations -8", "Security improved"]
    neutral: ["Test coverage unchanged"]
    negative: []
    net: "POSITIVE - System health improves"

reasoning:
  why_approved: |
    This proposal advances all three global optimization targets
    without violating any hard constraints. The changes are scoped
    appropriately and include proper rollback plans.
    
  why_rejected: |
    {{REJECTION_REASON if decision == REJECTED}}
    
  conditions: |
    {{CONDITIONS if decision == CONDITIONAL_APPROVAL}}
    
recommendations:
  - "Consider also migrating service X for consistency"
  - "Add integration test for new API boundary"
  - "Update system-module-map.yaml after completion"
  
approval_chain:
  reasoner: "architecture-reasoner-v1"
  reviewer: "{{HUMAN_REVIEWER_NAME}}"
  final_authority: "SynergyMesh Admin Team"
```

## 📚 References

- **AI Behavior Contract**: `.github/AI-BEHAVIOR-CONTRACT.md` (Section 9)
- **Refactor Prompts**: `docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md` (Section 1.5)
- **Playbook Template**: `docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md` (Section 3)
- **System Module Map**: `config/system-module-map.yaml`
- **Architecture Skeletons**: `automation/architecture-skeletons/`

## 🚀 Getting Started

### For Implementers

1. Read `.github/AI-BEHAVIOR-CONTRACT.md` Section 9
2. Review `config/system-module-map.yaml` for current constraints
3. Generate proposal following `REFRACTOR_PLAYBOOK_TEMPLATE.md`
4. Submit to Architecture Reasoner for evaluation
5. Address feedback and iterate

### For Reviewers

1. Check that Architecture Reasoner was consulted
2. Verify Global Optimization View is present
3. Confirm hard constraints are validated
4. Review Self-Check answers
5. Approve only if global impact is net positive

---

**Maintainer**: SynergyMesh Admin Team  
**Last Updated**: 2025-12-06  
**Version**: 1.0.0
