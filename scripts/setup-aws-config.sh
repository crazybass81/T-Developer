#!/bin/bash

# AWS 설정 관리 스크립트
ENVIRONMENT=${NODE_ENV:-development}
REGION=${AWS_REGION:-us-east-1}

echo "🔧 Setting up AWS configuration for environment: $ENVIRONMENT"

# Parameter Store에 일반 설정 저장
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/node_env" \
  --value "$ENVIRONMENT" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/port" \
  --value "3004" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/log_level" \
  --value "info" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/aws_region" \
  --value "$REGION" \
  --type "String" \
  --overwrite

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/bedrock_region" \
  --value "$REGION" \
  --type "String" \
  --overwrite

# Secrets Manager에 민감한 정보 저장
# 환경변수에서 민감한 정보 읽기
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found in environment variables"
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

SECRET_JSON=$(cat << EOF
{
  "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
  "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
  "OPENAI_API_KEY": "${OPENAI_API_KEY:-placeholder}",
  "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY:-placeholder}",
  "GITHUB_TOKEN": "${GITHUB_TOKEN:-placeholder}",
  "JWT_SECRET": "${JWT_SECRET:-t-developer-jwt-secret-key-2024-dev}",
  "ENCRYPTION_KEY": "${ENCRYPTION_KEY:-abcdef1234567890abcdef1234567890}",
  "JWT_ACCESS_SECRET": "${JWT_ACCESS_SECRET:-t-developer-access-secret-2024-dev}",
  "JWT_REFRESH_SECRET": "${JWT_REFRESH_SECRET:-t-developer-refresh-secret-2024-dev}",
  "API_KEY_ENCRYPTION_KEY": "${API_KEY_ENCRYPTION_KEY:-abcdef1234567890abcdef1234567890}",
  "AGNO_API_KEY": "${AGNO_API_KEY:-placeholder}"
}
EOF
)

aws secretsmanager create-secret \
  --name "t-developer/$ENVIRONMENT/secrets" \
  --description "T-Developer sensitive configuration" \
  --secret-string "$SECRET_JSON" \
  --region "$REGION" || \
aws secretsmanager update-secret \
  --secret-id "t-developer/$ENVIRONMENT/secrets" \
  --secret-string "$SECRET_JSON" \
  --region "$REGION"

echo "✅ AWS configuration setup complete"
echo "📋 Next steps:"
echo "1. Update IAM roles to access Parameter Store and Secrets Manager"
echo "2. Remove sensitive data from .env file"
echo "3. Test configuration loading"
echo ""
echo "💡 Usage:"
echo "export AWS_ACCESS_KEY_ID=your-key"
echo "export AWS_SECRET_ACCESS_KEY=your-secret"
echo "export OPENAI_API_KEY=your-openai-key"
echo "./scripts/setup-aws-config.sh"