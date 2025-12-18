# Namespace 高階實務與遷移落地手冊

## 目標
- 深化專案命名空間運用，對齊 canonical 規範與 URN/labels。
- 提供租戶/區域/環境分層、資源配額、RBAC、NetworkPolicy 範例。
- 提供舊 namespace 自動遷移流程，對應 `governance/34-config/naming/namespace-mapping.yaml`。

## 分層命名示例（符合 canonical regex）
```
tenant-prod-uav-apac
tenant-staging-ad-eu
team-dev-platform-us
```
- 前綴需落在 machine-spec 中的 prefix sets，並與 `environment` 標籤對齊。

## 標準標籤與 URN
- 必要標籤：`environment`, `tenant`, `app.kubernetes.io/managed-by`
- 建議：`namespace.io/domain`, `namespace.io/region`, `namespace.io/team`
- URN 樣板：`urn:axiom:{domain}:{component}:env:{environment}:{version}`
- 對應：`governance/34-config/naming/canonical-naming-machine-spec.yaml`

## 配額 (ResourceQuota) 範例
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: rq-standard
  namespace: tenant-prod-uav-apac
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 32Gi
    limits.cpu: "16"
    limits.memory: 64Gi
    pods: "200"
```

## RBAC 範例（租戶維運角色）
```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tenant-ops
  namespace: tenant-prod-uav-apac
rules:
  - apiGroups: [""]
    resources: ["pods","services","configmaps","secrets"]
    verbs: ["get","list","watch","create","update","delete"]
```

## NetworkPolicy 範例（同 namespace 內通訊 + Prometheus 抓 metrics）
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-ns-and-metrics
  namespace: tenant-prod-uav-apac
spec:
  podSelector: {}
  policyTypes: ["Ingress","Egress"]
  ingress:
    - from:
        - podSelector: {}
        - namespaceSelector:
            matchLabels:
              namespace.io/monitoring: "prometheus"
  egress:
    - to:
        - podSelector: {}
```

## 自動遷移流程（舊 → canonical）
1. 參考 `governance/34-config/naming/namespace-mapping.yaml` 確認 old→canonical/URN/labels。
2. 以腳本套用標籤（示意）：
   ```bash
   ns=unmanned-island-system
   canon=prod-unmanned-island-system
   urn="urn:axiom:unmanned-island:system:env:prod:v1"
   kubectl label ns $ns environment=prod tenant=platform app.kubernetes.io/managed-by=axiom-naming-controller --overwrite
   kubectl annotate ns $ns axiom.io/canonical-urn=$urn --overwrite
   kubectl annotate ns $ns axiom.io/qualifiers="region=apac" --overwrite
   kubectl create namespace $canon --dry-run=client -o yaml | kubectl apply -f -
   ```
3. 更新 GitOps/manifest：將 namespace 欄位換成 canonical 名稱並確保 labels/annotations 一致。
4. 驗證：
   - `conftest test <manifests> --policy governance/23-policies/conftest`
   - Gatekeeper 約束（若啟用）應通過 `K8sNamingPattern` / `K8sRequiredLabels`。

## 與既有資產的對齊
- Machine-spec：`governance/34-config/naming/canonical-naming-machine-spec.yaml`
- Policy：`governance/23-policies/conftest/naming_policy.rego`
- Mapping：`governance/34-config/naming/namespace-mapping.yaml`
- 基礎教學：`governance/29-docs/namespace-from-zero.md`
