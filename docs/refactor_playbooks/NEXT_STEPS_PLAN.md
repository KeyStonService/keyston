# Next Steps Plan: Refactor Playbook System Implementation

## Executive Summary

Following the successful extraction and integration of the three-phase refactor
playbook system, the next phase focuses on **end-to-end execution** starting
with the `core/architecture-stability` cluster as a template, then scaling to
other subsystems.

## Status: Foundation Complete ✅

### Completed Infrastructure (Current PR)

- ✅ Three-phase playbook system (01_deconstruction → 02_integration →
  03_refactor)
- ✅ Config integration (system-module-map.yaml v1.2.0,
  unified-config-index.yaml)
- ✅ Global defaults (language_policy, quality_thresholds)
- ✅ Architecture constraints (dependencies, skeleton rules, language strategy)
- ✅ Proposer/Critic AI workflow
- ✅ Validation tooling (validate-refactor-index.py)
- ✅ Comprehensive documentation (~50KB)

### Configuration Ready

```yaml
# system-module-map.yaml includes:
defaults:
  language_policy: ✅
  quality_thresholds: ✅

modules:
  core-architecture: ✅
  core-safety: ✅
  core-slsa: ✅
  automation-autonomous: ✅
  services-mcp: ✅
```

---

## Phase 1: Core Cluster End-to-End Template (Next 2-4 weeks)

### Objective

Create a complete, replicable template by executing the full refactor cycle on
`core/architecture-stability` cluster.

### 1.1 Deconstruction Phase (Week 1)

**Goal**: Analyze existing core architecture and document legacy patterns

**Tasks**:

- [ ] Create
      `docs/refactor_playbooks/01_deconstruction/core/core__architecture_deconstruction.md`
- [ ] Analyze `core/unified_integration/`, `core/mind_matrix/`,
      `core/lifecycle_systems/`
- [ ] Document architecture patterns, anti-patterns, technical debt
- [ ] Identify legacy asset dependencies
- [ ] Update `legacy_assets_index.yaml` with core-specific entries
- [ ] Run language governance scan and document violations
- [ ] Generate hotspot analysis for complexity metrics

**Deliverables**:

- Deconstruction report with architecture diagrams
- Legacy asset inventory
- Technical debt scorecard
- Language governance baseline metrics

### 1.2 Integration Phase (Week 2)

**Goal**: Design new architecture that aligns with system constraints

**Tasks**:

- [ ] Create
      `docs/refactor_playbooks/02_integration/core/core__architecture_integration.md`
- [ ] Design new architecture respecting skeleton rules
- [ ] Map old → new component transitions
- [ ] Define API boundaries and interfaces
- [ ] Validate against `system-module-map.yaml` constraints
- [ ] Create dependency graph showing allowed/banned dependencies
- [ ] Design migration strategy with risk assessment

**Deliverables**:

- Integration design document
- Architecture diagrams (before/after)
- Dependency validation report
- Migration roadmap with phases

### 1.3 Refactor Execution Phase (Week 3-4)

**Goal**: Execute refactor with Proposer/Critic AI workflow

**Tasks**:

- [ ] Create
      `docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md`
- [ ] Implement P0 refactorings (critical fixes)
- [ ] Implement P1 refactorings (high priority)
- [ ] Implement P2 refactorings (nice-to-have)
- [ ] Use Proposer/Critic workflow for each change
- [ ] Track quality metrics (before/after comparison)
- [ ] Run validation: language governance, semgrep, tests
- [ ] Update `03_refactor/index.yaml` with governance_status

**Deliverables**:

- Refactor playbook with execution results
- Quality metrics comparison table
- Validation reports (all green)
- Updated governance dashboard

### 1.4 Validation & Documentation (Week 4)

**Goal**: Validate success and document template process

**Tasks**:

- [ ] Verify all quality thresholds met:
  - Language violations ≤ 10 (or decreased)
  - Semgrep HIGH = 0
  - Cyclomatic complexity ≤ 15
  - Test coverage ≥ 70%
  - Hotspot score ≤ 85
- [ ] Update `03_refactor/INDEX.md` with status
- [ ] Document lessons learned
- [ ] Create template checklist for other clusters
- [ ] Run `python tools/validate-refactor-index.py`

**Deliverables**:

- Validation report
- Template process documentation
- Reusable checklist
- Case study writeup

---

## Phase 2: Scale to Additional Clusters (Weeks 5-12)

### 2.1 Priority Order

Following core template success, execute in order:

1. **core/safety-mechanisms** (Week 5-6)
   - Cluster ID: `core/safety-mechanisms`
   - Priority: P0 (critical security component)

2. **core/slsa-provenance** (Week 7-8)
   - Cluster ID: `core/slsa-provenance`
   - Priority: P0 (supply chain security)

3. **automation/autonomous** (Week 9-10)
   - Cluster ID: `automation/autonomous`
   - Priority: P1 (drone/ROS integration)

4. **services/gateway** (Week 11-12)
   - Cluster ID: `services/gateway`
   - Priority: P1 (MCP servers)

### 2.2 Scaling Checklist (per cluster)

- [ ] Copy core template structure
- [ ] Customize for cluster-specific constraints
- [ ] Execute 01 → 02 → 03 phases
- [ ] Validate with Proposer/Critic workflow
- [ ] Update indexes and dashboards
- [ ] Document cluster-specific lessons

---

## Phase 3: Infrastructure Enhancements (Parallel Track)

### 3.1 Automation Tools (Weeks 1-8)

- [ ] Create `tools/generate-refactor-playbook.py` enhancement
  - Auto-generate playbook from template
  - Populate with cluster-specific data from system-module-map.yaml
- [ ] Create `tools/map-violations-to-playbooks.py`
  - Link language governance violations to refactor playbooks
  - Auto-assign to appropriate cluster
- [ ] Create `tools/dashboard-generator.py`
  - Generate HTML dashboard from index.yaml
  - Show governance_status, priority, progress
- [ ] Enhance `validate-refactor-index.py`
  - Add orphaned file detection
  - Add cross-reference validation
  - Add quality metrics tracking

### 3.2 CI/CD Integration (Weeks 4-8)

- [ ] Create `.github/workflows/refactor-validation.yml`
  - Run validation on PR
  - Check architecture constraints
  - Validate quality metrics
- [ ] Create `.github/workflows/playbook-sync.yml`
  - Auto-update index.yaml when playbooks change
  - Trigger dashboard regeneration
- [ ] Enhance Auto-Fix Bot integration
  - Route violations to appropriate playbook
  - Suggest refactor actions based on playbook
  - Link to Proposer/Critic workflow

### 3.3 Dashboard & Visualization (Weeks 6-10)

- [ ] Language Governance Dashboard enhancement
  - Add refactor playbook status
  - Show cluster health metrics
  - Link violations to playbooks
- [ ] Create Refactor Progress Dashboard
  - Show all clusters status (draft/in_progress/completed)
  - Display quality trend graphs
  - Highlight P0/P1/P2 priorities
- [ ] Architecture Skeleton Validator
  - Visual dependency graph
  - Highlight violations in red
  - Show allowed paths in green

---

## Phase 4: Knowledge Base Integration (Weeks 8-12)

### 4.1 Living Knowledge Base

- [ ] Integrate refactor playbooks into knowledge graph
- [ ] Link playbooks to architecture skeletons
- [ ] Create searchable playbook index
- [ ] Add playbook recommendations to AI prompts

### 4.2 Admin CLI Enhancement

- [ ] `admin refactor analyze <cluster>` - Run deconstruction
- [ ] `admin refactor design <cluster>` - Generate integration plan
- [ ] `admin refactor execute <cluster>` - Run refactor with AI
- [ ] `admin refactor validate <cluster>` - Check quality metrics
- [ ] `admin refactor status` - Show all clusters dashboard

---

## Success Metrics

### Phase 1 Success Criteria

- ✅ core/architecture-stability cluster refactored end-to-end
- ✅ All quality thresholds met or improved
- ✅ Template process documented and repeatable
- ✅ Validation tools operational
- ✅ Proposer/Critic workflow proven

### Overall Success Criteria (By Week 12)

- ✅ 5+ clusters fully refactored (core, automation, services)
- ✅ Zero Semgrep HIGH severity issues
- ✅ Language violations reduced by 50%
- ✅ Test coverage ≥ 70% across all clusters
- ✅ Architecture skeleton violations = 0
- ✅ Dashboard showing real-time status
- ✅ CI/CD automated validation

---

## Risk Mitigation

### Risk 1: Scope Creep

**Mitigation**: Focus on one cluster at a time. Complete end-to-end before
moving to next.

### Risk 2: Breaking Changes

**Mitigation**: Use Proposer/Critic workflow. Validate after each change.
Maintain before/after metrics.

### Risk 3: Tool Complexity

**Mitigation**: Start simple. Add features iteratively. Document each tool
thoroughly.

### Risk 4: Resource Constraints

**Mitigation**: Prioritize P0 clusters. Automate repetitive tasks. Use AI for
assistance.

---

## Next Immediate Actions (This Week)

### For New Issue/PR: "Execute core/architecture-stability End-to-End Refactor"

1. Create Issue with Phase 1.1 tasks
2. Assign to @core-owners team
3. Set milestone: "Core Cluster Template"
4. Link to this NEXT_STEPS_PLAN.md

### For Current PR: Finalization

1. ✅ Scan and update all README.md files with refactor playbook references
2. ✅ Ensure all documentation cross-references are correct
3. ✅ Final validation run
4. ✅ Request merge approval

---

## Timeline Overview

```
Week 1-2:   Core deconstruction + integration design
Week 3-4:   Core refactor execution + validation
Week 5-6:   Safety mechanisms cluster
Week 7-8:   SLSA provenance cluster
Week 9-10:  Autonomous system cluster
Week 11-12: Gateway/MCP cluster + retrospective

Parallel: Infrastructure enhancements (tools, CI/CD, dashboards)
```

---

## References

- **Current PR**: Extract and integrate three-phase refactor playbook system
- **Config**: `config/system-module-map.yaml` (v1.2.0)
- **Workflow**:
  `docs/refactor_playbooks/03_refactor/meta/PROPOSER_CRITIC_WORKFLOW.md`
- **Template**:
  `docs/refactor_playbooks/03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md`
- **Validation**: `tools/validate-refactor-index.py`

---

**Last Updated**: 2025-12-06  
**Status**: Foundation Complete, Ready for Phase 1 Execution
