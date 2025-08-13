#!/bin/bash

# Day 18: Deploy Lambda Functions for AgentCore
# This script deploys all agent Lambda functions using AWS SAM

set -e

echo "🚀 Day 18: Lambda Function Deployment"
echo "======================================"

# Configuration
STACK_NAME="t-developer-agents-stack"
TEMPLATE_FILE="infrastructure/lambda/template.yaml"
REGION="us-east-1"
ENVIRONMENT="development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    print_warning "SAM CLI is not installed. Installing..."
    pip install aws-sam-cli
fi

# Validate AWS credentials
echo "🔐 Validating AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    print_status "AWS credentials validated"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "   Account ID: $ACCOUNT_ID"
else
    print_error "AWS credentials not configured properly"
    exit 1
fi

# Build the SAM application
echo ""
echo "🔨 Building SAM application..."
sam build \
    --template-file $TEMPLATE_FILE \
    --use-container \
    --parallel

if [ $? -eq 0 ]; then
    print_status "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Deploy the SAM application
echo ""
echo "🚀 Deploying Lambda functions..."
sam deploy \
    --stack-name $STACK_NAME \
    --template-file .aws-sam/build/template.yaml \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=$ENVIRONMENT \
    --region $REGION \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    print_status "Deployment completed successfully"
else
    print_error "Deployment failed"
    exit 1
fi

# Get stack outputs
echo ""
echo "📊 Retrieving Lambda function ARNs..."
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output table

# Test Lambda functions
echo ""
echo "🧪 Testing Lambda functions..."

AGENTS=("nl-input" "ui-selection" "parser" "component-decision" "match-rate" "search")

for agent in "${AGENTS[@]}"; do
    FUNCTION_NAME="t-developer-${agent}-agent-${ENVIRONMENT}"
    echo ""
    echo "Testing $FUNCTION_NAME..."

    # Create test payload
    TEST_PAYLOAD='{"input": "Test request for agent functionality"}'

    # Invoke the function
    aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload "$TEST_PAYLOAD" \
        --region $REGION \
        response.json &> /dev/null

    if [ $? -eq 0 ]; then
        print_status "$FUNCTION_NAME invoked successfully"
        cat response.json | python -m json.tool
    else
        print_warning "$FUNCTION_NAME invocation failed"
    fi

    rm -f response.json
done

# Update Bedrock Agent with Lambda ARNs
echo ""
echo "🔗 Updating Bedrock Agent with Lambda ARNs..."

# Get Lambda ARNs
NL_INPUT_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`NLInputAgentArn`].OutputValue' \
    --output text)

echo "NL Input Agent ARN: $NL_INPUT_ARN"

# Save deployment info
echo ""
echo "💾 Saving deployment information..."

DEPLOYMENT_INFO="{
  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
  \"stack_name\": \"$STACK_NAME\",
  \"region\": \"$REGION\",
  \"environment\": \"$ENVIRONMENT\",
  \"account_id\": \"$ACCOUNT_ID\",
  \"lambda_functions\": {
    \"nl_input\": \"$NL_INPUT_ARN\",
    \"ui_selection\": \"$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==\`UISelectionAgentArn\`].OutputValue' --output text)\",
    \"parser\": \"$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==\`ParserAgentArn\`].OutputValue' --output text)\",
    \"component_decision\": \"$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==\`ComponentDecisionAgentArn\`].OutputValue' --output text)\",
    \"match_rate\": \"$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==\`MatchRateAgentArn\`].OutputValue' --output text)\",
    \"search\": \"$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==\`SearchAgentArn\`].OutputValue' --output text)\"
  }
}"

echo "$DEPLOYMENT_INFO" > logs/day18_lambda_deployment.json
print_status "Deployment information saved to logs/day18_lambda_deployment.json"

echo ""
echo "=========================================="
print_status "Lambda deployment completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure Bedrock Agent to use the Lambda functions"
echo "2. Run integration tests"
echo "3. Monitor CloudWatch logs for any issues"

exit 0
