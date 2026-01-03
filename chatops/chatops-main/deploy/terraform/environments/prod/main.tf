# ChatOps Production Environment

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  backend "s3" {
    bucket         = "chatops-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "chatops-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "prod"
      Project     = "chatops"
      ManagedBy   = "terraform"
    }
  }
}

locals {
  environment = "prod"
  project     = "chatops"
}

# VPC
module "vpc" {
  source = "../../modules/vpc"

  environment = local.environment
  project     = local.project

  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  private_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnet_cidrs   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnet_cidrs = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false  # HA for prod
  enable_vpc_flow_logs = true

  tags = var.tags
}

# EKS
module "eks" {
  source = "../../modules/eks"

  environment = local.environment
  project     = local.project

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids

  cluster_version = "1.29"

  cluster_endpoint_public_access       = true
  cluster_endpoint_private_access      = true
  cluster_endpoint_public_access_cidrs = var.allowed_cidr_blocks

  node_groups = {
    system = {
      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"
      min_size       = 2
      max_size       = 4
      desired_size   = 2
      disk_size      = 100
      labels         = { "node-type" = "system" }
      taints         = []
    }
    application = {
      instance_types = ["t3.xlarge", "m5.xlarge"]
      capacity_type  = "ON_DEMAND"
      min_size       = 3
      max_size       = 20
      desired_size   = 3
      disk_size      = 100
      labels         = { "node-type" = "application" }
      taints         = []
    }
    spot = {
      instance_types = ["t3.xlarge", "m5.xlarge", "m5.2xlarge"]
      capacity_type  = "SPOT"
      min_size       = 0
      max_size       = 10
      desired_size   = 0
      disk_size      = 100
      labels         = { "node-type" = "spot" }
      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  enable_cluster_autoscaler          = true
  enable_aws_load_balancer_controller = true
  enable_external_dns                = true
  enable_ebs_csi_driver              = true

  tags = var.tags
}

# RDS
module "rds" {
  source = "../../modules/rds"

  environment = local.environment
  project     = local.project

  vpc_id                     = module.vpc.vpc_id
  db_subnet_group_name       = module.vpc.database_subnet_group_name
  allowed_security_group_ids = [module.eks.node_security_group_id]

  engine_version = "15"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 500

  database_name   = "chatops"
  master_username = "chatops_admin"
  master_password = var.rds_master_password

  backup_retention_period = 30
  multi_az                = true
  monitoring_interval     = 60

  performance_insights_enabled = true
  create_read_replica          = true
  replica_instance_class       = "db.r6g.large"

  tags = var.tags
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  value     = module.rds.db_instance_endpoint
  sensitive = true
}

output "rds_replica_endpoint" {
  value     = module.rds.db_replica_endpoint
  sensitive = true
}

output "kubeconfig_command" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
