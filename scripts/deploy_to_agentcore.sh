#!/bin/bash
# Day 12: Automated AgentCore Deployment Script
# Deploy T-Developer agents to AWS Bedrock AgentCore

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"
DEPLOYMENT_LOG="$SCRIPT_DIR/deployment.log"
PYTHONPATH="$BACKEND_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

# Check prerequisites
check_prereqs() {
    log "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is required but not installed"
    fi

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is required but not installed"
    fi

    # Check environment variables
    if [[ -z "$BEDROCK_AGENT_ID" ]]; then
        error "BEDROCK_AGENT_ID environment variable is required"
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or invalid"
    fi

    success "Prerequisites check passed"
}

# Deploy single agent
deploy_agent() {
    local agent_file=$1
    local agent_name=$(basename "$agent_file" .py)

    log "Deploying agent: $agent_name"

    # Check agent size constraint
    local file_size=$(stat -c%s "$agent_file" 2>/dev/null || stat -f%z "$agent_file" 2>/dev/null)
    if [[ $file_size -gt 6656 ]]; then  # 6.5KB in bytes
        error "Agent $agent_name exceeds 6.5KB limit: ${file_size} bytes"
    fi

    # Create deployment spec
    local temp_spec=$(mktemp)
    cat > "$temp_spec" << EOF
{
    "name": "$agent_name",
    "code": "$(cat "$agent_file" | sed 's/"/\\"/g' | tr '\n' ' ')",
    "version": "$(date +%Y%m%d_%H%M%S)",
    "description": "T-Developer auto-deployed agent: $agent_name"
}
EOF

    # Deploy using Python deployer
    local deploy_result=$(PYTHONPATH="$PYTHONPATH" python3 -c "
import asyncio
import json
import sys
from src.deployment.agentcore_deployer import AgentCoreDeployer, AgentSpec

async def deploy():
    with open('$temp_spec') as f:
        spec_data = json.load(f)

    spec = AgentSpec(
        name=spec_data['name'],
        code=spec_data['code'],
        version=spec_data['version'],
        description=spec_data['description']
    )

    deployer = AgentCoreDeployer()
    result = await deployer.deploy_agent(spec)
    print(json.dumps(result))

asyncio.run(deploy())
")

    # Check deployment result
    local deployment_status=$(echo "$deploy_result" | jq -r '.status' 2>/dev/null || echo "failed")

    if [[ "$deployment_status" == "deployed" ]]; then
        local duration=$(echo "$deploy_result" | jq -r '.duration' 2>/dev/null || echo "0")
        success "Agent $agent_name deployed successfully in ${duration}s"
    else
        local error_msg=$(echo "$deploy_result" | jq -r '.error' 2>/dev/null || echo "Unknown error")
        error "Failed to deploy agent $agent_name: $error_msg"
    fi

    # Cleanup
    rm -f "$temp_spec"
}

# Deploy all agents in directory
deploy_directory() {
    local agent_dir=$1

    if [[ ! -d "$agent_dir" ]]; then
        error "Agent directory not found: $agent_dir"
    fi

    log "Deploying all agents from: $agent_dir"
    local count=0

    for agent_file in "$agent_dir"/*.py; do
        if [[ -f "$agent_file" && ! "$(basename "$agent_file")" == "__init__.py" ]]; then
            deploy_agent "$agent_file"
            ((count++))
        fi
    done

    if [[ $count -eq 0 ]]; then
        warning "No agent files found in $agent_dir"
    else
        success "Deployed $count agents from $agent_dir"
    fi
}

# Test deployment
test_deployment() {
    local deployment_id=$1

    log "Testing deployment: $deployment_id"

    local test_result=$(PYTHONPATH="$PYTHONPATH" python3 -c "
import asyncio
from src.deployment.agentcore_deployer import AgentCoreDeployer

async def test():
    deployer = AgentCoreDeployer()
    result = await deployer.test_deployment('$deployment_id')
    print(result['status'])

asyncio.run(test())
")

    if [[ "$test_result" == "success" ]]; then
        success "Deployment test passed for $deployment_id"
    else
        warning "Deployment test failed for $deployment_id"
    fi
}

# Rollback deployment
rollback_deployment() {
    local deployment_id=$1
    local reason=${2:-"manual"}

    log "Rolling back deployment: $deployment_id"

    PYTHONPATH="$PYTHONPATH" python3 -c "
import asyncio
from src.deployment.rollback_manager import RollbackManager, RollbackSpec, RollbackReason

async def rollback():
    manager = RollbackManager()
    spec = RollbackSpec('$deployment_id', RollbackReason.MANUAL)
    result = await manager.initiate_rollback(spec)

    if result['status'] == 'completed':
        print('Rollback completed successfully')
    else:
        print(f'Rollback failed: {result.get(\"error\", \"Unknown error\")}')
        exit(1)

asyncio.run(rollback())
"

    success "Rollback completed for $deployment_id"
}

# Main function
main() {
    local command=${1:-"help"}

    case "$command" in
        "deploy")
            check_prereqs
            if [[ -n "$2" ]]; then
                if [[ -f "$2" ]]; then
                    deploy_agent "$2"
                elif [[ -d "$2" ]]; then
                    deploy_directory "$2"
                else
                    error "File or directory not found: $2"
                fi
            else
                error "Usage: $0 deploy <agent_file_or_directory>"
            fi
            ;;
        "test")
            if [[ -n "$2" ]]; then
                test_deployment "$2"
            else
                error "Usage: $0 test <deployment_id>"
            fi
            ;;
        "rollback")
            if [[ -n "$2" ]]; then
                rollback_deployment "$2" "$3"
            else
                error "Usage: $0 rollback <deployment_id> [reason]"
            fi
            ;;
        "help"|*)
            cat << EOF
T-Developer AgentCore Deployment Script

Usage: $0 <command> [options]

Commands:
    deploy <file|dir>     Deploy single agent file or all agents in directory
    test <deployment_id>  Test a deployment
    rollback <id> [reason] Rollback a deployment
    help                  Show this help message

Examples:
    $0 deploy src/agents/sample_agent.py
    $0 deploy src/agents/
    $0 test agent_123_20241118
    $0 rollback agent_123_20241118 failure

Environment Variables:
    BEDROCK_AGENT_ID      AWS Bedrock Agent ID (required)
    BEDROCK_AGENT_ALIAS_ID AWS Bedrock Agent Alias ID

EOF
            ;;
    esac
}

# Create log file if it doesn't exist
touch "$DEPLOYMENT_LOG"

# Run main function
main "$@"
