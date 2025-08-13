# T-Developer IAM Roles and Policies
# 최소 권한 원칙을 따라 필요한 권한만 부여합니다

# ===== T-Developer Evolution Engine IAM Role =====
resource "aws_iam_role" "t_developer_evolution_role" {
  name = "${var.project_name}-evolution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ecs-tasks.amazonaws.com",
            "lambda.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-evolution-role"
    Role = "EvolutionEngine"
  })
}

# Bedrock 접근 권한 (AI 모델 사용)
resource "aws_iam_policy" "bedrock_access_policy" {
  name        = "${var.project_name}-bedrock-access-${var.environment}"
  description = "T-Developer Bedrock 모델 및 Agent Core 접근 권한"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:GetModel",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel",
          "bedrock:CreateAgent",
          "bedrock:GetAgent", 
          "bedrock:UpdateAgent",
          "bedrock:DeleteAgent",
          "bedrock:ListAgents",
          "bedrock:CreateAgentActionGroup",
          "bedrock:GetAgentActionGroup",
          "bedrock:UpdateAgentActionGroup",
          "bedrock:DeleteAgentActionGroup",
          "bedrock:ListAgentActionGroups",
          "bedrock:PrepareAgent",
          "bedrock:InvokeAgent"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "bedrock:region" = var.aws_region
          }
        }
      }
    ]
  })

  tags = var.tags
}

# S3 접근 권한 (체크포인트, 에이전트 코드, 데이터 저장)
resource "aws_iam_policy" "s3_access_policy" {
  name        = "${var.project_name}-s3-access-${var.environment}"
  description = "T-Developer S3 버킷 접근 권한"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject", 
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-evolution-${var.environment}",
          "arn:aws:s3:::${var.project_name}-evolution-${var.environment}/*",
          "arn:aws:s3:::${var.project_name}-agents-${var.environment}",
          "arn:aws:s3:::${var.project_name}-agents-${var.environment}/*"
        ]
      }
    ]
  })

  tags = var.tags
}

# CloudWatch 로깅 권한
resource "aws_iam_policy" "cloudwatch_logs_policy" {
  name        = "${var.project_name}-cloudwatch-logs-${var.environment}"
  description = "T-Developer CloudWatch 로그 생성 및 메트릭 전송 권한"

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
          "logs:DescribeLogStreams",
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

# Parameter Store 및 Secrets Manager 권한
resource "aws_iam_policy" "parameters_access_policy" {
  name        = "${var.project_name}-parameters-access-${var.environment}"
  description = "T-Developer 환경변수 및 시크릿 접근 권한"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:PutParameter",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.project_name}/*"
      }
    ]
  })

  tags = var.tags
}

# ECS 태스크 실행 권한
resource "aws_iam_policy" "ecs_execution_policy" {
  name        = "${var.project_name}-ecs-execution-${var.environment}"
  description = "T-Developer ECS 태스크 실행 권한"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:DescribeTasks",
          "ecs:DescribeServices",
          "ecs:UpdateService",
          "ecs:ListTasks"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ecs:cluster" = "arn:aws:ecs:${var.aws_region}:*:cluster/${var.project_name}-*"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

# Evolution Safety 모니터링 권한
resource "aws_iam_policy" "evolution_safety_policy" {
  name        = "${var.project_name}-evolution-safety-${var.environment}"
  description = "진화 안전성 모니터링 및 제어 권한"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = "arn:aws:sns:${var.aws_region}:*:${var.project_name}-safety-alerts-*"
      },
      {
        Effect = "Allow"  
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "arn:aws:dynamodb:${var.aws_region}:*:table/${var.project_name}-evolution-state-*"
      }
    ]
  })

  tags = var.tags
}

# ===== 정책 연결 (Policy Attachments) =====
resource "aws_iam_role_policy_attachment" "evolution_bedrock_access" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.bedrock_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "evolution_s3_access" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "evolution_cloudwatch_logs" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs_policy.arn
}

resource "aws_iam_role_policy_attachment" "evolution_parameters_access" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.parameters_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "evolution_ecs_execution" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.ecs_execution_policy.arn
}

resource "aws_iam_role_policy_attachment" "evolution_safety" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = aws_iam_policy.evolution_safety_policy.arn
}

# AWS 관리형 정책 연결 (기본 ECS 실행 권한)
resource "aws_iam_role_policy_attachment" "evolution_ecs_task_execution" {
  role       = aws_iam_role.t_developer_evolution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ===== 출력값 (Outputs) =====
output "evolution_role_arn" {
  description = "T-Developer Evolution Engine IAM Role ARN"
  value       = aws_iam_role.t_developer_evolution_role.arn
}

output "evolution_role_name" {
  description = "T-Developer Evolution Engine IAM Role Name"
  value       = aws_iam_role.t_developer_evolution_role.name
}