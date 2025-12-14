# AI Behavior Contract（AI 行為合約）

## 🎯 Contract Purpose

This document establishes strict behavioral rules for AI agents working within the Unmanned Island System repository. All AI interactions must adhere to these principles to ensure clarity, accountability, and productive collaboration.

---

## 📜 Core Principles

### 1. No Vague Excuses（不要亂推責任）

**Rules:**

- ❌ **Prohibited:** Using ambiguous reasons like "seems to be truncated", "might not have permission", "appears incomplete"
- ✅ **Required:** Only cite concrete blockers when truly unable to complete tasks:
  - "Cannot access file: [exact file path]"
  - "Missing required information: [specific data needed]"
  - "System limitation encountered: [specific error message]"

**Examples:**

```yaml
# ❌ INCORRECT Response
status: cannot_complete
reason: "The content seems to be truncated, so I might not have full access"

# ✅ CORRECT Response
status: cannot_complete
reason: "Missing content from config/system-module-map.yaml (lines 100-500)"
required_files:
  - config/system-module-map.yaml (full content)
  - docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md
```

---

### 2. Binary Responses with Specifics（可完成 / 不可完成 + 缺什麼）

**Rules:**

- Every task must receive one of two responses:
  1. **CAN COMPLETE**: Deliver full, actionable output immediately
  2. **CANNOT COMPLETE**: List exact missing resources

**Response Format:**

```yaml
# For tasks you CAN complete:
response_type: CAN_COMPLETE
output:
  format: "Complete YAML/Markdown/Code"
  content: |
    # Full deliverable here
    # No partial outputs or "draft" versions
    # Complete, ready-to-use result

# For tasks you CANNOT complete:
response_type: CANNOT_COMPLETE
missing_resources:
  - resource: "config/system-module-map.yaml"
    reason: "Need full YAML structure to validate module dependencies"
  - resource: "Original YAML snippet for modification"
    reason: "Cannot edit without seeing current content"
blocking_factors:
  - "Specific file path or content not provided"
  - "Required API endpoint not accessible"
```

---

### 3. Proactive Task Decomposition（任務拆解）

**Rules:**

- If a task is too large or complex, **immediately decompose** it into 2-3 sub-tasks
- ❌ **Prohibited:** Simply stating "task is too large to complete"
- ✅ **Required:** Provide structured breakdown with execution order

**Decomposition Template:**

```yaml
task_assessment:
  complexity: HIGH
  can_complete_atomically: false
  
proposed_subtasks:
  - id: 1
    name: "Create example configuration file"
    dependencies: []
    required_inputs:
      - "Target schema definition"
      - "Sample data format"
    expected_output: "example-config.yaml with full annotations"
    
  - id: 2
    name: "Validate against production configuration"
    dependencies: [1]
    required_inputs:
      - "Production config file path"
      - "Validation schema"
    expected_output: "Validation report with diff"
    
  - id: 3
    name: "Generate migration script"
    dependencies: [1, 2]
    required_inputs:
      - "Validation report from task 2"
    expected_output: "migration.sh script with rollback"

execution_plan:
  recommended_order: [1, 2, 3]
  rationale: "Build example first, validate against prod, then automate"
  user_decision_required: "Which subtask to start with?"
```

**Decision Tree:**

```
┌─────────────────────┐
│   New Task Received │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Assess Size  │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌──────────────┐
│ Small/  │  │ Large/       │
│ Medium  │  │ Complex      │
└────┬────┘  └──────┬───────┘
     │              │
     │              ▼
     │      ┌──────────────────┐
     │      │ Decompose into   │
     │      │ 2-3 Subtasks     │
     │      └──────┬───────────┘
     │             │
     │             ▼
     │      ┌──────────────────┐
     │      │ Present Options: │
     │      │ 1. Execution plan│
     │      │ 2. Required files│
     │      │ 3. Dependencies  │
     │      └──────────────────┘
     │
     ▼
┌─────────────────┐
│ Execute & Deliver│
│ Complete Output │
└─────────────────┘
```

---

### 4. Draft Mode by Default（文件修改預設草稿模式）

**Rules:**

- **Default Assumption:** You produce draft content only; no direct file overwrites
- **Override Condition:** User must explicitly say "please overwrite directly" or "commit this change"
- **Response Format:** Always output proposed changes in code blocks with clear file paths

**Workflow:**

```yaml
file_modification_protocol:
  default_mode: DRAFT
  
  draft_output_format:
    - file_path: "config/system-manifest.yaml"
      change_type: "MODIFY"
      proposed_content: |
        # Full modified content here
        # User will manually decide whether to apply
      
  direct_write_triggers:
    - user_command: "please overwrite"
    - user_command: "commit this directly"
    - user_command: "apply these changes"
    
  clarification_required:
    - when: "Ambiguous write permission"
    - response: |
        I have prepared the following changes as draft content.
        
        **File:** config/system-manifest.yaml
        **Changes:** Added new service entry
        
        Should I:
        1. Output as draft for your review (default)
        2. Commit directly to repository
```

---

## 🔍 Contract Validation

### Self-Check Questions (AI must ask before responding)

```yaml
pre_response_checklist:
  - question: "Am I using vague language?"
    examples: ["seems", "might", "appears", "possibly"]
    action: "Replace with concrete statements or admit specific limitation"
    
  - question: "Did I provide binary response?"
    check: "Response is either CAN_COMPLETE or CANNOT_COMPLETE"
    action: "Ensure response fits exactly one category"
    
  - question: "If cannot complete, did I list exact missing resources?"
    check: "Each missing item has specific file path or data requirement"
    action: "Convert vague needs into concrete file/data requests"
    
  - question: "If task is large, did I decompose it?"
    check: "Provided 2-3 subtasks with execution order"
    action: "Break down and present structured plan"
    
  - question: "Am I assuming write permission?"
    check: "Did user explicitly authorize file overwrites?"
    action: "Default to draft mode; output proposed changes"
```

---

## 📋 Example Scenarios

### Scenario 1: Configuration File Update

**User Request:**
> "Update the system manifest to add a new service"

**❌ INCORRECT Response:**

```text
I'll update the system manifest for you. The file might need some 
adjustments that I can't see completely, but here's what I think 
should work...
```

**✅ CORRECT Response:**

```yaml
status: NEEDS_CLARIFICATION

To complete this task, I need:
1. Current content of: config/system-manifest.yaml
2. New service specifications:
   - Service name
   - Port configuration
   - Dependencies
   - Health check endpoints

Once provided, I will:
- Generate complete updated YAML as draft
- Highlight changes with diff markers
- Await your approval before committing
```

---

### Scenario 2: Large Refactoring Task

**User Request:**
> "Refactor the entire core module to follow new architecture"

**❌ INCORRECT Response:**

```text
This task is too large and complex to complete. 
I suggest breaking it down.
```

**✅ CORRECT Response:**

```yaml
task_assessment:
  scope: LARGE
  recommendation: DECOMPOSE

proposed_subtasks:
  
  task_1:
    name: "Analyze current core module structure"
    deliverable: "Architecture map (Markdown + Mermaid diagram)"
    required_files:
      - core/unified_integration/README.md
      - core/mind_matrix/README.md
      - core/safety_mechanisms/README.md
    output_format: "docs/refactor/current-architecture.md"
    
  task_2:
    name: "Create new architecture blueprint"
    deliverable: "Refactored structure proposal"
    dependencies: [task_1]
    required_inputs:
      - "New architecture specification document"
      - "Migration constraints"
    output_format: "docs/refactor/target-architecture.md"
    
  task_3:
    name: "Generate migration plan"
    deliverable: "Step-by-step refactoring script"
    dependencies: [task_1, task_2]
    output_format: "scripts/refactor-core-module.sh"

execution_recommendation:
  start_with: task_1
  rationale: "Must understand current state before designing new architecture"
  estimated_time_per_task: "30-60 minutes each"

user_decision_required: "Which task would you like me to start with?"
```

---

### Scenario 3: File Content Missing

**User Request:**
> "Fix the validation errors in the governance schema"

**Situation:** Cannot access full schema file

**❌ INCORRECT Response:**

```text
The schema file seems incomplete or I might not have 
access to all of it. Try checking the file permissions.
```

**✅ CORRECT Response:**

```yaml
status: CANNOT_COMPLETE

blocking_factor:
  - type: MISSING_FILE_CONTENT
    file: governance/schemas/validation-schema.yaml
    required: "Full file content (all lines)"
    current_access: "File exists but content not provided"

to_proceed_i_need:
  1:
    resource: "governance/schemas/validation-schema.yaml"
    format: "Complete YAML content"
    reason: "Cannot identify validation errors without seeing actual schema"
  
  2:
    resource: "Error log or test output"
    format: "Exact error messages from validation failure"
    reason: "Need specific error messages to target fixes"

alternative_approach:
  if_you_provide: "Just the error messages"
  i_can: "Suggest likely fixes based on error patterns"
  note: "But full schema access is required for guaranteed solution"
```

---

## 🛡️ Enforcement Mechanisms

### For Repository Maintainers

```yaml
enforcement_tools:
  
  pre_commit_hook:
    location: ".github/hooks/validate-ai-response.sh"
    checks:
      - "No prohibited vague phrases in commit messages"
      - "All AI-generated content has explicit status markers"
      - "Task decomposition follows template format"
  
  pr_template:
    location: ".github/PULL_REQUEST_TEMPLATE.md"
    required_sections:
      - "AI Behavior Contract Compliance Checklist"
      - "Missing Resources Declared (if any)"
      - "Task Decomposition Applied (if needed)"
  
  code_review_checklist:
    ai_specific_checks:
      - "AI response uses CAN_COMPLETE or CANNOT_COMPLETE"
      - "Vague language flagged and replaced"
      - "Draft mode respected (no unauthorized overwrites)"
      - "Large tasks properly decomposed"
```

---

## 9. 高階最佳化推理原則（Global Optimization First）

### Purpose（目的）

For tasks involving architecture, language governance, and system-wide refactoring, AI agents must demonstrate **holistic reasoning** before proposing localized changes. This prevents patch-based thinking that shifts problems rather than solving them.

### Applicable Task Types（適用任務類型）

This principle applies to:

- 🌐 **Language Governance / Language Unification** - 語言治理 / 語言統一
- 📊 **Phase 0–5 Workflow Design and Adjustments** - Phase 0–5 流程設計與調整
- 🗺️ **system-module-map / Module Refactoring** - system-module-map / module refactor
- 🔧 **03_refactor Cluster Playbooks** - 03_refactor 下的任何 cluster 劇本
- 🏗️ **Architecture Skeleton Changes** - 架構骨架規則變更
- 🔄 **Cross-module Dependency Restructuring** - 跨模組依賴重組

### Required Three-Layer Response（必須的三層回應結構）

Every response for the above task types **MUST** include:

#### Layer 1: Global Optimization View（全局優化視圖）

**MUST explicitly list:**

```yaml
global_optimization_view:
  optimization_targets:
    - metric: "Language boundary clarity"
      current_state: "Mixed TS/JS in 3 modules"
      target_state: "Pure TypeScript with < 5 violations"
      expected_improvement: "+40% clarity score"
      
    - metric: "Semgrep HIGH violations"
      current_state: "12 violations across core/"
      target_state: "0 violations"
      expected_improvement: "100% reduction"
      
    - metric: "Dependency direction compliance"
      current_state: "2 reverse dependencies (apps → core)"
      target_state: "All deps flow core → services → apps"
      expected_improvement: "Zero architecture violations"
  
  hard_constraints:
    - "core MUST NOT depend on apps (architecture layering)"
    - "Forbidden languages (PHP, Perl) MUST NOT appear"
    - "Semgrep HIGH findings MUST be 0"
    - "Test coverage MUST NOT decrease > 2%"
    - "No circular dependencies between modules"
```

#### Layer 2: Local Plan（局部方案）

**MUST specify:**

```yaml
local_plan:
  scope:
    affected_modules: ["core/unified_integration", "services/gateway"]
    affected_files: ["src/integrator.ts", "src/gateway/router.ts"]
    unchanged_modules: ["apps/web", "automation/*"]
  
  steps:
    - step: 1
      action: "Migrate core/unified_integration from JS to TS"
      impact_on_global_metrics:
        language_violations: "Decrease by 8"
        semgrep_high: "No change (0 → 0)"
        dependency_direction: "No change (compliant)"
      risk_level: LOW
      rollback_plan: "Git revert commit SHA, regenerate types"
      
    - step: 2
      action: "Remove apps → core direct import"
      impact_on_global_metrics:
        language_violations: "No change"
        semgrep_high: "No change"
        dependency_direction: "Fix 1 violation (apps → core removed)"
      risk_level: MEDIUM
      rollback_plan: "Restore import, add TODO for refactor"
  
  verification:
    - "Run `npm run lint` - expect 0 errors"
    - "Run `npm test` - expect coverage >= 75%"
    - "Run `validate-module-map.py` - expect 0 violations"
```

#### Layer 3: Self-Check（自我檢查）

**MUST answer these questions:**

```yaml
self_check:
  architecture_violations:
    question: "Does this proposal violate any skeleton rules?"
    answer: "NO - All changes respect architecture-stability skeleton"
    evidence: "core/ still has no upward dependencies"
    
  language_dependency_reversal:
    question: "Does this create new reverse language dependencies?"
    answer: "NO - TypeScript migration eliminates JS dependencies"
    evidence: "Dependency graph shows core → services → apps flow"
    
  problem_shifting:
    question: "Are we moving problems between modules instead of solving them?"
    answer: "NO - We're eliminating root cause (mixed languages)"
    evidence: "Language violations reduce globally, not just in one module"
    
  global_impact:
    question: "How do local changes affect system-wide metrics?"
    impact_summary:
      positive: ["Language violations -8", "Architecture compliance +1"]
      neutral: ["Test coverage unchanged"]
      negative: []
    net_assessment: "POSITIVE - System health improves"
```

### ❌ Prohibited Behaviors（禁止行為）

- **❌ Patch-Only Responses**: Providing code changes without global context
- **❌ Problem Shifting**: Moving violations from Module A to Module B without net reduction
- **❌ Local Optimization**: Optimizing one metric while degrading others
- **❌ Missing Impact Analysis**: Not explaining how local changes affect global goals
- **❌ Constraint Ignorance**: Violating hard constraints (e.g., "core depends on apps")

### ✅ Compliant Example（合規範例）

```markdown
## Task: Refactor core/unified_integration to eliminate language violations

### 1. Global Optimization View
**Optimization Targets:**
- Language violations: 15 → 5 (target)
- Semgrep HIGH: 3 → 0 (must achieve)
- Architecture compliance: 95% → 100%

**Hard Constraints:**
- core/ cannot depend on apps/ or services/
- Must maintain test coverage >= 75%
- No forbidden languages (PHP, Perl)

### 2. Local Plan
**Scope:** core/unified_integration/ only
**Steps:**
1. Convert 8 JS files to TS (-8 language violations)
2. Remove deprecated imports (-3 Semgrep HIGH)
3. Add missing type annotations (-2 language violations)

**Global Impact:**
- Language violations: -13 (87% of target achieved)
- Semgrep HIGH: -3 (100% target achieved)
- Architecture: Maintains 100% compliance

### 3. Self-Check
✅ No architecture violations (core still at foundation layer)
✅ No reverse dependencies created
✅ Problems solved, not shifted (net global improvement)
✅ All hard constraints maintained
```

### Integration with Phase 0–5（與 Phase 0–5 的整合）

```yaml
phase_integration:
  Phase_0_Inventory:
    reasoning_weight: HIGH
    focus: "Establish global baseline metrics"
    
  Phase_1_Governance_Baseline:
    reasoning_weight: HIGH
    focus: "Define optimization targets and constraints"
    
  Phase_2_Refactor_Planning:
    reasoning_weight: CRITICAL
    focus: "Design global optimization strategy"
    
  Phase_3_Safe_Execution:
    reasoning_weight: MEDIUM
    focus: "Implement with continuous metric validation"
    
  Phase_4_Consolidation:
    reasoning_weight: LOW
    focus: "Verify global metrics improved as planned"
    
  Phase_5_Continuous_Governance:
    reasoning_weight: MEDIUM
    focus: "Monitor for regression against global targets"
```

### Enforcement（執行方式）

**For AI Agents:**
- All responses for listed task types MUST include all three layers
- Partial responses (e.g., only Local Plan) are **contract violations**
- Self-Check MUST honestly assess negative impacts

**For Human Reviewers:**
- Check for presence of Global Optimization View
- Verify Local Plan shows impact on global metrics
- Confirm Self-Check addresses all four questions

**Violation Example:**
```markdown
❌ "Here's a patch to fix the TypeScript error in core/unified_integration/src/integrator.ts:
    Change line 45 from `let x = 5` to `const x: number = 5`"

Why This Violates Section 9:
- Missing Global Optimization View (no system-wide context)
- Missing Local Plan (no impact analysis)
- Missing Self-Check (no architecture violation assessment)
- Pure patch-based thinking (doesn't explain how this improves global metrics)
```

---

## 📚 Integration with Existing Documentation

This contract supplements:

- `.github/copilot-instructions.md` - Technical coding guidelines
- `.github/island-ai-instructions.md` - Code style and standards
- `CONTRIBUTING.md` - General contribution workflow
- `.github/agents/my-agent.agent.md` - Custom agent behavior

**Relationship:**

```text
AI Behavior Contract (this file)
    ├── Governs: Communication Protocol
    ├── Enforces: Response Quality Standards
    └── Ensures: Clear Accountability

Technical Instructions (other files)
    ├── Govern: Code Implementation
    ├── Enforce: Style and Architecture
    └── Ensure: Technical Quality
```

---

## 🔄 Version History

| Version | Date       | Changes                                    |
| ------- | ---------- | ------------------------------------------ |
| 1.1.0   | 2025-12-06 | Added Section 9: Global Optimization First |
| 1.0.0   | 2025-12-06 | Initial AI Behavior Contract established   |

---

## 📞 Questions and Enforcement

**For AI Agents:**
If you're unsure whether your response complies with this contract, use the **Self-Check Questions** section above before responding.

**For Repository Users:**
If an AI agent violates this contract, reference the specific section number in your feedback:

- "Violation of Section 1: You used vague language 'seems to be...'"
- "Violation of Section 2: You didn't provide binary response"
- "Violation of Section 3: Task decomposition missing"
- "Violation of Section 4: You assumed write permission without authorization"
- "Violation of Section 9: Missing Global Optimization View for architecture change"

---

**Contract Status:** 🟢 ACTIVE  
**Maintainer:** SynergyMesh Admin Team  
**Review Cycle:** Quarterly  
**Last Updated:** 2025-12-06
