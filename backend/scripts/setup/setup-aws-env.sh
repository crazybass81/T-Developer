#!/bin/bash

# AWS IAM Role 크레덴셜 설정
# EC2 인스턴스의 IAM Role을 사용하도록 환경 변수 설정

echo "Setting up AWS environment with IAM Role..."

# Get token for IMDSv2
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Get role name
ROLE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/)

if [ -z "$ROLE" ]; then
    echo "❌ No IAM Role attached to this instance"
    exit 1
fi

echo "✅ IAM Role found: $ROLE"

# Get temporary credentials
CREDS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE)

# Extract credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDS | python3 -c "import sys, json; print(json.load(sys.stdin)['AccessKeyId'])")
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | python3 -c "import sys, json; print(json.load(sys.stdin)['SecretAccessKey'])")
export AWS_SESSION_TOKEN=$(echo $CREDS | python3 -c "import sys, json; print(json.load(sys.stdin)['Token'])")
export AWS_DEFAULT_REGION=us-east-1

# Clear any existing credentials file
rm -f ~/.aws/credentials

# Test connection
echo ""
echo "Testing AWS connection..."
aws sts get-caller-identity

# Export for Python
echo ""
echo "Environment variables set:"
echo "  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:20}..."
echo "  AWS_SECRET_ACCESS_KEY: ***hidden***"
echo "  AWS_SESSION_TOKEN: ${AWS_SESSION_TOKEN:0:20}..."
echo "  AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"

# Create env file for persistence
cat > /home/ec2-user/T-DeveloperMVP/backend/.aws-env << EOF
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"
export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION"
EOF

echo ""
echo "✅ AWS environment configured successfully!"
echo ""
echo "To use in current shell:"
echo "  source /home/ec2-user/T-DeveloperMVP/backend/.aws-env"
