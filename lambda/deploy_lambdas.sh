#!/bin/bash
set -e

# Configuration
REGION=$(aws configure get region)
S3_BUCKET=$(grep S3_BUCKET_NAME /home/ec2-user/T-Developer/.env | cut -d'=' -f2)
SLACK_BOT_TOKEN=$(grep SLACK_BOT_TOKEN /home/ec2-user/T-Developer/.env | cut -d'=' -f2)
LAMBDA_ROLE_ARN=$(grep LAMBDA_ROLE_ARN /home/ec2-user/T-Developer/.env | cut -d'=' -f2)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying T-Developer Lambda Functions${NC}"
echo "========================================="

# Function to package and deploy a Lambda function
deploy_lambda() {
    local function_name=$1
    local function_dir=$2
    local handler=$3
    local timeout=$4
    local memory=$5
    local env_vars=$6
    
    echo -e "\n${GREEN}Deploying $function_name Lambda function${NC}"
    
    # Create a temporary directory for packaging
    echo "Creating package for $function_name..."
    temp_dir=$(mktemp -d)
    zip_file="$temp_dir/$function_name.zip"
    
    # Install dependencies to a temporary directory
    pip install -t $temp_dir/package -r $function_dir/requirements.txt
    
    # Copy function code
    cp $function_dir/*.py $temp_dir/package/
    
    # Create ZIP file
    cd $temp_dir/package
    zip -r $zip_file .
    cd - > /dev/null
    
    # Upload to S3
    echo "Uploading package to S3..."
    aws s3 cp $zip_file s3://$S3_BUCKET/lambda/$function_name.zip
    
    # Check if function exists
    if aws lambda get-function --function-name $function_name --region $REGION > /dev/null 2>&1; then
        # Update function
        echo "Updating existing Lambda function..."
        aws lambda update-function-code \
            --function-name $function_name \
            --s3-bucket $S3_BUCKET \
            --s3-key lambda/$function_name.zip \
            --region $REGION
            
        # Update configuration
        aws lambda update-function-configuration \
            --function-name $function_name \
            --timeout $timeout \
            --memory-size $memory \
            --environment "Variables={$env_vars}" \
            --region $REGION
    else
        # Create function
        echo "Creating new Lambda function..."
        aws lambda create-function \
            --function-name $function_name \
            --runtime python3.9 \
            --role $LAMBDA_ROLE_ARN \
            --handler $handler \
            --timeout $timeout \
            --memory-size $memory \
            --environment "Variables={$env_vars}" \
            --code S3Bucket=$S3_BUCKET,S3Key=lambda/$function_name.zip \
            --region $REGION
    fi
    
    # Clean up
    rm -rf $temp_dir
    
    echo -e "${GREEN}✓ $function_name deployed successfully${NC}"
}

# Create requirements.txt files if they don't exist
mkdir -p /home/ec2-user/T-Developer/lambda/slack_notifier
cat > /home/ec2-user/T-Developer/lambda/slack_notifier/requirements.txt << EOF
slack_sdk==3.19.5
boto3==1.26.135
EOF

mkdir -p /home/ec2-user/T-Developer/lambda/test_executor
cat > /home/ec2-user/T-Developer/lambda/test_executor/requirements.txt << EOF
boto3==1.26.135
pytest==7.3.1
EOF

# Deploy Slack notifier Lambda
deploy_lambda \
    "t-developer-slack-notifier" \
    "/home/ec2-user/T-Developer/lambda/slack_notifier" \
    "lambda_function.lambda_handler" \
    10 \
    128 \
    "SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN"

# Deploy test executor Lambda
deploy_lambda \
    "t-developer-test-executor" \
    "/home/ec2-user/T-Developer/lambda/test_executor" \
    "lambda_function.lambda_handler" \
    300 \
    512 \
    "S3_BUCKET=$S3_BUCKET"

# Deploy code generator Lambda
deploy_lambda \
    "t-developer-code-generator" \
    "/home/ec2-user/T-Developer/lambda/code_generator" \
    "lambda_function.lambda_handler" \
    300 \
    1024 \
    "S3_BUCKET=$S3_BUCKET"

echo -e "\n${GREEN}All Lambda functions deployed successfully!${NC}"