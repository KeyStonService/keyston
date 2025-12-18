# ═══════════════════════════════════════════════════════════════════════════════
#                    CLI Safe Mode Policy (OPA/Rego)
#                    CLI 安全模式策略
# ═══════════════════════════════════════════════════════════════════════════════
#
# 此策略定義 Admin Copilot CLI 的安全約束，確保：
# 1. 只允許白名單操作
# 2. 危險操作需要人類確認
# 3. 生產環境操作需要額外審批
#
# This policy defines safety constraints for Admin Copilot CLI, ensuring:
# 1. Only whitelisted operations are allowed
# 2. Dangerous operations require human confirmation
# 3. Production environment operations require additional approval
#
# ═══════════════════════════════════════════════════════════════════════════════

package cli.safe_mode

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# ═══════════════════════════════════════════════════════════════════════════════
# Default Deny (預設拒絕)
# ═══════════════════════════════════════════════════════════════════════════════

default allow := false

# ═══════════════════════════════════════════════════════════════════════════════
# Allowed Operations (允許的操作)
# ═══════════════════════════════════════════════════════════════════════════════

allowed_operations := {
    "build",
    "test",
    "lint",
    "fix",
    "analyze",
    "review",
    "generate"
}

# Operations requiring human approval
require_approval := {
    "fix",
    "generate"
}

# Dangerous patterns to detect
dangerous_patterns := {
    "rm -rf",
    "delete",
    "drop",
    "truncate",
    "format",
    "destroy"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Allow Rule (允許規則)
# ═══════════════════════════════════════════════════════════════════════════════

# Allow if operation is in whitelist and no dangerous patterns detected
allow if {
    input.operation in allowed_operations
    not has_dangerous_pattern
    not is_production_without_approval
}

# ═══════════════════════════════════════════════════════════════════════════════
# Safety Checks (安全檢查)
# ═══════════════════════════════════════════════════════════════════════════════

# Check for dangerous patterns in parameters
has_dangerous_pattern if {
    input.parameters_str
    some pattern in dangerous_patterns
    contains(lower(input.parameters_str), pattern)
}

# Check if targeting production without approval
is_production_without_approval if {
    is_production_target
    not input.has_approval
}

# Determine if target is production
is_production_target if {
    contains(lower(input.target_path), "prod")
}

is_production_target if {
    contains(lower(input.target_path), "production")
}

# ═══════════════════════════════════════════════════════════════════════════════
# Approval Requirements (審批要求)
# ═══════════════════════════════════════════════════════════════════════════════

# Determine if operation needs approval
needs_approval if {
    input.operation in require_approval
}

needs_approval if {
    is_production_target
}

# ═══════════════════════════════════════════════════════════════════════════════
# Risk Assessment (風險評估)
# ═══════════════════════════════════════════════════════════════════════════════

# Calculate risk score (0.0 - 1.0)
risk_score := score if {
    base_score := 0.0
    pattern_score := count([p | some p in dangerous_patterns; input.parameters_str; contains(lower(input.parameters_str), p)]) * 0.5
    production_score := 0.2 if is_production_target else 0.0
    operation_score := 0.1 if input.operation in require_approval else 0.0
    
    total := base_score + pattern_score + production_score + operation_score
    score := total if total <= 1.0 else 1.0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Violation Messages (違規訊息)
# ═══════════════════════════════════════════════════════════════════════════════

violations contains msg if {
    not input.operation in allowed_operations
    msg := sprintf("Operation '%s' is not in the whitelist", [input.operation])
}

violations contains msg if {
    input.parameters_str
    some pattern in dangerous_patterns
    contains(lower(input.parameters_str), pattern)
    msg := sprintf("Dangerous pattern detected: %s", [pattern])
}

violations contains msg if {
    is_production_target
    not input.has_approval
    msg := "Production target requires approval"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Recommendations (建議)
# ═══════════════════════════════════════════════════════════════════════════════

recommendations contains msg if {
    is_production_target
    msg := "Consider using staging environment first"
}

recommendations contains msg if {
    input.operation == "fix"
    msg := "Review changes before merging to main branch"
}

recommendations contains msg if {
    input.operation == "generate"
    msg := "Verify generated code meets security standards"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Audit Record (審計記錄)
# ═══════════════════════════════════════════════════════════════════════════════

audit_record := {
    "timestamp": time.now_ns(),
    "operation": input.operation,
    "target": input.target_path,
    "invoked_by": input.invoked_by,
    "allowed": allow,
    "risk_score": risk_score,
    "violations": violations,
    "recommendations": recommendations,
    "needs_approval": needs_approval
}
