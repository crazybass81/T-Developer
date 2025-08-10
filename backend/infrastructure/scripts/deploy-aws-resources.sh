#!/bin/bash

set -e

# Configuration
ENVIRONMENT=${1:-development}
AWS_REGION=${AWS_REGION:-us-east-1}
STACK_PREFIX="t-developer"

echo "🚀 Deploying T-Developer AWS Infrastructure"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please configure AWS CLI."
    exit 1
fi

# Function to deploy CloudFormation stack
deploy_stack() {
    local stack_name=$1
    local template_file=$2
    local parameters=$3
    
    echo "Deploying $stack_name..."
    
    if aws cloudformation describe-stacks --stack-name "$stack_name" --region "$AWS_REGION" &> /dev/null; then
        echo "Stack exists, updating..."
        aws cloudformation update-stack \
            --stack-name "$stack_name" \
            --template-body "file://$template_file" \
            --parameters "$parameters" \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "$AWS_REGION" || {
            if [ $? -eq 255 ]; then
                print_warning "No updates needed for $stack_name"
            else
                print_error "Failed to update $stack_name"
                exit 1
            fi
        }
    else
        echo "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name "$stack_name" \
            --template-body "file://$template_file" \
            --parameters "$parameters" \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "$AWS_REGION"
    fi
    
    # Wait for stack to complete
    echo "Waiting for stack operation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name "$stack_name" \
        --region "$AWS_REGION" 2>/dev/null || \
    aws cloudformation wait stack-update-complete \
        --stack-name "$stack_name" \
        --region "$AWS_REGION" 2>/dev/null || true
    
    print_status "$stack_name deployed successfully"
}

# Deploy IAM Stack
IAM_STACK_NAME="${STACK_PREFIX}-iam-${ENVIRONMENT}"
deploy_stack "$IAM_STACK_NAME" \
    "infrastructure/cloudformation/iam-stack.yaml" \
    "ParameterKey=Environment,ParameterValue=$ENVIRONMENT"

# Deploy Storage Stack
STORAGE_STACK_NAME="${STACK_PREFIX}-storage-${ENVIRONMENT}"
deploy_stack "$STORAGE_STACK_NAME" \
    "infrastructure/cloudformation/storage-stack.yaml" \
    "ParameterKey=Environment,ParameterValue=$ENVIRONMENT"

# Create Parameter Store entries
echo "Creating Parameter Store entries..."

# Function to create or update parameter
create_parameter() {
    local name=$1
    local value=$2
    local type=${3:-String}
    
    aws ssm put-parameter \
        --name "$name" \
        --value "$value" \
        --type "$type" \
        --overwrite \
        --region "$AWS_REGION" &> /dev/null || true
}

# Create parameters
create_parameter "/t-developer/$ENVIRONMENT/api_url" "https://api.t-developer.com"
create_parameter "/t-developer/$ENVIRONMENT/max_workers" "4"
create_parameter "/t-developer/$ENVIRONMENT/request_timeout" "300"
create_parameter "/t-developer/$ENVIRONMENT/log_level" "INFO"
create_parameter "/t-developer/$ENVIRONMENT/bedrock_model_id" "anthropic.claude-3-sonnet-20240229-v1:0"
create_parameter "/t-developer/$ENVIRONMENT/bedrock_max_tokens" "4096"
create_parameter "/t-developer/$ENVIRONMENT/bedrock_temperature" "0.7"

print_status "Parameter Store entries created"

# Create Secrets Manager entries (placeholders)
echo "Creating Secrets Manager entries..."

# Function to create or update secret
create_secret() {
    local name=$1
    local value=$2
    
    if aws secretsmanager describe-secret --secret-id "$name" --region "$AWS_REGION" &> /dev/null; then
        aws secretsmanager update-secret \
            --secret-id "$name" \
            --secret-string "$value" \
            --region "$AWS_REGION" &> /dev/null
    else
        aws secretsmanager create-secret \
            --name "$name" \
            --secret-string "$value" \
            --region "$AWS_REGION" &> /dev/null
    fi
}

# Create secrets (with placeholder values)
create_secret "t-developer/$ENVIRONMENT/openai-api-key" '{"api_key":"REPLACE_WITH_ACTUAL_KEY"}'
create_secret "t-developer/$ENVIRONMENT/anthropic-api-key" '{"api_key":"REPLACE_WITH_ACTUAL_KEY"}'
create_secret "t-developer/$ENVIRONMENT/jwt-secret" '{"secret":"'$(openssl rand -hex 32)'"}'

print_status "Secrets Manager entries created"

# Get stack outputs
echo ""
echo "Stack Outputs:"
echo "=============="

# Get IAM Role ARNs
IAM_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name "$IAM_STACK_NAME" \
    --query 'Stacks[0].Outputs' \
    --output json \
    --region "$AWS_REGION")

echo "IAM Roles:"
echo "$IAM_OUTPUTS" | jq -r '.[] | "  - \(.OutputKey): \(.OutputValue)"'

# Get Storage Resources
STORAGE_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name "$STORAGE_STACK_NAME" \
    --query 'Stacks[0].Outputs' \
    --output json \
    --region "$AWS_REGION")

echo ""
echo "Storage Resources:"
echo "$STORAGE_OUTPUTS" | jq -r '.[] | "  - \(.OutputKey): \(.OutputValue)"'

# Create environment file for application
echo ""
echo "Creating AWS environment configuration file..."

cat > aws-config-${ENVIRONMENT}.json << EOF
{
  "environment": "$ENVIRONMENT",
  "region": "$AWS_REGION",
  "iam": {
    "agentExecutionRole": $(echo "$IAM_OUTPUTS" | jq -r '.[] | select(.OutputKey=="AgentExecutionRoleArn") | .OutputValue // ""' | jq -R .),
    "lambdaExecutionRole": $(echo "$IAM_OUTPUTS" | jq -r '.[] | select(.OutputKey=="LambdaExecutionRoleArn") | .OutputValue // ""' | jq -R .),
    "ecsTaskRole": $(echo "$IAM_OUTPUTS" | jq -r '.[] | select(.OutputKey=="ECSTaskRoleArn") | .OutputValue // ""' | jq -R .),
    "ecsExecutionRole": $(echo "$IAM_OUTPUTS" | jq -r '.[] | select(.OutputKey=="ECSExecutionRoleArn") | .OutputValue // ""' | jq -R .)
  },
  "storage": {
    "pipelineStateTable": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="PipelineStateTableName") | .OutputValue // ""' | jq -R .),
    "agentMemoryTable": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="AgentMemoryTableName") | .OutputValue // ""' | jq -R .),
    "templateLibraryTable": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="TemplateLibraryTableName") | .OutputValue // ""' | jq -R .),
    "projectMetadataTable": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="ProjectMetadataTableName") | .OutputValue // ""' | jq -R .),
    "projectStorageBucket": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="ProjectStorageBucketName") | .OutputValue // ""' | jq -R .),
    "templateBucket": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="TemplateBucketName") | .OutputValue // ""' | jq -R .),
    "cacheBucket": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="CacheBucketName") | .OutputValue // ""' | jq -R .)
  },
  "logging": {
    "applicationLogGroup": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="ApplicationLogGroupName") | .OutputValue // ""' | jq -R .),
    "agentLogGroup": $(echo "$STORAGE_OUTPUTS" | jq -r '.[] | select(.OutputKey=="AgentLogGroupName") | .OutputValue // ""' | jq -R .)
  }
}
EOF

print_status "Configuration file created: aws-config-${ENVIRONMENT}.json"

echo ""
echo "✨ AWS Infrastructure deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update secret values in AWS Secrets Manager with actual API keys"
echo "2. Review and update Parameter Store values as needed"
echo "3. Configure Bedrock model access if not already done"
echo "4. Update .env file with AWS resource names"
echo ""
echo "To destroy the infrastructure, run:"
echo "  aws cloudformation delete-stack --stack-name $IAM_STACK_NAME --region $AWS_REGION"
echo "  aws cloudformation delete-stack --stack-name $STORAGE_STACK_NAME --region $AWS_REGION"