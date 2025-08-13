# SNS Topics and CloudWatch Alarms
# Day 5: Monitoring & Logging Infrastructure
# Generated: 2024-11-18

# ===================================
# SNS Topics
# ===================================

resource "aws_sns_topic" "evolution_alerts" {
  name              = "t-developer-evolution-alerts-${var.environment}"
  display_name      = "T-Developer Evolution System Alerts"
  kms_master_key_id = aws_kms_key.sns_encryption.id

  delivery_policy = jsonencode({
    "http" : {
      "defaultHealthyRetryPolicy" : {
        "minDelayTarget" : 20,
        "maxDelayTarget" : 20,
        "numRetries" : 3,
        "numMaxDelayRetries" : 0,
        "numNoDelayRetries" : 0,
        "numMinDelayRetries" : 0,
        "backoffFunction" : "linear"
      },
      "disableSubscriptionOverrides" : false
    }
  })

  tags = merge(
    var.common_tags,
    {
      Component = "SNS"
      Purpose   = "Alerts"
      Day       = "5"
    }
  )
}

resource "aws_sns_topic" "critical_alerts" {
  name              = "t-developer-critical-alerts-${var.environment}"
  display_name      = "T-Developer Critical Alerts"
  kms_master_key_id = aws_kms_key.sns_encryption.id

  tags = merge(
    var.common_tags,
    {
      Component = "SNS"
      Severity  = "Critical"
      Day       = "5"
    }
  )
}

resource "aws_sns_topic" "performance_alerts" {
  name              = "t-developer-performance-alerts-${var.environment}"
  display_name      = "T-Developer Performance Alerts"
  kms_master_key_id = aws_kms_key.sns_encryption.id

  tags = merge(
    var.common_tags,
    {
      Component = "SNS"
      Purpose   = "Performance"
      Day       = "5"
    }
  )
}

resource "aws_sns_topic" "safety_alerts" {
  name              = "t-developer-safety-alerts-${var.environment}"
  display_name      = "T-Developer Safety System Alerts"
  kms_master_key_id = aws_kms_key.sns_encryption.id

  tags = merge(
    var.common_tags,
    {
      Component = "SNS"
      Purpose   = "Safety"
      Critical  = "true"
      Day       = "5"
    }
  )
}

# ===================================
# SNS Topic Subscriptions
# ===================================

resource "aws_sns_topic_subscription" "evolution_email" {
  topic_arn = aws_sns_topic.evolution_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email

  depends_on = [aws_sns_topic.evolution_alerts]
}

resource "aws_sns_topic_subscription" "critical_sms" {
  count     = var.enable_sms_alerts ? 1 : 0
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "sms"
  endpoint  = var.alert_phone_number

  depends_on = [aws_sns_topic.critical_alerts]
}

resource "aws_sns_topic_subscription" "safety_lambda" {
  topic_arn = aws_sns_topic.safety_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.safety_response.arn

  depends_on = [aws_sns_topic.safety_alerts]
}

# ===================================
# CloudWatch Alarms - Evolution Engine
# ===================================

resource "aws_cloudwatch_metric_alarm" "evolution_error_rate" {
  alarm_name          = "evolution-high-error-rate-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "EvolutionErrors"
  namespace           = "T-Developer/Evolution"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors evolution engine error rate"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  tags = merge(
    var.common_tags,
    {
      Severity = "High"
      Day      = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "safety_violations" {
  alarm_name          = "evolution-safety-violations-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "SafetyViolations"
  namespace           = "T-Developer/Safety"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Critical: Safety violations detected"
  alarm_actions       = [
    aws_sns_topic.critical_alerts.arn,
    aws_sns_topic.safety_alerts.arn
  ]
  treat_missing_data = "notBreaching"

  tags = merge(
    var.common_tags,
    {
      Severity = "Critical"
      Day      = "5"
    }
  )
}

# ===================================
# CloudWatch Alarms - Agent Performance
# ===================================

resource "aws_cloudwatch_metric_alarm" "agent_size_violation" {
  alarm_name          = "agent-size-violation-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "AgentSizeViolations"
  namespace           = "T-Developer/Agents"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Agent size exceeds 6.5KB limit"
  alarm_actions       = [aws_sns_topic.performance_alerts.arn]

  tags = merge(
    var.common_tags,
    {
      Constraint = "SizeLimit"
      Day        = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "instantiation_time_violation" {
  alarm_name          = "instantiation-time-violation-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "InstantiationTime"
  namespace           = "T-Developer/Agents"
  period              = "300"
  statistic           = "Average"
  threshold           = "3"
  unit                = "Microseconds"
  alarm_description   = "Agent instantiation time exceeds 3μs target"
  alarm_actions       = [aws_sns_topic.performance_alerts.arn]

  tags = merge(
    var.common_tags,
    {
      Constraint = "SpeedLimit"
      Day        = "5"
    }
  )
}

# ===================================
# CloudWatch Alarms - Database
# ===================================

resource "aws_cloudwatch_metric_alarm" "rds_cpu_utilization" {
  alarm_name          = "rds-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  dimensions = {
    DBInstanceIdentifier = "t-developer-postgres-${var.environment}"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "RDS"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "rds_storage_space" {
  alarm_name          = "rds-low-storage-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10737418240" # 10GB in bytes
  alarm_description   = "RDS free storage space is low"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  dimensions = {
    DBInstanceIdentifier = "t-developer-postgres-${var.environment}"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "RDS"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "elasticache_cpu_utilization" {
  alarm_name          = "elasticache-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "ElastiCache CPU utilization is high"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  dimensions = {
    CacheClusterId = "t-developer-redis-${var.environment}"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "ElastiCache"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "elasticache_memory" {
  alarm_name          = "elasticache-high-memory-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "ElastiCache memory usage is high"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  dimensions = {
    CacheClusterId = "t-developer-redis-${var.environment}"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "ElastiCache"
      Day       = "5"
    }
  )
}

# ===================================
# CloudWatch Alarms - Lambda
# ===================================

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "lambda-high-error-rate-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Lambda function error rate is high"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  tags = merge(
    var.common_tags,
    {
      Component = "Lambda"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "lambda-throttles-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Lambda functions are being throttled"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  tags = merge(
    var.common_tags,
    {
      Component = "Lambda"
      Day       = "5"
    }
  )
}

# ===================================
# CloudWatch Alarms - Cost
# ===================================

resource "aws_cloudwatch_metric_alarm" "billing_alarm" {
  alarm_name          = "billing-threshold-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"
  statistic           = "Maximum"
  threshold           = var.billing_alert_threshold
  alarm_description   = "AWS charges exceed threshold"
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]

  dimensions = {
    Currency = "USD"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "Billing"
      Day       = "5"
    }
  )
}

# ===================================
# Composite Alarms
# ===================================

resource "aws_cloudwatch_composite_alarm" "system_critical" {
  alarm_name          = "system-critical-${var.environment}"
  alarm_description   = "Critical system-wide alarm"
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.critical_alerts.arn]

  alarm_rule = "ALARM(${aws_cloudwatch_metric_alarm.safety_violations.alarm_name}) OR (ALARM(${aws_cloudwatch_metric_alarm.evolution_error_rate.alarm_name}) AND ALARM(${aws_cloudwatch_metric_alarm.agent_size_violation.alarm_name}))"

  tags = merge(
    var.common_tags,
    {
      Severity = "Critical"
      Day      = "5"
    }
  )
}

# ===================================
# Safety Response Lambda
# ===================================

resource "aws_lambda_function" "safety_response" {
  filename         = "${path.module}/lambda/safety_response.zip"
  function_name    = "t-developer-safety-response-${var.environment}"
  role            = aws_iam_role.safety_response_lambda.arn
  handler         = "index.handler"
  source_code_hash = filebase64sha256("${path.module}/lambda/safety_response.zip")
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT     = var.environment
      EMERGENCY_STOP  = "true"
      ROLLBACK_ENABLED = "true"
    }
  }

  tags = merge(
    var.common_tags,
    {
      Component = "SafetyResponse"
      Critical  = "true"
      Day       = "5"
    }
  )
}

resource "aws_iam_role" "safety_response_lambda" {
  name = "t-developer-safety-response-lambda-${var.environment}"

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
}

resource "aws_iam_role_policy" "safety_response_lambda_policy" {
  name = "safety-response-policy"
  role = aws_iam_role.safety_response_lambda.id

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
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/t-developer-evolution-state-${var.environment}"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:t-developer-emergency-stop-${var.environment}"
      }
    ]
  })
}

resource "aws_lambda_permission" "sns_invoke_safety" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.safety_response.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.safety_alerts.arn
}

# ===================================
# KMS Key for SNS Encryption
# ===================================

resource "aws_kms_key" "sns_encryption" {
  description             = "KMS key for SNS topic encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

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
        Sid    = "Allow SNS to use the key"
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    var.common_tags,
    {
      Purpose = "SNSEncryption"
      Day     = "5"
    }
  )
}

resource "aws_kms_alias" "sns_encryption" {
  name          = "alias/sns-encryption-${var.environment}"
  target_key_id = aws_kms_key.sns_encryption.key_id
}

# ===================================
# Data Sources
# ===================================

data "aws_caller_identity" "current" {}

# ===================================
# Outputs
# ===================================

output "sns_topic_arns" {
  description = "ARNs of SNS topics"
  value = {
    evolution_alerts   = aws_sns_topic.evolution_alerts.arn
    critical_alerts    = aws_sns_topic.critical_alerts.arn
    performance_alerts = aws_sns_topic.performance_alerts.arn
    safety_alerts      = aws_sns_topic.safety_alerts.arn
  }
}

output "alarm_names" {
  description = "Names of CloudWatch alarms"
  value = {
    evolution_error_rate        = aws_cloudwatch_metric_alarm.evolution_error_rate.alarm_name
    safety_violations           = aws_cloudwatch_metric_alarm.safety_violations.alarm_name
    agent_size_violation        = aws_cloudwatch_metric_alarm.agent_size_violation.alarm_name
    instantiation_time_violation = aws_cloudwatch_metric_alarm.instantiation_time_violation.alarm_name
    system_critical             = aws_cloudwatch_composite_alarm.system_critical.alarm_name
  }
}
