# Conftest Policy for Canonical Naming Governance
# 基於 canonical/machine-spec.yaml 的 OPA Rego 驗證策略
# 此文件應從 machine-spec.yaml 自動生成或保持同步

package main

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# 配置（應從 canonical/machine-spec.yaml 讀取）
canonical_regex := "^(team|tenant|dev|test|staging|prod|learn)-[a-z0-9-]{1,56}[a-z0-9]$"

allowed_environments := [
    "dev",
    "test",
    "staging",
    "prod",
    "learn"
]

required_labels := [
    "environment",
    "tenant"
]

required_annotations := [
    "machinenativeops.io/canonical-urn"
]

reserved_keywords := [
    "core",
    "internal",
    "system",
    "legacy",
    "experimental",
    "kube",
    "kubernetes",
    "default"
]

exempted_namespaces := [
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "default",
    "gatekeeper-system",
    "cert-manager",
    "ingress-nginx",
    "monitoring",
    "logging"
]

##############################################
# 驗證規則: deny[] 表示失敗，違規阻止資源創建
##############################################

# 規則 1: Namespace 命名格式驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)
    not regex.match(canonical_regex, name)

    msg := sprintf(
        "❌ RULE-001: Namespace '%s' does not match canonical naming pattern.\n   Expected: %s\n   Examples: team-frontend-prod, tenant-payment-prod-uswest, prod-api-v2",
        [name, canonical_regex]
    )
}

# 規則 2: 必需標籤驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    required_label := required_labels[_]
    labels := object.get(input.metadata, "labels", {})
    not labels[required_label]

    msg := sprintf(
        "❌ RULE-002: Namespace '%s' is missing required label '%s'.\n   Required labels: %v",
        [name, required_label, required_labels]
    )
}

# 規則 3: 環境標籤值驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    labels := object.get(input.metadata, "labels", {})
    env := labels.environment
    env  # 確保標籤存在
    not env in allowed_environments

    msg := sprintf(
        "❌ RULE-005: Namespace '%s' has invalid environment '%s'.\n   Allowed: %v",
        [name, env, allowed_environments]
    )
}

# 規則 4: 保留關鍵字驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_system_namespace(name)

    keyword := reserved_keywords[_]
    contains_keyword(name, keyword)

    msg := sprintf(
        "❌ RULE-004: Namespace '%s' contains reserved keyword '%s'.\n   Reserved keywords: %v",
        [name, keyword, reserved_keywords]
    )
}

# 規則 5: Tenant 標籤格式驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    labels := object.get(input.metadata, "labels", {})
    tenant := labels.tenant
    tenant  # 確保標籤存在
    not regex.match("^[a-z0-9-]{2,32}$", tenant)

    msg := sprintf(
        "❌ Namespace '%s' has invalid tenant label format '%s'.\n   Expected format: ^[a-z0-9-]{2,32}$",
        [name, tenant]
    )
}

# 規則 6: 字符限制驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)
    not regex.match("^[a-z0-9-]+$", name)

    msg := sprintf(
        "❌ RULE-002 (Characters): Namespace '%s' contains invalid characters.\n   Only lowercase letters, numbers, and hyphens are allowed.",
        [name]
    )
}

# 規則 7: 長度驗證
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    length := count(name)
    length > 63

    msg := sprintf(
        "❌ RULE-003 (Length): Namespace '%s' exceeds maximum length of 63 characters (current: %d).",
        [name, length]
    )
}

deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    length := count(name)
    length < 3

    msg := sprintf(
        "❌ RULE-003 (Length): Namespace '%s' is too short (minimum 3 characters, current: %d).",
        [name, length]
    )
}

# 規則 8: 連續破折號檢查
deny[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)
    contains(name, "--")

    msg := sprintf(
        "❌ RULE-005: Namespace '%s' contains consecutive hyphens '--'.\n   Remove extra hyphens.",
        [name]
    )
}

##############################################
# 驗證規則: warn[] 表示警告，不阻止資源創建
##############################################

# 警告 1: 缺少 URN annotation
warn[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    annotations := object.get(input.metadata, "annotations", {})
    not annotations["machinenativeops.io/canonical-urn"]

    msg := sprintf(
        "⚠️  RULE-003: Namespace '%s' is missing recommended URN annotation 'machinenativeops.io/canonical-urn'.\n   Example: urn:machinenativeops:team:frontend:env:prod:v1",
        [name]
    )
}

# 警告 2: 缺少推薦標籤
warn[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    labels := object.get(input.metadata, "labels", {})
    not labels["app.kubernetes.io/managed-by"]

    msg := sprintf(
        "⚠️  Namespace '%s' is missing recommended label 'app.kubernetes.io/managed-by'.\n   Example values: helm, kubectl, terraform, argocd, flux",
        [name]
    )
}

# 警告 3: 缺少描述 annotation
warn[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    annotations := object.get(input.metadata, "annotations", {})
    not annotations["machinenativeops.io/description"]

    msg := sprintf(
        "⚠️  Namespace '%s' is missing recommended annotation 'machinenativeops.io/description'.\n   Add a brief description of this namespace's purpose.",
        [name]
    )
}

# 警告 4: 缺少 owner annotation
warn[msg] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    annotations := object.get(input.metadata, "annotations", {})
    not annotations["machinenativeops.io/owner"]

    msg := sprintf(
        "⚠️  Namespace '%s' is missing recommended annotation 'machinenativeops.io/owner'.\n   Specify the team or contact email responsible for this namespace.",
        [name]
    )
}

##############################################
# 輔助函數
##############################################

# 檢查資源是否豁免
is_exempted(name) {
    exempted := exempted_namespaces[_]
    name == exempted
}

# 檢查資源是否豁免（支持 glob 模式）
is_exempted(name) {
    exemption := exempted_namespaces[_]
    contains(exemption, "*")
    prefix := trim_suffix(exemption, "*")
    startswith(name, prefix)
}

# 檢查是否為系統命名空間
is_system_namespace(name) {
    system_namespaces := ["kube-system", "kube-public", "kube-node-lease", "default"]
    name == system_namespaces[_]
}

# 檢查字符串是否包含另一個字符串
contains_keyword(str, keyword) {
    contains(str, keyword)
}

##############################################
# Deployment 驗證規則
##############################################

# Deployment 必需標籤
deny[msg] {
    input.kind == "Deployment"
    name := input.metadata.name

    required_deployment_labels := ["environment", "app.kubernetes.io/name"]
    required_label := required_deployment_labels[_]

    labels := object.get(input.metadata, "labels", {})
    not labels[required_label]

    msg := sprintf(
        "❌ LABEL-002: Deployment '%s' is missing required label '%s'.\n   Required labels: %v",
        [name, required_label, required_deployment_labels]
    )
}

# Deployment 環境標籤值驗證
deny[msg] {
    input.kind == "Deployment"
    name := input.metadata.name

    labels := object.get(input.metadata, "labels", {})
    env := labels.environment
    env
    not env in allowed_environments

    msg := sprintf(
        "❌ Deployment '%s' has invalid environment '%s'.\n   Allowed: %v",
        [name, env, allowed_environments]
    )
}

##############################################
# Service 驗證規則
##############################################

# Service 必需標籤
deny[msg] {
    input.kind == "Service"
    name := input.metadata.name

    required_service_labels := ["environment", "app.kubernetes.io/name"]
    required_label := required_service_labels[_]

    labels := object.get(input.metadata, "labels", {})
    not labels[required_label]

    msg := sprintf(
        "❌ LABEL-003: Service '%s' is missing required label '%s'.\n   Required labels: %v",
        [name, required_label, required_service_labels]
    )
}

##############################################
# 信息級別反饋 (不阻止，僅提供信息)
##############################################

# 檢測使用的命名模式
violation[{"msg": msg, "level": "info"}] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    # 檢測模式 1: team-domain-env
    regex.match("^team-[a-z0-9-]+-(?:dev|test|staging|prod|learn)$", name)

    msg := sprintf(
        "ℹ️  Namespace '%s' uses naming mode: team-domain-env",
        [name]
    )
}

violation[{"msg": msg, "level": "info"}] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    # 檢測模式 2: tenant-workload-env-region
    regex.match("^tenant-[a-z0-9-]+-(?:dev|test|staging|prod)-[a-z0-9-]+$", name)

    msg := sprintf(
        "ℹ️  Namespace '%s' uses naming mode: tenant-workload-env-region",
        [name]
    )
}

violation[{"msg": msg, "level": "info"}] {
    input.kind == "Namespace"
    name := input.metadata.name
    not is_exempted(name)

    # 檢測模式 3: env-app-version
    regex.match("^(?:dev|test|staging|prod)-[a-z0-9-]+-v[0-9]+$", name)

    msg := sprintf(
        "ℹ️  Namespace '%s' uses naming mode: env-app-version",
        [name]
    )
}

##############################################
# 測試數據 (用於本地測試)
##############################################

# 使用方法:
# conftest test -p templates/conftest/naming.rego examples/governance/naming/sample-namespace.yaml
#
# 預期輸出:
# PASS - examples/governance/naming/sample-namespace.yaml - 3 tests
# WARN - examples/governance/naming/bad-namespace.yaml - Missing URN annotation
# FAIL - examples/governance/naming/bad-namespace.yaml - Namespace 'BadNamespace' does not match canonical pattern
