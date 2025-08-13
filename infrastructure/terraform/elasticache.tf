# T-Developer Evolution System - ElastiCache Redis Infrastructure

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "t_developer" {
  name       = "t-developer-cache-subnet-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-subnet-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
    }
  )
}

# ElastiCache Parameter Group for Redis 7
resource "aws_elasticache_parameter_group" "t_developer_redis7" {
  name   = "t-developer-redis7-${var.environment}"
  family = "redis7"

  # Redis configuration for Evolution System
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"  # Evict least recently used keys
  }

  parameter {
    name  = "timeout"
    value = "300"  # 5 minutes idle timeout
  }

  parameter {
    name  = "tcp-keepalive"
    value = "60"
  }

  parameter {
    name  = "tcp-backlog"
    value = "511"
  }

  parameter {
    name  = "maxclients"
    value = "65000"
  }

  # Evolution System optimizations
  parameter {
    name  = "slowlog-log-slower-than"
    value = "10000"  # Log queries slower than 10ms
  }

  parameter {
    name  = "slowlog-max-len"
    value = "512"
  }

  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"  # Expired events for Evolution tracking
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-redis7-params-${var.environment}"
      Environment = var.environment
    }
  )
}

# Security Group for ElastiCache
resource "aws_security_group" "elasticache" {
  name        = "t-developer-elasticache-sg-${var.environment}"
  description = "Security group for T-Developer ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis from application"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  ingress {
    description     = "Redis from Evolution Engine"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.evolution.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-elasticache-sg-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
    }
  )
}

# ElastiCache Replication Group (Redis Cluster Mode Disabled)
resource "aws_elasticache_replication_group" "t_developer" {
  replication_group_id       = "t-developer-cache-${var.environment}"
  replication_group_description = "Redis cache for T-Developer Evolution System"
  
  # Redis configuration
  engine               = "redis"
  engine_version       = "7.0"
  port                 = 6379
  parameter_group_name = aws_elasticache_parameter_group.t_developer_redis7.name
  node_type           = var.cache_node_type
  
  # Cluster configuration
  number_cache_clusters      = var.environment == "production" ? 3 : 2
  automatic_failover_enabled = var.environment == "production" ? true : false
  multi_az_enabled          = var.environment == "production" ? true : false
  
  # Network configuration
  subnet_group_name  = aws_elasticache_subnet_group.t_developer.name
  security_group_ids = [aws_security_group.elasticache.id]
  
  # Security
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = random_password.redis_auth_token.result
  kms_key_id               = aws_kms_key.cache_kms.arn
  
  # Backup configuration
  snapshot_retention_limit = var.environment == "production" ? 5 : 1
  snapshot_window         = "03:00-05:00"
  maintenance_window      = "sun:05:00-sun:07:00"
  
  # Notifications
  notification_topic_arn = aws_sns_topic.alerts.arn
  
  # Auto Minor Version Upgrade
  auto_minor_version_upgrade = var.environment != "production"
  apply_immediately         = var.environment != "production"
  
  # Logging
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.elasticache_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }
  
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.elasticache_engine_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "engine-log"
  }
  
  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
      Engine      = "Redis"
      Mode        = "Replication"
    }
  )
}

# Random auth token for Redis
resource "random_password" "redis_auth_token" {
  length  = 32
  special = true
  # Redis AUTH token restrictions
  override_special = "!&#$^<>-"
}

# Store auth token in Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth_token" {
  name                    = "t-developer/cache/${var.environment}/auth-token"
  description             = "Auth token for T-Developer ElastiCache Redis"
  recovery_window_in_days = var.environment == "production" ? 30 : 0
  kms_key_id             = aws_kms_key.secrets_kms.arn

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-redis-auth-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
      Type        = "Credential"
    }
  )
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  secret_id = aws_secretsmanager_secret.redis_auth_token.id
  secret_string = jsonencode({
    auth_token = random_password.redis_auth_token.result
    endpoint   = aws_elasticache_replication_group.t_developer.configuration_endpoint_address
    port       = aws_elasticache_replication_group.t_developer.port
    ssl        = true
  })
}

# CloudWatch Log Groups for ElastiCache
resource "aws_cloudwatch_log_group" "elasticache_slow_log" {
  name              = "/aws/elasticache/t-developer-${var.environment}/slow-log"
  retention_in_days = var.log_retention_days
  kms_key_id       = aws_kms_key.logs_kms.arn

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-slow-log-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
      LogType     = "SlowLog"
    }
  )
}

resource "aws_cloudwatch_log_group" "elasticache_engine_log" {
  name              = "/aws/elasticache/t-developer-${var.environment}/engine-log"
  retention_in_days = var.log_retention_days
  kms_key_id       = aws_kms_key.logs_kms.arn

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-engine-log-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
      LogType     = "EngineLog"
    }
  )
}

# CloudWatch Alarms for ElastiCache
resource "aws_cloudwatch_metric_alarm" "elasticache_cpu" {
  alarm_name          = "t-developer-cache-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = var.environment == "production" ? 75 : 85
  alarm_description   = "ElastiCache CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.t_developer.id
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-cpu-alarm-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "elasticache_memory" {
  alarm_name          = "t-developer-cache-memory-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "ElastiCache memory usage is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.t_developer.id
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-memory-alarm-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "elasticache_evictions" {
  alarm_name          = "t-developer-cache-evictions-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Evictions"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = 1000
  alarm_description   = "ElastiCache evictions are too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.t_developer.id
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-cache-evictions-alarm-${var.environment}"
      Environment = var.environment
      Component   = "Cache"
    }
  )
}

# Outputs
output "elasticache_endpoint" {
  description = "ElastiCache configuration endpoint"
  value       = aws_elasticache_replication_group.t_developer.configuration_endpoint_address
  sensitive   = true
}

output "elasticache_port" {
  description = "ElastiCache port"
  value       = aws_elasticache_replication_group.t_developer.port
}

output "elasticache_reader_endpoint" {
  description = "ElastiCache reader endpoint"
  value       = aws_elasticache_replication_group.t_developer.reader_endpoint_address
  sensitive   = true
}

output "elasticache_secret_arn" {
  description = "ARN of the secret containing Redis auth token"
  value       = aws_secretsmanager_secret.redis_auth_token.arn
}

output "elasticache_cluster_id" {
  description = "ElastiCache replication group ID"
  value       = aws_elasticache_replication_group.t_developer.id
}