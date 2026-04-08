---
name: terraform-iac
description: Terraform infrastructure as code with modules, state management, AWS/GCP/Azure providers, workspaces, and CI/CD pipelines.
---

# Terraform IaC

## Overview

Terraform is the industry-standard IaC tool for provisioning cloud infrastructure across AWS, GCP, Azure, and 300+ providers. It uses declarative HCL configuration with plan/apply workflow.

## Project Structure

```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tf          # Provider/backend config
├── locals.tf
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   └── database/
└── environments/
    ├── dev/
    │   ├── main.tf
    │   └── terraform.tfvars
    └── prod/
        ├── main.tf
        └── terraform.tfvars
```

## Provider & Backend Configuration

```hcl
# terraform.tf
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Remote state in S3
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "infra/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    }
  }
}

# Multi-region provider alias
provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}
```

## Variables & Locals

```hcl
# variables.tf
variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  type    = string
  default = "myapp"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "instance_types" {
  type = map(string)
  default = {
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.medium"
  }
}

# locals.tf
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  azs = slice(data.aws_availability_zones.available.names, 0, 3)

  public_subnet_cidrs  = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnet_cidrs = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 8, i + 10)]

  common_tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
```

## Reusable Modules

```hcl
# modules/networking/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "${var.name_prefix}-vpc" }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "${var.name_prefix}-public-${count.index + 1}", Tier = "public" }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = { Name = "${var.name_prefix}-private-${count.index + 1}", Tier = "private" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.name_prefix}-igw" }
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = { Name = "${var.name_prefix}-nat-${count.index + 1}" }
}

# modules/networking/outputs.tf
output "vpc_id"              { value = aws_vpc.main.id }
output "public_subnet_ids"   { value = aws_subnet.public[*].id }
output "private_subnet_ids"  { value = aws_subnet.private[*].id }
```

## ECS + RDS + ElastiCache Example

```hcl
# main.tf - Compose modules
module "networking" {
  source = "./modules/networking"

  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = local.public_subnet_cidrs
  private_subnet_cidrs = local.private_subnet_cidrs
  availability_zones   = local.azs
  enable_nat_gateway   = var.environment == "prod"
}

module "ecs_cluster" {
  source = "./modules/compute"

  name_prefix       = local.name_prefix
  vpc_id            = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  public_subnet_ids  = module.networking.public_subnet_ids

  container_image = "${module.ecr.repository_url}:${var.image_tag}"
  cpu             = var.environment == "prod" ? 1024 : 256
  memory          = var.environment == "prod" ? 2048 : 512
  desired_count   = var.environment == "prod" ? 3 : 1

  environment_variables = {
    DATABASE_URL = "postgresql://${module.rds.username}:${random_password.db.result}@${module.rds.endpoint}/${var.db_name}"
    REDIS_URL    = "redis://${module.elasticache.primary_endpoint}:6379"
  }
}

resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-db"

  engine         = "postgres"
  engine_version = "16.1"
  instance_class = var.environment == "prod" ? "db.t3.medium" : "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100      # Auto-scaling
  storage_encrypted     = true

  db_name  = var.db_name
  username = "admin"
  password = random_password.db.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = var.environment == "prod" ? 7 : 1
  deletion_protection     = var.environment == "prod"
  skip_final_snapshot     = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${local.name_prefix}-final" : null

  tags = local.common_tags
}

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${local.name_prefix}/db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db.result
}
```

## Workspaces for Environments

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Use workspace in config
locals {
  instance_type = {
    default = "t3.micro"
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.large"
  }[terraform.workspace]
}
```

## CI/CD with GitHub Actions

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  push:
    branches: [main]
    paths: ["infra/**"]
  pull_request:
    paths: ["infra/**"]

env:
  TF_VERSION: "1.6.0"
  AWS_REGION: "us-east-1"

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init
        working-directory: infra/

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        working-directory: infra/

      - name: Terraform Validate
        run: terraform validate
        working-directory: infra/

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        working-directory: infra/
        env:
          TF_VAR_environment: ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}

      - name: Post plan to PR
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const output = `#### Terraform Plan 📋
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\``;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

  apply:
    needs: plan
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init && terraform apply -auto-approve
        working-directory: infra/
```

## Key Patterns

- **Remote state** with S3 + DynamoDB locking prevents concurrent modifications
- **`-auto-approve` only in CI** — always review plan output in PRs
- **OIDC for AWS auth** — no long-lived access keys in CI secrets
- **`for_each` over `count`** when resources have meaningful identifiers
- **`lifecycle { prevent_destroy = true }`** on databases and critical resources
- **`terraform.tfvars`** per environment, never commit secrets — use SSM/Secrets Manager
- **Module versioning**: pin to specific Git tags or Terraform Registry versions

## Models to Use

- **claude-opus-4-5**: Multi-cloud architecture, complex module design, security hardening
- **claude-sonnet-4-5**: Standard AWS/GCP resource provisioning, CI/CD pipelines
- **claude-haiku-3-5**: Simple resource additions, variable declarations, output definitions
