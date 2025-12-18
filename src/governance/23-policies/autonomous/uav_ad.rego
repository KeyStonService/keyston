package uav_ad.policy

# UAV/AD 系統必須標註系統類型
deny[msg] {
  input.kind == "Deployment"
  not input.metadata.labels["uav.io/system"]
  msg := "Missing label uav.io/system (must be 'uav' or 'ad')"
}

# UAV/AD 系統必須標註安全等級
deny[msg] {
  input.kind == "Deployment"
  lvl := input.metadata.labels["uav.io/safety-level"]
  not lvl
  msg := "Missing label uav.io/safety-level (L0-L5)"
}

# 驗證安全等級格式
deny[msg] {
  input.kind == "Deployment"
  lvl := input.metadata.labels["uav.io/safety-level"]
  not regex.match("^L[0-5]$", lvl)
  msg := sprintf("Invalid safety-level '%s', must be L0-L5", [lvl])
}

# 驗證系統類型
deny[msg] {
  input.kind == "Deployment"
  system := input.metadata.labels["uav.io/system"]
  not system_type_valid(system)
  msg := sprintf("Invalid system type '%s', must be 'uav' or 'ad'", [system])
}

system_type_valid(system) {
  system == "uav"
}

system_type_valid(system) {
  system == "ad"
}

# UAV 系統的 ConfigMap 必須啟用地理圍欄配置
deny[msg] {
  input.kind == "ConfigMap"
  input.metadata.labels["uav.io/system"] == "uav"
  not input.data["geo.fence.enabled"]
  msg := "UAV config requires geo.fence.enabled field"
}

# 啟用地理圍欄時必須指定區域
deny[msg] {
  input.kind == "ConfigMap"
  input.data["geo.fence.enabled"] == "true"
  not input.data["geo.fence.regions"]
  msg := "Geo-fence regions must be specified when enabled"
}

# 驗證地理圍欄區域格式
deny[msg] {
  input.kind == "ConfigMap"
  input.data["geo.fence.enabled"] == "true"
  regions := input.data["geo.fence.regions"]
  not regex.match(`^([A-Z]{2}-[A-Za-z0-9_-]+)(,\s*[A-Z]{2}-[A-Za-z0-9_-]+)*$`, regions)
  msg := sprintf("Invalid geo-fence regions format: '%s', expected format: 'XX-RegionName' (e.g., 'TW-Taipei, JP-Tokyo')", [regions])
}

# 高風險操作必須標註風險類別
deny[msg] {
  input.kind == "Deployment"
  lvl := input.metadata.labels["uav.io/safety-level"]
  regex.match("^L[4-5]$", lvl)
  not input.metadata.labels["uav.io/risk-category"]
  msg := sprintf("High safety-level '%s' requires uav.io/risk-category label", [lvl])
}

# 驗證風險類別值
deny[msg] {
  input.kind == "Deployment"
  category := input.metadata.labels["uav.io/risk-category"]
  not risk_category_valid(category)
  msg := sprintf("Invalid risk-category '%s', must be 'low', 'medium', or 'high'", [category])
}

risk_category_valid(category) {
  category == "low"
}

risk_category_valid(category) {
  category == "medium"
}

risk_category_valid(category) {
  category == "high"
}

# Namespace 必須包含必要的標準標籤
deny[msg] {
  input.kind == "Namespace"
  required_labels := ["namespace.io/managed-by", "namespace.io/domain", "namespace.io/environment", "namespace.io/lifecycle"]
  label := required_labels[_]
  not input.metadata.labels[label]
  msg := sprintf("Namespace missing required label: %s", [label])
}

# Service 必須包含系統標註（如果用於 UAV/AD）
warn[msg] {
  input.kind == "Service"
  input.metadata.namespace
  not input.metadata.labels["uav.io/system"]
  msg := "Service in UAV/AD namespace should include uav.io/system label for traceability"
}

# 容器必須設置資源限制（UAV/AD 系統）
deny[msg] {
  input.kind == "Deployment"
  input.metadata.labels["uav.io/system"]
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf("Container '%s' in UAV/AD system must set memory limits", [container.name])
}

deny[msg] {
  input.kind == "Deployment"
  input.metadata.labels["uav.io/system"]
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf("Container '%s' in UAV/AD system must set CPU limits", [container.name])
}

# 建議使用 SHA256 digest 而非 tag（安全最佳實踐）
warn[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not contains(container.image, "@sha256:")
  msg := sprintf("Container '%s' uses tag instead of SHA256 digest; consider using immutable image reference", [container.name])
}
