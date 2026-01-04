# External Secrets Operator 整合

## 概述

使用 External Secrets Operator (ESO) 從 AWS Secrets Manager 同步密鑰到 Kubernetes。

## 架構

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  AWS Secrets        │────▶│  External Secrets   │────▶│  Kubernetes         │
│  Manager            │     │  Operator           │     │  Secrets            │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────────┐
                            │  ClusterSecretStore │
                            │  (AWS Provider)     │
                            └─────────────────────┘
```

## 前置條件

### 1. 安裝 External Secrets Operator

```bash
# 使用 Helm 安裝
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace \
  --set installCRDs=true
```

### 2. 配置 IAM 權限

使用 IRSA (IAM Roles for Service Accounts):

```hcl
# Terraform
module "external_secrets_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name = "external-secrets"

  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = ["external-secrets:external-secrets-sa"]
    }
  }

  role_policy_arns = {
    secrets_manager = aws_iam_policy.secrets_manager_read.arn
  }
}

resource "aws_iam_policy" "secrets_manager_read" {
  name = "external-secrets-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:us-east-1:*:secret:chatops/*"
      }
    ]
  })
}
```

### 3. 在 AWS Secrets Manager 創建密鑰

```bash
# Database credentials
aws secretsmanager create-secret \
  --name chatops/prod/database \
  --secret-string '{
    "username": "chatops",
    "password": "your-secure-password",
    "host": "chatops-prod.xxx.us-east-1.rds.amazonaws.com",
    "port": "5432",
    "database": "chatops"
  }'

# Redis credentials
aws secretsmanager create-secret \
  --name chatops/prod/redis \
  --secret-string '{
    "host": "chatops-redis.xxx.cache.amazonaws.com",
    "port": "6379",
    "password": "your-redis-password"
  }'

# API keys
aws secretsmanager create-secret \
  --name chatops/prod/integrations \
  --secret-string '{
    "slack_bot_token": "xoxb-xxx",
    "slack_signing_secret": "xxx",
    "github_app_private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
    "github_app_id": "123456",
    "pagerduty_api_key": "xxx"
  }'
```

## 部署

```bash
# 部署 ClusterSecretStore
kubectl apply -f cluster-secret-store.yaml

# 部署 ExternalSecrets
kubectl apply -f database-secret.yaml
kubectl apply -f redis-secret.yaml
kubectl apply -f api-keys-secret.yaml
```

## 驗證

```bash
# 檢查 ClusterSecretStore 狀態
kubectl get clustersecretstore aws-secrets-manager

# 檢查 ExternalSecret 狀態
kubectl get externalsecret -n chatops

# 檢查生成的 Secret
kubectl get secret -n chatops

# 查看 Secret 內容
kubectl get secret chatops-database-credentials -n chatops -o jsonpath='{.data.POSTGRES_USER}' | base64 -d
```

## 故障排除

### ExternalSecret 狀態為 SecretSyncedError

```bash
# 查看詳細錯誤
kubectl describe externalsecret chatops-database-credentials -n chatops

# 常見原因:
# 1. IAM 權限不足
# 2. Secret 路徑錯誤
# 3. Secret 屬性名稱錯誤
```

### ClusterSecretStore 連接失敗

```bash
# 檢查 Service Account
kubectl get sa external-secrets-sa -n external-secrets -o yaml

# 檢查 Pod logs
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets
```

## 密鑰輪換

ESO 會根據 `refreshInterval` 自動同步更新:

```yaml
spec:
  refreshInterval: 1h  # 每小時同步一次
```

手動觸發同步:

```bash
kubectl annotate externalsecret chatops-database-credentials \
  force-sync=$(date +%s) --overwrite -n chatops
```

## 最佳實踐

1. **使用 IRSA**: 避免使用 Access Keys
2. **最小權限**: 只授予必要的 Secrets 讀取權限
3. **適當的刷新間隔**: 根據安全需求設定
4. **監控同步狀態**: 設置告警監控 ExternalSecret 狀態
5. **版本控制**: ExternalSecret 定義應納入版本控制
