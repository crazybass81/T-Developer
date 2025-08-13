# 🔧 AWS Complete Setup Guide

## 📋 Overview

Complete AWS setup guide for T-Developer AI Autonomous Evolution System, including IAM, credentials, and infrastructure configuration.

## 🔐 IAM Setup

### 1. Service Roles

#### ECS Task Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### Attached Policies
```bash
# Create role
aws iam create-role \
  --role-name t-developer-ecs-task-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name t-developer-ecs-task-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Custom policy for Bedrock
aws iam put-role-policy \
  --role-name t-developer-ecs-task-role \
  --policy-name bedrock-access \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock-runtime:*"
        ],
        "Resource": "*"
      }
    ]
  }'
```

### 2. User/Developer Access

#### Development Team Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DevelopmentAccess",
      "Effect": "Allow",
      "Action": [
        "ecs:*",
        "ecr:*",
        "logs:*",
        "cloudwatch:*",
        "s3:*",
        "dynamodb:*",
        "bedrock:*",
        "lambda:*",
        "apigateway:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestTag/Environment": ["dev", "staging"]
        }
      }
    }
  ]
}
```

## 🔑 AWS Credentials Configuration

### 1. Local Development Setup

#### AWS CLI Configuration
```bash
# Configure AWS CLI
aws configure --profile t-developer

# Enter credentials
AWS Access Key ID: AKIA...
AWS Secret Access Key: ********
Default region name: us-east-1
Default output format: json
```

#### Environment Variables
```bash
# .env file for local development
export AWS_PROFILE=t-developer
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1

# Bedrock specific
export BEDROCK_ENDPOINT=https://bedrock-runtime.us-east-1.amazonaws.com
export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Application specific
export ENVIRONMENT=development
export EVOLUTION_MODE=autonomous
export AI_AUTONOMY_LEVEL=85
```

### 2. Secrets Management

#### AWS Secrets Manager
```bash
# Create secret for API keys
aws secretsmanager create-secret \
  --name t-developer/production/api-keys \
  --secret-string '{
    "openai_api_key": "sk-...",
    "anthropic_api_key": "sk-ant-...",
    "github_token": "ghp_..."
  }'

# Retrieve secret in Python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('t-developer/production/api-keys')
```

#### Parameter Store
```bash
# Store configuration
aws ssm put-parameter \
  --name /t-developer/production/config/memory_limit \
  --value "6.5" \
  --type String

# Store secure string
aws ssm put-parameter \
  --name /t-developer/production/database_url \
  --value "postgresql://..." \
  --type SecureString
```

## 🏗️ Infrastructure Setup

### 1. VPC Configuration
```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=t-developer-vpc}]'

# Create subnets
aws ec2 create-subnet \
  --vpc-id vpc-xxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=t-developer-private-1a}]'
```

### 2. ECS Cluster Setup
```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name t-developer-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=4,base=0
```

### 3. S3 Buckets
```bash
# Create buckets
aws s3 mb s3://t-developer-artifacts --region us-east-1
aws s3 mb s3://t-developer-evolution-checkpoints --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket t-developer-evolution-checkpoints \
  --versioning-configuration Status=Enabled

# Setup lifecycle
aws s3api put-bucket-lifecycle-configuration \
  --bucket t-developer-artifacts \
  --lifecycle-configuration file://lifecycle.json
```

### 4. DynamoDB Tables
```bash
# Agent registry table
aws dynamodb create-table \
  --table-name t-developer-agents \
  --attribute-definitions \
    AttributeName=agent_id,AttributeType=S \
    AttributeName=generation,AttributeType=N \
  --key-schema \
    AttributeName=agent_id,KeyType=HASH \
    AttributeName=generation,KeyType=RANGE \
  --provisioned-throughput \
    ReadCapacityUnits=5,WriteCapacityUnits=5

# Evolution history table
aws dynamodb create-table \
  --table-name t-developer-evolution \
  --attribute-definitions \
    AttributeName=evolution_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=evolution_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
```

## 🚀 Deployment Configuration

### 1. Task Definition
```json
{
  "family": "t-developer-evolution",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "taskRoleArn": "arn:aws:iam::xxx:role/t-developer-ecs-task-role",
  "executionRoleArn": "arn:aws:iam::xxx:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "evolution-engine",
      "image": "xxx.dkr.ecr.us-east-1.amazonaws.com/t-developer:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "environment": [
        {"name": "EVOLUTION_MODE", "value": "autonomous"},
        {"name": "AI_AUTONOMY_LEVEL", "value": "85"}
      ],
      "secrets": [
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/t-developer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "evolution"
        }
      }
    }
  ]
}
```

### 2. Service Configuration
```bash
# Create service
aws ecs create-service \
  --cluster t-developer-cluster \
  --service-name evolution-service \
  --task-definition t-developer-evolution:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-xxx,subnet-yyy],
    securityGroups=[sg-xxx],
    assignPublicIp=DISABLED
  }"
```

## 📊 Monitoring Setup

### CloudWatch Dashboards
```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name t-developer-evolution \
  --dashboard-body file://dashboard.json
```

### Alarms
```bash
# High memory usage alarm
aws cloudwatch put-metric-alarm \
  --alarm-name t-developer-high-memory \
  --alarm-description "Alert when memory exceeds 6.5KB" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 6.5 \
  --comparison-operator GreaterThanThreshold
```

## 🔒 Security Configuration

### 1. Security Groups
```bash
# Create security group
aws ec2 create-security-group \
  --group-name t-developer-sg \
  --description "Security group for T-Developer" \
  --vpc-id vpc-xxx

# Add rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 443 \
  --source-group sg-yyy
```

### 2. KMS Keys
```bash
# Create KMS key
aws kms create-key \
  --description "T-Developer encryption key" \
  --key-policy file://key-policy.json

# Create alias
aws kms create-alias \
  --alias-name alias/t-developer \
  --target-key-id key-xxx
```

### 3. WAF Configuration
```bash
# Create WebACL
aws wafv2 create-web-acl \
  --name t-developer-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

## 🔄 CI/CD Pipeline

### CodePipeline
```bash
# Create pipeline
aws codepipeline create-pipeline \
  --pipeline file://pipeline.json
```

### CodeBuild Project
```yaml
# buildspec.yml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
```

## 📝 Environment Variables Summary

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| AWS_REGION | AWS region | us-east-1 |
| AWS_ACCOUNT_ID | AWS account ID | 123456789012 |
| BEDROCK_ENDPOINT | Bedrock API endpoint | https://bedrock-runtime.us-east-1.amazonaws.com |
| EVOLUTION_MODE | Evolution mode | autonomous |
| AI_AUTONOMY_LEVEL | AI autonomy percentage | 85 |
| AGENT_MEMORY_LIMIT | Memory limit in KB | 6.5 |
| INSTANTIATION_TARGET_US | Speed target in microseconds | 3 |

## 🚨 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Check IAM role
aws sts get-caller-identity

# Verify permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::xxx:role/role-name \
  --action-names bedrock:InvokeModel \
  --resource-arns "*"
```

#### 2. Network Issues
```bash
# Check VPC endpoints
aws ec2 describe-vpc-endpoints \
  --filters Name=vpc-id,Values=vpc-xxx

# Verify security groups
aws ec2 describe-security-groups \
  --group-ids sg-xxx
```

#### 3. Service Not Starting
```bash
# Check task status
aws ecs describe-tasks \
  --cluster t-developer-cluster \
  --tasks task-arn

# View logs
aws logs tail /ecs/t-developer --follow
```

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-01  
**AWS Region**: us-east-1