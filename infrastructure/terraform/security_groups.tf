# T-Developer Security Groups - Detailed Configuration
# 세밀한 보안 제어를 위한 추가 보안 그룹 규칙

# ===== Network ACL for T-Developer Subnet =====
# 추가적인 네트워크 레벨 보안을 위한 Network ACL
resource "aws_network_acl" "t_developer_nacl" {
  vpc_id     = data.aws_vpc.existing.id
  subnet_ids = var.subnet_ids

  # Evolution Engine 트래픽 허용
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = data.aws_vpc.existing.cidr_block
    from_port  = 8000
    to_port    = 8010
  }

  # HTTPS 트래픽 허용 (Bedrock, AWS 서비스 접근)
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # HTTP 응답 트래픽 허용
  ingress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-network-acl"
    Type = "NetworkSecurity"
  })
}

# ===== WAF Web ACL for Evolution Dashboard =====
# Evolution Dashboard에 대한 웹 애플리케이션 방화벽
resource "aws_wafv2_web_acl" "t_developer_waf" {
  name  = "${var.project_name}-evolution-dashboard-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # IP 차단 규칙
  rule {
    name     = "BlockMaliciousIPs"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "BlockMaliciousIPs"
      sampled_requests_enabled    = true
    }
  }

  # SQL 인젝션 방지
  rule {
    name     = "SQLiProtection"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "SQLiProtection"
      sampled_requests_enabled    = true
    }
  }

  # Evolution API 접근 제한 (VPC 내부에서만)
  rule {
    name     = "RestrictEvolutionAPI"
    priority = 3

    action {
      block {}
    }

    statement {
      and_statement {
        statement {
          byte_match_statement {
            search_string = "/evolution/api"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "STARTS_WITH"
          }
        }

        statement {
          not_statement {
            statement {
              ip_set_reference_statement {
                arn = aws_wafv2_ip_set.vpc_ip_set.arn
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                 = "RestrictEvolutionAPI"
      sampled_requests_enabled    = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                 = "TDeveloperWAF"
    sampled_requests_enabled    = true
  }

  tags = var.tags
}

# WAF용 IP 세트 (VPC CIDR)
resource "aws_wafv2_ip_set" "vpc_ip_set" {
  name  = "${var.project_name}-vpc-ip-set"
  scope = "REGIONAL"

  ip_address_version = "IPV4"
  addresses          = [data.aws_vpc.existing.cidr_block]

  tags = var.tags
}

# ===== Security Group Rules - 세부 규칙 =====

# Note: HTTPS egress rules are already included in the main security group definition

# Agents 보안 그룹 - 추가 규칙
resource "aws_security_group_rule" "agents_registry_access" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.t_developer_database.id
  security_group_id        = aws_security_group.t_developer_agents.id
  description              = "Database access for Agent Registry"
}

# ===== CloudWatch Security Group =====
resource "aws_security_group" "t_developer_monitoring" {
  name_prefix = "${var.project_name}-monitoring-"
  vpc_id      = data.aws_vpc.existing.id
  description = "T-Developer Monitoring and Logging System"

  # CloudWatch Agent 포트
  ingress {
    description     = "CloudWatch Agent"
    from_port       = 25888
    to_port         = 25888
    protocol        = "tcp"
    security_groups = [
      aws_security_group.t_developer_evolution.id,
      aws_security_group.t_developer_agents.id
    ]
  }

  # Prometheus 메트릭 수집
  ingress {
    description = "Prometheus metrics"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]
  }

  # Grafana Dashboard
  ingress {
    description = "Grafana Dashboard"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-monitoring-sg"
    Type = "Monitoring"
  })
}

# ===== Evolution Emergency System Security Group =====
resource "aws_security_group" "t_developer_emergency" {
  name_prefix = "${var.project_name}-emergency-"
  vpc_id      = data.aws_vpc.existing.id
  description = "Emergency Response System (Evolution Stop, Rollback)"

  # 긴급 중지 API (매우 제한적 접근)
  ingress {
    description = "Emergency Stop API (Admin only)"
    from_port   = 9999
    to_port     = 9999
    protocol    = "tcp"
    cidr_blocks = ["172.31.0.0/20"]  # 관리자 서브넷에서만 접근
  }

  # SNS 알림용 HTTPS
  egress {
    description = "SNS notifications"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-emergency-sg"
    Type = "Emergency"
    CriticalityLevel = "Critical"
  })
}

# ===== 보안 그룹 연결 규칙 =====

# Evolution Engine과 Safety System 간 통신
resource "aws_security_group_rule" "evolution_to_safety" {
  type                     = "egress"
  from_port                = 8888
  to_port                  = 8888
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.t_developer_safety.id
  security_group_id        = aws_security_group.t_developer_evolution.id
  description              = "Evolution Engine to Safety System"
}

# Safety System에서 Emergency System 접근
resource "aws_security_group_rule" "safety_to_emergency" {
  type                     = "egress"
  from_port                = 9999
  to_port                  = 9999
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.t_developer_emergency.id
  security_group_id        = aws_security_group.t_developer_safety.id
  description              = "Safety System to Emergency Stop"
}

# ===== 출력값 =====
output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN for Evolution Dashboard"
  value       = aws_wafv2_web_acl.t_developer_waf.arn
}

output "security_group_monitoring" {
  description = "Monitoring Security Group ID"
  value       = aws_security_group.t_developer_monitoring.id
}

output "security_group_emergency" {
  description = "Emergency System Security Group ID"
  value       = aws_security_group.t_developer_emergency.id
}
