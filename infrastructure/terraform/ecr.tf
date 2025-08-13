# T-Developer Evolution System - ECR Repositories

# ECR Repository for Backend
resource "aws_ecr_repository" "t_developer_backend" {
  name                 = "t-developer-backend-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key        = aws_kms_key.evolution_kms.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-backend-${var.environment}"
      Component   = "Backend"
      Purpose     = "Evolution System Container Images"
    }
  )
}

# ECR Repository for Evolution Agents
resource "aws_ecr_repository" "evolution_agents" {
  name                 = "t-developer-evolution-agents-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key        = aws_kms_key.agents_kms.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-evolution-agents-${var.environment}"
      Component   = "Evolution"
      Purpose     = "AI Agent Container Images"
      Constraint  = "6.5KB per agent"
    }
  )
}

# ECR Lifecycle Policy - 이미지 보관 정책
resource "aws_ecr_lifecycle_policy" "backend_lifecycle" {
  repository = aws_ecr_repository.t_developer_backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 production images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["prod"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep last 20 development images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["dev"]
          countType     = "imageCountMoreThan"
          countNumber   = 20
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 3
        description  = "Remove untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Lifecycle Policy for Evolution Agents
resource "aws_ecr_lifecycle_policy" "agents_lifecycle" {
  repository = aws_ecr_repository.evolution_agents.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep all evolution versions for audit"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["evolution-v"]
          countType     = "imageCountMoreThan"
          countNumber   = 100
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep successful evolution generations"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["gen-"]
          countType     = "imageCountMoreThan"
          countNumber   = 50
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Repository Policy - 접근 권한
resource "aws_ecr_repository_policy" "backend_policy" {
  repository = aws_ecr_repository.t_developer_backend.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.evolution_role.arn,
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
          ]
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      },
      {
        Sid    = "AllowCodeBuild"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage"
        ]
      }
    ]
  })
}

# ECR Pull Through Cache for Docker Hub (비용 절감)
resource "aws_ecr_pull_through_cache_rule" "docker_hub" {
  ecr_repository_prefix = "docker-hub"
  upstream_registry_url = "registry-1.docker.io"
}

# Outputs
output "backend_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.t_developer_backend.repository_url
}

output "agents_repository_url" {
  description = "URL of the evolution agents ECR repository"
  value       = aws_ecr_repository.evolution_agents.repository_url
}

output "backend_repository_arn" {
  description = "ARN of the backend ECR repository"
  value       = aws_ecr_repository.t_developer_backend.arn
}

output "agents_repository_arn" {
  description = "ARN of the evolution agents ECR repository"
  value       = aws_ecr_repository.evolution_agents.arn
}
