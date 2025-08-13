# CloudWatch Dashboard for T-Developer Evolution System
# Day 5: Monitoring & Logging Infrastructure
# Generated: 2024-11-18

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ===================================
# CloudWatch Dashboard
# ===================================

resource "aws_cloudwatch_dashboard" "evolution_system" {
  dashboard_name = "t-developer-evolution-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      # Evolution Engine Metrics
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["T-Developer/Evolution", "AgentCount", { stat = "Average" }],
            [".", "EvolutionCycles", { stat = "Sum" }],
            [".", "FitnessScore", { stat = "Average" }],
            [".", "SafetyViolations", { stat = "Sum", color = "#d62728" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Evolution Engine Metrics"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },

      # Agent Performance Metrics
      {
        type = "metric"
        x    = 12
        y    = 0
        width = 12
        height = 6
        properties = {
          metrics = [
            ["T-Developer/Agents", "InstantiationTime", { stat = "Average", unit = "Microseconds" }],
            [".", "MemoryUsage", { stat = "Average", unit = "Kilobytes" }],
            [".", "ProcessingTime", { stat = "Average", unit = "Milliseconds" }],
            [".", "ErrorRate", { stat = "Sum", color = "#ff7f0e" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Agent Performance (Target: <3μs, <6.5KB)"
          annotations = {
            horizontal = [
              {
                value = 3
                fill  = "below"
                label = "3μs Target"
                color = "#77b300"
              },
              {
                value = 6.5
                fill  = "below"
                label = "6.5KB Memory Limit"
                color = "#77b300"
              }
            ]
          }
        }
      },

      # Database Performance
      {
        type = "metric"
        x    = 0
        y    = 6
        width = 8
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "DatabaseConnections", { stat = "Average", dimensions = { DBInstanceIdentifier = aws_db_instance.postgresql.id }}],
            [".", "CPUUtilization", { stat = "Average", dimensions = { DBInstanceIdentifier = aws_db_instance.postgresql.id }}],
            [".", "FreeableMemory", { stat = "Average", dimensions = { DBInstanceIdentifier = aws_db_instance.postgresql.id }}],
            [".", "ReadLatency", { stat = "Average", dimensions = { DBInstanceIdentifier = aws_db_instance.postgresql.id }}],
            [".", "WriteLatency", { stat = "Average", dimensions = { DBInstanceIdentifier = aws_db_instance.postgresql.id }}]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "RDS PostgreSQL Performance"
        }
      },

      # Redis Cache Performance
      {
        type = "metric"
        x    = 8
        y    = 6
        width = 8
        height = 6
        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", { stat = "Average", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}],
            [".", "DatabaseMemoryUsagePercentage", { stat = "Average", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}],
            [".", "CacheHits", { stat = "Sum", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}],
            [".", "CacheMisses", { stat = "Sum", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}],
            [".", "NetworkBytesIn", { stat = "Sum", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}],
            [".", "NetworkBytesOut", { stat = "Sum", dimensions = { CacheClusterId = aws_elasticache_replication_group.redis.id }}]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ElastiCache Redis Performance"
        }
      },

      # DynamoDB Performance
      {
        type = "metric"
        x    = 16
        y    = 6
        width = 8
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", { stat = "Sum", dimensions = { TableName = "t-developer-evolution-state-${var.environment}" }}],
            [".", "ConsumedWriteCapacityUnits", { stat = "Sum", dimensions = { TableName = "t-developer-evolution-state-${var.environment}" }}],
            [".", "UserErrors", { stat = "Sum", dimensions = { TableName = "t-developer-evolution-state-${var.environment}" }}],
            [".", "SystemErrors", { stat = "Sum", dimensions = { TableName = "t-developer-evolution-state-${var.environment}" }}],
            [".", "ThrottledRequests", { stat = "Sum", dimensions = { TableName = "t-developer-evolution-state-${var.environment}" }}]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "DynamoDB Performance"
        }
      },

      # Lambda Functions Performance
      {
        type = "metric"
        x    = 0
        y    = 12
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum" }],
            [".", "Errors", { stat = "Sum", color = "#d62728" }],
            [".", "Duration", { stat = "Average" }],
            [".", "Throttles", { stat = "Sum", color = "#ff7f0e" }],
            [".", "ConcurrentExecutions", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Lambda Functions Overview"
        }
      },

      # API Gateway Metrics
      {
        type = "metric"
        x    = 12
        y    = 12
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", { stat = "Sum" }],
            [".", "4XXError", { stat = "Sum", color = "#ff7f0e" }],
            [".", "5XXError", { stat = "Sum", color = "#d62728" }],
            [".", "Latency", { stat = "Average" }],
            [".", "IntegrationLatency", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "API Gateway Performance"
        }
      },

      # Cost and Usage
      {
        type = "metric"
        x    = 0
        y    = 18
        width = 24
        height = 4
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", { stat = "Maximum", dimensions = { Currency = "USD" }}]
          ]
          period = 86400
          stat   = "Maximum"
          region = "us-east-1"
          title  = "Estimated AWS Charges (Daily)"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },

      # Evolution Safety Metrics
      {
        type = "log"
        x    = 0
        y    = 22
        width = 24
        height = 4
        properties = {
          query = "SOURCE '/aws/lambda/evolution-safety-check' | fields @timestamp, @message | filter @message like /SAFETY/ | sort @timestamp desc | limit 20"
          region = var.aws_region
          title  = "Evolution Safety Events"
        }
      }
    ]
  })
}

# ===================================
# CloudWatch Log Groups
# ===================================

resource "aws_cloudwatch_log_group" "evolution_engine" {
  name              = "/aws/evolution/engine"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.evolution_logs.arn

  tags = merge(
    var.common_tags,
    {
      Component = "EvolutionEngine"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_log_group" "agent_registry" {
  name              = "/aws/evolution/agents"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.evolution_logs.arn

  tags = merge(
    var.common_tags,
    {
      Component = "AgentRegistry"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_log_group" "safety_system" {
  name              = "/aws/evolution/safety"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.evolution_logs.arn

  tags = merge(
    var.common_tags,
    {
      Component = "SafetySystem"
      Critical  = "true"
      Day       = "5"
    }
  )
}

resource "aws_cloudwatch_log_group" "performance_metrics" {
  name              = "/aws/evolution/performance"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.evolution_logs.arn

  tags = merge(
    var.common_tags,
    {
      Component = "PerformanceMetrics"
      Day       = "5"
    }
  )
}

# ===================================
# CloudWatch Log Streams
# ===================================

resource "aws_cloudwatch_log_stream" "evolution_main" {
  name           = "main"
  log_group_name = aws_cloudwatch_log_group.evolution_engine.name
}

resource "aws_cloudwatch_log_stream" "evolution_mutations" {
  name           = "mutations"
  log_group_name = aws_cloudwatch_log_group.evolution_engine.name
}

resource "aws_cloudwatch_log_stream" "evolution_fitness" {
  name           = "fitness"
  log_group_name = aws_cloudwatch_log_group.evolution_engine.name
}

# ===================================
# Metric Filters
# ===================================

resource "aws_cloudwatch_log_metric_filter" "evolution_errors" {
  name           = "evolution-errors"
  log_group_name = aws_cloudwatch_log_group.evolution_engine.name
  pattern        = "[ERROR]"

  metric_transformation {
    name      = "EvolutionErrors"
    namespace = "T-Developer/Evolution"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "safety_violations" {
  name           = "safety-violations"
  log_group_name = aws_cloudwatch_log_group.safety_system.name
  pattern        = "[VIOLATION]"

  metric_transformation {
    name      = "SafetyViolations"
    namespace = "T-Developer/Safety"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "agent_size_violations" {
  name           = "agent-size-violations"
  log_group_name = aws_cloudwatch_log_group.agent_registry.name
  pattern        = "[SIZE_VIOLATION]"

  metric_transformation {
    name      = "AgentSizeViolations"
    namespace = "T-Developer/Agents"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "instantiation_time_violations" {
  name           = "instantiation-time-violations"
  log_group_name = aws_cloudwatch_log_group.performance_metrics.name
  pattern        = "[time > 3]"

  metric_transformation {
    name      = "InstantiationTimeViolations"
    namespace = "T-Developer/Performance"
    value     = "1"
  }
}

# ===================================
# CloudWatch Composite Alarms
# ===================================

resource "aws_cloudwatch_composite_alarm" "evolution_system_health" {
  alarm_name          = "evolution-system-health-${var.environment}"
  alarm_description   = "Composite alarm for overall Evolution System health"
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.evolution_alerts.arn]
  ok_actions          = [aws_sns_topic.evolution_alerts.arn]

  alarm_rule = "ALARM(${aws_cloudwatch_metric_alarm.high_error_rate.alarm_name}) OR ALARM(${aws_cloudwatch_metric_alarm.safety_violations.alarm_name}) OR ALARM(${aws_cloudwatch_metric_alarm.agent_constraint_violations.alarm_name})"

  tags = merge(
    var.common_tags,
    {
      Severity = "Critical"
      Day      = "5"
    }
  )
}

# ===================================
# KMS Key for Log Encryption
# ===================================

resource "aws_kms_key" "evolution_logs" {
  description             = "KMS key for Evolution System log encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = merge(
    var.common_tags,
    {
      Purpose = "LogEncryption"
      Day     = "5"
    }
  )
}

resource "aws_kms_alias" "evolution_logs" {
  name          = "alias/evolution-logs-${var.environment}"
  target_key_id = aws_kms_key.evolution_logs.key_id
}

# ===================================
# CloudWatch Insights Queries
# ===================================

resource "aws_cloudwatch_query_definition" "evolution_performance" {
  name = "Evolution System Performance Analysis"

  log_group_names = [
    aws_cloudwatch_log_group.evolution_engine.name,
    aws_cloudwatch_log_group.performance_metrics.name
  ]

  query_string = <<-QUERY
    fields @timestamp, @message
    | filter @message like /PERFORMANCE/
    | stats avg(instantiation_time) as avg_time,
            max(instantiation_time) as max_time,
            min(instantiation_time) as min_time,
            avg(memory_usage) as avg_memory,
            max(memory_usage) as max_memory
    by bin(5m)
  QUERY
}

resource "aws_cloudwatch_query_definition" "safety_analysis" {
  name = "Evolution Safety Analysis"

  log_group_names = [
    aws_cloudwatch_log_group.safety_system.name
  ]

  query_string = <<-QUERY
    fields @timestamp, @message, violation_type, agent_id
    | filter @message like /SAFETY/
    | stats count() as violation_count by violation_type
    | sort violation_count desc
  QUERY
}

# ===================================
# Outputs
# ===================================

output "dashboard_url" {
  description = "URL to CloudWatch Dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.evolution_system.dashboard_name}"
}

output "log_group_names" {
  description = "CloudWatch Log Group names"
  value = {
    evolution_engine    = aws_cloudwatch_log_group.evolution_engine.name
    agent_registry      = aws_cloudwatch_log_group.agent_registry.name
    safety_system       = aws_cloudwatch_log_group.safety_system.name
    performance_metrics = aws_cloudwatch_log_group.performance_metrics.name
  }
}

output "kms_key_id" {
  description = "KMS key ID for log encryption"
  value       = aws_kms_key.evolution_logs.id
}
