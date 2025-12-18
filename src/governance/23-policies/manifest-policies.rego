# ==============================================================================
# Kubernetes Manifest 策略 - 可執行政策
# ==============================================================================
# 用途: 對 Kubernetes manifests 進行策略驗證
# 語言: 繁體中文註解
# 對齊: Kubernetes 1.30, OPA 最新版本
# ==============================================================================

package kubernetes

import future.keywords.if
import future.keywords.in

# ------------------------------------------------------------------------------
# 拒絕規則 (Deny Rules)
# ------------------------------------------------------------------------------

# 禁止使用 latest tag
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf(
    "容器 '%s' 使用 latest tag，必須使用明確版本或 SHA256 digest",
    [container.name]
  )
}

# 強制設置資源限制
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf(
    "容器 '%s' 缺少記憶體限制 (resources.limits.memory)",
    [container.name]
  )
}

deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf(
    "容器 '%s' 缺少 CPU 限制 (resources.limits.cpu)",
    [container.name]
  )
}

# 強制設置資源請求
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.requests
  msg := sprintf(
    "容器 '%s' 缺少資源請求 (resources.requests)",
    [container.name]
  )
}

# 禁止 privileged 模式
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf(
    "容器 '%s' 不允許使用 privileged 模式",
    [container.name]
  )
}

# 強制 runAsNonRoot
deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := "Deployment 必須設置 runAsNonRoot: true"
}

# 檢查必要標籤
required_labels := [
  "app",
  "version",
  "environment"
]

deny[msg] {
  input.kind == "Deployment"
  label := required_labels[_]
  not input.metadata.labels[label]
  msg := sprintf(
    "Deployment 缺少必要標籤: %s",
    [label]
  )
}

# 強制 readOnlyRootFilesystem
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.securityContext.readOnlyRootFilesystem
  msg := sprintf(
    "容器 '%s' 必須設置 readOnlyRootFilesystem: true",
    [container.name]
  )
}

# 禁止 hostNetwork
deny[msg] {
  input.kind == "Deployment"
  input.spec.template.spec.hostNetwork == true
  msg := "禁止使用 hostNetwork: true"
}

# 禁止 hostPID
deny[msg] {
  input.kind == "Deployment"
  input.spec.template.spec.hostPID == true
  msg := "禁止使用 hostPID: true"
}

# 禁止 hostIPC
deny[msg] {
  input.kind == "Deployment"
  input.spec.template.spec.hostIPC == true
  msg := "禁止使用 hostIPC: true"
}

# Service 類型限制
deny[msg] {
  input.kind == "Service"
  input.spec.type == "LoadBalancer"
  not input.metadata.annotations["approved-loadbalancer"]
  msg := "LoadBalancer 類型的 Service 需要 approved-loadbalancer 註解"
}

# Ingress TLS 要求
deny[msg] {
  input.kind == "Ingress"
  not input.spec.tls
  msg := "Ingress 必須配置 TLS"
}

# ------------------------------------------------------------------------------
# 警告規則 (Warn Rules)
# ------------------------------------------------------------------------------

warn[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[_].livenessProbe
  msg := "建議配置 livenessProbe 以確保容器健康"
}

warn[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.containers[_].readinessProbe
  msg := "建議配置 readinessProbe 以確保流量路由正確"
}

warn[msg] {
  input.kind == "Deployment"
  input.spec.replicas < 2
  msg := sprintf(
    "建議 replica 數量至少為 2 以確保高可用性，當前: %d",
    [input.spec.replicas]
  )
}

# ------------------------------------------------------------------------------
# 通過規則 (Pass Rules)
# ------------------------------------------------------------------------------

pass[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  contains(container.image, "@sha256:")
  msg := sprintf(
    "✓ 容器 '%s' 使用 SHA256 digest，符合最佳實踐",
    [container.name]
  )
}

pass[msg] {
  input.kind == "Deployment"
  input.spec.template.spec.securityContext.runAsNonRoot == true
  msg := "✓ 已設置 runAsNonRoot: true"
}

# ==============================================================================
# 策略說明
# ==============================================================================
# 拒絕規則 (deny): 違反將導致部署失敗
# 警告規則 (warn): 違反將產生警告但不阻止部署
# 通過規則 (pass): 符合最佳實踐的配置
#
# 使用方式:
# opa eval --data manifest-policies.rego --input deployment.yaml 'data.kubernetes.deny'
# opa eval --data manifest-policies.rego --input deployment.yaml 'data.kubernetes.warn'
# opa eval --data manifest-policies.rego --input deployment.yaml 'data.kubernetes.pass'
# ==============================================================================
