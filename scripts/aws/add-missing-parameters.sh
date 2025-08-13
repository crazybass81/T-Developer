#!/bin/bash

# Add missing parameters to Parameter Store
# Usage: ./add-missing-parameters.sh [environment]

ENVIRONMENT=${1:-development}
AWS_REGION="us-east-1"

# AWS credentials should be set as environment variables before running this script
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: AWS credentials not set. Please export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "🔧 Adding missing parameters for environment: $ENVIRONMENT"

# CORS and Frontend
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/ALLOWED_ORIGINS" \
  --value "http://localhost:3000,http://localhost:5173" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/FRONTEND_URL" \
  --value "http://localhost:5173" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Logging
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/LOG_LEVEL" \
  --value "info" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# JWT
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/JWT_EXPIRES_IN" \
  --value "7d" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/JWT_REFRESH_EXPIRES_IN" \
  --value "30d" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Database
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DATABASE_URL" \
  --value "postgresql://postgres:postgres123@localhost:5432/t_developer" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Redis
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/REDIS_URL" \
  --value "redis://localhost:6379" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/REDIS_DB" \
  --value "0" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# DynamoDB
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/DYNAMODB_TABLE_PREFIX" \
  --value "t-developer" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Memory Management
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/MAX_MEMORY_MB" \
  --value "512" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/MAX_MEMORY_AGE_DAYS" \
  --value "7" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/MIN_RELEVANCE" \
  --value "0.1" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/GC_INTERVAL_SECONDS" \
  --value "300" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# API Configuration
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/API_PREFIX" \
  --value "/api" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/API_VERSION" \
  --value "v1" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Bundle Analyzer (optional)
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/ANALYZE" \
  --value "false" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

# Tracing (Jaeger)
aws ssm put-parameter \
  --name "/t-developer/$ENVIRONMENT/JAEGER_ENDPOINT" \
  --value "http://localhost:14268/api/traces" \
  --type "String" \
  --overwrite \
  --region $AWS_REGION

echo "✅ Added missing parameters!"
echo ""
echo "📝 Total parameters now:"
aws ssm get-parameters-by-path --path "/t-developer/$ENVIRONMENT" --recursive --region $AWS_REGION --query 'length(Parameters)' --output text
