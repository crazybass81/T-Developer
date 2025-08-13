#!/bin/bash

# T-Developer Deployment Script
# Handles deployment to AWS ECS with comprehensive validation and rollback

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${ENVIRONMENT:-production}
AWS_REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME="t-developer-cluster-${ENVIRONMENT}"
SERVICE_NAME="t-developer-service-${ENVIRONMENT}"
REPOSITORY_NAME="t-developer-backend-${ENVIRONMENT}"
STACK_NAME="t-developer-stack-${ENVIRONMENT}"

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
INFRA_DIR="${PROJECT_ROOT}/infrastructure/aws"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
T-Developer Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (development|staging|production)
    -r, --region REGION      AWS region (default: us-east-1)
    -v, --validate-only      Only validate configuration, don't deploy
    -s, --skip-tests         Skip running tests before deployment
    -f, --force              Force deployment without confirmation
    -h, --help               Show this help message

EXAMPLES:
    $0 -e production                    # Deploy to production
    $0 -e staging -r us-west-2          # Deploy to staging in us-west-2
    $0 -e development --validate-only   # Only validate development config
    $0 -e production --skip-tests       # Deploy without running tests

ENVIRONMENT VARIABLES:
    ENVIRONMENT              Target environment
    AWS_REGION              AWS region
    AWS_PROFILE             AWS CLI profile to use
    SKIP_CONFIRMATION       Skip deployment confirmation (true/false)

EOF
}

# Parse command line arguments
VALIDATE_ONLY=false
SKIP_TESTS=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -v|--validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Update cluster and service names based on environment
CLUSTER_NAME="t-developer-cluster-${ENVIRONMENT}"
SERVICE_NAME="t-developer-service-${ENVIRONMENT}"
REPOSITORY_NAME="t-developer-backend-${ENVIRONMENT}"
STACK_NAME="t-developer-stack-${ENVIRONMENT}"

# Validation functions
validate_prerequisites() {
    log "Validating prerequisites..."

    # Check required tools
    local required_tools=("aws" "docker" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool '$tool' not found"
            exit 1
        fi
    done

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or invalid"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon not running"
        exit 1
    fi

    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        error "Invalid environment: $ENVIRONMENT"
        exit 1
    fi

    success "Prerequisites validated"
}

validate_configuration() {
    log "Validating configuration for $ENVIRONMENT environment..."

    # Check if backend directory exists
    if [[ ! -d "$BACKEND_DIR" ]]; then
        error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi

    # Check if Dockerfile exists
    if [[ ! -f "$BACKEND_DIR/Dockerfile" ]]; then
        error "Dockerfile not found in backend directory"
        exit 1
    fi

    # Check if CloudFormation template exists
    if [[ ! -f "$INFRA_DIR/cloudformation-template.yml" ]]; then
        error "CloudFormation template not found: $INFRA_DIR/cloudformation-template.yml"
        exit 1
    fi

    # Validate CloudFormation template
    log "Validating CloudFormation template..."
    if ! aws cloudformation validate-template \
        --template-body "file://$INFRA_DIR/cloudformation-template.yml" \
        --region "$AWS_REGION" > /dev/null; then
        error "CloudFormation template validation failed"
        exit 1
    fi

    success "Configuration validated"
}

run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        warning "Skipping tests as requested"
        return 0
    fi

    log "Running tests..."

    # Run backend tests
    log "Running backend tests..."
    cd "$BACKEND_DIR"

    if [[ -f "requirements-dev.txt" ]]; then
        pip install -q -r requirements-dev.txt
    fi

    # Run linting
    if command -v flake8 &> /dev/null; then
        flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
    fi

    # Run security checks
    if command -v bandit &> /dev/null; then
        bandit -r src/ -ll
    fi

    # Run unit tests
    if [[ -d "tests" ]]; then
        python -m pytest tests/unit/ -v --tb=short
    fi

    cd "$PROJECT_ROOT"
    success "Tests passed"
}

build_and_push_image() {
    log "Building and pushing Docker image..."

    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

    # ECR repository URI
    ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}"

    # Login to ECR
    log "Logging in to Amazon ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_URI"

    # Create ECR repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names "$REPOSITORY_NAME" --region "$AWS_REGION" &> /dev/null; then
        log "Creating ECR repository: $REPOSITORY_NAME"
        aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region "$AWS_REGION"
    fi

    # Build image
    IMAGE_TAG="$(date +%Y%m%d%H%M%S)-$(git rev-parse --short HEAD)"
    log "Building Docker image with tag: $IMAGE_TAG"

    cd "$BACKEND_DIR"
    docker build \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        -t "$ECR_URI:$IMAGE_TAG" \
        -t "$ECR_URI:latest" \
        .

    # Push image
    log "Pushing Docker image to ECR..."
    docker push "$ECR_URI:$IMAGE_TAG"
    docker push "$ECR_URI:latest"

    cd "$PROJECT_ROOT"
    echo "$ECR_URI:$IMAGE_TAG" > .last_image_tag

    success "Image built and pushed: $ECR_URI:$IMAGE_TAG"
}

deploy_infrastructure() {
    log "Deploying infrastructure..."

    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" &> /dev/null; then
        log "Updating existing stack: $STACK_NAME"
        STACK_ACTION="update-stack"
    else
        log "Creating new stack: $STACK_NAME"
        STACK_ACTION="create-stack"
    fi

    # Deploy CloudFormation stack
    aws cloudformation "$STACK_ACTION" \
        --stack-name "$STACK_NAME" \
        --template-body "file://$INFRA_DIR/cloudformation-template.yml" \
        --parameters \
            ParameterKey=Environment,ParameterValue="$ENVIRONMENT" \
            ParameterKey=VpcId,ParameterValue="$(get_default_vpc)" \
            ParameterKey=SubnetIds,ParameterValue="$(get_public_subnets)" \
            ParameterKey=SecurityGroupId,ParameterValue="$(get_default_security_group)" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION"

    # Wait for stack operation to complete
    log "Waiting for CloudFormation stack operation to complete..."
    aws cloudformation wait "stack-${STACK_ACTION%-*}-complete" \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION"

    success "Infrastructure deployed successfully"
}

deploy_application() {
    log "Deploying application to ECS..."

    # Get the current task definition
    CURRENT_TASK_DEF=$(aws ecs describe-task-definition \
        --task-definition "$SERVICE_NAME" \
        --region "$AWS_REGION" \
        --query 'taskDefinition' 2>/dev/null || echo "{}")

    if [[ "$CURRENT_TASK_DEF" == "{}" ]]; then
        error "Task definition not found. Please ensure infrastructure is deployed first."
        exit 1
    fi

    # Get the latest image URI
    if [[ -f ".last_image_tag" ]]; then
        IMAGE_URI=$(cat .last_image_tag)
    else
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:latest"
    fi

    # Update task definition with new image
    NEW_TASK_DEF=$(echo "$CURRENT_TASK_DEF" | jq --arg IMAGE_URI "$IMAGE_URI" '
        .containerDefinitions[0].image = $IMAGE_URI |
        del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)
    ')

    # Register new task definition
    log "Registering new task definition..."
    NEW_TASK_DEF_ARN=$(echo "$NEW_TASK_DEF" | aws ecs register-task-definition \
        --region "$AWS_REGION" \
        --cli-input-json file:///dev/stdin \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)

    # Update service
    log "Updating ECS service..."
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --task-definition "$NEW_TASK_DEF_ARN" \
        --region "$AWS_REGION" > /dev/null

    # Wait for deployment to complete
    log "Waiting for service deployment to complete..."
    aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region "$AWS_REGION"

    success "Application deployed successfully"
}

run_smoke_tests() {
    log "Running smoke tests..."

    # Get service endpoint
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text 2>/dev/null || echo "")

    if [[ -z "$ALB_DNS" ]]; then
        warning "Could not get load balancer DNS name, skipping smoke tests"
        return 0
    fi

    SERVICE_URL="http://$ALB_DNS"

    # Wait a bit for the service to be ready
    log "Waiting for service to be ready..."
    sleep 30

    # Test health endpoint
    log "Testing health endpoint..."
    if ! curl -f -s "$SERVICE_URL/health" > /dev/null; then
        error "Health check failed"
        return 1
    fi

    # Test API status endpoint
    log "Testing API status endpoint..."
    if ! curl -f -s "$SERVICE_URL/api/v1/status" > /dev/null; then
        error "API status check failed"
        return 1
    fi

    success "Smoke tests passed"
    log "Service is available at: $SERVICE_URL"
}

rollback() {
    log "Rolling back deployment..."

    # Get previous task definition
    PREVIOUS_TASK_DEF=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region "$AWS_REGION" \
        --query 'services[0].deployments[?status==`PRIMARY`].taskDefinition' \
        --output text)

    if [[ -n "$PREVIOUS_TASK_DEF" ]]; then
        # Extract revision number and decrement
        CURRENT_REVISION=$(echo "$PREVIOUS_TASK_DEF" | sed 's/.*://')
        PREVIOUS_REVISION=$((CURRENT_REVISION - 1))
        PREVIOUS_TASK_DEF_ARN="${PREVIOUS_TASK_DEF%:*}:$PREVIOUS_REVISION"

        log "Rolling back to: $PREVIOUS_TASK_DEF_ARN"

        # Update service with previous task definition
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$SERVICE_NAME" \
            --task-definition "$PREVIOUS_TASK_DEF_ARN" \
            --region "$AWS_REGION" > /dev/null

        success "Rollback initiated"
    else
        error "Could not determine previous task definition for rollback"
    fi
}

# Utility functions
get_default_vpc() {
    aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --region "$AWS_REGION" \
        --query 'Vpcs[0].VpcId' \
        --output text
}

get_public_subnets() {
    local vpc_id=$(get_default_vpc)
    aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$vpc_id" \
        --region "$AWS_REGION" \
        --query 'Subnets[0:2].SubnetId' \
        --output text | tr '\t' ','
}

get_default_security_group() {
    local vpc_id=$(get_default_vpc)
    aws ec2 describe-security-groups \
        --filters "Name=vpc-id,Values=$vpc_id" "Name=group-name,Values=default" \
        --region "$AWS_REGION" \
        --query 'SecurityGroups[0].GroupId' \
        --output text
}

cleanup() {
    log "Performing cleanup..."
    # Remove temporary files
    rm -f .last_image_tag
}

# Trap cleanup on exit
trap cleanup EXIT

# Main deployment flow
main() {
    log "Starting T-Developer deployment to $ENVIRONMENT environment"

    # Validate prerequisites
    validate_prerequisites

    # Validate configuration
    validate_configuration

    if [[ "$VALIDATE_ONLY" == "true" ]]; then
        success "Validation completed successfully"
        exit 0
    fi

    # Confirmation prompt
    if [[ "$FORCE" != "true" && "${SKIP_CONFIRMATION:-false}" != "true" ]]; then
        echo
        warning "You are about to deploy to: $ENVIRONMENT"
        warning "AWS Region: $AWS_REGION"
        warning "Cluster: $CLUSTER_NAME"
        echo
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Deployment cancelled by user"
            exit 0
        fi
    fi

    # Run tests
    run_tests

    # Build and push Docker image
    build_and_push_image

    # Deploy infrastructure
    deploy_infrastructure

    # Deploy application
    deploy_application

    # Run smoke tests
    if ! run_smoke_tests; then
        error "Smoke tests failed, initiating rollback..."
        rollback
        exit 1
    fi

    success "Deployment completed successfully!"
    log "Environment: $ENVIRONMENT"
    log "Region: $AWS_REGION"

    # Get service URL for user
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text 2>/dev/null || echo "")

    if [[ -n "$ALB_DNS" ]]; then
        log "Service URL: http://$ALB_DNS"
    fi
}

# Execute main function
main "$@"
