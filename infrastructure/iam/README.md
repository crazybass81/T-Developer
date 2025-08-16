# GitHub Actions OIDC & IAM Security Setup

## Overview
This directory contains the IAM configurations for secure GitHub Actions deployment using OIDC (OpenID Connect) federation. This eliminates the need for long-lived AWS credentials.

## Architecture
```
GitHub Actions → OIDC Token → AWS STS → Temporary Credentials → AWS Resources
```

## Setup Instructions

### 1. Prerequisites
- AWS Account with appropriate permissions
- GitHub repository with Actions enabled
- AWS CLI configured locally

### 2. Initial Setup
```bash
# Step 1: Deploy OIDC Provider (one-time per AWS account)
aws cloudformation deploy \
  --template-file github-actions-role.yml \
  --stack-name t-developer-github-actions \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    GitHubOrg=YOUR_GITHUB_ORG \
    GitHubRepo=T-DeveloperMVP

# Step 2: Get the role ARN
aws cloudformation describe-stacks \
  --stack-name t-developer-github-actions \
  --query 'Stacks[0].Outputs[?OutputKey==`RoleArn`].OutputValue' \
  --output text
```

### 3. GitHub Configuration
Add the following secrets to your GitHub repository:
- `AWS_ACCOUNT_ID`: Your AWS account ID

Update your workflows to use:
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-t-developer
    aws-region: us-east-1
```

## Files

### `github-actions-role.yml`
CloudFormation template that creates:
- OIDC Provider (if needed)
- GitHub Actions IAM Role with appropriate permissions
- Setup role for initial configuration

### `security-policy.json`
Additional security policies including:
- MFA requirements for destructive actions
- Encryption enforcement
- Region restrictions
- Tagging requirements
- Privilege escalation prevention

## Security Best Practices

1. **Principle of Least Privilege**: Roles have minimal required permissions
2. **No Long-Lived Credentials**: Uses temporary STS tokens only
3. **Audit Trail**: All actions are logged in CloudTrail
4. **Encryption**: Enforces encryption for all data at rest
5. **Region Locking**: Restricts operations to specific regions

## Permissions Overview

### GitHub Actions Role
- **Bedrock**: Invoke models and agents
- **S3**: Read/write to t-developer buckets
- **DynamoDB**: CRUD operations on t-developer tables
- **SQS**: Send/receive messages
- **CloudWatch**: Metrics and logs
- **Secrets Manager**: Read secrets
- **ECR**: Push/pull Docker images

### Setup Role (Temporary)
- **IAM**: Full access for initial setup
- **CloudFormation**: Deploy stacks
- Should be deleted after initial setup

## Troubleshooting

### OIDC Token Validation Failed
Ensure the thumbprint is correct:
```bash
# Get current GitHub OIDC thumbprint
echo | openssl s_client -servername token.actions.githubusercontent.com \
  -connect token.actions.githubusercontent.com:443 2>/dev/null \
  | openssl x509 -fingerprint -noout -sha1 \
  | cut -d= -f2 | tr -d : | tr '[:upper:]' '[:lower:]'
```

### Permission Denied
Check CloudTrail logs:
```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRoleWithWebIdentity \
  --max-items 10
```

### Role Trust Relationship
Verify the trust policy:
```bash
aws iam get-role --role-name github-actions-t-developer \
  --query 'Role.AssumeRolePolicyDocument' | jq
```

## Monitoring

### CloudWatch Metrics
- Failed authentication attempts
- API throttling
- Resource usage

### CloudTrail Events
All API calls are logged with:
- Source IP
- User identity
- Request parameters
- Response elements

## Compliance

This setup follows:
- AWS Well-Architected Framework
- CIS AWS Foundations Benchmark
- NIST Cybersecurity Framework
- SOC 2 requirements

## Support

For issues or questions:
1. Check CloudTrail logs
2. Review IAM policy simulator
3. Verify OIDC provider configuration
4. Check GitHub Actions logs