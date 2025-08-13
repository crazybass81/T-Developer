#!/bin/bash
# Deploy Docker image to Amazon ECR

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}
ECR_REGISTRY=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
IMAGE_NAME=t-developer-backend
VERSION=${VERSION:-$(git rev-parse --short HEAD)}
ENVIRONMENT=${ENVIRONMENT:-dev}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting ECR deployment...${NC}"
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION}"
echo "Registry: ${ECR_REGISTRY}"

# Check if repository exists, create if not
echo -e "${YELLOW}Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names ${IMAGE_NAME} --region ${AWS_REGION} >/dev/null 2>&1; then
    echo -e "${YELLOW}Creating ECR repository ${IMAGE_NAME}...${NC}"
    aws ecr create-repository \
        --repository-name ${IMAGE_NAME} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 \
        --tags Key=Project,Value=TDeveloper Key=Environment,Value=${ENVIRONMENT}

    # Set lifecycle policy
    aws ecr put-lifecycle-policy \
        --repository-name ${IMAGE_NAME} \
        --region ${AWS_REGION} \
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
        }'
fi

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build \
    -f docker/Dockerfile.production \
    -t ${IMAGE_NAME}:${VERSION} \
    -t ${IMAGE_NAME}:${ENVIRONMENT} \
    -t ${IMAGE_NAME}:latest \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION=${VERSION} \
    --build-arg VCS_REF=$(git rev-parse HEAD) \
    .

# Tag for ECR
echo -e "${YELLOW}Tagging images for ECR...${NC}"
docker tag ${IMAGE_NAME}:${VERSION} ${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:${ENVIRONMENT} ${ECR_REGISTRY}/${IMAGE_NAME}:${ENVIRONMENT}
docker tag ${IMAGE_NAME}:latest ${ECR_REGISTRY}/${IMAGE_NAME}:latest

# Push to ECR
echo -e "${YELLOW}Pushing images to ECR...${NC}"
docker push ${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${ECR_REGISTRY}/${IMAGE_NAME}:${ENVIRONMENT}
docker push ${ECR_REGISTRY}/${IMAGE_NAME}:latest

# Verify image
echo -e "${YELLOW}Verifying pushed image...${NC}"
aws ecr describe-images \
    --repository-name ${IMAGE_NAME} \
    --image-ids imageTag=${VERSION} \
    --region ${AWS_REGION}

echo -e "${GREEN}✓ Successfully deployed to ECR${NC}"
echo "Image URI: ${ECR_REGISTRY}/${IMAGE_NAME}:${VERSION}"

# Optional: Trigger ECS service update
if [ "${UPDATE_ECS_SERVICE}" = "true" ]; then
    echo -e "${YELLOW}Updating ECS service...${NC}"
    aws ecs update-service \
        --cluster t-developer-${ENVIRONMENT} \
        --service t-developer-backend \
        --force-new-deployment \
        --region ${AWS_REGION}

    echo -e "${GREEN}✓ ECS service update triggered${NC}"
fi
