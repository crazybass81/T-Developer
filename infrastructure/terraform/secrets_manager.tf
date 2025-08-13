# T-Developer AWS Secrets Manager 설정
# API 키, 데이터베이스 비밀번호 등 민감한 정보 관리

# ===== OpenAI API Key =====
# Evolution Engine에서 사용할 OpenAI GPT 모델 접근용
resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${var.project_name}/evolution/openai-api-key"
  description             = "OpenAI API key for T-Developer Evolution Engine"
  kms_key_id              = aws_kms_key.secrets_manager.arn
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "OpenAI API Key"
    Type = "APICredentials"
    Service = "OpenAI"
    Purpose = "EvolutionEngine"
  })
}

# OpenAI API Key 버전 (실제 값은 수동으로 설정)
resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = jsonencode({
    api_key = "PLACEHOLDER_OPENAI_API_KEY"
    model = "gpt-4"
    max_tokens = 4096
    temperature = 0.7
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# ===== Anthropic API Key =====
# Claude 모델 접근용 (Bedrock 대신 직접 API 사용시)
resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name                    = "${var.project_name}/evolution/anthropic-api-key"
  description             = "Anthropic Claude API key for T-Developer Evolution Engine"
  kms_key_id              = aws_kms_key.secrets_manager.arn
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "Anthropic API Key"
    Type = "APICredentials"
    Service = "Anthropic"
    Purpose = "EvolutionEngine"
  })
}

resource "aws_secretsmanager_secret_version" "anthropic_api_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_api_key.id
  secret_string = jsonencode({
    api_key = "PLACEHOLDER_ANTHROPIC_API_KEY"
    model = "claude-3-sonnet-20240229"
    max_tokens = 4096
    temperature = 0.7
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# ===== Evolution System 마스터 키 =====
# Agent 간 통신, 데이터 서명 등에 사용
resource "aws_secretsmanager_secret" "evolution_master_secret" {
  name                    = "${var.project_name}/evolution/master-secret"
  description             = "Master secret for T-Developer Evolution System internal authentication"
  kms_key_id              = aws_kms_key.secrets_manager.arn
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "Evolution Master Secret"
    Type = "SystemCredentials"
    Service = "EvolutionEngine"
    Purpose = "InternalAuth"
    SecurityLevel = "Critical"
  })
}

# 마스터 시크릿 생성 (랜덤 생성)
resource "aws_secretsmanager_secret_version" "evolution_master_secret" {
  secret_id = aws_secretsmanager_secret.evolution_master_secret.id
  secret_string = jsonencode({
    master_key = random_password.evolution_master_key.result
    jwt_secret = random_password.jwt_secret.result
    encryption_salt = random_password.encryption_salt.result
    created_at = timestamp()
  })
}

# 랜덤 비밀번호 생성
resource "random_password" "evolution_master_key" {
  length  = 64
  special = true
}

resource "random_password" "jwt_secret" {
  length  = 32
  special = false  # JWT는 특수문자 제외
}

resource "random_password" "encryption_salt" {
  length  = 32
  special = false
}

# ===== Database 접속 정보 =====
# 추후 RDS/PostgreSQL 사용시를 위한 준비
resource "aws_secretsmanager_secret" "database_credentials" {
  name                    = "${var.project_name}/database/credentials"
  description             = "Database connection credentials for T-Developer Evolution System"
  kms_key_id              = aws_kms_key.secrets_manager.arn
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "Database Credentials"
    Type = "DatabaseCredentials"
    Service = "PostgreSQL"
    Purpose = "EvolutionData"
  })
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    engine = "postgres"
    host = "localhost"
    port = 5432
    dbname = "t_developer_evolution"
    username = "t_developer_user"
    password = random_password.db_password.result
  })
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# ===== Agent 통신 암호화 키 =====
# Evolution Engine과 Agent 간 통신 암호화
resource "aws_secretsmanager_secret" "agent_communication_key" {
  name                    = "${var.project_name}/agents/communication-key"
  description             = "Encryption key for secure communication between Evolution Engine and Agents"
  kms_key_id              = aws_kms_key.secrets_manager.arn
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "Agent Communication Key"
    Type = "EncryptionKey"
    Service = "AgentCommunication"
    Purpose = "SecureMessaging"
  })
}

resource "aws_secretsmanager_secret_version" "agent_communication_key" {
  secret_id = aws_secretsmanager_secret.agent_communication_key.id
  secret_string = jsonencode({
    symmetric_key = random_password.agent_comm_key.result
    algorithm = "AES-256-GCM"
    key_derivation = "PBKDF2"
    iterations = 100000
  })
}

resource "random_password" "agent_comm_key" {
  length = 32
  special = false
}

# ===== Evolution Safety 시크릿 =====
# Safety System 전용 비밀 (최고 보안 등급)
resource "aws_secretsmanager_secret" "safety_system_secret" {
  name                    = "${var.project_name}/safety/system-secret"
  description             = "Critical security secret for Evolution Safety System"
  kms_key_id              = aws_kms_key.evolution_safety.arn  # Safety 전용 KMS 키 사용
  recovery_window_in_days = 30

  # 자동 rotation 설정은 별도 리소스로 구성 (추후 구현)

  tags = merge(var.tags, {
    Name = "Safety System Secret"
    Type = "SafetyCredentials"
    Service = "EvolutionSafety"
    Purpose = "SafetyMonitoring"
    SecurityLevel = "Critical"
  })
}

resource "aws_secretsmanager_secret_version" "safety_system_secret" {
  secret_id = aws_secretsmanager_secret.safety_system_secret.id
  secret_string = jsonencode({
    emergency_stop_token = random_password.emergency_stop_token.result
    safety_override_key = random_password.safety_override_key.result
    quarantine_key = random_password.quarantine_key.result
    alert_signing_key = random_password.alert_signing_key.result
  })
}

resource "random_password" "emergency_stop_token" {
  length = 64
  special = true
}

resource "random_password" "safety_override_key" {
  length = 32
  special = false
}

resource "random_password" "quarantine_key" {
  length = 32
  special = false
}

resource "random_password" "alert_signing_key" {
  length = 32
  special = false
}

# ===== 접근 로그 모니터링 =====
# Secrets Manager 접근 이벤트를 CloudWatch로 전송
resource "aws_cloudwatch_event_rule" "secrets_access" {
  name        = "${var.project_name}-secrets-access-monitor"
  description = "Monitor Secrets Manager access events"

  event_pattern = jsonencode({
    source      = ["aws.secretsmanager"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["secretsmanager.amazonaws.com"]
      eventName = [
        "GetSecretValue",
        "BatchGetSecretValue",
        "RotateSecret",
        "UpdateSecret",
        "PutSecretValue"
      ]
    }
  })

  tags = var.tags
}

# Secrets 접근 로그를 SNS로 알림
resource "aws_cloudwatch_event_target" "secrets_access_notification" {
  rule      = aws_cloudwatch_event_rule.secrets_access.name
  target_id = "SecretsAccessNotification"
  arn       = aws_sns_topic.safety_alerts.arn
}

# ===== 비밀 복제 (Multi-Region) =====
# 재해 복구를 위한 다른 리전 복제 설정 (향후 구현 예정)
# 현재는 단일 리전에서만 운영

# ===== 출력값 =====
output "secrets_manager" {
  description = "Secrets Manager configuration"
  value = {
    openai_secret_arn = aws_secretsmanager_secret.openai_api_key.arn
    anthropic_secret_arn = aws_secretsmanager_secret.anthropic_api_key.arn
    evolution_master_secret_arn = aws_secretsmanager_secret.evolution_master_secret.arn
    database_secret_arn = aws_secretsmanager_secret.database_credentials.arn
    agent_comm_secret_arn = aws_secretsmanager_secret.agent_communication_key.arn
    safety_secret_arn = aws_secretsmanager_secret.safety_system_secret.arn
  }
  sensitive = true
}

output "secret_rotation_schedule" {
  description = "Secret rotation schedule"
  value = {
    api_keys = "180 days"
    system_secrets = "90 days"
    database = "30 days"
    safety_secrets = "30 days"
    agent_communication = "60 days"
  }
}
