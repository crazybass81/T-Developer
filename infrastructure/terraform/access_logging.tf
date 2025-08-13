# T-Developer Access Logging Configuration
# 보안 모니터링 및 감사를 위한 종합 접근 로그 시스템

# ===== CloudTrail for AWS API Logging =====
# 모든 AWS API 호출 로깅 및 보안 감사

# CloudTrail 로그 저장용 S3 버킷
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "${var.project_name}-cloudtrail-logs-${var.environment}-${local.deployment_id}"

  tags = merge(var.tags, {
    Name = "T-Developer CloudTrail Logs"
    Type = "SecurityLogging"
    Purpose = "AuditTrail"
  })
}

# CloudTrail S3 버킷 버전 관리
resource "aws_s3_bucket_versioning" "cloudtrail_versioning" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CloudTrail S3 버킷 암호화 (안전 KMS 키 사용)
resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_encryption" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evolution_safety.arn
    }
    bucket_key_enabled = true
  }
}

# CloudTrail S3 버킷 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "cloudtrail_pab" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudTrail S3 버킷 정책
resource "aws_s3_bucket_policy" "cloudtrail_policy" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/${var.project_name}-security-trail"
          }
        }
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
            "aws:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/${var.project_name}-security-trail"
          }
        }
      }
    ]
  })
}

# CloudTrail 설정
resource "aws_cloudtrail" "security_trail" {
  name           = "${var.project_name}-security-trail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_logs.id
  s3_key_prefix  = "cloudtrail-logs"

  # 모든 리전에서 로깅 활성화
  is_multi_region_trail = true

  # 관리 이벤트 및 데이터 이벤트 모두 기록
  include_global_service_events = true

  # 로그 파일 검증 활성화 (무결성 보장)
  enable_log_file_validation = true

  # KMS 암호화
  kms_key_id = aws_kms_key.evolution_safety.arn

  # 중요한 데이터 이벤트 로깅 설정
  event_selector {
    read_write_type           = "All"
    include_management_events = true

    # S3 데이터 이벤트 로깅
    data_resource {
      type = "AWS::S3::Object"
      values = [
        "${aws_s3_bucket.evolution_storage.arn}/*",
        "${aws_s3_bucket.agents_storage.arn}/*"
      ]
    }

    # DynamoDB 데이터 이벤트 로깅
    data_resource {
      type = "AWS::DynamoDB::Table"
      values = [aws_dynamodb_table.evolution_state.arn]
    }
  }

  # Insight 이벤트 로깅 (비정상 활동 감지)
  insight_selector {
    insight_type = "ApiCallRateInsight"
  }

  depends_on = [aws_s3_bucket_policy.cloudtrail_policy]

  tags = merge(var.tags, {
    Name = "T-Developer Security Trail"
    Type = "SecurityAudit"
    CriticalityLevel = "High"
  })
}

# ===== VPC Flow Logs =====
# 네트워크 트래픽 모니터링

# VPC Flow Logs용 CloudWatch Log Group
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  name              = "/aws/t-developer/vpc-flow-logs/${var.environment}"
  retention_in_days = var.environment == "production" ? 90 : 30
  kms_key_id        = aws_kms_key.evolution_safety.arn

  tags = merge(var.tags, {
    Name = "T-Developer VPC Flow Logs"
    Type = "NetworkLogging"
    SecurityLevel = "Critical"
  })
}

# VPC Flow Logs IAM Role
resource "aws_iam_role" "flow_logs_role" {
  name = "${var.project_name}-flow-logs-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Flow Logs 정책
resource "aws_iam_role_policy" "flow_logs_policy" {
  name = "${var.project_name}-flow-logs-policy"
  role = aws_iam_role.flow_logs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# VPC Flow Logs 활성화
resource "aws_flow_log" "vpc_flow_logs" {
  iam_role_arn    = aws_iam_role.flow_logs_role.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = data.aws_vpc.existing.id

  # 상세 로깅 포맷 (보안 분석용)
  log_format = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${windowstart} $${windowend} $${action} $${flowlogstatus} $${vpc-id} $${subnet-id} $${instance-id} $${tcp-flags} $${type} $${pkt-srcaddr} $${pkt-dstaddr} $${region} $${az-id}"

  tags = merge(var.tags, {
    Name = "T-Developer VPC Flow Logs"
    Type = "NetworkSecurity"
  })
}

# ===== S3 Access Logging =====
# S3 버킷 접근 로깅

# S3 액세스 로그 저장용 버킷
resource "aws_s3_bucket" "access_logs" {
  bucket = "${var.project_name}-access-logs-${var.environment}-${local.deployment_id}"

  tags = merge(var.tags, {
    Name = "T-Developer Access Logs"
    Type = "AccessLogging"
    Purpose = "SecurityAudit"
  })
}

# Access Log 버킷 암호화
resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs_encryption" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evolution_safety.arn
    }
    bucket_key_enabled = true
  }
}

# Access Log 버킷 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "access_logs_pab" {
  bucket = aws_s3_bucket.access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Evolution Storage 버킷 액세스 로깅 활성화
resource "aws_s3_bucket_logging" "evolution_storage_logging" {
  bucket = aws_s3_bucket.evolution_storage.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "evolution-storage/"

  # 더 상세한 로깅을 위한 이벤트 설정
  target_object_key_format {
    partitioned_prefix {
      partition_date_source = "EventTime"
    }
  }
}

# Agents Storage 버킷 액세스 로깅 활성화
resource "aws_s3_bucket_logging" "agents_storage_logging" {
  bucket = aws_s3_bucket.agents_storage.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "agents-storage/"

  target_object_key_format {
    partitioned_prefix {
      partition_date_source = "EventTime"
    }
  }
}

# ===== 액세스 로그 분석 및 알림 =====
# 의심스러운 활동 감지

# 의심스러운 API 호출 패턴 감지
resource "aws_cloudwatch_log_metric_filter" "suspicious_api_calls" {
  name           = "${var.project_name}-suspicious-api-calls"
  log_group_name = "/aws/cloudtrail/${var.project_name}-security-trail"
  pattern        = "[version, account, time, region, source, event=\"ConsoleLogin\", responseElements.ConsoleLogin=\"Failure\", ...]"

  metric_transformation {
    name      = "SuspiciousAPILoginFailures"
    namespace = "T-Developer/${title(var.environment)}/Security"
    value     = "1"

    # 추가 메트릭 정보
    default_value = "0"
  }
}

# 비정상적인 Secrets Manager 접근 감지
resource "aws_cloudwatch_log_metric_filter" "unusual_secrets_access" {
  name           = "${var.project_name}-unusual-secrets-access"
  log_group_name = "/aws/cloudtrail/${var.project_name}-security-trail"
  pattern        = "[version, account, time, region, source, event=\"GetSecretValue\", errorCode=\"AccessDenied\", ...]"

  metric_transformation {
    name      = "UnauthorizedSecretsAccess"
    namespace = "T-Developer/${title(var.environment)}/Security"
    value     = "1"
  }
}

# 대량 데이터 다운로드 감지 (VPC Flow Logs)
resource "aws_cloudwatch_log_metric_filter" "large_data_transfer" {
  name           = "${var.project_name}-large-data-transfer"
  log_group_name = aws_cloudwatch_log_group.vpc_flow_logs.name
  pattern        = "[version, account, eni, source, destination, srcport, destport, protocol, packets=\">100000\", bytes=\">104857600\", ...]"

  metric_transformation {
    name      = "LargeDataTransfer"
    namespace = "T-Developer/${title(var.environment)}/Network"
    value     = "1"
  }
}

# 비정상적인 네트워크 트래픽 패턴 감지
resource "aws_cloudwatch_log_metric_filter" "unusual_network_patterns" {
  name           = "${var.project_name}-unusual-network-patterns"
  log_group_name = aws_cloudwatch_log_group.vpc_flow_logs.name
  pattern        = "[version, account, eni, source!=\"172.31.*\", destination, srcport, destport, protocol, packets, bytes, windowstart, windowend, action=\"REJECT\", ...]"

  metric_transformation {
    name      = "UnusualNetworkActivity"
    namespace = "T-Developer/${title(var.environment)}/Network"
    value     = "1"
  }
}

# ===== 보안 알림 =====
# 의심스러운 활동에 대한 자동 알림

# 의심스러운 API 호출 알림
resource "aws_cloudwatch_metric_alarm" "suspicious_api_calls_alarm" {
  alarm_name          = "${var.project_name}-suspicious-api-calls"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "SuspiciousAPILoginFailures"
  namespace           = "T-Developer/${title(var.environment)}/Security"
  period             = "300"
  statistic          = "Sum"
  threshold          = "5"
  alarm_description  = "의심스러운 API 호출 패턴 감지"
  alarm_actions      = [aws_sns_topic.emergency_alerts.arn]
  ok_actions         = [aws_sns_topic.safety_alerts.arn]

  tags = var.tags
}

# 비인가 Secrets 접근 알림
resource "aws_cloudwatch_metric_alarm" "unauthorized_secrets_alarm" {
  alarm_name          = "${var.project_name}-unauthorized-secrets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "UnauthorizedSecretsAccess"
  namespace           = "T-Developer/${title(var.environment)}/Security"
  period             = "60"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "비인가 Secrets Manager 접근 시도 감지"
  alarm_actions      = [aws_sns_topic.emergency_alerts.arn]

  tags = var.tags
}

# 대량 데이터 전송 알림
resource "aws_cloudwatch_metric_alarm" "large_data_transfer_alarm" {
  alarm_name          = "${var.project_name}-large-data-transfer"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "LargeDataTransfer"
  namespace           = "T-Developer/${title(var.environment)}/Network"
  period             = "300"
  statistic          = "Sum"
  threshold          = "10"  # 5분 내 10회 이상 대량 전송
  alarm_description  = "비정상적인 대량 데이터 전송 감지"
  alarm_actions      = [aws_sns_topic.safety_alerts.arn]

  tags = var.tags
}

# 비정상 네트워크 활동 알림
resource "aws_cloudwatch_metric_alarm" "unusual_network_alarm" {
  alarm_name          = "${var.project_name}-unusual-network-activity"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "UnusualNetworkActivity"
  namespace           = "T-Developer/${title(var.environment)}/Network"
  period             = "300"
  statistic          = "Sum"
  threshold          = "50"
  alarm_description  = "비정상적인 네트워크 활동 패턴 감지"
  alarm_actions      = [aws_sns_topic.safety_alerts.arn]

  tags = var.tags
}

# ===== 액세스 로그 분석 대시보드 =====
# CloudWatch 대시보드로 보안 상황 시각화

resource "aws_cloudwatch_dashboard" "security_dashboard" {
  dashboard_name = "${var.project_name}-security-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["T-Developer/${title(var.environment)}/Security", "SuspiciousAPILoginFailures"],
            [".", "UnauthorizedSecretsAccess"],
            ["T-Developer/${title(var.environment)}/Network", "LargeDataTransfer"],
            [".", "UnusualNetworkActivity"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Security Events Overview"
          period  = 300
          stat    = "Sum"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query = "SOURCE '/aws/cloudtrail/${var.project_name}-security-trail' | fields @timestamp, sourceIPAddress, eventName, userIdentity.type, errorMessage\n| filter eventName like /GetSecretValue|PutObject|GetObject/\n| sort @timestamp desc\n| limit 100"
          region = var.aws_region
          title = "Recent Security-Related Events"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          query = "SOURCE '${aws_cloudwatch_log_group.vpc_flow_logs.name}' | fields @timestamp, srcaddr, dstaddr, srcport, dstport, protocol, action\n| filter action = \"REJECT\"\n| sort @timestamp desc\n| limit 50"
          region = var.aws_region
          title = "Blocked Network Traffic"
        }
      }
    ]
  })
}

# ===== 로그 보존 및 아카이브 정책 =====
# 장기 보관을 위한 S3 Intelligent Tiering

resource "aws_s3_bucket_intelligent_tiering_configuration" "cloudtrail_tiering" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  name   = "EntireBucket"

  status = "Enabled"

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }
}

# 액세스 로그 Lifecycle 정책
resource "aws_s3_bucket_lifecycle_configuration" "access_logs_lifecycle" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    id     = "security_logs_lifecycle"
    status = "Enabled"

    filter {
      prefix = ""  # 모든 객체에 적용
    }

    # 30일 후 IA로 전환
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # 90일 후 Glacier로 전환
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # 1년 후 Deep Archive로 전환
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # 보안 규정에 따른 보존 기간 (환경별 차이)
    expiration {
      days = var.environment == "production" ? 2557 : 1095  # 7년 vs 3년
    }
  }
}

# ===== 출력값 =====
output "access_logging_configuration" {
  description = "Access logging configuration summary"
  value = {
    cloudtrail_arn = aws_cloudtrail.security_trail.arn
    cloudtrail_bucket = aws_s3_bucket.cloudtrail_logs.id
    vpc_flow_logs_group = aws_cloudwatch_log_group.vpc_flow_logs.name
    access_logs_bucket = aws_s3_bucket.access_logs.id
    security_dashboard = aws_cloudwatch_dashboard.security_dashboard.dashboard_name
    monitoring_enabled = {
      api_calls = true
      secrets_access = true
      network_traffic = true
      data_transfer = true
    }
  }
}

output "security_monitoring_endpoints" {
  description = "보안 모니터링 엔드포인트"
  value = {
    dashboard_url = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.security_dashboard.dashboard_name}"
    cloudtrail_console = "https://${var.aws_region}.console.aws.amazon.com/cloudtrail/home?region=${var.aws_region}#/trails/${aws_cloudtrail.security_trail.name}"
    flow_logs_console = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups/log-group/${replace(aws_cloudwatch_log_group.vpc_flow_logs.name, "/", "$252F")}"
    alert_topics = {
      emergency = aws_sns_topic.emergency_alerts.arn
      safety = aws_sns_topic.safety_alerts.arn
    }
  }
}
