#!/bin/bash

# T-Developer Lambda Deployment Script
# Production-ready deployment for all 9 agents

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="t-developer-lambda-stack-${ENVIRONMENT}"

echo -e "${GREEN}T-Developer Lambda Deployment${NC}"
echo "================================"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack: ${STACK_NAME}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}AWS CLI is not installed${NC}"
        exit 1
    fi
    
    # Check SAM CLI
    if ! command -v sam &> /dev/null; then
        echo -e "${RED}SAM CLI is not installed${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}AWS credentials not configured${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Create Lambda handler files for each agent
create_lambda_handlers() {
    echo -e "${YELLOW}Creating Lambda handler files...${NC}"
    
    agents=("nl_input" "ui_selection" "parser" "component_decision" "match_rate" "search" "generation" "assembly" "download")
    
    for agent in "${agents[@]}"; do
        handler_dir="../../src/agents/production/${agent}"
        handler_file="${handler_dir}/lambda_handler.py"
        
        if [ ! -f "$handler_file" ]; then
            echo "Creating handler for ${agent}..."
            mkdir -p "$handler_dir"
            
            cat > "$handler_file" << EOF
"""
Lambda Handler for ${agent} Agent
AWS Lambda entry point
"""

import json
import os
from typing import Dict, Any
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from core import ${agent^}Agent

logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Initialize agent
agent = ${agent^}Agent()

@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for ${agent} agent
    
    Args:
        event: Lambda event containing request data
        context: Lambda context
        
    Returns:
        Response with agent execution results
    """
    
    try:
        # Log request
        logger.info(f"Processing ${agent} request", extra={"event": event})
        
        # Add metric
        metrics.add_metric(name="RequestCount", unit=MetricUnit.Count, value=1)
        
        # Extract parameters from event
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)
        
        # Execute agent
        result = agent.execute(body)
        
        # Add success metric
        metrics.add_metric(name="SuccessCount", unit=MetricUnit.Count, value=1)
        
        # Return response
        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json",
                "X-Agent-Name": "${agent}"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in ${agent} agent", exc_info=True)
        
        # Add error metric
        metrics.add_metric(name="ErrorCount", unit=MetricUnit.Count, value=1)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "agent": "${agent}"
            }),
            "headers": {
                "Content-Type": "application/json",
                "X-Agent-Name": "${agent}"
            }
        }
EOF
        fi
    done
    
    echo -e "${GREEN}Lambda handlers created${NC}"
}

# Create Lambda layer
create_layer() {
    echo -e "${YELLOW}Creating Lambda layer...${NC}"
    
    layer_dir="layers/common"
    mkdir -p "${layer_dir}/python"
    
    # Create requirements file for layer
    cat > "${layer_dir}/requirements.txt" << EOF
boto3>=1.34.0
aws-lambda-powertools>=2.28.0
pydantic>=2.5.0
aiohttp>=3.9.0
numpy>=1.24.0
scikit-learn>=1.3.0
EOF
    
    # Install dependencies
    pip install -r "${layer_dir}/requirements.txt" -t "${layer_dir}/python" --upgrade
    
    echo -e "${GREEN}Lambda layer created${NC}"
}

# Build SAM application
build_application() {
    echo -e "${YELLOW}Building SAM application...${NC}"
    
    sam build \
        --template template.yaml \
        --config-env "${ENVIRONMENT}" \
        --parallel \
        --cached
    
    echo -e "${GREEN}Build completed${NC}"
}

# Deploy SAM application
deploy_application() {
    echo -e "${YELLOW}Deploying SAM application...${NC}"
    
    # Get VPC information (you need to provide these)
    VPC_ID=${VPC_ID:-"vpc-xxxxx"}
    SUBNET_IDS=${SUBNET_IDS:-"subnet-xxxxx,subnet-yyyyy"}
    SECURITY_GROUP_ID=${SECURITY_GROUP_ID:-"sg-xxxxx"}
    
    sam deploy \
        --template-file .aws-sam/build/template.yaml \
        --stack-name "${STACK_NAME}" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --config-env "${ENVIRONMENT}" \
        --parameter-overrides \
            Environment="${ENVIRONMENT}" \
            VpcId="${VPC_ID}" \
            SubnetIds="${SUBNET_IDS}" \
            SecurityGroupId="${SECURITY_GROUP_ID}" \
        --no-confirm-changeset \
        --no-fail-on-empty-changeset
    
    echo -e "${GREEN}Deployment completed${NC}"
}

# Test Lambda functions
test_functions() {
    echo -e "${YELLOW}Testing Lambda functions...${NC}"
    
    agents=("nl-input" "ui-selection" "parser" "component-decision" "match-rate" "search" "generation" "assembly" "download")
    
    for agent in "${agents[@]}"; do
        function_name="t-developer-${agent}-agent-${ENVIRONMENT}"
        
        echo "Testing ${function_name}..."
        
        # Create test event
        test_event=$(cat <<EOF
{
    "body": {
        "test": true,
        "message": "Test invocation for ${agent}"
    }
}
EOF
        )
        
        # Invoke function
        aws lambda invoke \
            --function-name "${function_name}" \
            --payload "${test_event}" \
            --cli-binary-format raw-in-base64-out \
            response.json
        
        # Check response
        if grep -q "statusCode.*200" response.json; then
            echo -e "${GREEN}✓ ${function_name} test passed${NC}"
        else
            echo -e "${RED}✗ ${function_name} test failed${NC}"
            cat response.json
        fi
        
        rm -f response.json
    done
    
    echo -e "${GREEN}Function testing completed${NC}"
}

# Get stack outputs
get_outputs() {
    echo -e "${YELLOW}Getting stack outputs...${NC}"
    
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Main deployment flow
main() {
    check_prerequisites
    create_lambda_handlers
    create_layer
    build_application
    deploy_application
    
    if [ "${ENVIRONMENT}" == "development" ]; then
        test_functions
    fi
    
    get_outputs
    
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo "Stack Name: ${STACK_NAME}"
    echo "Environment: ${ENVIRONMENT}"
    echo "Region: ${REGION}"
}

# Run main function
main