# Kubernetes Baseline Resources / Kubernetes 基線資源

## 📋 Overview / 概覽

This directory contains the foundational Kubernetes resources extracted from the 6 baseline YAML files. These resources establish the constitutional-level (L-A) governance, security, and operational standards for the entire cluster.

本目錄包含從 6 個基線 YAML 檔案中提取的基礎 Kubernetes 資源。這些資源為整個集群建立憲法級別 (L-A) 的治理、安全和營運標準。

## 📦 Baseline Components / 基線組件

### 1. Namespace Governance (baseline-01)
- Namespace naming conventions
- Mandatory labels validation
- Lifecycle state machine
- Capability registry

### 2. Security & RBAC (baseline-02)
- Zero Trust principles
- 5-tier RBAC role matrix
- Encryption standards (AES-256-GCM, mTLS, post-quantum)
- Audit policy

### 3. Resource Management (baseline-03)
- 4 tenant tiers (enterprise, business, startup, development)
- VPA + HPA autoscaling
- Cost allocation model
- Quota enforcement

### 4. Network Policy (baseline-04)
- Microsegmentation (4 zones)
- Istio service mesh (mTLS STRICT)
- Ingress/egress control
- Network observability

### 5. Compliance Attestation (baseline-05)
- Policy-as-Code (OPA, Kyverno, Conftest)
- Attestation providers (Cosign, in-toto, SLSA)
- Drift detection
- Evidence collection

### 6. Quantum Orchestration (baseline-06)
- Quantum circuit library (QAOA, VQE, QNN, QSVM)
- Quantum resource pool (IBM, AWS Braket)
- Hybrid workflow orchestration

## 🚀 Quick Start

```bash
# Deploy in order
kubectl apply -f baseline-01-namespace-governance.yaml
kubectl apply -f baseline-02-security-rbac.yaml
kubectl apply -f baseline-03-resource-management.yaml
kubectl apply -f baseline-04-network-policy.yaml
kubectl apply -f baseline-05-compliance-attestation.yaml
kubectl apply -f baseline-06-quantum-orchestration.yaml  # optional
```

## 📚 Documentation

See [KUBERNETES_BASELINE_GUIDE.md](../../../docs/refactor_playbooks/03_refactor/meta/KUBERNETES_BASELINE_GUIDE.md) for detailed deployment guide.

**Version:** v1.0.0  
**Maintainers:** Platform Engineering Team
