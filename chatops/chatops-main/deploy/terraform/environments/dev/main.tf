# ChatOps Development Environment

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
    key            = "dev/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "chatops-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "dev"
      Project     = "chatops"
      ManagedBy   = "terraform"
    }
  }
}

locals {
  environment = "dev"
  project     = "chatops"
}

# VPC
module "vpc" {
  source = "../../modules/vpc"

  environment = local.environment
  project     = local.project

  vpc_cidr           = "10.10.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b"]

  private_subnet_cidrs  = ["10.10.1.0/24", "10.10.2.0/24"]
  public_subnet_cidrs   = ["10.10.101.0/24", "10.10.102.0/24"]
  database_subnet_cidrs = ["10.10.201.0/24", "10.10.202.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true  # Cost saving for dev
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

  node_groups = {
    system = {
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
      min_size       = 1
      max_size       = 2
      desired_size   = 1
      disk_size      = 50
      labels         = { "node-type" = "system" }
      taints         = []
    }
    application = {
      instance_types = ["t3.large"]
      capacity_type  = "SPOT"  # Cost saving for dev
      min_size       = 1
      max_size       = 3
      desired_size   = 1
      disk_size      = 50
      labels         = { "node-type" = "application" }
      taints         = []
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
  instance_class = "db.t3.micro"  # Smallest for dev

  allocated_storage     = 20
  max_allocated_storage = 50

  database_name   = "chatops_dev"
  master_username = "chatops_admin"
  master_password = var.rds_master_password

  backup_retention_period = 1  # Minimal for dev
  multi_az                = false
  monitoring_interval     = 0  # Disable for dev

  performance_insights_enabled = false
  create_read_replica          = false

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

output "kubeconfig_command" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
