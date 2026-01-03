# ChatOps Terraform Infrastructure

Enterprise-grade AWS infrastructure for ChatOps platform using Terraform.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Account                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                        VPC                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│  │
│  │  │ Public      │  │ Private     │  │ Database            ││  │
│  │  │ Subnets     │  │ Subnets     │  │ Subnets             ││  │
│  │  │ (NAT/ALB)   │  │ (EKS Nodes) │  │ (RDS)               ││  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘│  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    EKS Cluster                       │  │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │  │  │
│  │  │  │ System  │  │ App     │  │ Spot    │             │  │  │
│  │  │  │ Nodes   │  │ Nodes   │  │ Nodes   │             │  │  │
│  │  │  └─────────┘  └─────────┘  └─────────┘             │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│  │
│  │  │ RDS         │  │ ElastiCache │  │ S3 Buckets          ││  │
│  │  │ PostgreSQL  │  │ Redis       │  │ (artifacts/logs)    ││  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘│  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
deploy/terraform/
├── modules/
│   ├── vpc/           # VPC, subnets, NAT, route tables
│   ├── eks/           # EKS cluster, node groups, IRSA
│   ├── rds/           # RDS PostgreSQL with encryption
│   ├── iam/           # IAM roles, policies, OIDC
│   └── monitoring/    # CloudWatch, alarms, dashboards
├── environments/
│   ├── dev/           # Development environment
│   ├── staging/       # Staging environment
│   └── prod/          # Production environment
└── scripts/           # Helper scripts
```

## Quick Start

```bash
# Initialize
cd deploy/terraform/environments/dev
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

## Naming Convention

All resources follow the pattern:
```
{env}-{project}-{component}-{resource}
```

Example: `prod-chatops-eks-cluster`

## Security Features

- ✅ VPC with private subnets
- ✅ Encryption at rest (RDS, EBS, S3)
- ✅ Encryption in transit (TLS)
- ✅ IRSA for pod-level IAM
- ✅ Security groups with least privilege
- ✅ CloudTrail logging
- ✅ VPC Flow Logs
