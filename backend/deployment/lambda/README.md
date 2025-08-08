# T-Developer Lambda Deployment

Production-ready Lambda deployment configuration for all 9 T-Developer agents.

## Architecture

Each agent runs as an independent Lambda function with:
- **Memory**: 1024MB-3008MB (optimized per agent)
- **Timeout**: 300-900 seconds (based on agent requirements)
- **Runtime**: Python 3.11
- **Concurrency**: Reserved concurrency to prevent throttling

### Agent-Specific Configurations

| Agent | Memory | Timeout | Concurrency | Tasks |
|-------|--------|---------|-------------|-------|
| NL Input | 1024MB | 300s | 10 | 4.1-4.10 |
| UI Selection | 1024MB | 300s | 10 | 4.11-4.20 |
| Parser | 1024MB | 300s | 10 | 4.21-4.30 |
| Component Decision | 1024MB | 300s | 10 | 4.31-4.40 |
| Match Rate | 1024MB | 300s | 10 | 4.41-4.50 |
| Search | 2048MB | 300s | 5 | 4.51-4.60 |
| Generation | 3008MB | 900s | 5 | 4.61-4.70 |
| Assembly | 2048MB | 600s | 5 | 4.71-4.80 |
| Download | 2048MB | 600s | 5 | 4.81-4.90 |

## Prerequisites

1. AWS CLI configured
2. SAM CLI installed
3. Python 3.11
4. VPC with private subnets for Lambda
5. AWS credentials with appropriate permissions

## Quick Start

### 1. Install Dependencies
```bash
make install
```

### 2. Deploy to Development
```bash
make deploy ENV=development
```

### 3. Deploy to Production
```bash
make deploy ENV=production
```

### 4. Test Deployed Functions
```bash
make test-deployed ENV=development
```

## Deployment Commands

### Using Makefile

```bash
# Show all available commands
make help

# Validate template
make validate

# Build application
make build ENV=development

# Deploy to AWS
make deploy ENV=production

# Test locally
make test-local

# Test deployed functions
make test-deployed ENV=production

# View logs
make logs

# Check stack status
make status ENV=production

# View stack outputs
make outputs ENV=production

# Update function code only (fast update)
make update-code ENV=production

# Delete stack
make delete ENV=development

# Full deployment pipeline
make all ENV=production
```

### Using Shell Script

```bash
# Deploy to development
./deploy.sh development

# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh production
```

### Using SAM CLI Directly

```bash
# Build
sam build --config-env development

# Deploy
sam deploy --config-env production

# Local testing
sam local start-api --env-vars env.json
```

## Local Testing

### 1. Start Local API
```bash
./local-test.sh
# Then select option 2: Start local API
```

### 2. Test Specific Function
```bash
./local-test.sh
# Then select option 3: Test specific function
```

### 3. Test All Functions
```bash
./local-test.sh
# Then select option 4: Test all functions
```

## Environment Configuration

### Development
- Stack: `t-developer-lambda-stack-dev`
- Confirm changeset: No
- Auto-rollback: Enabled

### Staging
- Stack: `t-developer-lambda-stack-staging`
- Confirm changeset: Yes
- Auto-rollback: Enabled

### Production
- Stack: `t-developer-lambda-stack-prod`
- Confirm changeset: Yes
- Auto-rollback: Enabled

## Monitoring

### CloudWatch Logs
```bash
# View logs for specific agent
make logs
# Enter agent name when prompted

# Or directly with AWS CLI
aws logs tail /aws/lambda/t-developer-nl-input-agent-production --follow
```

### CloudWatch Metrics
```bash
# View metrics
make metrics ENV=production

# Open dashboard
make monitor ENV=production
```

### X-Ray Tracing
All functions have X-Ray tracing enabled for performance monitoring:
```bash
aws xray get-service-graph --start-time $(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S') --end-time $(date -u '+%Y-%m-%dT%H:%M:%S')
```

## Troubleshooting

### Common Issues

1. **VPC Configuration**
   - Ensure Lambda functions have internet access via NAT Gateway
   - Security group must allow outbound HTTPS (443)

2. **Timeout Issues**
   - Generation Agent has maximum timeout (900s)
   - Consider using Step Functions for longer operations

3. **Memory Issues**
   - Monitor CloudWatch metrics for memory usage
   - Adjust memory in template.yaml if needed

4. **Cold Start**
   - Reserved concurrency prevents cold starts
   - Consider provisioned concurrency for critical functions

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
make deploy ENV=development
```

## Cost Optimization

### Lambda Costs
- **Compute**: $0.0000166667 per GB-second
- **Requests**: $0.20 per 1M requests
- **Storage**: First 75GB free

### Optimization Tips
1. Use Lambda layers for shared dependencies
2. Enable reserved concurrency to prevent over-provisioning
3. Use S3 lifecycle policies for download cleanup
4. Monitor with Cost Explorer

## Security

### IAM Permissions
- Least privilege principle applied
- Separate roles per environment
- No wildcard permissions except where required

### Network Security
- VPC isolation for Lambda functions
- Private subnets with NAT Gateway
- Security groups restrict outbound traffic

### Secrets Management
- AWS Secrets Manager for sensitive data
- AWS Systems Manager Parameter Store for configuration
- KMS encryption for data at rest

## CI/CD Integration

### GitHub Actions
```yaml
name: Deploy Lambda
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: make deploy ENV=production
```

### GitLab CI
```yaml
deploy:
  stage: deploy
  script:
    - make deploy ENV=production
  only:
    - main
```

## Support

For issues or questions:
1. Check CloudWatch Logs
2. Review X-Ray traces
3. Check AWS Service Health Dashboard
4. Contact the development team