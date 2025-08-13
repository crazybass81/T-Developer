#!/bin/bash

# AWS Credentials Setup Script
# AWS 자격 증명 설정 스크립트

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}AWS Credentials Setup${NC}"
echo "====================="
echo ""

# Function to validate AWS credentials
validate_credentials() {
    if aws sts get-caller-identity &>/dev/null; then
        echo -e "${GREEN}✓ AWS credentials are valid${NC}"

        # Display account info
        echo -e "${YELLOW}Account Information:${NC}"
        aws sts get-caller-identity --output table
        return 0
    else
        echo -e "${RED}✗ AWS credentials are invalid or not set${NC}"
        return 1
    fi
}

# Check if credentials already exist
if [ -f ~/.aws/credentials ]; then
    echo -e "${YELLOW}AWS credentials file already exists${NC}"
    echo "Current configuration:"
    validate_credentials

    read -p "Do you want to reconfigure? (y/N): " reconfigure
    if [ "$reconfigure" != "y" ] && [ "$reconfigure" != "Y" ]; then
        echo "Using existing credentials"
        exit 0
    fi
fi

# Setup methods
echo ""
echo "Choose AWS credential setup method:"
echo "1) Enter Access Key and Secret Key"
echo "2) Use IAM Role (for EC2 instances)"
echo "3) Configure AWS SSO"
echo "4) Use environment variables"
echo "5) Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        # Manual credential entry
        echo -e "${YELLOW}Enter AWS Credentials:${NC}"
        read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
        read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
        echo ""
        read -p "Default Region [us-east-1]: " AWS_REGION
        AWS_REGION=${AWS_REGION:-us-east-1}

        # Create AWS config directory
        mkdir -p ~/.aws

        # Write credentials
        cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

        # Write config
        cat > ~/.aws/config << EOF
[default]
region = ${AWS_REGION}
output = json
EOF

        echo -e "${GREEN}AWS credentials saved${NC}"

        # Validate
        echo -e "${YELLOW}Validating credentials...${NC}"
        validate_credentials
        ;;

    2)
        # IAM Role (for EC2)
        echo -e "${YELLOW}Checking for EC2 instance metadata...${NC}"

        if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/ &>/dev/null; then
            echo -e "${GREEN}EC2 instance detected${NC}"

            # Get instance role
            ROLE=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/)
            if [ -n "$ROLE" ]; then
                echo "IAM Role: $ROLE"

                # Set region
                read -p "Default Region [us-east-1]: " AWS_REGION
                AWS_REGION=${AWS_REGION:-us-east-1}

                mkdir -p ~/.aws
                cat > ~/.aws/config << EOF
[default]
region = ${AWS_REGION}
output = json
EOF

                # Test with IAM role
                export AWS_DEFAULT_REGION=${AWS_REGION}
                validate_credentials
            else
                echo -e "${RED}No IAM role attached to this instance${NC}"
                echo "Please attach an IAM role to the EC2 instance"
                exit 1
            fi
        else
            echo -e "${RED}Not running on EC2 instance${NC}"
            echo "IAM role authentication is only available on EC2"
            exit 1
        fi
        ;;

    3)
        # AWS SSO
        echo -e "${YELLOW}Configuring AWS SSO...${NC}"

        read -p "SSO Start URL: " SSO_START_URL
        read -p "SSO Region [us-east-1]: " SSO_REGION
        SSO_REGION=${SSO_REGION:-us-east-1}
        read -p "SSO Account ID: " SSO_ACCOUNT_ID
        read -p "SSO Role Name: " SSO_ROLE_NAME
        read -p "Default Region [us-east-1]: " AWS_REGION
        AWS_REGION=${AWS_REGION:-us-east-1}

        # Configure SSO
        aws configure sso --profile default <<EOF
${SSO_START_URL}
${SSO_REGION}
${SSO_ACCOUNT_ID}
${SSO_ROLE_NAME}
${AWS_REGION}
json
EOF

        # Login to SSO
        echo -e "${YELLOW}Logging in to AWS SSO...${NC}"
        aws sso login --profile default

        # Validate
        AWS_PROFILE=default validate_credentials
        ;;

    4)
        # Environment variables
        echo -e "${YELLOW}Setting up environment variables...${NC}"

        read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
        read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
        echo ""
        read -p "Default Region [us-east-1]: " AWS_REGION
        AWS_REGION=${AWS_REGION:-us-east-1}

        # Create env file
        cat > ~/.aws_env << EOF
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"
export AWS_DEFAULT_REGION="${AWS_REGION}"
EOF

        # Add to bashrc
        echo "" >> ~/.bashrc
        echo "# AWS Credentials" >> ~/.bashrc
        echo "source ~/.aws_env" >> ~/.bashrc

        # Source immediately
        source ~/.aws_env

        echo -e "${GREEN}Environment variables set${NC}"
        echo "Run 'source ~/.bashrc' to apply in new terminals"

        # Validate
        validate_credentials
        ;;

    5)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Additional AWS resources check
if validate_credentials; then
    echo ""
    echo -e "${YELLOW}Checking AWS resources...${NC}"

    # Check S3 buckets
    echo "S3 Buckets:"
    aws s3 ls 2>/dev/null | head -5 || echo "  No S3 buckets or no permissions"

    # Check Lambda functions
    echo ""
    echo "Lambda Functions:"
    aws lambda list-functions --query 'Functions[*].FunctionName' --output text 2>/dev/null | head -5 || echo "  No Lambda functions or no permissions"

    # Check ECS clusters
    echo ""
    echo "ECS Clusters:"
    aws ecs list-clusters --query 'clusterArns[*]' --output text 2>/dev/null | head -5 || echo "  No ECS clusters or no permissions"

    echo ""
    echo -e "${GREEN}AWS credentials setup complete!${NC}"
    echo ""
    echo "You can now run:"
    echo "  - Lambda deployment: cd backend/deployment/lambda && make deploy"
    echo "  - ECS deployment: cd backend/deployment/ecs && ./deploy.sh production"
fi
