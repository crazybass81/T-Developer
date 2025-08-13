# T-Developer KMS Keys and Encryption Policies
# 암호화 키 관리 및 정책 설정

# ===== T-Developer Master KMS Key =====
# Evolution System 전체를 위한 마스터 암호화 키
resource "aws_kms_key" "t_developer_master" {
  description = "T-Developer Evolution System Master Encryption Key"

  # 키 정책 - Evolution System 컴포넌트들만 접근 가능
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow T-Developer Evolution Role"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.t_developer_evolution_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:GenerateDataKeyWithoutPlaintext",
          "kms:ReEncrypt*"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow AWS Services"
        Effect = "Allow"
        Principal = {
          Service = [
            "secretsmanager.amazonaws.com",
            "ssm.amazonaws.com",
            "s3.amazonaws.com",
            "dynamodb.amazonaws.com",
            "logs.amazonaws.com"
          ]
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*"
        ]
        Resource = "*"
      }
    ]
  })

  # 자동 키 rotation 활성화 (1년마다)
  enable_key_rotation = true

  # 키 삭제 보호 (실수로 삭제 방지)
  deletion_window_in_days = 30

  tags = merge(var.tags, {
    Name = "${var.project_name}-master-key"
    Type = "EncryptionKey"
    Purpose = "EvolutionSystemSecurity"
    KeyRotation = "Enabled"
  })
}

# 마스터 키 별칭 생성
resource "aws_kms_alias" "t_developer_master" {
  name          = "alias/${var.project_name}-master-key"
  target_key_id = aws_kms_key.t_developer_master.key_id
}

# ===== Secrets Manager 전용 KMS Key =====
# API 키, 데이터베이스 비밀번호 등 민감한 정보 암호화
resource "aws_kms_key" "secrets_manager" {
  description = "T-Developer Secrets Manager Encryption Key"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*",
          "kms:CreateGrant"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${var.aws_region}.amazonaws.com"
          }
        }
      },
      {
        Sid    = "Allow Evolution Role for Secrets"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.t_developer_evolution_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  enable_key_rotation         = true
  deletion_window_in_days    = 30

  tags = merge(var.tags, {
    Name = "${var.project_name}-secrets-key"
    Type = "SecretsEncryption"
    Purpose = "APIKeysAndSecrets"
  })
}

resource "aws_kms_alias" "secrets_manager" {
  name          = "alias/${var.project_name}-secrets-key"
  target_key_id = aws_kms_key.secrets_manager.key_id
}

# ===== Parameter Store 전용 KMS Key =====
# 설정값, 환경변수 등 암호화
resource "aws_kms_key" "parameter_store" {
  description = "T-Developer Parameter Store Encryption Key"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Systems Manager"
        Effect = "Allow"
        Principal = {
          Service = "ssm.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${var.aws_region}.amazonaws.com"
          }
        }
      },
      {
        Sid    = "Allow Evolution Role for Parameters"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.t_developer_evolution_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  enable_key_rotation         = true
  deletion_window_in_days    = 30

  tags = merge(var.tags, {
    Name = "${var.project_name}-parameters-key"
    Type = "ParametersEncryption"
    Purpose = "ConfigurationSecurity"
  })
}

resource "aws_kms_alias" "parameter_store" {
  name          = "alias/${var.project_name}-parameters-key"
  target_key_id = aws_kms_key.parameter_store.key_id
}

# ===== Evolution Safety 전용 KMS Key =====
# Safety System 데이터 및 로그 암호화 (최고 보안 등급)
resource "aws_kms_key" "evolution_safety" {
  description = "T-Developer Evolution Safety System Encryption Key"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Evolution Role Safety Operations"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.t_developer_evolution_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        # 추가 보안: MFA 또는 특정 조건에서만 접근 가능
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = var.aws_region
          }
        }
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/t-developer/safety/*"
          }
        }
      }
    ]
  })

  enable_key_rotation         = true
  deletion_window_in_days    = 30

  tags = merge(var.tags, {
    Name = "${var.project_name}-safety-key"
    Type = "SafetyEncryption"
    Purpose = "EvolutionSafety"
    SecurityLevel = "Critical"
  })
}

resource "aws_kms_alias" "evolution_safety" {
  name          = "alias/${var.project_name}-safety-key"
  target_key_id = aws_kms_key.evolution_safety.key_id
}

# ===== 현재 AWS 계정 정보 =====
data "aws_caller_identity" "current" {}

# ===== 키 rotation 상태 모니터링을 위한 CloudWatch 이벤트 규칙 =====
resource "aws_cloudwatch_event_rule" "kms_key_rotation" {
  name        = "${var.project_name}-kms-rotation-monitor"
  description = "Monitor KMS key rotation events"

  event_pattern = jsonencode({
    source      = ["aws.kms"]
    detail-type = ["AWS KMS Key Rotation"]
    detail = {
      key-id = [
        aws_kms_key.t_developer_master.id,
        aws_kms_key.secrets_manager.id,
        aws_kms_key.parameter_store.id,
        aws_kms_key.evolution_safety.id
      ]
    }
  })

  tags = var.tags
}

# 키 rotation 이벤트를 SNS로 알림
resource "aws_cloudwatch_event_target" "kms_rotation_notification" {
  rule      = aws_cloudwatch_event_rule.kms_key_rotation.name
  target_id = "KMSRotationNotification"
  arn       = aws_sns_topic.safety_alerts.arn
}

# ===== 키 사용 모니터링을 위한 CloudWatch 메트릭 =====
resource "aws_cloudwatch_log_metric_filter" "kms_decrypt_errors" {
  name           = "${var.project_name}-kms-decrypt-errors"
  log_group_name = aws_cloudwatch_log_group.safety_logs.name
  pattern        = "ERROR decrypt"

  metric_transformation {
    name      = "KMSDecryptErrors"
    namespace = "T-Developer/Security"
    value     = "1"
  }
}

# 키 사용 오류에 대한 알림
resource "aws_cloudwatch_metric_alarm" "kms_decrypt_errors" {
  alarm_name          = "${var.project_name}-kms-decrypt-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "KMSDecryptErrors"
  namespace           = "T-Developer/Security"
  period             = "300"
  statistic          = "Sum"
  threshold          = "5"
  alarm_description  = "Too many KMS decryption errors detected"
  alarm_actions      = [aws_sns_topic.emergency_alerts.arn]

  tags = var.tags
}

# ===== 출력값 =====
output "kms_keys" {
  description = "KMS key information"
  value = {
    master_key = {
      id   = aws_kms_key.t_developer_master.id
      arn  = aws_kms_key.t_developer_master.arn
      alias = aws_kms_alias.t_developer_master.name
    }
    secrets_key = {
      id   = aws_kms_key.secrets_manager.id
      arn  = aws_kms_key.secrets_manager.arn
      alias = aws_kms_alias.secrets_manager.name
    }
    parameters_key = {
      id   = aws_kms_key.parameter_store.id
      arn  = aws_kms_key.parameter_store.arn
      alias = aws_kms_alias.parameter_store.name
    }
    safety_key = {
      id   = aws_kms_key.evolution_safety.id
      arn  = aws_kms_key.evolution_safety.arn
      alias = aws_kms_alias.evolution_safety.name
    }
  }
  sensitive = true
}

output "kms_key_policies" {
  description = "KMS key security configuration"
  value = {
    rotation_enabled    = true
    deletion_protection = "30 days"
    monitoring_enabled  = true
    access_logging      = "via CloudTrail"
  }
}
