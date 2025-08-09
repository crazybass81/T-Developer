#!/bin/bash

# ECS Deployment Script for T-Developer
# This script deploys the T-Developer platform to AWS ECS Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
CLUSTER_NAME="t-developer-cluster"
PROJECT_NAME="t-developer"

echo -e "${GREEN}Starting T-Developer ECS Deployment${NC}"
echo "AWS Account: ${AWS_ACCOUNT}"
echo "AWS Region: ${AWS_REGION}"
echo "ECR Registry: ${ECR_REGISTRY}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
for cmd in aws docker jq; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}Error: $cmd is not installed${NC}"
        exit 1
    fi
done

# Login to ECR
echo -e "${YELLOW}Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create ECR repositories if they don't exist
echo -e "${YELLOW}Creating ECR repositories...${NC}"
for repo in analysis decision generation orchestrator; do
    aws ecr describe-repositories --repository-names "${PROJECT_NAME}/${repo}" --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name "${PROJECT_NAME}/${repo}" --region ${AWS_REGION}
done

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
docker build -f Dockerfile.ecs -t ${PROJECT_NAME}:latest .

# Tag images for different services
echo -e "${YELLOW}Tagging images...${NC}"
for service in analysis decision generation orchestrator; do
    docker tag ${PROJECT_NAME}:latest ${ECR_REGISTRY}/${PROJECT_NAME}/${service}:latest
done

# Push images to ECR
echo -e "${YELLOW}Pushing images to ECR...${NC}"
for service in analysis decision generation orchestrator; do
    docker push ${ECR_REGISTRY}/${PROJECT_NAME}/${service}:latest
done

# Create ECS cluster if it doesn't exist
echo -e "${YELLOW}Creating ECS cluster...${NC}"
aws ecs describe-clusters --clusters ${CLUSTER_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecs create-cluster --cluster-name ${CLUSTER_NAME} --region ${AWS_REGION} \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=2 capacityProvider=FARGATE,weight=1,base=1

# Create CloudWatch log group
echo -e "${YELLOW}Creating CloudWatch log group...${NC}"
aws logs create-log-group --log-group-name /ecs/${PROJECT_NAME} --region ${AWS_REGION} 2>/dev/null || true

# Register task definitions
echo -e "${YELLOW}Registering task definitions...${NC}"
# Update task definition with actual account and region
sed -e "s/ACCOUNT/${AWS_ACCOUNT}/g" \
    -e "s/REGION/${AWS_REGION}/g" \
    infrastructure/ecs/task-definition.json > /tmp/task-definition.json

aws ecs register-task-definition --cli-input-json file:///tmp/task-definition.json --region ${AWS_REGION}

# Create or update services
echo -e "${YELLOW}Creating/Updating ECS services...${NC}"

# Check if service exists
if aws ecs describe-services --cluster ${CLUSTER_NAME} --services ${PROJECT_NAME}-service --region ${AWS_REGION} 2>/dev/null | jq -e '.services[0].status == "ACTIVE"' >/dev/null; then
    echo "Updating existing service..."
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${PROJECT_NAME}-service \
        --task-definition ${PROJECT_NAME}-agents \
        --desired-count 2 \
        --region ${AWS_REGION}
else
    echo "Creating new service..."
    # Update service definition with actual values
    sed -e "s/ACCOUNT/${AWS_ACCOUNT}/g" \
        -e "s/REGION/${AWS_REGION}/g" \
        infrastructure/ecs/service-definition.json > /tmp/service-definition.json
    
    aws ecs create-service --cli-input-json file:///tmp/service-definition.json --region ${AWS_REGION}
fi

# Set up auto-scaling
echo -e "${YELLOW}Configuring auto-scaling...${NC}"
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/${CLUSTER_NAME}/${PROJECT_NAME}-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10 \
    --region ${AWS_REGION}

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/${CLUSTER_NAME}/${PROJECT_NAME}-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name ${PROJECT_NAME}-cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
        },
        "ScaleOutCooldown": 60,
        "ScaleInCooldown": 300
    }' \
    --region ${AWS_REGION}

# Wait for service to stabilize
echo -e "${YELLOW}Waiting for service to stabilize...${NC}"
aws ecs wait services-stable --cluster ${CLUSTER_NAME} --services ${PROJECT_NAME}-service --region ${AWS_REGION}

# Get service details
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Service Details:${NC}"
aws ecs describe-services \
    --cluster ${CLUSTER_NAME} \
    --services ${PROJECT_NAME}-service \
    --region ${AWS_REGION} \
    --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount}' \
    --output table

# Get task IPs (if using public IPs)
echo -e "${YELLOW}Running Tasks:${NC}"
TASK_ARNS=$(aws ecs list-tasks --cluster ${CLUSTER_NAME} --service-name ${PROJECT_NAME}-service --region ${AWS_REGION} --query 'taskArns[]' --output text)
if [ ! -z "$TASK_ARNS" ]; then
    aws ecs describe-tasks --cluster ${CLUSTER_NAME} --tasks ${TASK_ARNS} --region ${AWS_REGION} \
        --query 'tasks[].{TaskId:taskArn,Status:lastStatus,CPU:cpu,Memory:memory}' \
        --output table
fi

echo -e "${GREEN}Deployment complete! Your T-Developer platform is now running on ECS Fargate.${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your load balancer to point to the ECS service"
echo "2. Set up Route 53 for DNS"
echo "3. Configure CloudFront for CDN"
echo "4. Monitor the service in CloudWatch"