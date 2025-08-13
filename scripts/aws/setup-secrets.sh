#!/bin/bash

# Setup AWS Secrets Manager for sensitive data only
# Usage: ./setup-secrets.sh [environment]

ENVIRONMENT=${1:-development}
AWS_REGION="us-east-1"

# AWS credentials should be set as environment variables before running this script
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Error: AWS credentials not set. Please export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "🔐 Setting up Secrets Manager for environment: $ENVIRONMENT"

# Create JSON with sensitive data only
cat > /tmp/secrets-only.json <<EOF
{
  "DB_PASSWORD": "postgres123",
  "REDIS_PASSWORD": "",
  "JWT_SECRET": "t-developer-jwt-secret-key-2024"
}
EOF

# Create or update the secret
SECRET_NAME="t-developer/$ENVIRONMENT/secrets"

# Check if secret exists
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region $AWS_REGION 2>/dev/null; then
  echo "Updating existing secret..."
  aws secretsmanager update-secret \
    --secret-id "$SECRET_NAME" \
    --secret-string file:///tmp/secrets-only.json \
    --region $AWS_REGION
else
  echo "Creating new secret..."
  aws secretsmanager create-secret \
    --name "$SECRET_NAME" \
    --description "T-Developer $ENVIRONMENT environment secrets (sensitive data only)" \
    --secret-string file:///tmp/secrets-only.json \
    --region $AWS_REGION
fi

# Clean up
rm -f /tmp/secrets-only.json

echo "✅ Secrets Manager setup complete!"
echo ""
echo "📝 To view secret:"
echo "aws secretsmanager get-secret-value --secret-id '$SECRET_NAME' --region $AWS_REGION | jq '.SecretString | fromjson'"
echo ""
echo "💰 Cost optimization achieved:"
echo "  - Parameter Store (14 parameters): FREE"
echo "  - Secrets Manager (1 secret): \$0.40/month"
echo "  - Previous cost (all in Secrets): ~\$5.60/month"
echo "  - Savings: ~\$5.20/month (93% reduction)"
