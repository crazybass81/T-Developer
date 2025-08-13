#!/bin/bash

# Setup AWS Parameter Store values for T-Developer
# Usage: ./setup-parameters.sh [environment]

ENVIRONMENT=${1:-development}
AWS_REGION="us-east-1"

# AWS credentials should be set as environment variables before running this script
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: AWS credentials not set. Please export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "🚀 Setting up Parameter Store for environment: $ENVIRONMENT"

# General configuration parameters (non-sensitive)
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DB_HOST" \
  --value "localhost" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DB_PORT" \
  --value "5432" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DB_NAME" \
  --value "t_developer" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DB_USER" \
  --value "postgres" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/REDIS_HOST" \
  --value "localhost" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/REDIS_PORT" \
  --value "6379" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/NODE_ENV" \
  --value "$ENVIRONMENT" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/PORT" \
  --value "8000" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/BEDROCK_AGENT_ID" \
  --value "NYZHMLSDOJ" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/BEDROCK_AGENT_ALIAS_ID" \
  --value "IBQK7SYNGG" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/BEDROCK_MODEL_ID" \
  --value "anthropic.claude-v2" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/ENABLE_CACHE" \
  --value "true" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/ENABLE_METRICS" \
  --value "false" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/ENABLE_TRACING" \
  --value "false" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

echo "✅ Parameter Store setup complete!"
echo ""
echo "📝 To view parameters:"
echo "aws ssm get-parameters-by-path --path '/t-developer/$ENVIRONMENT' --recursive --region $AWS_REGION"
