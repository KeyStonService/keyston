# 安全合规 (Security Compliance)

> **治理模块**: 安全与合规 (Security and Compliance)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

安全合规模块确保所有系统和实践符合安全标准和合规要求。通过集成安全检查到治理框架，我们实现"左移"安全，在开发早期发现和修复安全问题。

## 目标

- 🔒 **安全默认**: 默认配置遵循安全最佳实践
- 🔍 **早期发现**: CI/CD 中自动化安全检查
- 📋 **合规性**: 满足行业标准和法规要求
- 🚨 **快速响应**: 安全问题的快速识别和修复
- 📊 **可追溯**: 完整的安全审计记录

## 安全要求

### 1. 数据分类

所有资源必须标记数据分类级别：

```yaml
# Kubernetes 资源标签
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prod-payment-api-deploy-v1.3.0
  labels:
    # 数据分类（必需）
    data-classification: "confidential"  # public | internal | confidential | restricted

    # 合规范围（可选）
    compliance-scope: "pci-dss,soc2"    # 逗号分隔的合规标准

spec:
  template:
    metadata:
      labels:
        data-classification: "confidential"
```

**数据分类级别定义**:

| 级别 | 定义 | 示例 | 安全要求 |
|------|------|------|----------|
| **public** | 公开信息 | 产品文档、公告 | 基础安全 |
| **internal** | 内部信息 | 内部文档、日志 | 基础安全 + 访问控制 |
| **confidential** | 机密信息 | 用户数据、交易记录 | 加密 + 严格访问控制 + 审计 |
| **restricted** | 高度机密 | 支付信息、身份证号 | 全程加密 + 最小权限 + 完整审计 |

### 2. 密钥管理

**禁止硬编码密钥**:

```yaml
# ❌ 错误: 硬编码密钥
apiVersion: v1
kind: ConfigMap
data:
  database_password: "MyP@ssw0rd123"  # 禁止！

# ✅ 正确: 使用 Secret
apiVersion: v1
kind: Secret
metadata:
  name: prod-payment-api-secret-v1.3.0
type: Opaque
data:
  database_password: "TXlQQHNzdzByZDEyMw=="  # Base64 编码
```

**命名规范**:

```yaml
Secret 命名: {environment}-{app}-secret-{version}
示例: prod-payment-api-secret-v1.3.0

Secret 内容必须:
  - [ ] Base64 编码
  - [ ] 不包含注释或元数据
  - [ ] 定期轮换（至少每 90 天）
  - [ ] 使用外部密钥管理系统（推荐）
```

**外部密钥管理**:

```yaml
# HashiCorp Vault 集成
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "payment-api"
        vault.hashicorp.com/agent-inject-secret-database: "database/creds/payment"

# AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: prod-payment-api-external-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: prod-payment-api-secret-v1.3.0
  data:
    - secretKey: database_password
      remoteRef:
        key: prod/payment-api/database
        property: password
```

### 3. 网络安全

**网络策略 (Network Policy)**:

```yaml
# 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress

---
# 只允许特定服务访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payment-api-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: payment-api
  policyTypes:
    - Ingress
  ingress:
    # 允许从 API Gateway
    - from:
        - namespaceSelector:
            matchLabels:
              name: api-gateway
          podSelector:
            matchLabels:
              app: gateway
      ports:
        - protocol: TCP
          port: 8080

    # 允许从 Prometheus
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
          podSelector:
            matchLabels:
              app: prometheus
      ports:
        - protocol: TCP
          port: 8080
```

**服务网格 (Service Mesh)**:

```yaml
# Istio PeerAuthentication
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # 强制 mTLS

---
# AuthorizationPolicy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-api-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-api
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/api-gateway/sa/gateway-sa"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/payment"]
```

### 4. 容器安全

**安全上下文 (Security Context)**:

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      # Pod 安全上下文
      securityContext:
        runAsNonRoot: true          # 不以 root 运行
        runAsUser: 1000            # 指定用户 ID
        runAsGroup: 1000           # 指定组 ID
        fsGroup: 1000              # 文件系统组
        seccompProfile:            # Seccomp 配置
          type: RuntimeDefault

      containers:
      - name: payment-api
        image: payment-api:v1.3.0

        # 容器安全上下文
        securityContext:
          allowPrivilegeEscalation: false  # 禁止特权升级
          readOnlyRootFilesystem: true     # 只读根文件系统
          runAsNonRoot: true
          capabilities:
            drop:
              - ALL                          # 移除所有能力

        # 资源限制（防止资源耗尽攻击）
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"

        # 卷挂载
        volumeMounts:
          - name: tmp
            mountPath: /tmp            # 临时文件目录

      volumes:
        - name: tmp
          emptyDir: {}
```

**镜像安全**:

```yaml
镜像要求:
  - [ ] 使用官方或受信任的基础镜像
  - [ ] 定期扫描漏洞
  - [ ] 不包含调试工具（生产环境）
  - [ ] 使用多阶段构建减小体积
  - [ ] 使用特定版本标签（不使用 latest）
  - [ ] 签名和验证镜像

# Dockerfile 最佳实践
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o app

# 最小运行时镜像
FROM alpine:3.19
RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app
USER app
COPY --from=builder /app/app /app
ENTRYPOINT ["/app"]
```

### 5. RBAC 权限

**最小权限原则**:

```yaml
# ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prod-payment-api-sa
  namespace: production

---
# Role (命名空间级别)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payment-api-role
  namespace: production
rules:
  # 只读配置
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]

  # 只读密钥
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["prod-payment-api-secret-v1.3.0"]
    verbs: ["get"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payment-api-rolebinding
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payment-api-role
subjects:
  - kind: ServiceAccount
    name: prod-payment-api-sa
    namespace: production
```

## 安全检查

### 1. 静态代码分析 (SAST)

**工具集成**:

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      # Semgrep
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

      # CodeQL
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v2

      # SonarQube
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**检查规则**:

```yaml
检查内容:
  - 硬编码密钥和密码
  - SQL 注入风险
  - XSS 风险
  - 不安全的依赖
  - 不安全的加密算法
  - 路径遍历风险
  - 命令注入风险
```

### 2. 依赖扫描

```yaml
# .github/workflows/dependency-scan.yml
name: Dependency Scan
on: [pull_request, push]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      # Snyk
      - name: Snyk Test
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      # OWASP Dependency Check
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          format: 'ALL'

      # Trivy
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

### 3. 容器镜像扫描

```yaml
# .github/workflows/container-scan.yml
name: Container Scan
on: [push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Build image
        run: docker build -t $IMAGE_NAME:$TAG .

      # Trivy 扫描
      - name: Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: $IMAGE_NAME:$TAG
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      # Grype 扫描
      - name: Grype vulnerability scanner
        uses: anchore/scan-action@v3
        with:
          image: $IMAGE_NAME:$TAG
          fail-build: true
          severity-cutoff: high

      # 上传结果到 GitHub Security
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### 4. Kubernetes 配置扫描

```yaml
# .github/workflows/k8s-security-scan.yml
name: Kubernetes Security Scan
on: [pull_request]

jobs:
  k8s-scan:
    runs-on: ubuntu-latest
    steps:
      # Kubesec
      - name: Kubesec scan
        uses: controlplaneio/kubesec-action@master
        with:
          input: k8s/*.yaml

      # Kube-bench
      - name: Kube-bench
        uses: aquasecurity/kube-bench-action@v1

      # Polaris
      - name: Polaris Audit
        uses: fairwindsops/polaris-action@v1
        with:
          checks: |
            security
            efficiency
            reliability
```

### 5. 运行时安全

```yaml
# Falco 规则示例
- rule: Unauthorized Process in Container
  desc: Detect process not in allowed list
  condition: >
    spawned_process and
    container and
    not proc.name in (allowed_processes)
  output: >
    Unauthorized process in container
    (user=%user.name command=%proc.cmdline container=%container.id)
  priority: WARNING

- rule: Sensitive File Access
  desc: Detect access to sensitive files
  condition: >
    open_read and
    container and
    fd.name in (sensitive_files)
  output: >
    Sensitive file accessed
    (user=%user.name file=%fd.name container=%container.id)
  priority: WARNING
```

## 合规标准

### 1. SOC 2

**控制要求**:

```yaml
# SOC 2 Type II 控制映射
controls:
  CC6.1 - 逻辑和物理访问控制:
    - RBAC 权限管理
    - 网络策略
    - 密钥管理
    - 多因素认证

  CC6.6 - 加密:
    - 传输加密（mTLS）
    - 静态数据加密
    - 密钥轮换

  CC7.2 - 系统监控:
    - 日志聚合和分析
    - 告警和响应
    - 安全事件审计

  CC8.1 - 变更管理:
    - 变更请求流程
    - 代码审查
    - 自动化测试
```

**证据收集**:

```bash
# 自动生成 SOC 2 合规证据
python tools/governance/python/generate_soc2_evidence.py \
  --period 2025-01 \
  --output compliance/soc2/2025-01-evidence.yaml

# 证据包括:
# - RBAC 配置历史
# - 变更请求记录
# - 安全扫描结果
# - 访问日志
# - 事件响应记录
```

### 2. PCI DSS

**适用场景**: 处理支付卡信息的服务

```yaml
# PCI DSS 要求映射
requirements:
  Requirement 3 - 保护存储的持卡人数据:
    - 数据分类标签: restricted
    - 静态数据加密
    - 密钥管理
    - 访问日志

  Requirement 4 - 在开放公共网络上传输持卡人数据时进行加密:
    - mTLS 强制执行
    - TLS 1.2+ only
    - 证书管理

  Requirement 6 - 开发和维护安全的系统和应用程序:
    - SAST/DAST 扫描
    - 依赖扫描
    - 安全代码审查
    - 漏洞管理

  Requirement 10 - 跟踪和监控对网络资源和持卡人数据的所有访问:
    - 审计日志
    - 日志保留（至少 90 天）
    - 日志完整性保护
```

### 3. GDPR

**数据保护要求**:

```yaml
# GDPR 合规要求
requirements:
  数据分类:
    - 标记包含 PII 的资源
    - 数据处理记录

  数据最小化:
    - 只收集必需的数据
    - 定期清理过期数据

  数据主体权利:
    - 访问权（数据导出）
    - 删除权（数据擦除）
    - 更正权

  安全措施:
    - 加密传输和存储
    - 访问控制
    - 数据泄露通知机制

  数据保留:
    - 明确保留期限
    - 自动删除过期数据
```

**隐私标签**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    data-classification: "confidential"
    pii: "true"                        # 包含个人身份信息
    data-retention: "90d"              # 数据保留期限
    gdpr-scope: "true"                 # GDPR 适用范围
```

## 安全审计

### 审计日志要求

**必需审计事件**:

```yaml
审计事件类型:
  认证和授权:
    - 登录成功/失败
    - 权限变更
    - 令牌颁发和吊销

  数据访问:
    - 敏感数据访问
    - 数据导出
    - 数据修改和删除

  配置变更:
    - 安全配置变更
    - 密钥轮换
    - RBAC 变更

  安全事件:
    - 安全扫描发现
    - 漏洞修复
    - 安全事件响应
```

**审计日志格式**:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "event_type": "data_access",
  "actor": {
    "user_id": "user-12345",
    "service_account": "prod-payment-api-sa",
    "ip_address": "10.0.1.50"
  },
  "resource": {
    "type": "secret",
    "name": "prod-payment-api-secret-v1.3.0",
    "namespace": "production"
  },
  "action": "read",
  "result": "success",
  "metadata": {
    "request_id": "req-abc123",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
  }
}
```

### 安全审计流程

```yaml
定期审计:
  月度:
    - [ ] 审查所有高严重性漏洞
    - [ ] 审查权限变更
    - [ ] 审查安全事件

  季度:
    - [ ] 全面安全扫描
    - [ ] 渗透测试
    - [ ] 合规性审计
    - [ ] 权限审查

  年度:
    - [ ] 第三方安全评估
    - [ ] 灾难恢复演练
    - [ ] 安全策略审查
```

## 事件响应

### 安全事件分类

| 级别 | 描述 | 响应时间 | 示例 |
|------|------|----------|------|
| **P0 - 严重** | 数据泄露、系统入侵 | < 15 分钟 | 数据库被入侵、密钥泄露 |
| **P1 - 高** | 重大漏洞、服务中断 | < 1 小时 | 高危漏洞利用、DDoS 攻击 |
| **P2 - 中** | 中等漏洞、可疑活动 | < 4 小时 | 中危漏洞、异常登录 |
| **P3 - 低** | 低风险问题 | < 1 天 | 低危漏洞、配置建议 |

### 事件响应流程

```yaml
1. 检测 (Detection):
   - 自动化告警
   - 人工发现
   - 第三方报告

2. 分类 (Triage):
   - 确定严重性级别
   - 评估影响范围
   - 指定响应团队

3. 遏制 (Containment):
   - 隔离受影响系统
   - 阻止进一步损害
   - 保留证据

4. 根除 (Eradication):
   - 删除恶意代码
   - 修复漏洞
   - 重置凭证

5. 恢复 (Recovery):
   - 恢复服务
   - 验证系统完整性
   - 增强监控

6. 总结 (Lessons Learned):
   - 事后分析
   - 改进措施
   - 更新 runbook
```

## 最佳实践

### ✅ DO

1. **默认安全**: 使用安全的默认配置
2. **纵深防御**: 多层安全控制
3. **最小权限**: 只授予必需的权限
4. **定期扫描**: 自动化安全扫描
5. **及时修复**: 快速修复漏洞
6. **审计日志**: 完整的审计记录
7. **加密传输**: 使用 TLS/mTLS
8. **密钥管理**: 使用密钥管理系统
9. **定期演练**: 事件响应演练

### ❌ DON'T

1. **硬编码密钥**: 不要在代码中硬编码密钥
2. **root 运行**: 不要以 root 运行容器
3. **过度权限**: 不要授予过多权限
4. **忽略告警**: 不要忽视安全告警
5. **推迟修复**: 不要拖延漏洞修复
6. **禁用安全**: 不要为了方便禁用安全功能
7. **共享密钥**: 不要跨环境共享密钥

## 工具和资源

### 安全扫描工具

- Semgrep - 静态代码分析
- Snyk - 依赖和容器扫描
- Trivy - 容器和文件系统扫描
- Kubesec - Kubernetes 配置扫描
- Falco - 运行时安全监控

### 模板和示例

- `templates/governance/k8s/deployment.template.yaml` - 安全 Deployment 模板
- `src/governance/dimensions/examples/security-review-checklist.yaml` - 安全审查清单

### 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [NSA Kubernetes Hardening Guide](https://media.defense.gov/2021/Aug/03/2002820425/-1/-1/1/CTR_KUBERNETES_HARDENING_GUIDANCE_1.1_20220315.PDF)
- [SOC 2 Framework](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [GDPR](https://gdpr-info.eu/)

## FAQ

### Q: 所有服务都需要数据分类标签吗？

A: 是的。数据分类标签是强制要求，用于确定安全和合规要求。

### Q: 如何处理遗留的不安全配置？

A: 为遗留系统创建例外，并制定迁移计划。新服务必须符合安全要求。

### Q: 密钥轮换频率是多少？

A: 至少每 90 天轮换一次。高风险密钥（如生产数据库密码）应更频繁。

### Q: 如何报告安全漏洞？

A: 发送邮件到 <security@example.com> 或使用内部安全报告系统。

### Q: CI/CD 安全扫描失败怎么办？

A: 高危和严重漏洞会阻止 PR 合并。必须修复或申请例外。

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义安全合规要求 | Governance Team |

---

**下一步**: 阅读 [10-cross-team-governance.md](./10-cross-team-governance.md) 了解跨团队治理协作。
