#!/bin/bash

# Update AI keys in Secrets Manager
# Usage: ./update-ai-keys.sh [environment]

ENVIRONMENT=${1:-development}
AWS_REGION="us-east-1"

# AWS credentials should be set as environment variables before running this script
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: AWS credentials not set. Please export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "🤖 Updating AI keys for environment: $ENVIRONMENT"

# Get current secrets
CURRENT_SECRETS=$(aws secretsmanager get-secret-value \
  --secret-id "t-developer/$ENVIRONMENT/secrets" \
  --region $AWS_REGION \
  --output json | jq -r '.SecretString')

# Add AI keys to the secrets
UPDATED_SECRETS=$(echo $CURRENT_SECRETS | jq '. + {
  "OPENAI_API_KEY": "'${OPENAI_API_KEY:-}'",
  "ANTHROPIC_API_KEY": "'${ANTHROPIC_API_KEY:-}'",
  "GOOGLE_AI_API_KEY": "'${GOOGLE_AI_API_KEY:-}'",
  "HUGGINGFACE_API_KEY": "'${HUGGINGFACE_API_KEY:-}'"
}')

# Create temporary file with updated secrets
echo "$UPDATED_SECRETS" > /tmp/updated-secrets.json

# Update the secret
aws secretsmanager update-secret \
  --secret-id "t-developer/$ENVIRONMENT/secrets" \
  --secret-string file:///tmp/updated-secrets.json \
  --region $AWS_REGION

# Clean up
rm -f /tmp/updated-secrets.json

echo "✅ AI keys have been added to Secrets Manager"
echo ""
echo "📝 Current AI keys in secret:"
echo "$UPDATED_SECRETS" | jq 'keys[] | select(contains("AI") or contains("OPENAI") or contains("ANTHROPIC"))'
echo ""
echo "🔐 To set AI keys, run:"
echo "  export OPENAI_API_KEY='your-key-here'"
echo "  export ANTHROPIC_API_KEY='your-key-here'"
echo "  ./update-ai-keys.sh $ENVIRONMENT"