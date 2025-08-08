#!/bin/bash
# AWS S3-only Infrastructure Deployment Script
# T-Developer MVP S3 버킷만 배포

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 기본 설정
STACK_NAME="t-developer-s3-stack"
REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-development}"
PROJECT_NAME="t-developer-mvp"

log_info "🚀 Starting S3-only Infrastructure Deployment"
log_info "Stack Name: $STACK_NAME"
log_info "Region: $REGION"
log_info "Environment: $ENVIRONMENT"

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

# 간단한 S3 전용 CloudFormation 템플릿 생성
log_info "Creating simple S3-only CloudFormation template..."
cat > /tmp/t-developer-s3-only.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'T-Developer MVP S3-only Infrastructure'

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
            ExpirationInDays: 7
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
EOF

log_success "CloudFormation template created"

# CloudFormation 스택 배포
log_info "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file /tmp/t-developer-s3-only.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides \
    Environment=$ENVIRONMENT \
    ProjectName=$PROJECT_NAME \
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

cat > .env.aws << EOF
# AWS S3 Infrastructure Configuration
# Generated by deploy-s3-only.sh on $(date)

AWS_REGION=$REGION
ENVIRONMENT=$ENVIRONMENT
PROJECT_NAME=$PROJECT_NAME
STACK_NAME=$STACK_NAME

# S3 Buckets
PROJECTS_BUCKET=$PROJECTS_BUCKET
ASSETS_BUCKET=$ASSETS_BUCKET

# For application use
T_DEVELOPER_PROJECTS_BUCKET=$PROJECTS_BUCKET
T_DEVELOPER_ASSETS_BUCKET=$ASSETS_BUCKET
EOF

log_success "Environment variables saved to .env.aws"

# S3 버킷에 샘플 파일 업로드
log_info "Uploading sample files to assets bucket..."
cat > /tmp/index.html << EOF
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
        <h3>✅ S3 Infrastructure Successfully Deployed!</h3>
        <p>AWS S3 infrastructure is ready for T-Developer MVP.</p>
        <ul>
            <li>S3 bucket created for generated projects: $PROJECTS_BUCKET</li>
            <li>S3 bucket created for static assets: $ASSETS_BUCKET</li>
            <li>Website hosting enabled</li>
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
rm -f /tmp/t-developer-s3-only.yaml /tmp/index.html

# 최종 요약
echo ""
echo "🎉 S3 Infrastructure Deployment Complete!"
echo "================================================"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"
echo ""
echo "📦 Resources Created:"
echo "  • S3 Projects Bucket: $PROJECTS_BUCKET"
echo "  • S3 Assets Bucket: $ASSETS_BUCKET"
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
echo ""