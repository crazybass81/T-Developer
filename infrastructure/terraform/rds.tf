# T-Developer Evolution System - RDS PostgreSQL Infrastructure

# RDS Subnet Group
resource "aws_db_subnet_group" "t_developer" {
  name       = "t-developer-db-subnet-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-db-subnet-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

# RDS Parameter Group for PostgreSQL 15
resource "aws_db_parameter_group" "t_developer_pg15" {
  name   = "t-developer-pg15-${var.environment}"
  family = "postgres15"

  # Performance optimizations for Evolution System
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,pgaudit,auto_explain"
  }

  parameter {
    name  = "max_connections"
    value = "500"
  }

  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/4}"
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "256000"  # 256MB
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "16384"  # 16MB
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"  # SSD optimized
  }

  parameter {
    name  = "effective_io_concurrency"
    value = "200"  # SSD optimized
  }

  # Evolution System specific
  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  parameter {
    name  = "auto_explain.log_min_duration"
    value = "100"  # Log queries slower than 100ms
  }

  parameter {
    name  = "pgaudit.log"
    value = "ALL"
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-pg15-params-${var.environment}"
      Environment = var.environment
    }
  )
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "t-developer-rds-sg-${var.environment}"
  description = "Security group for T-Developer RDS PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from application"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  ingress {
    description     = "PostgreSQL from Evolution Engine"
    from_port       = 5432
    to_port         = 5432
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
      Name        = "t-developer-rds-sg-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

# RDS Instance - Primary
resource "aws_db_instance" "t_developer_primary" {
  identifier     = "t-developer-db-${var.environment}"
  engine         = "postgres"
  engine_version = "15.4"

  # Instance configuration
  instance_class               = var.db_instance_class
  allocated_storage           = var.db_allocated_storage
  max_allocated_storage       = var.db_max_allocated_storage
  storage_type                = "gp3"
  storage_encrypted           = true
  kms_key_id                  = aws_kms_key.database_kms.arn
  iops                        = var.db_iops
  storage_throughput          = var.db_storage_throughput

  # Database configuration
  db_name  = "t_developer"
  username = "t_developer_admin"
  password = random_password.db_password.result
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.t_developer.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.t_developer_pg15.name

  # Backup configuration
  backup_retention_period         = var.backup_retention_days
  backup_window                   = "03:00-04:00"
  maintenance_window              = "sun:04:00-sun:05:00"
  skip_final_snapshot            = var.environment != "production"
  final_snapshot_identifier      = var.environment == "production" ? "t-developer-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null
  copy_tags_to_snapshot          = true

  # Performance Insights
  performance_insights_enabled          = true
  performance_insights_kms_key_id      = aws_kms_key.database_kms.arn
  performance_insights_retention_period = var.environment == "production" ? 731 : 7

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql"]
  monitoring_interval             = 60
  monitoring_role_arn            = aws_iam_role.rds_monitoring.arn

  # High Availability
  multi_az               = var.environment == "production"
  deletion_protection    = var.environment == "production"

  # Auto Minor Version Upgrade
  auto_minor_version_upgrade = var.environment != "production"
  apply_immediately         = var.environment != "production"

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-db-primary-${var.environment}"
      Environment = var.environment
      Component   = "Database"
      Role        = "Primary"
      BackupSchedule = "Daily"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.rds_logs
  ]
}

# RDS Read Replica (Production only)
resource "aws_db_instance" "t_developer_read_replica" {
  count = var.environment == "production" ? 1 : 0

  identifier             = "t-developer-db-read-${var.environment}"
  replicate_source_db    = aws_db_instance.t_developer_primary.identifier

  # Instance configuration
  instance_class         = var.db_instance_class_replica
  storage_encrypted      = true

  # Performance Insights
  performance_insights_enabled          = true
  performance_insights_kms_key_id      = aws_kms_key.database_kms.arn
  performance_insights_retention_period = 7

  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # No backups on read replica
  backup_retention_period = 0

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-db-replica-${var.environment}"
      Environment = var.environment
      Component   = "Database"
      Role        = "ReadReplica"
    }
  )
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "t-developer/database/${var.environment}/master-password"
  description             = "Master password for T-Developer RDS PostgreSQL"
  recovery_window_in_days = var.environment == "production" ? 30 : 0
  kms_key_id             = aws_kms_key.secrets_kms.arn

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-db-password-${var.environment}"
      Environment = var.environment
      Component   = "Database"
      Type        = "Credential"
    }
  )
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.t_developer_primary.username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.t_developer_primary.address
    port     = aws_db_instance.t_developer_primary.port
    dbname   = aws_db_instance.t_developer_primary.db_name
  })
}

# CloudWatch Log Group for RDS
resource "aws_cloudwatch_log_group" "rds_logs" {
  name              = "/aws/rds/instance/t-developer-db-${var.environment}/postgresql"
  retention_in_days = var.log_retention_days
  kms_key_id       = aws_kms_key.logs_kms.arn

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-rds-logs-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

# IAM Role for RDS Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "t-developer-rds-monitoring-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-rds-monitoring-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms for RDS
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "t-developer-rds-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.environment == "production" ? 80 : 90
  alarm_description   = "RDS CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.t_developer_primary.id
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-rds-cpu-alarm-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "rds_storage" {
  alarm_name          = "t-developer-rds-storage-low-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = 10737418240  # 10GB in bytes
  alarm_description   = "RDS free storage space is low"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.t_developer_primary.id
  }

  tags = merge(
    local.common_tags,
    {
      Name        = "t-developer-rds-storage-alarm-${var.environment}"
      Environment = var.environment
      Component   = "Database"
    }
  )
}

# Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.t_developer_primary.endpoint
  sensitive   = true
}

output "rds_address" {
  description = "RDS instance address"
  value       = aws_db_instance.t_developer_primary.address
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.t_developer_primary.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.t_developer_primary.db_name
}

output "rds_secret_arn" {
  description = "ARN of the secret containing RDS credentials"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "rds_read_replica_endpoint" {
  description = "RDS read replica endpoint"
  value       = var.environment == "production" ? aws_db_instance.t_developer_read_replica[0].endpoint : null
  sensitive   = true
}
