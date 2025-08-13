# AWS X-Ray Tracing Configuration
# Day 5: Monitoring & Logging Infrastructure
# Generated: 2024-11-18

# ===================================
# X-Ray Service Map
# ===================================

resource "aws_xray_sampling_rule" "evolution_system" {
  rule_name      = "EvolutionSystem"
  priority       = 1000
  version        = 1
  reservoir_size = 1
  fixed_rate     = 0.1
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "t-developer-*"
  resource_arn   = "*"

  attributes = {
    "evolution" = "true"
  }
}

resource "aws_xray_sampling_rule" "agent_traces" {
  rule_name      = "AgentTraces"
  priority       = 2000
  version        = 1
  reservoir_size = 2
  fixed_rate     = 0.05
  url_path       = "/api/agents/*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "agent-*"
  resource_arn   = "*"

  attributes = {
    "component" = "agent"
  }
}

resource "aws_xray_sampling_rule" "critical_operations" {
  rule_name      = "CriticalOperations"
  priority       = 500
  version        = 1
  reservoir_size = 5
  fixed_rate     = 1.0  # 100% sampling for critical operations
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*safety*"
  resource_arn   = "*"

  attributes = {
    "critical" = "true"
  }
}

# ===================================
# X-Ray Group for Evolution System
# ===================================

resource "aws_xray_group" "evolution_system" {
  group_name        = "EvolutionSystem"
  filter_expression = "service(\"t-developer-*\") OR service(\"evolution-*\")"

  insights_configuration {
    insights_enabled      = true
    notifications_enabled = true
  }

  tags = merge(
    var.common_tags,
    {
      Component = "XRay"
      Day       = "5"
    }
  )
}

resource "aws_xray_group" "agent_performance" {
  group_name        = "AgentPerformance"
  filter_expression = "annotation.agent_type = \"evolution\" AND responseTime > 3"

  insights_configuration {
    insights_enabled      = true
    notifications_enabled = true
  }

  tags = merge(
    var.common_tags,
    {
      Component = "XRay"
      Focus     = "Performance"
      Day       = "5"
    }
  )
}

# ===================================
# X-Ray Encryption Configuration
# ===================================

resource "aws_xray_encryption_config" "evolution" {
  type   = "KMS"
  key_id = aws_kms_key.xray_encryption.arn
}

resource "aws_kms_key" "xray_encryption" {
  description             = "KMS key for X-Ray trace encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = merge(
    var.common_tags,
    {
      Purpose = "XRayEncryption"
      Day     = "5"
    }
  )
}

resource "aws_kms_alias" "xray_encryption" {
  name          = "alias/xray-encryption-${var.environment}"
  target_key_id = aws_kms_key.xray_encryption.key_id
}

# ===================================
# IAM Role for X-Ray Daemon
# ===================================

resource "aws_iam_role" "xray_daemon" {
  name = "t-developer-xray-daemon-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com",
            "lambda.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = merge(
    var.common_tags,
    {
      Component = "XRayDaemon"
      Day       = "5"
    }
  )
}

resource "aws_iam_role_policy_attachment" "xray_daemon_policy" {
  role       = aws_iam_role.xray_daemon.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy" "xray_write_policy" {
  name = "xray-write-policy"
  role = aws_iam_role.xray_daemon.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "xray:GetSamplingStatisticSummaries"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.xray_encryption.arn
      }
    ]
  })
}

# ===================================
# Lambda Function X-Ray Configuration
# ===================================

resource "aws_iam_role_policy" "lambda_xray_policy" {
  for_each = var.lambda_functions

  name = "xray-policy-${each.key}"
  role = each.value.role

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
}

# ===================================
# X-Ray Service Map Configuration
# ===================================

resource "aws_cloudwatch_event_rule" "xray_insights" {
  name                = "xray-insights-${var.environment}"
  description         = "Trigger X-Ray insights analysis"
  schedule_expression = "rate(1 hour)"

  tags = merge(
    var.common_tags,
    {
      Component = "XRayInsights"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_event_target" "xray_insights_lambda" {
  rule      = aws_cloudwatch_event_rule.xray_insights.name
  target_id = "XRayInsightsLambda"
  arn       = aws_lambda_function.xray_insights_analyzer.arn
}

# ===================================
# X-Ray Insights Analyzer Lambda
# ===================================

resource "aws_lambda_function" "xray_insights_analyzer" {
  filename         = "${path.module}/lambda/xray_insights.zip"
  function_name    = "t-developer-xray-insights-${var.environment}"
  role            = aws_iam_role.xray_insights_lambda.arn
  handler         = "index.handler"
  source_code_hash = filebase64sha256("${path.module}/lambda/xray_insights.zip")
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      SNS_TOPIC   = aws_sns_topic.evolution_alerts.arn
    }
  }

  tracing_config {
    mode = "Active"
  }

  tags = merge(
    var.common_tags,
    {
      Component = "XRayInsights"
      Day       = "5"
    }
  )
}

resource "aws_iam_role" "xray_insights_lambda" {
  name = "t-developer-xray-insights-lambda-${var.environment}"

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

resource "aws_iam_role_policy" "xray_insights_lambda_policy" {
  name = "xray-insights-policy"
  role = aws_iam_role.xray_insights_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:GetServiceGraph",
          "xray:GetTraceGraph",
          "xray:GetTraceSummaries",
          "xray:GetInsightSummaries",
          "xray:GetInsightEvents",
          "xray:GetInsightImpactGraph"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.evolution_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# ===================================
# Outputs
# ===================================

output "xray_service_map_url" {
  description = "URL to X-Ray Service Map"
  value       = "https://console.aws.amazon.com/xray/home?region=${var.aws_region}#/service-map"
}

output "xray_daemon_role_arn" {
  description = "IAM role ARN for X-Ray daemon"
  value       = aws_iam_role.xray_daemon.arn
}

output "xray_encryption_key_id" {
  description = "KMS key ID for X-Ray encryption"
  value       = aws_kms_key.xray_encryption.id
}
