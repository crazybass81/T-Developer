# T-Developer Evolution System - DynamoDB Infrastructure

# DynamoDB Table for Agent Evolution State
resource "aws_dynamodb_table" "evolution_state" {
  name           = "t-developer-evolution-state-${var.environment}"
  billing_mode   = var.environment == "production" ? "PROVISIONED" : "PAY_PER_REQUEST"
  read_capacity  = var.environment == "production" ? 10 : null
  write_capacity = var.environment == "production" ? 10 : null
  hash_key       = "agent_id"
  range_key      = "version"
  
  # Enable encryption
  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.dynamodb_kms.arn
  }
  
  # Enable Point-in-Time Recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # TTL for old evolution states
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Attributes
  attribute {
    name = "agent_id"
    type = "S"
  }
  
  attribute {
    name = "version"
    type = "N"
  }
  
  attribute {
    name = "generation"
    type = "N"
  }
  
  attribute {
    name = "fitness_score"
    type = "N"
  }
  
  attribute {
    name = "created_at"
    type = "N"
  }
  
  # Global Secondary Indexes
  global_secondary_index {
    name            = "generation-index"
    hash_key        = "generation"
    range_key       = "fitness_score"
    projection_type = "ALL"
    read_capacity   = var.environment == "production" ? 5 : null
    write_capacity  = var.environment == "production" ? 5 : null
  }
  
  global_secondary_index {
    name            = "fitness-index"
    hash_key        = "agent_id"
    range_key       = "fitness_score"
    projection_type = "INCLUDE"
    non_key_attributes = ["generation", "created_at", "parent_id"]
    read_capacity   = var.environment == "production" ? 5 : null
    write_capacity  = var.environment == "production" ? 5 : null
  }
  
  # Stream for real-time evolution tracking
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-evolution-state-${var.environment}"
      Environment = var.environment
      Component   = "Evolution"
      DataType    = "State"
    }
  )
}

# DynamoDB Table for Agent Registry
resource "aws_dynamodb_table" "agent_registry" {
  name           = "t-developer-agent-registry-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "agent_id"
  
  # Enable encryption
  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.dynamodb_kms.arn
  }
  
  # Enable Point-in-Time Recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # Attributes
  attribute {
    name = "agent_id"
    type = "S"
  }
  
  attribute {
    name = "agent_name"
    type = "S"
  }
  
  attribute {
    name = "capability"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  attribute {
    name = "last_evolved"
    type = "N"
  }
  
  # Global Secondary Indexes
  global_secondary_index {
    name            = "name-index"
    hash_key        = "agent_name"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "capability-index"
    hash_key        = "capability"
    range_key       = "last_evolved"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "status-index"
    hash_key        = "status"
    range_key       = "last_evolved"
    projection_type = "INCLUDE"
    non_key_attributes = ["agent_name", "capability", "fitness_score"]
  }
  
  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-agent-registry-${var.environment}"
      Environment = var.environment
      Component   = "Registry"
      DataType    = "Metadata"
    }
  )
}

# DynamoDB Table for Performance Metrics
resource "aws_dynamodb_table" "performance_metrics" {
  name           = "t-developer-performance-metrics-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "metric_id"
  range_key      = "timestamp"
  
  # Enable encryption
  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.dynamodb_kms.arn
  }
  
  # TTL for old metrics (30 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Attributes
  attribute {
    name = "metric_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "N"
  }
  
  attribute {
    name = "agent_id"
    type = "S"
  }
  
  attribute {
    name = "metric_type"
    type = "S"
  }
  
  # Global Secondary Indexes
  global_secondary_index {
    name            = "agent-metrics-index"
    hash_key        = "agent_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "type-index"
    hash_key        = "metric_type"
    range_key       = "timestamp"
    projection_type = "INCLUDE"
    non_key_attributes = ["value", "agent_id", "constraint_met"]
  }
  
  # Stream for real-time metric analysis
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  
  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-performance-metrics-${var.environment}"
      Environment = var.environment
      Component   = "Monitoring"
      DataType    = "Metrics"
    }
  )
}

# DynamoDB Table for Evolution History
resource "aws_dynamodb_table" "evolution_history" {
  name           = "t-developer-evolution-history-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "evolution_id"
  range_key      = "timestamp"
  
  # Enable encryption
  server_side_encryption {
    enabled     = true
    kms_key_id  = aws_kms_key.dynamodb_kms.arn
  }
  
  # Enable Point-in-Time Recovery for audit trail
  point_in_time_recovery {
    enabled = true
  }
  
  # Attributes
  attribute {
    name = "evolution_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "N"
  }
  
  attribute {
    name = "parent_agent_id"
    type = "S"
  }
  
  attribute {
    name = "child_agent_id"
    type = "S"
  }
  
  attribute {
    name = "evolution_type"
    type = "S"
  }
  
  # Global Secondary Indexes
  global_secondary_index {
    name            = "parent-index"
    hash_key        = "parent_agent_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "child-index"
    hash_key        = "child_agent_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  global_secondary_index {
    name            = "type-index"
    hash_key        = "evolution_type"
    range_key       = "timestamp"
    projection_type = "INCLUDE"
    non_key_attributes = ["parent_agent_id", "child_agent_id", "success", "fitness_delta"]
  }
  
  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-evolution-history-${var.environment}"
      Environment = var.environment
      Component   = "Evolution"
      DataType    = "History"
      Retention   = "Permanent"
    }
  )
}

# Auto-scaling for Production DynamoDB tables
resource "aws_appautoscaling_target" "evolution_state_read" {
  count              = var.environment == "production" ? 1 : 0
  max_capacity       = 100
  min_capacity       = 10
  resource_id        = "table/${aws_dynamodb_table.evolution_state.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "evolution_state_read" {
  count              = var.environment == "production" ? 1 : 0
  name               = "DynamoDBReadCapacityUtilization:${aws_appautoscaling_target.evolution_state_read[0].resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.evolution_state_read[0].resource_id
  scalable_dimension = aws_appautoscaling_target.evolution_state_read[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.evolution_state_read[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_appautoscaling_target" "evolution_state_write" {
  count              = var.environment == "production" ? 1 : 0
  max_capacity       = 100
  min_capacity       = 10
  resource_id        = "table/${aws_dynamodb_table.evolution_state.name}"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "evolution_state_write" {
  count              = var.environment == "production" ? 1 : 0
  name               = "DynamoDBWriteCapacityUtilization:${aws_appautoscaling_target.evolution_state_write[0].resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.evolution_state_write[0].resource_id
  scalable_dimension = aws_appautoscaling_target.evolution_state_write[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.evolution_state_write[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70.0
  }
}

# CloudWatch Alarms for DynamoDB
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttle" {
  for_each = {
    evolution_state    = aws_dynamodb_table.evolution_state.name
    agent_registry     = aws_dynamodb_table.agent_registry.name
    performance_metrics = aws_dynamodb_table.performance_metrics.name
    evolution_history  = aws_dynamodb_table.evolution_history.name
  }
  
  alarm_name          = "t-developer-dynamodb-${each.key}-throttle-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "DynamoDB table ${each.key} is being throttled"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    TableName = each.value
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-dynamodb-throttle-alarm-${each.key}-${var.environment}"
      Environment = var.environment
      Component   = "DynamoDB"
      Table       = each.key
    }
  )
}

# Outputs
output "dynamodb_evolution_state_table" {
  description = "Name of the Evolution State DynamoDB table"
  value       = aws_dynamodb_table.evolution_state.name
}

output "dynamodb_evolution_state_arn" {
  description = "ARN of the Evolution State DynamoDB table"
  value       = aws_dynamodb_table.evolution_state.arn
}

output "dynamodb_agent_registry_table" {
  description = "Name of the Agent Registry DynamoDB table"
  value       = aws_dynamodb_table.agent_registry.name
}

output "dynamodb_agent_registry_arn" {
  description = "ARN of the Agent Registry DynamoDB table"
  value       = aws_dynamodb_table.agent_registry.arn
}

output "dynamodb_performance_metrics_table" {
  description = "Name of the Performance Metrics DynamoDB table"
  value       = aws_dynamodb_table.performance_metrics.name
}

output "dynamodb_evolution_history_table" {
  description = "Name of the Evolution History DynamoDB table"
  value       = aws_dynamodb_table.evolution_history.name
}

output "dynamodb_stream_arns" {
  description = "ARNs of DynamoDB streams for real-time processing"
  value = {
    evolution_state     = aws_dynamodb_table.evolution_state.stream_arn
    performance_metrics = aws_dynamodb_table.performance_metrics.stream_arn
  }
}