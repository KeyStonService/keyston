package main

import future.keywords.in

# Canonical naming pattern from governance/34-config/naming/canonical-naming-machine-spec.yaml
canonical_pattern := "^(?!.*--)(team|tenant|dev|test|staging|prod|learn|sandbox)-[a-z0-9]+(?:-[a-z0-9]+)*$"
max_name_length := 63

# Required labels per canonical governance
required_labels := ["environment", "tenant", "app.kubernetes.io/managed-by"]

# Allowed environments
allowed_environments := ["dev", "test", "staging", "prod", "learn", "sandbox"]

# Reserved tokens that cannot be used as component names
reserved_tokens := ["core", "internal", "system", "legacy", "experimental"]

# Resource kinds to validate
validated_kinds := ["Namespace", "Deployment", "Service", "StatefulSet", "DaemonSet", "Pod"]

# ==========================================
# Naming Pattern Violations
# ==========================================

# Deny if name doesn't match canonical pattern
deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    not regex.match(canonical_pattern, name)
    msg := sprintf("❌ Resource name '%v' does not match canonical pattern. Expected: {env}-{component}-{suffix} (lowercase, alphanumeric with hyphens, no consecutive hyphens)", [name])
}

# Deny if name contains consecutive hyphens
deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    contains(name, "--")
    msg := sprintf("❌ Resource name '%v' contains forbidden consecutive hyphens '--'", [name])
}

# Deny if name exceeds maximum length
deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    count(name) > max_name_length
    msg := sprintf("❌ Resource name '%v' exceeds maximum length of %v characters (current: %v)", [name, max_name_length, count(name)])
}

# Deny if name starts or ends with hyphen
deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    startswith(name, "-")
    msg := sprintf("❌ Resource name '%v' cannot start with a hyphen", [name])
}

deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    endswith(name, "-")
    msg := sprintf("❌ Resource name '%v' cannot end with a hyphen", [name])
}

# Deny if name uses reserved tokens as component name
deny[msg] {
    input.kind in validated_kinds
    name := input.metadata.name
    parts := split(name, "-")
    count(parts) >= 2
    component := parts[1]  # Second part is component in {env}-{component}-{suffix}
    component in reserved_tokens
    msg := sprintf("❌ Resource name '%v' uses reserved token '%v' as component name. Reserved: %v", [name, component, reserved_tokens])
}

# ==========================================
# Label Violations
# ==========================================

# Deny if required labels are missing
deny[msg] {
    input.metadata
    not is_system_resource
    missing_labels := [label | label := required_labels[_]; not input.metadata.labels[label]]
    count(missing_labels) > 0
    msg := sprintf("❌ Missing required labels: %v. All resources must have: %v", [missing_labels, required_labels])
}

# Deny if environment label value is not allowed
deny[msg] {
    input.metadata.labels.environment
    env := input.metadata.labels.environment
    not env in allowed_environments
    msg := sprintf("❌ Invalid environment label '%v'. Allowed environments: %v", [env, allowed_environments])
}

# Deny if name prefix doesn't match environment label
deny[msg] {
    input.kind in validated_kinds
    input.metadata.labels.environment
    name := input.metadata.name
    env := input.metadata.labels.environment

    # Check if name starts with any allowed environment prefix
    env_prefixes := [sprintf("%v-", [e]) | e := allowed_environments[_]]
    has_env_prefix := [prefix | prefix := env_prefixes[_]; startswith(name, prefix)][_]

    # If it has an env prefix, it must match the label
    has_env_prefix
    not startswith(name, sprintf("%v-", [env]))
    msg := sprintf("❌ Name prefix does not match environment label. Name starts with '%v' but environment label is '%v'", [split(name, "-")[0], env])
}

# ==========================================
# Annotation Warnings
# ==========================================

# Warn if canonical URN annotation is missing
warn[msg] {
    input.metadata
    not is_system_resource
    not input.metadata.annotations["axiom.io/canonical-urn"]
    msg := sprintf("⚠️  Missing recommended annotation: axiom.io/canonical-urn for %v/%v", [input.kind, input.metadata.name])
}

# Warn if governance mode annotation is missing
warn[msg] {
    input.metadata
    not is_system_resource
    not input.metadata.annotations["axiom.io/governance-mode"]
    msg := sprintf("⚠️  Missing recommended annotation: axiom.io/governance-mode (minimal|strict) for %v/%v", [input.kind, input.metadata.name])
}

# Warn if tenant label is 'platform' but no cost-center label
warn[msg] {
    input.metadata.labels.tenant == "platform"
    input.metadata.labels.environment in ["prod", "staging"]
    not input.metadata.labels["cost-center"]
    msg := sprintf("⚠️  Production/staging platform resources should have a cost-center label for %v/%v", [input.kind, input.metadata.name])
}

# ==========================================
# Helper Functions
# ==========================================

# Check if resource is a system resource (exempt from some rules)
is_system_resource {
    input.metadata.namespace in ["kube-system", "kube-public", "kube-node-lease", "gatekeeper-system"]
}

is_system_resource {
    startswith(input.metadata.name, "kube-")
}

is_system_resource {
    input.kind == "ComponentStatus"
}

is_system_resource {
    input.kind == "Node"
}
