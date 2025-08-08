#!/bin/bash
# AWS Basic Infrastructure Deployment Script
# T-Developer MVP 기본 AWS 인프라 배포

set -e  # Exit on any error

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 기본 설정
STACK_NAME="t-developer-mvp-stack"
REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-development}"
PROJECT_NAME="t-developer-mvp"

log_info "🚀 Starting AWS Infrastructure Deployment"
log_info "Stack Name: $STACK_NAME"
log_info "Region: $REGION"
log_info "Environment: $ENVIRONMENT"

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed"
    exit 1
fi

# AWS 자격증명 확인
log_info "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials not configured. Please run 'aws configure'"
    exit 1
fi

log_success "AWS credentials verified"

# S3 버킷 생성 (CloudFormation 템플릿 저장용)
BUCKET_NAME="t-developer-cfn-templates-$(date +%s)"
log_info "Creating S3 bucket for CloudFormation templates: $BUCKET_NAME"

aws s3 mb s3://$BUCKET_NAME --region $REGION || {
    log_warning "Bucket creation failed or bucket already exists"
}

# CloudFormation 템플릿 생성
log_info "Creating CloudFormation template..."
cat > /tmp/t-developer-infrastructure.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'T-Developer MVP Basic Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: development
    AllowedValues: [development, staging, production]
  
  ProjectName:
    Type: String
    Default: t-developer-mvp

Resources:
  # S3 Bucket for generated projects
  ProjectsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${ProjectName}-projects-${Environment}-${AWS::AccountId}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldProjects
            Status: Enabled
            ExpirationInDays: 7  # 7일 후 자동 삭제
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # S3 Bucket for static assets
  AssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${ProjectName}-assets-${Environment}-${AWS::AccountId}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # S3 Bucket Policy for static assets
  AssetsBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref AssetsBucket
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal: '*'
            Action: 's3:GetObject'
            Resource: !Sub "${AssetsBucket}/*"

  # DynamoDB Table for project metadata
  ProjectsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${ProjectName}-projects-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: project_id
          AttributeType: S
        - AttributeName: created_at
          AttributeType: S
      KeySchema:
        - AttributeName: project_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: created-at-index
          KeySchema:
            - AttributeName: created_at
              KeyType: HASH
          Projection:
            ProjectionType: ALL
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # IAM Role for Lambda functions
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-lambda-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: T-DeveloperLambdaPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource:
                  - !Sub "${ProjectsBucket}/*"
                  - !Sub "${AssetsBucket}/*"
              - Effect: Allow
                Action:
                  - s3:ListBucket
                Resource:
                  - !Ref ProjectsBucket
                  - !Ref AssetsBucket
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource:
                  - !GetAtt ProjectsTable.Arn
                  - !Sub "${ProjectsTable.Arn}/index/*"
              - Effect: Allow
                Action:
                  - bedrock:InvokeAgent
                  - bedrock:GetAgent
                  - bedrock:ListAgents
                Resource: "*"
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: "*"

  # IAM Role for ECS tasks
  ECSTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-ecs-task-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: T-DeveloperECSTaskPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource:
                  - !Sub "${ProjectsBucket}/*"
                  - !Sub "${AssetsBucket}/*"
              - Effect: Allow
                Action:
                  - s3:ListBucket
                Resource:
                  - !Ref ProjectsBucket
                  - !Ref AssetsBucket
              - Effect: Allow
                Action:
                  - dynamodb:*
                Resource:
                  - !GetAtt ProjectsTable.Arn
                  - !Sub "${ProjectsTable.Arn}/index/*"
              - Effect: Allow
                Action:
                  - bedrock:*
                Resource: "*"
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: "*"
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"

  # ECS Execution Role
  ECSExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-ecs-execution-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/ecs/${ProjectName}-${Environment}"
      RetentionInDays: 14

  # Security Group for ECS
  ECSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for T-Developer ECS tasks
      GroupName: !Sub "${ProjectName}-ecs-sg-${Environment}"
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 3000
          ToPort: 3000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

Outputs:
  ProjectsBucketName:
    Description: Name of the projects S3 bucket
    Value: !Ref ProjectsBucket
    Export:
      Name: !Sub "${AWS::StackName}-projects-bucket"
  
  AssetsBucketName:
    Description: Name of the assets S3 bucket
    Value: !Ref AssetsBucket
    Export:
      Name: !Sub "${AWS::StackName}-assets-bucket"
  
  AssetsBucketWebsiteURL:
    Description: URL of the assets bucket website
    Value: !GetAtt AssetsBucket.WebsiteURL
    Export:
      Name: !Sub "${AWS::StackName}-assets-website-url"
  
  ProjectsTableName:
    Description: Name of the DynamoDB projects table
    Value: !Ref ProjectsTable
    Export:
      Name: !Sub "${AWS::StackName}-projects-table"
  
  LambdaExecutionRoleArn:
    Description: ARN of the Lambda execution role
    Value: !GetAtt LambdaExecutionRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-lambda-role-arn"
  
  ECSTaskRoleArn:
    Description: ARN of the ECS task role
    Value: !GetAtt ECSTaskRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-ecs-task-role-arn"
  
  ECSExecutionRoleArn:
    Description: ARN of the ECS execution role
    Value: !GetAtt ECSExecutionRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-ecs-execution-role-arn"
  
  ECSSecurityGroupId:
    Description: ID of the ECS security group
    Value: !Ref ECSSecurityGroup
    Export:
      Name: !Sub "${AWS::StackName}-ecs-security-group"
EOF

log_success "CloudFormation template created"

# CloudFormation 템플릿 업로드
log_info "Uploading CloudFormation template to S3..."
aws s3 cp /tmp/t-developer-infrastructure.yaml s3://$BUCKET_NAME/infrastructure.yaml --region $REGION

# CloudFormation 스택 배포
log_info "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file /tmp/t-developer-infrastructure.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides \
    Environment=$ENVIRONMENT \
    ProjectName=$PROJECT_NAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION || {
    log_error "CloudFormation deployment failed"
    exit 1
}

log_success "CloudFormation stack deployed successfully"

# 스택 정보 출력
log_info "Getting stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs' \
  --output table)

echo "📋 Stack Outputs:"
echo "$OUTPUTS"

# 환경변수 파일 생성
log_info "Creating environment variables file..."
PROJECTS_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ProjectsBucketName`].OutputValue' \
  --output text)

ASSETS_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketName`].OutputValue' \
  --output text)

PROJECTS_TABLE=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ProjectsTableName`].OutputValue' \
  --output text)

LAMBDA_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`LambdaExecutionRoleArn`].OutputValue' \
  --output text)

ECS_TASK_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSTaskRoleArn`].OutputValue' \
  --output text)

cat > .env.aws << EOF
# AWS Infrastructure Configuration
# Generated by deploy-basic.sh on $(date)

AWS_REGION=$REGION
ENVIRONMENT=$ENVIRONMENT
PROJECT_NAME=$PROJECT_NAME
STACK_NAME=$STACK_NAME

# S3 Buckets
PROJECTS_BUCKET=$PROJECTS_BUCKET
ASSETS_BUCKET=$ASSETS_BUCKET

# DynamoDB Tables
PROJECTS_TABLE=$PROJECTS_TABLE

# IAM Roles
LAMBDA_EXECUTION_ROLE_ARN=$LAMBDA_ROLE_ARN
ECS_TASK_ROLE_ARN=$ECS_TASK_ROLE_ARN

# For application use
T_DEVELOPER_PROJECTS_BUCKET=$PROJECTS_BUCKET
T_DEVELOPER_ASSETS_BUCKET=$ASSETS_BUCKET
T_DEVELOPER_PROJECTS_TABLE=$PROJECTS_TABLE
EOF

log_success "Environment variables saved to .env.aws"

# S3 버킷에 샘플 파일 업로드
log_info "Uploading sample files to assets bucket..."
cat > /tmp/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>T-Developer MVP</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #2196F3; }
        .status { padding: 10px; background: #E8F5E8; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🚀 T-Developer MVP</h1>
    <div class="status">
        <h3>✅ Infrastructure Successfully Deployed!</h3>
        <p>AWS infrastructure is ready for T-Developer MVP.</p>
        <ul>
            <li>S3 buckets created for projects and assets</li>
            <li>DynamoDB table configured for project metadata</li>
            <li>IAM roles set up for Lambda and ECS</li>
            <li>Security groups configured</li>
        </ul>
        <p><strong>Next steps:</strong> Deploy your application using ECS or Lambda.</p>
    </div>
    <footer>
        <p>Deployed on $(date)</p>
    </footer>
</body>
</html>
EOF

aws s3 cp /tmp/index.html s3://$ASSETS_BUCKET/index.html --region $REGION

# 웹사이트 URL 가져오기
WEBSITE_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketWebsiteURL`].OutputValue' \
  --output text)

log_success "Sample website deployed to: $WEBSITE_URL"

# 정리
log_info "Cleaning up temporary files..."
rm -f /tmp/t-developer-infrastructure.yaml /tmp/index.html

# 최종 요약
echo ""
echo "🎉 AWS Infrastructure Deployment Complete!"
echo "================================================"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"
echo ""
echo "📦 Resources Created:"
echo "  • S3 Projects Bucket: $PROJECTS_BUCKET"
echo "  • S3 Assets Bucket: $ASSETS_BUCKET"
echo "  • DynamoDB Table: $PROJECTS_TABLE"
echo "  • Website URL: $WEBSITE_URL"
echo ""
echo "📁 Configuration saved to: .env.aws"
echo ""
echo "🔧 Next Steps:"
echo "  1. Source the environment: source .env.aws"
echo "  2. Deploy your application using ECS or Lambda"
echo "  3. Configure domain and SSL certificates"
echo "  4. Set up CloudFront CDN"
echo ""
echo "💡 To destroy this infrastructure later:"
echo "  aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
echo "