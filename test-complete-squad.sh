#!/bin/bash

echo "================================================"
echo "    AGENT SQUAD COMPLETE TEST"
echo "================================================"
echo ""

# Load configuration from AWS Secrets Manager
echo "🔐 Loading configuration from AWS Secrets Manager..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required to run this script"
    exit 1
fi

# Get environment from command line or default to development
ENVIRONMENT="${1:-development}"
echo "📍 Environment: $ENVIRONMENT"

# Load secrets using the setup script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Retrieve secrets and export them
echo "🔑 Retrieving secrets for $ENVIRONMENT environment..."
node -e "
const { retrieveSecret, SECRET_CONFIGS } = require('./scripts/setup-aws-secrets.js');

async function loadSecrets() {
  try {
    const config = SECRET_CONFIGS['$ENVIRONMENT'];
    if (!config) {
      console.error('Invalid environment: $ENVIRONMENT');
      process.exit(1);
    }
    
    const secrets = await retrieveSecret('$ENVIRONMENT');
    
    // Export secrets as environment variables
    Object.entries(secrets).forEach(([key, value]) => {
      if (value) {
        console.log(\`export \${key}=\"\${value}\"\`);
      }
    });
  } catch (error) {
    console.error('Failed to load secrets:', error.message);
    console.log('# Falling back to environment variables');
    console.log('export AWS_REGION=\"\${AWS_REGION:-us-east-1}\"');
    console.log('export BEDROCK_AGENT_ID=\"\${BEDROCK_AGENT_ID}\"');
    console.log('export BEDROCK_AGENT_ALIAS_ID=\"\${BEDROCK_AGENT_ALIAS_ID}\"');
  }
}

loadSecrets();
" > /tmp/secrets_export.sh

# Source the exported variables
if [ -f /tmp/secrets_export.sh ]; then
    source /tmp/secrets_export.sh
    rm /tmp/secrets_export.sh
    echo "✅ Secrets loaded successfully"
else
    echo "⚠️ Using environment variables as fallback"
    export AWS_REGION="${AWS_REGION:-us-east-1}"
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1️⃣  System Configuration:"
echo "   AWS Region: $AWS_REGION"
echo "   Bedrock Agent ID: $BEDROCK_AGENT_ID"
echo "   Bedrock Agent Alias: $BEDROCK_AGENT_ALIAS_ID"
echo ""

echo "2️⃣  Testing Agent Squad Integration..."
echo ""

# Test the agent squad
node scripts/test-agent-squad-integration.js

echo ""
echo "3️⃣  Testing Agno API..."
echo ""

# Test Agno API
./test-agno-api.sh

echo ""
echo "================================================"
echo "    TEST COMPLETE"
echo "================================================"