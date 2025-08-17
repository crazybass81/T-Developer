#!/bin/bash

# T-Developer Deployment Script
# Usage: ./deploy.sh [environment] [component]
# Environments: dev, staging, prod
# Components: all, backend, frontend, lambda, infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
COMPONENT=${2:-all}
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Use dev, staging, or prod${NC}"
    exit 1
fi

# Validate component
if [[ ! "$COMPONENT" =~ ^(all|backend|frontend|lambda|infrastructure)$ ]]; then
    echo -e "${RED}Error: Invalid component. Use all, backend, frontend, lambda, or infrastructure${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}T-Developer Deployment${NC}"
echo -e "${GREEN}Environment: $ENVIRONMENT${NC}"
echo -e "${GREEN}Component: $COMPONENT${NC}"
echo -e "${GREEN}AWS Region: $AWS_REGION${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to deploy backend
deploy_backend() {
    echo -e "${YELLOW}Deploying Backend...${NC}"
    
    # Run tests
    echo "Running backend tests..."
    cd backend
    python -m pytest tests/ -v --cov=packages --cov-report=term-missing
    
    # Package backend
    echo "Packaging backend..."
    pip install -r requirements.txt -t package/
    cp -r packages/ package/
    cd package
    zip -r ../backend-$ENVIRONMENT.zip .
    cd ..
    
    # Upload to S3
    echo "Uploading to S3..."
    aws s3 cp backend-$ENVIRONMENT.zip s3://t-developer-artifacts-$ENVIRONMENT/backend/
    
    echo -e "${GREEN}Backend deployed successfully${NC}"
    cd ..
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "${YELLOW}Deploying Frontend...${NC}"
    
    cd frontend
    
    # Install dependencies
    echo "Installing dependencies..."
    npm ci
    
    # Run tests
    echo "Running frontend tests..."
    npm run test:ci
    
    # Build frontend
    echo "Building frontend..."
    REACT_APP_ENV=$ENVIRONMENT npm run build
    
    # Deploy to S3
    echo "Deploying to S3..."
    aws s3 sync build/ s3://t-developer-frontend-$ENVIRONMENT/ --delete
    
    # Invalidate CloudFront cache (if exists)
    if [ "$ENVIRONMENT" = "prod" ]; then
        DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[0].DomainName=='t-developer-frontend-$ENVIRONMENT.s3.amazonaws.com'].Id" --output text)
        if [ ! -z "$DISTRIBUTION_ID" ]; then
            echo "Invalidating CloudFront cache..."
            aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
        fi
    fi
    
    echo -e "${GREEN}Frontend deployed successfully${NC}"
    cd ..
}

# Function to deploy Lambda functions
deploy_lambda() {
    echo -e "${YELLOW}Deploying Lambda Functions...${NC}"
    
    cd lambda_handlers
    
    # Package each Lambda function
    for handler in evolution_handler agent_handler metrics_handler; do
        echo "Packaging $handler..."
        
        # Create deployment package
        mkdir -p deployment
        cp $handler.py deployment/
        cd deployment
        pip install -r ../requirements.txt -t .
        zip -r ../$handler.zip .
        cd ..
        rm -rf deployment
        
        # Update Lambda function
        echo "Updating Lambda function: t-developer-$handler-$ENVIRONMENT"
        aws lambda update-function-code \
            --function-name t-developer-${handler%_handler}-$ENVIRONMENT \
            --zip-file fileb://$handler.zip \
            --region $AWS_REGION
        
        # Update environment variables
        aws lambda update-function-configuration \
            --function-name t-developer-${handler%_handler}-$ENVIRONMENT \
            --environment "Variables={
                ENVIRONMENT=$ENVIRONMENT,
                EVOLUTION_TABLE=t-developer-evolution-$ENVIRONMENT,
                AGENTS_TABLE=t-developer-agents-$ENVIRONMENT,
                METRICS_TABLE=t-developer-metrics-$ENVIRONMENT,
                EXECUTION_TABLE=t-developer-executions-$ENVIRONMENT,
                ARTIFACTS_BUCKET=t-developer-artifacts-$ENVIRONMENT
            }" \
            --region $AWS_REGION
    done
    
    echo -e "${GREEN}Lambda functions deployed successfully${NC}"
    cd ..
}

# Function to deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}Deploying Infrastructure...${NC}"
    
    cd infrastructure
    
    # Deploy DynamoDB tables
    echo "Deploying DynamoDB tables..."
    aws cloudformation deploy \
        --template-file dynamodb.yaml \
        --stack-name t-developer-dynamodb-$ENVIRONMENT \
        --parameter-overrides \
            EnvironmentName=$ENVIRONMENT \
            ReadCapacityUnits=5 \
            WriteCapacityUnits=5 \
        --capabilities CAPABILITY_IAM \
        --region $AWS_REGION
    
    # Deploy API Gateway
    echo "Deploying API Gateway..."
    aws cloudformation deploy \
        --template-file api-gateway.yaml \
        --stack-name t-developer-api-$ENVIRONMENT \
        --parameter-overrides \
            EnvironmentName=$ENVIRONMENT \
        --capabilities CAPABILITY_IAM \
        --region $AWS_REGION
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name t-developer-api-$ENVIRONMENT \
        --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
        --output text \
        --region $AWS_REGION)
    
    echo -e "${GREEN}API Gateway URL: $API_URL${NC}"
    
    echo -e "${GREEN}Infrastructure deployed successfully${NC}"
    cd ..
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    echo -e "${YELLOW}Running post-deployment tests...${NC}"
    
    # Get API endpoint
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name t-developer-api-$ENVIRONMENT \
        --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
        --output text \
        --region $AWS_REGION)
    
    # Test API health
    echo "Testing API health..."
    curl -s -o /dev/null -w "%{http_code}" $API_URL/health | grep -q "200" && \
        echo -e "${GREEN}API health check passed${NC}" || \
        echo -e "${RED}API health check failed${NC}"
    
    # Test Lambda functions
    echo "Testing Lambda functions..."
    for func in evolution agent metrics; do
        aws lambda invoke \
            --function-name t-developer-$func-$ENVIRONMENT \
            --payload '{"test": true}' \
            --region $AWS_REGION \
            response.json > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Lambda function t-developer-$func-$ENVIRONMENT test passed${NC}"
        else
            echo -e "${RED}Lambda function t-developer-$func-$ENVIRONMENT test failed${NC}"
        fi
    done
    
    rm -f response.json
}

# Function to update monitoring dashboard
update_monitoring() {
    echo -e "${YELLOW}Updating monitoring dashboard...${NC}"
    
    # Create CloudWatch dashboard
    cat > dashboard.json << EOF
{
    "name": "T-Developer-$ENVIRONMENT",
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "TDeveloper/Agents", "ExecutionTime", { "stat": "Average" } ],
                    [ ".", "ExecutionCount", { "stat": "Sum" } ]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$AWS_REGION",
                "title": "Agent Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "TDeveloper/Metrics", "evolution.cycles.completed", { "stat": "Sum" } ],
                    [ ".", "evolution.improvement.rate", { "stat": "Average" } ]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$AWS_REGION",
                "title": "Evolution Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Invocations", { "dimension": { "FunctionName": "t-developer-evolution-$ENVIRONMENT" } } ],
                    [ ".", "Errors", { "dimension": { "FunctionName": "t-developer-evolution-$ENVIRONMENT" } } ],
                    [ ".", "Duration", { "dimension": { "FunctionName": "t-developer-evolution-$ENVIRONMENT" } } ]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "$AWS_REGION",
                "title": "Lambda Metrics"
            }
        }
    ]
}
EOF
    
    aws cloudwatch put-dashboard \
        --dashboard-name T-Developer-$ENVIRONMENT \
        --dashboard-body file://dashboard.json \
        --region $AWS_REGION
    
    rm dashboard.json
    
    echo -e "${GREEN}Monitoring dashboard updated${NC}"
}

# Main deployment flow
main() {
    case $COMPONENT in
        all)
            deploy_infrastructure
            deploy_backend
            deploy_lambda
            deploy_frontend
            update_monitoring
            run_post_deployment_tests
            ;;
        backend)
            deploy_backend
            ;;
        frontend)
            deploy_frontend
            ;;
        lambda)
            deploy_lambda
            ;;
        infrastructure)
            deploy_infrastructure
            ;;
    esac
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}Environment: $ENVIRONMENT${NC}"
    echo -e "${GREEN}Component: $COMPONENT${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Run main function
main