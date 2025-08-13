# T-Developer Evolution System - Main Configuration
# AWS 인프라 구성 메인 파일

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  # Terraform State 백엔드 설정 (S3 + DynamoDB)
  # 실제 운영시에는 주석 해제하고 사용
  /*
  backend "s3" {
    bucket         = "t-developer-terraform-state"
    key            = "evolution/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "t-developer-terraform-locks"
  }
  */
}

# AWS Provider 설정
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = var.tags
  }
}

# Random Provider 설정 (고유 식별자 생성용)
provider "random" {}

# ===== Random ID for Unique Resource Names =====
resource "random_id" "deployment" {
  byte_length = 4
}

locals {
  deployment_id = random_id.deployment.hex
  common_name   = "${var.project_name}-${var.environment}-${local.deployment_id}"
}

# ===== S3 Buckets for T-Developer Data =====

# Evolution 체크포인트 및 상태 저장용 S3 버킷
resource "aws_s3_bucket" "evolution_storage" {
  bucket = "${var.project_name}-evolution-${var.environment}-${local.deployment_id}"

  tags = merge(var.tags, {
    Name = "T-Developer Evolution Storage"
    Type = "EvolutionData"
  })
}

# Evolution 버킷 버전 관리 활성화
resource "aws_s3_bucket_versioning" "evolution_versioning" {
  bucket = aws_s3_bucket.evolution_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Evolution 버킷 암호화 설정
resource "aws_s3_bucket_server_side_encryption_configuration" "evolution_encryption" {
  bucket = aws_s3_bucket.evolution_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Evolution 버킷 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "evolution_pab" {
  bucket = aws_s3_bucket.evolution_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 에이전트 코드 및 아티팩트 저장용 S3 버킷
resource "aws_s3_bucket" "agents_storage" {
  bucket = "${var.project_name}-agents-${var.environment}-${local.deployment_id}"

  tags = merge(var.tags, {
    Name = "T-Developer Agents Storage"
    Type = "AgentArtifacts"
  })
}

# Agents 버킷 버전 관리
resource "aws_s3_bucket_versioning" "agents_versioning" {
  bucket = aws_s3_bucket.agents_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Agents 버킷 암호화
resource "aws_s3_bucket_server_side_encryption_configuration" "agents_encryption" {
  bucket = aws_s3_bucket.agents_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Agents 버킷 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "agents_pab" {
  bucket = aws_s3_bucket.agents_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ===== CloudWatch Log Groups =====

# Evolution Engine 로그 그룹
resource "aws_cloudwatch_log_group" "evolution_logs" {
  name              = "/aws/t-developer/evolution/${var.environment}"
  retention_in_days = 30

  tags = merge(var.tags, {
    Name = "T-Developer Evolution Logs"
    Type = "Logging"
  })
}

# Safety System 로그 그룹
resource "aws_cloudwatch_log_group" "safety_logs" {
  name              = "/aws/t-developer/safety/${var.environment}"
  retention_in_days = 90  # 안전 로그는 더 오래 보관

  tags = merge(var.tags, {
    Name = "T-Developer Safety Logs"
    Type = "SafetyLogging"
    CriticalityLevel = "High"
  })
}

# Agent Registry 로그 그룹
resource "aws_cloudwatch_log_group" "registry_logs" {
  name              = "/aws/t-developer/registry/${var.environment}"
  retention_in_days = 30

  tags = merge(var.tags, {
    Name = "T-Developer Registry Logs"
    Type = "RegistryLogging"
  })
}

# ===== SNS Topics for Alerts =====

# Evolution Safety 알림 토픽
resource "aws_sns_topic" "safety_alerts" {
  name = "${var.project_name}-safety-alerts-${var.environment}"

  tags = merge(var.tags, {
    Name = "T-Developer Safety Alerts"
    Type = "SafetyNotifications"
  })
}

# Emergency Stop 알림 토픽
resource "aws_sns_topic" "emergency_alerts" {
  name = "${var.project_name}-emergency-alerts-${var.environment}"

  tags = merge(var.tags, {
    Name = "T-Developer Emergency Alerts"
    Type = "EmergencyNotifications"
    CriticalityLevel = "Critical"
  })
}

# ===== DynamoDB Tables =====

# Evolution 상태 관리 테이블
resource "aws_dynamodb_table" "evolution_state" {
  name           = "${var.project_name}-evolution-state-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "evolution_id"
  range_key      = "generation"

  attribute {
    name = "evolution_id"
    type = "S"
  }

  attribute {
    name = "generation"
    type = "N"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # 최근 상태에 대한 GSI
  global_secondary_index {
    name            = "timestamp-index"
    hash_key        = "evolution_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # 포인트 인 타임 복구 활성화
  point_in_time_recovery {
    enabled = true
  }

  tags = merge(var.tags, {
    Name = "T-Developer Evolution State"
    Type = "EvolutionData"
  })
}

# ===== Parameter Store 설정값 =====

# Evolution Engine 설정
resource "aws_ssm_parameter" "evolution_config" {
  name  = "/${var.project_name}/evolution/config"
  type  = "String"
  
  value = jsonencode({
    ai_autonomy_level         = var.ai_autonomy_level
    max_agent_memory_kb       = var.max_agent_memory_kb
    evolution_mode_enabled    = var.enable_evolution_mode
    safety_threshold          = 0.95
    checkpoint_interval       = 10
    max_generations          = 100
    population_size          = 50
  })

  description = "T-Developer Evolution Engine 설정"
  
  tags = merge(var.tags, {
    Name = "T-Developer Evolution Config"
    Type = "Configuration"
  })
}

# AWS 리소스 정보
resource "aws_ssm_parameter" "aws_resources" {
  name = "/${var.project_name}/aws/resources"
  type = "String"
  
  value = jsonencode({
    vpc_id                    = data.aws_vpc.existing.id
    subnet_ids                = var.subnet_ids
    evolution_bucket          = aws_s3_bucket.evolution_storage.id
    agents_bucket            = aws_s3_bucket.agents_storage.id
    evolution_role_arn       = aws_iam_role.t_developer_evolution_role.arn
    safety_sns_topic         = aws_sns_topic.safety_alerts.arn
    emergency_sns_topic      = aws_sns_topic.emergency_alerts.arn
    evolution_state_table    = aws_dynamodb_table.evolution_state.name
  })

  description = "T-Developer AWS 리소스 정보"
  
  tags = merge(var.tags, {
    Name = "T-Developer AWS Resources"
    Type = "ResourceInfo"
  })
}

# ===== 메인 출력값 =====
output "deployment_info" {
  description = "T-Developer 배포 정보"
  value = {
    deployment_id             = local.deployment_id
    environment              = var.environment
    aws_region               = var.aws_region
    vpc_id                   = data.aws_vpc.existing.id
    evolution_bucket         = aws_s3_bucket.evolution_storage.id
    agents_bucket           = aws_s3_bucket.agents_storage.id
    evolution_role_arn      = aws_iam_role.t_developer_evolution_role.arn
    safety_alerts_topic     = aws_sns_topic.safety_alerts.arn
    emergency_alerts_topic  = aws_sns_topic.emergency_alerts.arn
    evolution_state_table   = aws_dynamodb_table.evolution_state.name
  }
}

output "security_groups" {
  description = "T-Developer 보안 그룹 정보"
  value = {
    evolution_sg  = aws_security_group.t_developer_evolution.id
    agents_sg     = aws_security_group.t_developer_agents.id
    database_sg   = aws_security_group.t_developer_database.id
    safety_sg     = aws_security_group.t_developer_safety.id
    monitoring_sg = aws_security_group.t_developer_monitoring.id
    emergency_sg  = aws_security_group.t_developer_emergency.id
  }
}

output "next_steps" {
  description = "다음 단계 안내"
  value = <<-EOT
  🎉 T-Developer AWS 인프라가 성공적으로 배포되었습니다!
  
  다음 단계:
  1. Bedrock AgentCore 활성화
  2. Evolution Engine 배포
  3. Safety System 설정
  4. Agent Registry 초기화
  
  리소스 정보:
  - Evolution Role: ${aws_iam_role.t_developer_evolution_role.name}
  - S3 Buckets: ${aws_s3_bucket.evolution_storage.id}, ${aws_s3_bucket.agents_storage.id}
  - DynamoDB: ${aws_dynamodb_table.evolution_state.name}
  EOT
}