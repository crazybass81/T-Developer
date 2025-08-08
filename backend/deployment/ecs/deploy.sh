#!/bin/bash

# T-Developer ECS Deployment Script
# Production-ready deployment for ECS/Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
REGION=${AWS_REGION:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="t-developer-backend"
CLUSTER_NAME="t-developer-cluster-${ENVIRONMENT}"
SERVICE_NAME="t-developer-backend-${ENVIRONMENT}"
STACK_NAME="t-developer-ecs-${ENVIRONMENT}"

echo -e "${GREEN}T-Developer ECS Deployment${NC}"
echo "================================"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Account: ${ACCOUNT_ID}"
echo "Cluster: ${CLUSTER_NAME}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}AWS CLI is not installed${NC}"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}AWS credentials not configured${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Create ECR repository if not exists
create_ecr_repository() {
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    
    if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${REGION} 2>/dev/null; then
        echo "ECR repository already exists"
    else
        aws ecr create-repository \
            --repository-name ${ECR_REPOSITORY} \
            --region ${REGION} \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        
        echo -e "${GREEN}ECR repository created${NC}"
    fi
    
    # Set lifecycle policy
    aws ecr put-lifecycle-policy \
        --repository-name ${ECR_REPOSITORY} \
        --lifecycle-policy-text '{
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Keep last 10 images",
                    "selection": {
                        "tagStatus": "any",
                        "countType": "imageCountMoreThan",
                        "countNumber": 10
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }' \
        --region ${REGION} || true
}

# Build Docker image
build_docker_image() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    
    # Get ECR login token
    aws ecr get-login-password --region ${REGION} | \
        docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    
    # Build image
    docker build \
        -t ${ECR_REPOSITORY}:latest \
        -t ${ECR_REPOSITORY}:${ENVIRONMENT} \
        -f Dockerfile \
        ../../
    
    echo -e "${GREEN}Docker image built${NC}"
}

# Push Docker image to ECR
push_docker_image() {
    echo -e "${YELLOW}Pushing Docker image to ECR...${NC}"
    
    # Tag images
    docker tag ${ECR_REPOSITORY}:latest \
        ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
    
    docker tag ${ECR_REPOSITORY}:${ENVIRONMENT} \
        ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:${ENVIRONMENT}
    
    # Push images
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:${ENVIRONMENT}
    
    echo -e "${GREEN}Docker image pushed to ECR${NC}"
}

# Register task definition
register_task_definition() {
    echo -e "${YELLOW}Registering task definition...${NC}"
    
    # Update task definition with actual account ID
    sed "s/ACCOUNT_ID/${ACCOUNT_ID}/g" task-definition.json > task-definition-updated.json
    
    # Register task definition
    aws ecs register-task-definition \
        --cli-input-json file://task-definition-updated.json \
        --region ${REGION}
    
    rm task-definition-updated.json
    
    echo -e "${GREEN}Task definition registered${NC}"
}

# Deploy CloudFormation stack
deploy_stack() {
    echo -e "${YELLOW}Deploying CloudFormation stack...${NC}"
    
    # Get VPC and subnet information (you need to provide these)
    VPC_ID=${VPC_ID:-$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=t-developer-vpc" --query 'Vpcs[0].VpcId' --output text)}
    PRIVATE_SUBNETS=${PRIVATE_SUBNETS:-$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:Type,Values=private" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')}
    PUBLIC_SUBNETS=${PUBLIC_SUBNETS:-$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:Type,Values=public" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')}
    CERTIFICATE_ARN=${CERTIFICATE_ARN:-$(aws acm list-certificates --query 'CertificateSummaryList[0].CertificateArn' --output text)}
    
    aws cloudformation deploy \
        --template-file service-definition.yaml \
        --stack-name ${STACK_NAME} \
        --parameter-overrides \
            Environment=${ENVIRONMENT} \
            VpcId=${VPC_ID} \
            PrivateSubnetIds=${PRIVATE_SUBNETS} \
            PublicSubnetIds=${PUBLIC_SUBNETS} \
            CertificateArn=${CERTIFICATE_ARN} \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset
    
    echo -e "${GREEN}CloudFormation stack deployed${NC}"
}

# Update ECS service
update_service() {
    echo -e "${YELLOW}Updating ECS service...${NC}"
    
    # Force new deployment
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --force-new-deployment \
        --region ${REGION}
    
    echo -e "${GREEN}ECS service update initiated${NC}"
}

# Wait for service to be stable
wait_for_service() {
    echo -e "${YELLOW}Waiting for service to stabilize...${NC}"
    
    aws ecs wait services-stable \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --region ${REGION}
    
    echo -e "${GREEN}Service is stable${NC}"
}

# Run health check
health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    
    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    if [ -z "$ALB_DNS" ]; then
        echo -e "${YELLOW}Could not get ALB DNS, skipping health check${NC}"
        return
    fi
    
    # Check health endpoint
    for i in {1..30}; do
        if curl -f -s "http://${ALB_DNS}/health" > /dev/null; then
            echo -e "${GREEN}Health check passed${NC}"
            echo "Application URL: http://${ALB_DNS}"
            return
        fi
        echo "Attempt $i/30: Waiting for application to be healthy..."
        sleep 10
    done
    
    echo -e "${RED}Health check failed after 30 attempts${NC}"
}

# Scale service
scale_service() {
    local desired_count=$1
    echo -e "${YELLOW}Scaling service to ${desired_count} tasks...${NC}"
    
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --desired-count ${desired_count} \
        --region ${REGION}
    
    echo -e "${GREEN}Service scaled to ${desired_count} tasks${NC}"
}

# View logs
view_logs() {
    echo -e "${YELLOW}Viewing recent logs...${NC}"
    
    aws logs tail "/ecs/t-developer-backend-${ENVIRONMENT}" \
        --follow \
        --region ${REGION}
}

# Get service info
get_service_info() {
    echo -e "${YELLOW}Service Information:${NC}"
    
    # Get service details
    aws ecs describe-services \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount,PendingCount:pendingCount}' \
        --output table
    
    # Get running tasks
    echo ""
    echo "Running Tasks:"
    aws ecs list-tasks \
        --cluster ${CLUSTER_NAME} \
        --service-name ${SERVICE_NAME} \
        --desired-status RUNNING \
        --query 'taskArns' \
        --output table
    
    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    echo ""
    echo -e "${GREEN}Application URL: http://${ALB_DNS}${NC}"
}

# Main deployment flow
main() {
    check_prerequisites
    create_ecr_repository
    build_docker_image
    push_docker_image
    register_task_definition
    deploy_stack
    update_service
    wait_for_service
    health_check
    get_service_info
    
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo "Environment: ${ENVIRONMENT}"
    echo "Cluster: ${CLUSTER_NAME}"
    echo "Service: ${SERVICE_NAME}"
}

# Parse command
case "${2:-deploy}" in
    "deploy")
        main
        ;;
    "scale")
        scale_service ${3:-2}
        ;;
    "logs")
        view_logs
        ;;
    "info")
        get_service_info
        ;;
    "update")
        build_docker_image
        push_docker_image
        update_service
        wait_for_service
        health_check
        ;;
    *)
        echo "Usage: $0 [environment] [deploy|scale|logs|info|update]"
        exit 1
        ;;
esac