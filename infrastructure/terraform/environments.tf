# T-Developer Multi-Environment Configuration
# dev/staging/prod 환경별 변수 분리 및 관리 시스템

# ===== Environment-Specific Variable Definitions =====
# 각 환경별로 다른 설정값들을 정의

locals {
  # 환경별 설정 맵핑
  environment_configs = {
    development = {
      # AI & Evolution Settings
      ai_autonomy_level = 0.7  # 개발환경에서는 낮은 자율성
      max_agent_memory_kb = 4.0  # 메모리 제한 완화
      evolution_mode_enabled = true
      safety_threshold = 0.90  # 개발을 위해 약간 낮춤
      checkpoint_interval_minutes = 5  # 더 자주 체크포인트
      max_generations = 50  # 제한된 세대수
      population_size = 20  # 작은 개체군 크기

      # Performance & Resource Settings
      max_concurrent_agents = 5
      max_concurrent_evolutions = 1
      agent_timeout_minutes = 15
      agent_memory_limit_mb = 256
      request_timeout_seconds = 30

      # Database Settings
      connection_pool_size = 10
      backup_retention_days = 3
      query_timeout_seconds = 30

      # Monitoring & Logging
      log_level = "DEBUG"
      log_retention_days = 7
      metrics_interval_seconds = 30
      alerting_enabled = true

      # Feature Flags
      debug_mode_enabled = true
      profiling_enabled = true
      advanced_mutation_enabled = true
      mock_external_apis = false

      # API Rate Limits
      openai_rate_limit_per_minute = 30
      anthropic_rate_limit_per_minute = 25
      bedrock_rate_limit_per_minute = 50

      # Security Settings
      strict_security_mode = false
      advanced_threat_detection = true
      session_timeout_minutes = 60
    }

    staging = {
      # AI & Evolution Settings
      ai_autonomy_level = 0.8  # 운영 환경에 가까운 설정
      max_agent_memory_kb = 6.0
      evolution_mode_enabled = true
      safety_threshold = 0.93
      checkpoint_interval_minutes = 8
      max_generations = 75
      population_size = 35

      # Performance & Resource Settings
      max_concurrent_agents = 8
      max_concurrent_evolutions = 2
      agent_timeout_minutes = 20
      agent_memory_limit_mb = 384
      request_timeout_seconds = 25

      # Database Settings
      connection_pool_size = 15
      backup_retention_days = 5
      query_timeout_seconds = 45

      # Monitoring & Logging
      log_level = "INFO"
      log_retention_days = 14
      metrics_interval_seconds = 60
      alerting_enabled = true

      # Feature Flags
      debug_mode_enabled = false
      profiling_enabled = true
      advanced_mutation_enabled = true
      mock_external_apis = false

      # API Rate Limits
      openai_rate_limit_per_minute = 50
      anthropic_rate_limit_per_minute = 40
      bedrock_rate_limit_per_minute = 75

      # Security Settings
      strict_security_mode = true
      advanced_threat_detection = true
      session_timeout_minutes = 45
    }

    production = {
      # AI & Evolution Settings
      ai_autonomy_level = 0.85  # 최대 자율성
      max_agent_memory_kb = 6.5  # 최대 성능
      evolution_mode_enabled = true
      safety_threshold = 0.95  # 최고 안전성
      checkpoint_interval_minutes = 10
      max_generations = 100
      population_size = 50

      # Performance & Resource Settings
      max_concurrent_agents = 20
      max_concurrent_evolutions = 5
      agent_timeout_minutes = 30
      agent_memory_limit_mb = 512
      request_timeout_seconds = 20

      # Database Settings
      connection_pool_size = 25
      backup_retention_days = 14
      query_timeout_seconds = 60

      # Monitoring & Logging
      log_level = "WARN"
      log_retention_days = 30
      metrics_interval_seconds = 120
      alerting_enabled = true

      # Feature Flags
      debug_mode_enabled = false
      profiling_enabled = false
      advanced_mutation_enabled = false  # 안정성을 위해 비활성화
      mock_external_apis = false

      # API Rate Limits
      openai_rate_limit_per_minute = 100
      anthropic_rate_limit_per_minute = 80
      bedrock_rate_limit_per_minute = 150

      # Security Settings
      strict_security_mode = true
      advanced_threat_detection = true
      session_timeout_minutes = 30
    }
  }

  # 현재 환경 설정 선택
  current_env_config = local.environment_configs[var.environment]
}

# ===== Environment-Specific Evolution Engine Configuration =====
resource "aws_ssm_parameter" "env_evolution_engine_config" {
  name  = "/${var.project_name}/${var.environment}/evolution/engine/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    environment = var.environment
    ai_autonomy_level = local.current_env_config.ai_autonomy_level
    max_agent_memory_kb = local.current_env_config.max_agent_memory_kb
    safety_threshold = local.current_env_config.safety_threshold
    checkpoint_interval_minutes = local.current_env_config.checkpoint_interval_minutes
    max_generations = local.current_env_config.max_generations
    population_size = local.current_env_config.population_size

    # Evolution Algorithm Parameters (환경별 다름)
    mutation_rate = var.environment == "production" ? 0.05 : 0.1
    crossover_rate = var.environment == "production" ? 0.9 : 0.8
    selection_pressure = var.environment == "production" ? 1.2 : 1.0
    diversity_threshold = var.environment == "production" ? 0.8 : 0.7

    # Performance Optimization (환경별)
    parallel_evolution = var.environment == "production" ? true : false
    gpu_acceleration = var.environment == "production" ? true : false
    memory_optimization = var.environment == "production" ? "aggressive" : "balanced"
  })

  description = "T-Developer Evolution Engine ${var.environment} 환경 설정"

  tags = merge(var.tags, {
    Name = "Evolution Engine Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
    Criticality = "High"
  })
}

# ===== Environment-Specific Agent Configuration =====
resource "aws_ssm_parameter" "env_agent_config" {
  name  = "/${var.project_name}/${var.environment}/agents/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    environment = var.environment
    max_concurrent_agents = local.current_env_config.max_concurrent_agents
    agent_timeout_minutes = local.current_env_config.agent_timeout_minutes
    agent_memory_limit_mb = local.current_env_config.agent_memory_limit_mb

    # Environment-specific Agent Policies
    auto_scaling_policy = {
      enabled = var.environment == "production" ? true : var.environment == "staging"
      min_instances = var.environment == "production" ? 2 : 1
      max_instances = local.current_env_config.max_concurrent_agents
      target_cpu_percent = var.environment == "production" ? 60 : 70
      scale_up_cooldown_seconds = var.environment == "production" ? 180 : 300
      scale_down_cooldown_seconds = var.environment == "production" ? 300 : 600
    }

    # Resource Allocation Strategy
    resource_strategy = var.environment == "production" ? "performance" : "cost_optimized"
    health_check_strategy = var.environment == "production" ? "comprehensive" : "basic"

    # Agent Communication Settings
    communication_timeout_seconds = local.current_env_config.request_timeout_seconds
    retry_policy = {
      max_retries = var.environment == "production" ? 5 : 3
      backoff_strategy = "exponential"
      initial_delay_ms = 100
      max_delay_ms = var.environment == "production" ? 5000 : 2000
    }
  })

  description = "T-Developer Agent ${var.environment} 환경별 설정"

  tags = merge(var.tags, {
    Name = "Agent Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
  })
}

# ===== Environment-Specific Database Configuration =====
resource "aws_ssm_parameter" "env_database_config" {
  name  = "/${var.project_name}/${var.environment}/database/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    environment = var.environment
    connection_pool_size = local.current_env_config.connection_pool_size
    backup_retention_days = local.current_env_config.backup_retention_days
    query_timeout_seconds = local.current_env_config.query_timeout_seconds

    # Environment-specific Database Settings
    performance_insights = var.environment == "production" ? true : false
    multi_az_deployment = var.environment == "production" ? true : false
    backup_window = var.environment == "production" ? "03:00-04:00" : "02:00-03:00"
    maintenance_window = var.environment == "production" ? "sun:04:00-sun:05:00" : "sun:03:00-sun:04:00"

    # Connection Management
    connection_lifetime_seconds = var.environment == "production" ? 3600 : 1800
    idle_timeout_seconds = var.environment == "production" ? 600 : 300

    # Monitoring & Alerting
    slow_query_threshold_seconds = var.environment == "production" ? 1 : 2
    deadlock_timeout_seconds = var.environment == "production" ? 10 : 30
    lock_timeout_seconds = var.environment == "production" ? 30 : 60
  })

  description = "T-Developer Database ${var.environment} 환경별 설정"

  tags = merge(var.tags, {
    Name = "Database Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
  })
}

# ===== Environment-Specific API Configuration =====
resource "aws_ssm_parameter" "env_api_config" {
  name  = "/${var.project_name}/${var.environment}/api/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    environment = var.environment

    # Rate Limiting (환경별 다른 제한)
    openai_config = {
      rate_limit_per_minute = local.current_env_config.openai_rate_limit_per_minute
      burst_limit = local.current_env_config.openai_rate_limit_per_minute * 2
      timeout_seconds = local.current_env_config.request_timeout_seconds
    }
    anthropic_config = {
      rate_limit_per_minute = local.current_env_config.anthropic_rate_limit_per_minute
      burst_limit = local.current_env_config.anthropic_rate_limit_per_minute * 2
      timeout_seconds = local.current_env_config.request_timeout_seconds
    }
    bedrock_config = {
      rate_limit_per_minute = local.current_env_config.bedrock_rate_limit_per_minute
      burst_limit = local.current_env_config.bedrock_rate_limit_per_minute * 2
      timeout_seconds = local.current_env_config.request_timeout_seconds + 15
    }

    # Circuit Breaker Settings (환경별)
    circuit_breaker = {
      failure_threshold = var.environment == "production" ? 5 : 10
      recovery_timeout_seconds = var.environment == "production" ? 60 : 30
      half_open_max_calls = var.environment == "production" ? 3 : 5
    }

    # Caching Strategy (환경별)
    caching_strategy = {
      enabled = var.environment == "development" ? false : true
      ttl_seconds = var.environment == "production" ? 3600 : 1800
      max_cache_size_mb = var.environment == "production" ? 1024 : 512
    }
  })

  description = "T-Developer API ${var.environment} 환경별 설정"

  tags = merge(var.tags, {
    Name = "API Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
  })
}

# ===== Environment-Specific Monitoring Configuration =====
resource "aws_ssm_parameter" "env_monitoring_config" {
  name  = "/${var.project_name}/${var.environment}/monitoring/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.parameter_store.arn

  value = jsonencode({
    environment = var.environment
    log_level = local.current_env_config.log_level
    log_retention_days = local.current_env_config.log_retention_days
    metrics_interval_seconds = local.current_env_config.metrics_interval_seconds

    # Environment-specific Alert Thresholds
    alert_thresholds = {
      cpu_percent = var.environment == "production" ? 70 : 85
      memory_percent = var.environment == "production" ? 75 : 90
      disk_percent = var.environment == "production" ? 80 : 90
      error_rate_percent = var.environment == "production" ? 1 : 5
      response_time_ms = var.environment == "production" ? 1000 : 3000

      # Evolution-specific Thresholds
      evolution_failure_rate = var.environment == "production" ? 0.05 : 0.1
      agent_creation_failure_rate = var.environment == "production" ? 0.02 : 0.05
      safety_violation_rate = 0.01  # 모든 환경에서 동일하게 엄격
    }

    # Dashboard Configuration
    dashboard_config = {
      auto_refresh_seconds = var.environment == "production" ? 30 : 60
      detailed_metrics = var.environment != "development"
      real_time_alerts = var.environment == "production"
      historical_data_days = var.environment == "production" ? 90 : 30
    }

    # Trace and Debug Settings
    tracing_config = {
      enabled = local.current_env_config.profiling_enabled
      sample_rate = var.environment == "production" ? 0.1 : 1.0
      detailed_traces = var.environment == "development"
    }
  })

  description = "T-Developer Monitoring ${var.environment} 환경별 설정"

  tags = merge(var.tags, {
    Name = "Monitoring Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
  })
}

# ===== Environment-Specific Security Configuration =====
resource "aws_ssm_parameter" "env_security_config" {
  name  = "/${var.project_name}/${var.environment}/security/env-specific-config"
  type  = "SecureString"
  key_id = aws_kms_key.evolution_safety.arn  # 보안 설정은 최고 보안 키 사용

  value = jsonencode({
    environment = var.environment
    strict_security_mode = local.current_env_config.strict_security_mode
    session_timeout_minutes = local.current_env_config.session_timeout_minutes

    # Authentication & Authorization
    auth_config = {
      password_policy = {
        min_length = var.environment == "production" ? 12 : 8
        require_uppercase = true
        require_lowercase = true
        require_numbers = true
        require_symbols = var.environment == "production" ? true : false
        max_age_days = var.environment == "production" ? 90 : 180
      }

      session_management = {
        max_concurrent_sessions = var.environment == "production" ? 1 : 3
        idle_timeout_minutes = local.current_env_config.session_timeout_minutes
        absolute_timeout_hours = var.environment == "production" ? 8 : 24
      }

      mfa_settings = {
        required = var.environment == "production" ? true : false
        backup_codes = var.environment == "production" ? 10 : 5
        remember_device_days = var.environment == "production" ? 7 : 30
      }
    }

    # Network Security
    network_security = {
      ip_whitelist_enabled = var.environment == "production"
      rate_limiting_strict = var.environment == "production"
      ddos_protection = var.environment == "production" ? "enhanced" : "basic"
      ssl_only = true  # 모든 환경에서 필수
      min_tls_version = "1.2"
    }

    # Data Protection
    data_protection = {
      encryption_at_rest = "AES-256"  # 모든 환경 동일
      encryption_in_transit = "TLS-1.2+"  # 모든 환경 동일
      data_classification_required = var.environment == "production"
      pii_detection_enabled = true
      data_masking_enabled = var.environment != "development"
    }
  })

  description = "T-Developer Security ${var.environment} 환경별 설정"

  tags = merge(var.tags, {
    Name = "Security Environment Config"
    Type = "EnvironmentSpecificConfiguration"
    Environment = var.environment
    SecurityLevel = "Critical"
  })
}

# ===== Environment Validation Rules =====
# 환경별 설정값 검증을 위한 CloudWatch Metric Filter

resource "aws_cloudwatch_log_metric_filter" "environment_config_errors" {
  name           = "${var.project_name}-${var.environment}-config-errors"
  log_group_name = aws_cloudwatch_log_group.registry_logs.name
  pattern        = "ERROR environment configuration"

  metric_transformation {
    name      = "EnvironmentConfigErrors"
    namespace = "T-Developer/${title(var.environment)}/Config"
    value     = "1"
  }
}

# 환경별 설정 오류 알림
resource "aws_cloudwatch_metric_alarm" "environment_config_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-config-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "EnvironmentConfigErrors"
  namespace           = "T-Developer/${title(var.environment)}/Config"
  period             = "300"
  statistic          = "Sum"
  threshold          = "1"
  alarm_description  = "${title(var.environment)} 환경 설정 오류 발생"
  alarm_actions      = [
    var.environment == "production" ? aws_sns_topic.emergency_alerts.arn : aws_sns_topic.safety_alerts.arn
  ]

  tags = var.tags
}

# ===== 출력값 =====
output "environment_configuration" {
  description = "Environment-specific configuration summary"
  value = {
    environment = var.environment
    ai_autonomy_level = local.current_env_config.ai_autonomy_level
    max_agents = local.current_env_config.max_concurrent_agents
    security_mode = local.current_env_config.strict_security_mode ? "strict" : "standard"
    monitoring_level = local.current_env_config.log_level
    feature_flags_count = length([
      for k, v in local.current_env_config : k if k == "debug_mode_enabled" || k == "profiling_enabled" || k == "advanced_mutation_enabled"
    ])
  }
}

output "environment_parameters" {
  description = "Environment-specific parameter paths"
  value = {
    evolution_config = aws_ssm_parameter.env_evolution_engine_config.name
    agent_config = aws_ssm_parameter.env_agent_config.name
    database_config = aws_ssm_parameter.env_database_config.name
    api_config = aws_ssm_parameter.env_api_config.name
    monitoring_config = aws_ssm_parameter.env_monitoring_config.name
    security_config = aws_ssm_parameter.env_security_config.name
  }
}

output "environment_deployment_guide" {
  description = "다른 환경 배포 가이드"
  value = <<-EOT
  🔧 다른 환경 배포 방법:

  Staging 환경:
  terraform workspace new staging
  terraform apply -var="environment=staging"

  Production 환경:
  terraform workspace new production
  terraform apply -var="environment=production"

  환경별 차이점:
  - AI 자율성: dev(70%) < staging(80%) < production(85%)
  - 리소스: dev(5 agents) < staging(8 agents) < production(20 agents)
  - 보안: dev(표준) < staging(강화) < production(최고)
  - 모니터링: dev(DEBUG) < staging(INFO) < production(WARN)
  EOT
}
