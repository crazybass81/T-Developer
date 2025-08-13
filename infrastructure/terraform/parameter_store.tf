# T-Developer Parameter Store Configuration
# 환경 변수 및 설정값 체계적 관리 시스템

# ===== Evolution Engine Core Configuration =====
# AI 자율성 및 진화 엔진 핵심 설정

resource "aws_ssm_parameter" "evolution_engine_config" {
  name  = "/${var.project_name}/${var.environment}/evolution/engine/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    ai_autonomy_level = var.ai_autonomy_level
    max_agent_memory_kb = var.max_agent_memory_kb
    evolution_mode_enabled = var.enable_evolution_mode
    safety_threshold = 0.95
    checkpoint_interval_minutes = 10
    max_generations = 100
    population_size = 50
    mutation_rate = 0.1
    crossover_rate = 0.8
    selection_strategy = "tournament"
    fitness_function = "multi_objective"
    convergence_threshold = 0.001
  })

  description = "T-Developer Evolution Engine 핵심 설정"

  tags = merge(var.tags, {
    Name = "Evolution Engine Config"
    Type = "EngineConfiguration"
    Environment = var.environment
    Criticality = "High"
  })
}

# Evolution Safety System Configuration
resource "aws_ssm_parameter" "evolution_safety_config" {
  name  = "/${var.project_name}/${var.environment}/safety/system/config"
  type  = "SecureString"
  key_id = aws_kms_key.evolution_safety.arn

  value = jsonencode({
    emergency_stop_enabled = true
    malicious_pattern_detection = true
    safety_monitoring_interval_seconds = 30
    quarantine_threshold = 0.9
    auto_rollback_enabled = true
    safety_log_retention_days = 90
    critical_alert_channels = ["sns", "email"]
    monitoring_metrics = [
      "memory_usage",
      "cpu_utilization",
      "network_activity",
      "file_system_access",
      "api_call_frequency"
    ]
  })

  description = "T-Developer Evolution Safety System 설정"

  tags = merge(var.tags, {
    Name = "Safety System Config"
    Type = "SafetyConfiguration"
    Environment = var.environment
    SecurityLevel = "Critical"
  })
}

# ===== Agent Registry Configuration =====
# Agent 생명주기 및 레지스트리 관리

resource "aws_ssm_parameter" "agent_registry_config" {
  name  = "/${var.project_name}/${var.environment}/agents/registry/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    max_concurrent_agents = 10
    agent_timeout_minutes = 30
    agent_memory_limit_mb = 512
    agent_cpu_limit_cores = 1.0
    registry_cleanup_interval_hours = 24
    agent_versioning_enabled = true
    auto_scaling_enabled = true
    scaling_target_cpu_percent = 70
    scaling_min_instances = 1
    scaling_max_instances = 5
    health_check_interval_seconds = 60
    failed_agent_retry_count = 3
  })

  description = "T-Developer Agent Registry 설정"

  tags = merge(var.tags, {
    Name = "Agent Registry Config"
    Type = "AgentConfiguration"
    Environment = var.environment
  })
}

# ===== Database Configuration =====
# 데이터베이스 연결 및 성능 튜닝

resource "aws_ssm_parameter" "database_config" {
  name  = "/${var.project_name}/${var.environment}/database/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    connection_pool_size = 20
    connection_timeout_seconds = 30
    query_timeout_seconds = 60
    retry_attempts = 3
    backup_retention_days = 7
    maintenance_window = "sun:03:00-sun:04:00"
    monitoring_enabled = true
    slow_query_log_enabled = true
    slow_query_threshold_seconds = 2
    vacuum_schedule = "daily"
    analyze_schedule = "weekly"
  })

  description = "T-Developer Database 설정"

  tags = merge(var.tags, {
    Name = "Database Config"
    Type = "DatabaseConfiguration"
    Environment = var.environment
  })
}

# ===== API Configuration =====
# 외부 API 호출 설정 및 제한

resource "aws_ssm_parameter" "api_config" {
  name  = "/${var.project_name}/${var.environment}/api/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    openai_config = {
      model = "gpt-4"
      max_tokens = 4096
      temperature = 0.7
      timeout_seconds = 30
      rate_limit_per_minute = 60
      retry_attempts = 3
      retry_backoff_seconds = 2
    }
    anthropic_config = {
      model = "claude-3-sonnet-20240229"
      max_tokens = 4096
      temperature = 0.7
      timeout_seconds = 30
      rate_limit_per_minute = 50
      retry_attempts = 3
      retry_backoff_seconds = 2
    }
    bedrock_config = {
      region = var.aws_region
      timeout_seconds = 45
      retry_attempts = 3
      rate_limit_per_minute = 100
    }
  })

  description = "T-Developer 외부 API 설정"

  tags = merge(var.tags, {
    Name = "API Config"
    Type = "APIConfiguration"
    Environment = var.environment
  })
}

# ===== Monitoring & Logging Configuration =====
# 모니터링 및 로깅 설정

resource "aws_ssm_parameter" "monitoring_config" {
  name  = "/${var.project_name}/${var.environment}/monitoring/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    log_level = var.environment == "production" ? "INFO" : "DEBUG"
    log_retention_days = var.environment == "production" ? 30 : 7
    metrics_enabled = true
    metrics_interval_seconds = 60
    alerting_enabled = true
    alert_thresholds = {
      cpu_percent = 80
      memory_percent = 85
      disk_percent = 90
      error_rate_percent = 5
      response_time_ms = 2000
    }
    dashboard_enabled = true
    custom_metrics = [
      "evolution_generations_per_hour",
      "agent_success_rate",
      "safety_violations_count",
      "api_calls_per_minute"
    ]
  })

  description = "T-Developer 모니터링 및 로깅 설정"

  tags = merge(var.tags, {
    Name = "Monitoring Config"
    Type = "MonitoringConfiguration"
    Environment = var.environment
  })
}

# ===== Feature Flags =====
# 기능 플래그 및 실험 설정

resource "aws_ssm_parameter" "feature_flags" {
  name  = "/${var.project_name}/${var.environment}/features/flags"
  type  = "String"  # 비민감 데이터이므로 일반 문자열 사용

  value = jsonencode({
    # Core Features
    evolution_engine_enabled = var.enable_evolution_mode
    agent_auto_scaling_enabled = true
    safety_monitoring_enabled = true

    # Experimental Features
    advanced_mutation_enabled = var.environment != "production"
    neural_architecture_search_enabled = false
    quantum_optimization_enabled = false
    distributed_evolution_enabled = false

    # Development Features
    debug_mode_enabled = var.environment == "development"
    profiling_enabled = var.environment != "production"
    test_data_generation_enabled = var.environment != "production"

    # Security Features
    advanced_threat_detection_enabled = true
    behavior_analysis_enabled = true
    anomaly_detection_enabled = true

    # Performance Features
    caching_enabled = true
    compression_enabled = true
    cdn_enabled = var.environment == "production"

    # Integration Features
    slack_notifications_enabled = false
    email_notifications_enabled = true
    webhook_notifications_enabled = false
  })

  description = "T-Developer 기능 플래그 설정"

  tags = merge(var.tags, {
    Name = "Feature Flags"
    Type = "FeatureFlags"
    Environment = var.environment
  })
}

# ===== System Limits & Performance =====
# 시스템 제한 및 성능 튜닝 파라미터

resource "aws_ssm_parameter" "system_limits" {
  name  = "/${var.project_name}/${var.environment}/system/limits"
  type  = "String"

  value = jsonencode({
    # Resource Limits
    max_concurrent_evolutions = var.environment == "production" ? 5 : 2
    max_agent_instances = var.environment == "production" ? 50 : 10
    max_memory_per_agent_mb = var.max_agent_memory_kb * 1024
    max_cpu_per_agent_cores = 1.0
    max_disk_per_agent_gb = 10

    # Request Limits
    max_requests_per_second = var.environment == "production" ? 1000 : 100
    max_concurrent_requests = var.environment == "production" ? 500 : 50
    request_timeout_seconds = 30

    # Data Limits
    max_evolution_history_entries = 1000
    max_log_file_size_mb = 100
    max_checkpoint_age_hours = 24

    # Network Limits
    max_bandwidth_mbps = var.environment == "production" ? 1000 : 100
    connection_pool_size = var.environment == "production" ? 100 : 20
    keepalive_timeout_seconds = 300

    # Storage Limits
    max_s3_object_size_gb = 10
    s3_multipart_threshold_mb = 100
    s3_upload_timeout_minutes = 30
  })

  description = "T-Developer 시스템 제한 및 성능 설정"

  tags = merge(var.tags, {
    Name = "System Limits"
    Type = "PerformanceConfiguration"
    Environment = var.environment
  })
}

# ===== Environment-Specific Overrides =====
# 환경별 특화 설정 오버라이드

resource "aws_ssm_parameter" "environment_overrides" {
  name  = "/${var.project_name}/${var.environment}/overrides"
  type  = "String"

  value = jsonencode({
    # Development Environment
    development = {
      debug_enabled = true
      verbose_logging = true
      mock_external_apis = false
      bypass_safety_checks = false  # 안전을 위해 항상 false
      extended_timeouts = true
    }

    # Staging Environment
    staging = {
      debug_enabled = false
      verbose_logging = false
      mock_external_apis = false
      performance_testing_enabled = true
      load_testing_enabled = true
    }

    # Production Environment
    production = {
      debug_enabled = false
      verbose_logging = false
      strict_security_mode = true
      performance_optimization = true
      auto_scaling_aggressive = true
      backup_frequency_hours = 6
    }
  })

  description = "T-Developer 환경별 설정 오버라이드"

  tags = merge(var.tags, {
    Name = "Environment Overrides"
    Type = "EnvironmentConfiguration"
    Environment = var.environment
  })
}

# ===== Notification Configuration =====
# 알림 및 커뮤니케이션 설정

resource "aws_ssm_parameter" "notification_config" {
  name  = "/${var.project_name}/${var.environment}/notifications/config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    email_enabled = true
    sms_enabled = false
    slack_enabled = false
    webhook_enabled = false

    # Alert Levels
    critical_alerts = {
      channels = ["email", "sns"]
      frequency = "immediate"
      escalation_minutes = 5
    }
    warning_alerts = {
      channels = ["email"]
      frequency = "batched"
      batch_interval_minutes = 15
    }
    info_alerts = {
      channels = ["sns"]
      frequency = "daily_digest"
      digest_time = "09:00"
    }

    # Alert Types
    evolution_alerts_enabled = true
    safety_alerts_enabled = true
    performance_alerts_enabled = true
    security_alerts_enabled = true
    system_alerts_enabled = true
  })

  description = "T-Developer 알림 시스템 설정"

  tags = merge(var.tags, {
    Name = "Notification Config"
    Type = "NotificationConfiguration"
    Environment = var.environment
  })
}

# ===== Parameter Access Monitoring =====
# Parameter Store 접근 모니터링을 위한 CloudWatch 이벤트

resource "aws_cloudwatch_event_rule" "parameter_access" {
  name        = "${var.project_name}-parameter-access-monitor"
  description = "Monitor Parameter Store access events"

  event_pattern = jsonencode({
    source      = ["aws.ssm"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["ssm.amazonaws.com"]
      eventName = [
        "GetParameter",
        "GetParameters",
        "GetParametersByPath",
        "PutParameter",
        "DeleteParameter"
      ]
      requestParameters = {
        name = [{
          prefix = "/${var.project_name}/"
        }]
      }
    }
  })

  tags = var.tags
}

# Parameter 접근 이벤트를 SNS로 알림
resource "aws_cloudwatch_event_target" "parameter_access_notification" {
  rule      = aws_cloudwatch_event_rule.parameter_access.name
  target_id = "ParameterAccessNotification"
  arn       = aws_sns_topic.safety_alerts.arn
}

# ===== 출력값 =====
output "parameter_store" {
  description = "Parameter Store configuration"
  value = {
    evolution_engine_config = aws_ssm_parameter.evolution_engine_config.name
    safety_config = aws_ssm_parameter.evolution_safety_config.name
    agent_registry_config = aws_ssm_parameter.agent_registry_config.name
    database_config = aws_ssm_parameter.database_config.name
    api_config = aws_ssm_parameter.api_config.name
    monitoring_config = aws_ssm_parameter.monitoring_config.name
    feature_flags = aws_ssm_parameter.feature_flags.name
    system_limits = aws_ssm_parameter.system_limits.name
    environment_overrides = aws_ssm_parameter.environment_overrides.name
    notification_config = aws_ssm_parameter.notification_config.name
  }
}

output "parameter_hierarchy" {
  description = "Parameter Store 계층 구조 가이드"
  value = {
    structure = "/${var.project_name}/${var.environment}/{component}/{subcomponent}/{parameter}"
    examples = [
      "/${var.project_name}/development/evolution/engine/config",
      "/${var.project_name}/production/safety/system/config",
      "/${var.project_name}/staging/agents/registry/config"
    ]
    encryption = "KMS encrypted for sensitive parameters"
    monitoring = "CloudWatch Events + SNS notifications"
    access_control = "IAM role-based with least privilege"
  }
}
