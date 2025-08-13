# T-Developer VPC and Networking Configuration
# 기존 VPC를 활용하되 T-Developer 전용 보안 구성을 추가합니다

# ===== 기존 VPC 데이터 소스 =====
data "aws_vpc" "existing" {
  id = var.vpc_id
}

data "aws_subnets" "existing" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

data "aws_subnet" "selected" {
  for_each = toset(var.subnet_ids)
  id       = each.value
}

# ===== T-Developer Evolution Engine 보안 그룹 =====
resource "aws_security_group" "t_developer_evolution" {
  name_prefix = "${var.project_name}-evolution-"
  vpc_id      = data.aws_vpc.existing.id
  description = "T-Developer Evolution Engine Security Group"

  # Inbound Rules (인바운드 규칙)
  
  # HTTP/HTTPS 접근 (Evolution Dashboard)
  ingress {
    description = "HTTP access for Evolution Dashboard"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  ingress {
    description = "HTTPS access for Evolution Dashboard"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Evolution API 포트
  ingress {
    description = "Evolution Engine API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]  # VPC 내부에서만 접근
  }

  # Agent Communication 포트
  ingress {
    description = "Agent Communication"
    from_port   = 8001
    to_port     = 8010
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]  # VPC 내부에서만 접근
  }

  # SSH 접근 (관리용 - 제한적)
  ingress {
    description = "SSH access (restricted)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["172.31.0.0/16"]  # VPC 내부에서만 SSH 접근
  }

  # Outbound Rules (아웃바운드 규칙)
  
  # 모든 아웃바운드 트래픽 허용 (AWS 서비스 접근용)
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-evolution-sg"
    Type = "EvolutionEngine"
  })
}

# ===== T-Developer Agent Runtime 보안 그룹 =====
resource "aws_security_group" "t_developer_agents" {
  name_prefix = "${var.project_name}-agents-"
  vpc_id      = data.aws_vpc.existing.id
  description = "T-Developer Agents Runtime Security Group"

  # Inbound Rules
  
  # Agent API 포트 (Evolution Engine에서 접근)
  ingress {
    description     = "Agent API from Evolution Engine"
    from_port       = 9000
    to_port         = 9099
    protocol        = "tcp"
    security_groups = [aws_security_group.t_developer_evolution.id]
  }

  # Agent 간 통신 포트
  ingress {
    description = "Inter-agent communication"
    from_port   = 9100
    to_port     = 9199
    protocol    = "tcp"
    self        = true  # 같은 보안 그룹 내에서만 접근
  }

  # Outbound Rules
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-agents-sg"
    Type = "AgentRuntime"
  })
}

# ===== T-Developer Database 보안 그룹 =====
resource "aws_security_group" "t_developer_database" {
  name_prefix = "${var.project_name}-database-"
  vpc_id      = data.aws_vpc.existing.id
  description = "T-Developer Database Security Group (Registry, Metrics)"

  # Inbound Rules
  
  # PostgreSQL/MySQL (Agent Registry용)
  ingress {
    description     = "Database access from Evolution Engine"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [
      aws_security_group.t_developer_evolution.id,
      aws_security_group.t_developer_agents.id
    ]
  }

  # Redis (캐싱용)
  ingress {
    description     = "Redis access"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [
      aws_security_group.t_developer_evolution.id,
      aws_security_group.t_developer_agents.id
    ]
  }

  # Outbound Rules
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-database-sg"
    Type = "Database"
  })
}

# ===== Evolution Safety 전용 보안 그룹 =====
resource "aws_security_group" "t_developer_safety" {
  name_prefix = "${var.project_name}-safety-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Evolution Safety Monitoring and Quarantine System"

  # Inbound Rules - 매우 제한적
  
  # Safety API (Evolution Engine에서만 접근)
  ingress {
    description     = "Safety API access"
    from_port       = 8888
    to_port         = 8888
    protocol        = "tcp"
    security_groups = [aws_security_group.t_developer_evolution.id]
  }

  # Emergency Stop 포트
  ingress {
    description     = "Emergency Stop Interface"
    from_port       = 9999
    to_port         = 9999
    protocol        = "tcp"
    security_groups = [aws_security_group.t_developer_evolution.id]
  }

  # Outbound Rules - SNS, CloudWatch 접근용
  egress {
    description = "AWS Services only"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-safety-sg"
    Type = "EvolutionSafety"
    CriticalityLevel = "High"
  })
}

# ===== 출력값 =====
output "vpc_id" {
  description = "VPC ID"
  value       = data.aws_vpc.existing.id
}

output "vpc_cidr_block" {
  description = "VPC CIDR Block"
  value       = data.aws_vpc.existing.cidr_block
}

output "subnet_ids" {
  description = "Selected Subnet IDs"
  value       = var.subnet_ids
}

output "security_group_evolution" {
  description = "T-Developer Evolution Engine Security Group ID"
  value       = aws_security_group.t_developer_evolution.id
}

output "security_group_agents" {
  description = "T-Developer Agents Security Group ID"
  value       = aws_security_group.t_developer_agents.id
}

output "security_group_database" {
  description = "T-Developer Database Security Group ID"
  value       = aws_security_group.t_developer_database.id
}

output "security_group_safety" {
  description = "T-Developer Safety Security Group ID"
  value       = aws_security_group.t_developer_safety.id
}