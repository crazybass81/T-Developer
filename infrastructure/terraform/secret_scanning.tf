# T-Developer Secret Scanning Automation
# 비밀번호, API 키 등 민감한 정보 자동 탐지 및 보호 시스템

# ===== Lambda Function for Secret Scanning =====
# S3 객체와 코드에서 민감한 정보를 자동으로 탐지

# Lambda 실행 역할
resource "aws_iam_role" "secret_scanner_role" {
  name = "${var.project_name}-secret-scanner-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Lambda 실행 정책
resource "aws_iam_role_policy" "secret_scanner_policy" {
  name = "${var.project_name}-secret-scanner-policy"
  role = aws_iam_role.secret_scanner_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.evolution_storage.arn,
          "${aws_s3_bucket.evolution_storage.arn}/*",
          aws_s3_bucket.agents_storage.arn,
          "${aws_s3_bucket.agents_storage.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [
          aws_sns_topic.emergency_alerts.arn,
          aws_sns_topic.safety_alerts.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:UpdateSecret",
          "secretsmanager:TagResource"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "secretsmanager:Name" = "/${var.project_name}/discovered-secrets/*"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [
          aws_kms_key.secrets_manager.arn,
          aws_kms_key.evolution_safety.arn
        ]
      }
    ]
  })
}

# Lambda 로그 그룹
resource "aws_cloudwatch_log_group" "secret_scanner_logs" {
  name              = "/aws/lambda/${var.project_name}-secret-scanner"
  retention_in_days = var.environment == "production" ? 90 : 30
  kms_key_id        = aws_kms_key.evolution_safety.arn

  tags = merge(var.tags, {
    Name = "Secret Scanner Logs"
    Type = "SecurityLogging"
    Purpose = "SecretDetection"
  })
}

# Lambda function package (placeholder - 실제 코드는 별도 배포)
resource "aws_lambda_function" "secret_scanner" {
  function_name = "${var.project_name}-secret-scanner"
  role         = aws_iam_role.secret_scanner_role.arn
  handler      = "lambda_function.lambda_handler"
  runtime      = "python3.11"
  timeout      = 300  # 5분
  memory_size  = 512

  # 인라인 코드 (실제 환경에서는 ZIP 파일 사용)
  filename         = "secret_scanner.zip"
  source_code_hash = data.archive_file.secret_scanner_zip.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT_NAME = var.project_name
      EMERGENCY_SNS_TOPIC = aws_sns_topic.emergency_alerts.arn
      SAFETY_SNS_TOPIC = aws_sns_topic.safety_alerts.arn
      SECRETS_KMS_KEY = aws_kms_key.secrets_manager.arn
      DISCOVERY_PREFIX = "/${var.project_name}/discovered-secrets"
    }
  }

  depends_on = [
    aws_iam_role_policy.secret_scanner_policy,
    aws_cloudwatch_log_group.secret_scanner_logs
  ]

  tags = merge(var.tags, {
    Name = "Secret Scanner Function"
    Type = "SecurityAutomation"
    Purpose = "SecretDetection"
  })
}

# Lambda 코드 패키지 생성
data "archive_file" "secret_scanner_zip" {
  type        = "zip"
  output_path = "secret_scanner.zip"

  source {
    content = templatefile("${path.module}/lambda_code/secret_scanner.py", {
      project_name = var.project_name
      environment = var.environment
    })
    filename = "lambda_function.py"
  }
}

# ===== S3 이벤트 트리거 설정 =====
# S3에 새 파일이 업로드되면 자동으로 스캔

# Evolution Storage 버킷 알림 설정
resource "aws_s3_bucket_notification" "evolution_storage_notification" {
  bucket = aws_s3_bucket.evolution_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.secret_scanner.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix      = ""
    filter_suffix      = ""
  }

  depends_on = [aws_lambda_permission.allow_s3_evolution]
}

# Agents Storage 버킷 알림 설정
resource "aws_s3_bucket_notification" "agents_storage_notification" {
  bucket = aws_s3_bucket.agents_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.secret_scanner.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix      = ""
    filter_suffix      = ""
  }

  depends_on = [aws_lambda_permission.allow_s3_agents]
}

# Lambda S3 호출 권한 (Evolution Storage)
resource "aws_lambda_permission" "allow_s3_evolution" {
  statement_id  = "AllowExecutionFromS3Evolution"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_scanner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.evolution_storage.arn
}

# Lambda S3 호출 권한 (Agents Storage)
resource "aws_lambda_permission" "allow_s3_agents" {
  statement_id  = "AllowExecutionFromS3Agents"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_scanner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.agents_storage.arn
}

# ===== 정기적인 전체 스캔 =====
# CloudWatch Events로 정기적으로 전체 스캔 실행

resource "aws_cloudwatch_event_rule" "weekly_full_scan" {
  name        = "${var.project_name}-weekly-secret-scan"
  description = "Weekly full secret scan of all S3 buckets"

  # 매주 일요일 오전 2시 (UTC)
  schedule_expression = "cron(0 2 ? * SUN *)"

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "weekly_scan_target" {
  rule      = aws_cloudwatch_event_rule.weekly_full_scan.name
  target_id = "WeeklySecretScan"
  arn       = aws_lambda_function.secret_scanner.arn

  input = jsonencode({
    scan_type = "full"
    buckets = [
      aws_s3_bucket.evolution_storage.id,
      aws_s3_bucket.agents_storage.id
    ]
  })
}

resource "aws_lambda_permission" "allow_cloudwatch_weekly_scan" {
  statement_id  = "AllowExecutionFromCloudWatchWeekly"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_scanner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_full_scan.arn
}

# ===== 발견된 비밀 저장소 =====
# 발견된 비밀을 안전하게 저장하기 위한 전용 버킷

resource "aws_s3_bucket" "discovered_secrets" {
  bucket = "${var.project_name}-discovered-secrets-${var.environment}-${local.deployment_id}"

  tags = merge(var.tags, {
    Name = "Discovered Secrets Quarantine"
    Type = "SecurityQuarantine"
    Purpose = "SecretDetection"
    SecurityLevel = "Critical"
  })
}

# 발견된 비밀 버킷 암호화 (최고 보안 키 사용)
resource "aws_s3_bucket_server_side_encryption_configuration" "discovered_secrets_encryption" {
  bucket = aws_s3_bucket.discovered_secrets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evolution_safety.arn
    }
    bucket_key_enabled = true
  }
}

# 발견된 비밀 버킷 완전 차단
resource "aws_s3_bucket_public_access_block" "discovered_secrets_pab" {
  bucket = aws_s3_bucket.discovered_secrets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 발견된 비밀 버킷 정책 (극도로 제한적)
resource "aws_s3_bucket_policy" "discovered_secrets_policy" {
  bucket = aws_s3_bucket.discovered_secrets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyAllExceptSecretScanner"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.discovered_secrets.arn,
          "${aws_s3_bucket.discovered_secrets.arn}/*"
        ]
        Condition = {
          StringNotEquals = {
            "aws:PrincipalArn" = [
              aws_iam_role.secret_scanner_role.arn,
              "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
            ]
          }
        }
      }
    ]
  })
}

# ===== 비밀 탐지 규칙 설정 =====
# Parameter Store에 탐지 규칙 저장

resource "aws_ssm_parameter" "secret_detection_rules" {
  name  = "/${var.project_name}/${var.environment}/security/secret-detection-rules"
  type  = "SecureString"
  key_id = aws_kms_key.evolution_safety.arn

  value = jsonencode({
    enabled_patterns = [
      "aws_access_key",
      "aws_secret_key",
      "api_key",
      "password",
      "token",
      "private_key",
      "certificate",
      "connection_string",
      "oauth",
      "webhook_url"
    ]

    regex_patterns = {
      # AWS Access Key
      aws_access_key = "AKIA[0-9A-Z]{16}"

      # AWS Secret Key
      aws_secret_key = "aws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]"

      # Generic API Keys
      api_key = "(api[_-]?key|apikey).{0,20}['\"][0-9a-zA-Z]{20,}['\"]"

      # Passwords
      password = "(password|pass|pwd).{0,20}['\"][^'\"\\s]{6,}['\"]"

      # Tokens
      token = "(token|auth[_-]?token).{0,20}['\"][0-9a-zA-Z]{20,}['\"]"

      # Private Keys
      private_key = "-----BEGIN [A-Z]+ PRIVATE KEY-----"

      # Database Connection Strings
      connection_string = "(connection[_-]?string|conn[_-]?str).{0,20}['\"][^'\"]+['\"]"

      # OAuth Secrets
      oauth = "(oauth|client[_-]?secret).{0,20}['\"][0-9a-zA-Z]{20,}['\"]"

      # Webhook URLs with secrets
      webhook_url = "https?://[^\\s]*webhook[^\\s]*[?&].*(?:token|key|secret)=[^\\s&]*"
    }

    file_extensions = [
      ".py", ".js", ".ts", ".java", ".go", ".rb", ".php",
      ".json", ".yaml", ".yml", ".xml", ".conf", ".cfg",
      ".env", ".properties", ".ini", ".toml"
    ]

    excluded_patterns = [
      "password.*placeholder",
      "password.*example",
      "password.*dummy",
      "key.*test",
      "token.*fake"
    ]

    severity_levels = {
      aws_access_key = "CRITICAL"
      aws_secret_key = "CRITICAL"
      private_key = "CRITICAL"
      api_key = "HIGH"
      token = "HIGH"
      password = "MEDIUM"
      connection_string = "HIGH"
      oauth = "HIGH"
      webhook_url = "MEDIUM"
    }
  })

  description = "T-Developer 비밀 탐지 규칙 및 패턴 정의"

  tags = merge(var.tags, {
    Name = "Secret Detection Rules"
    Type = "SecurityConfiguration"
    Purpose = "SecretDetection"
    SecurityLevel = "Critical"
  })
}

# ===== 탐지 메트릭 및 알림 =====
# CloudWatch 메트릭으로 탐지 상황 모니터링

resource "aws_cloudwatch_log_metric_filter" "critical_secrets_detected" {
  name           = "${var.project_name}-critical-secrets-detected"
  log_group_name = aws_cloudwatch_log_group.secret_scanner_logs.name
  pattern        = "[timestamp, request_id, \"CRITICAL_SECRET_DETECTED\", ...]"

  metric_transformation {
    name      = "CriticalSecretsDetected"
    namespace = "T-Developer/${title(var.environment)}/Security"
    value     = "1"

    # 추가 컨텍스트 추출
    default_value = "0"
  }
}

resource "aws_cloudwatch_log_metric_filter" "high_severity_secrets" {
  name           = "${var.project_name}-high-severity-secrets"
  log_group_name = aws_cloudwatch_log_group.secret_scanner_logs.name
  pattern        = "[timestamp, request_id, \"HIGH_SEVERITY_SECRET\", ...]"

  metric_transformation {
    name      = "HighSeveritySecretsDetected"
    namespace = "T-Developer/${title(var.environment)}/Security"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "scanner_errors" {
  name           = "${var.project_name}-secret-scanner-errors"
  log_group_name = aws_cloudwatch_log_group.secret_scanner_logs.name
  pattern        = "[timestamp, request_id, \"ERROR\", ...]"

  metric_transformation {
    name      = "SecretScannerErrors"
    namespace = "T-Developer/${title(var.environment)}/Security"
    value     = "1"
  }
}

# ===== 긴급 알림 =====
# 중요한 비밀 발견시 즉시 알림

resource "aws_cloudwatch_metric_alarm" "critical_secrets_alarm" {
  alarm_name          = "${var.project_name}-critical-secrets-detected"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "CriticalSecretsDetected"
  namespace           = "T-Developer/${title(var.environment)}/Security"
  period             = "60"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "중요한 비밀 정보가 탐지되었습니다"
  alarm_actions      = [aws_sns_topic.emergency_alerts.arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "high_severity_secrets_alarm" {
  alarm_name          = "${var.project_name}-high-severity-secrets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HighSeveritySecretsDetected"
  namespace           = "T-Developer/${title(var.environment)}/Security"
  period             = "300"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "높은 위험도의 비밀 정보가 탐지되었습니다"
  alarm_actions      = [aws_sns_topic.safety_alerts.arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "scanner_failure_alarm" {
  alarm_name          = "${var.project_name}-secret-scanner-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "SecretScannerErrors"
  namespace           = "T-Developer/${title(var.environment)}/Security"
  period             = "300"
  statistic          = "Sum"
  threshold          = "5"
  alarm_description  = "비밀 스캐너에 오류가 발생했습니다"
  alarm_actions      = [aws_sns_topic.safety_alerts.arn]

  tags = var.tags
}

# ===== 자동 수정 조치 =====
# Step Functions으로 자동 수정 워크플로우

resource "aws_iam_role" "secret_remediation_role" {
  name = "${var.project_name}-secret-remediation-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "secret_remediation_policy" {
  name = "${var.project_name}-secret-remediation-policy"
  role = aws_iam_role.secret_remediation_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          "${aws_s3_bucket.evolution_storage.arn}/*",
          "${aws_s3_bucket.agents_storage.arn}/*",
          "${aws_s3_bucket.discovered_secrets.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [
          aws_sns_topic.emergency_alerts.arn,
          aws_sns_topic.safety_alerts.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.secret_scanner.arn
      }
    ]
  })
}

# Step Functions 상태 머신 (자동 수정)
resource "aws_sfn_state_machine" "secret_remediation" {
  name     = "${var.project_name}-secret-remediation"
  role_arn = aws_iam_role.secret_remediation_role.arn

  definition = jsonencode({
    Comment = "T-Developer Secret Remediation Workflow"
    StartAt = "AssessSecretSeverity"
    States = {
      AssessSecretSeverity = {
        Type = "Choice"
        Choices = [
          {
            Variable = "$.severity"
            StringEquals = "CRITICAL"
            Next = "QuarantineImmediately"
          },
          {
            Variable = "$.severity"
            StringEquals = "HIGH"
            Next = "NotifyAndQuarantine"
          }
        ]
        Default = "LogAndNotify"
      }

      QuarantineImmediately = {
        Type = "Parallel"
        Branches = [
          {
            StartAt = "MoveToQuarantine"
            States = {
              MoveToQuarantine = {
                Type = "Task"
                Resource = aws_lambda_function.secret_scanner.arn
                Parameters = {
                  "action" = "quarantine"
                  "source_bucket.$" = "$.bucket"
                  "source_key.$" = "$.key"
                  "severity.$" = "$.severity"
                }
                End = true
              }
            }
          },
          {
            StartAt = "SendEmergencyAlert"
            States = {
              SendEmergencyAlert = {
                Type = "Task"
                Resource = "arn:aws:states:::sns:publish"
                Parameters = {
                  TopicArn = aws_sns_topic.emergency_alerts.arn
                  Message = "CRITICAL SECRET DETECTED AND QUARANTINED"
                  Subject = "🚨 Critical Security Alert - Secret Detected"
                }
                End = true
              }
            }
          }
        ]
        Next = "RemediationComplete"
      }

      NotifyAndQuarantine = {
        Type = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.safety_alerts.arn
          Message = "High severity secret detected - Review required"
          Subject = "⚠️ Security Alert - Secret Detected"
        }
        Next = "RemediationComplete"
      }

      LogAndNotify = {
        Type = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.safety_alerts.arn
          Message = "Medium severity secret detected - Logged for review"
          Subject = "📝 Security Log - Secret Detected"
        }
        Next = "RemediationComplete"
      }

      RemediationComplete = {
        Type = "Succeed"
      }
    }
  })

  tags = var.tags
}

# ===== 출력값 =====
output "secret_scanning_configuration" {
  description = "Secret scanning system configuration"
  value = {
    lambda_function_name = aws_lambda_function.secret_scanner.function_name
    lambda_function_arn = aws_lambda_function.secret_scanner.arn
    quarantine_bucket = aws_s3_bucket.discovered_secrets.id
    detection_rules_parameter = aws_ssm_parameter.secret_detection_rules.name
    remediation_workflow = aws_sfn_state_machine.secret_remediation.name
    monitoring_enabled = {
      critical_secrets = true
      high_severity_secrets = true
      scanner_errors = true
      automatic_remediation = true
    }
  }
}

output "secret_scanning_endpoints" {
  description = "비밀 스캐닝 시스템 관리 엔드포인트"
  value = {
    lambda_logs = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups/log-group/${replace(aws_cloudwatch_log_group.secret_scanner_logs.name, "/", "$252F")}"
    quarantine_bucket = "https://s3.console.aws.amazon.com/s3/buckets/${aws_s3_bucket.discovered_secrets.id}"
    remediation_workflow = "https://${var.aws_region}.console.aws.amazon.com/states/home?region=${var.aws_region}#/statemachines/view/${aws_sfn_state_machine.secret_remediation.arn}"
    detection_rules = "https://${var.aws_region}.console.aws.amazon.com/systems-manager/parameters/${replace(aws_ssm_parameter.secret_detection_rules.name, "/", "%2F")}/description"
  }
}
