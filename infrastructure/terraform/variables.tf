# T-Developer Infrastructure Variables
# 변수 설정: 환경별로 다른 값을 사용할 수 있게 합니다

variable "environment" {
  description = "배포 환경 (development, staging, production)"
  type        = string
  default     = "development"
}

variable "project_name" {
  description = "프로젝트 이름"
  type        = string
  default     = "t-developer"
}

variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "기존 VPC ID (기본값: 기본 VPC 사용)"
  type        = string
  default     = "vpc-021655951c69fab62"
}

variable "subnet_ids" {
  description = "서브넷 ID 목록"
  type        = list(string)
  default     = [
    "subnet-08f9b59af0539c3e5",  # us-east-1c
    "subnet-0307ae6aaa9f8ffde"   # us-east-1f
  ]
}

variable "allowed_cidr_blocks" {
  description = "접근을 허용할 CIDR 블록 목록"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # 주의: 프로덕션에서는 더 제한적으로 설정
}

variable "enable_evolution_mode" {
  description = "진화 모드 활성화 여부"
  type        = bool
  default     = true
}

variable "max_agent_memory_kb" {
  description = "에이전트 최대 메모리 (KB)"
  type        = number
  default     = 6.5
}

variable "ai_autonomy_level" {
  description = "AI 자율성 수준 (0.0 ~ 1.0)"
  type        = number
  default     = 0.85
  
  validation {
    condition     = var.ai_autonomy_level >= 0 && var.ai_autonomy_level <= 1
    error_message = "AI 자율성 수준은 0.0과 1.0 사이여야 합니다."
  }
}

variable "tags" {
  description = "모든 리소스에 적용할 공통 태그"
  type        = map(string)
  default = {
    Project     = "T-Developer"
    Environment = "development" 
    ManagedBy   = "Terraform"
    Purpose     = "AI-Autonomous-Evolution"
  }
}