# T-Developer v1.0 Deployment Guide

This guide provides step-by-step instructions for deploying T-Developer v1.0 on an EC2 instance with an S3-hosted frontend.

## Prerequisites

- An AWS account with access to EC2, S3, and DynamoDB
- A GitHub account with a repository for code changes
- A Slack workspace with a bot token

## Backend Deployment

### 1. Set Up the EC2 Instance

1. Launch an EC2 instance (Amazon Linux 2 or Ubuntu recommended)
2. Ensure the instance has an IAM role with permissions for:
   - DynamoDB (read/write)
   - S3 (read/write)
3. Configure security groups to allow:
   - SSH (port 22)
   - HTTP/HTTPS (ports 80/443)
   - API port (8000)

### 2. Install Dependencies

```bash
# Update system packages
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python and Git
sudo yum install -y python3 python3-pip git  # Amazon Linux
# or
sudo apt install -y python3 python3-pip git  # Ubuntu

# Clone the repository
git clone https://github.com/your-username/T-Developer.git
cd T-Developer

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

Key environment variables to set:

- `AWS_REGION`: Your AWS region (e.g., `us-east-1`)
- `DYNAMODB_TABLE_PREFIX`: Prefix for DynamoDB tables (e.g., `TDeveloper-`)
- `S3_BUCKET_NAME`: S3 bucket for artifacts (e.g., `t-developer-context`)
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GITHUB_OWNER`: GitHub username or organization
- `GITHUB_REPO`: GitHub repository name
- `SLACK_BOT_TOKEN`: Slack Bot User OAuth Token
- `SLACK_CHANNEL`: Default Slack channel (e.g., `#t-developer`)
- `SLACK_SIGNING_SECRET`: Slack app signing secret
- `USE_LAMBDA_NOTIFIER`: Set to `false` for v1.0
- `USE_LAMBDA_TEST_EXECUTOR`: Set to `false` for v1.0
- `USE_LAMBDA_CODE_GENERATOR`: Set to `false` for v1.0

### 4. Set Up Infrastructure

```bash
# Run the infrastructure setup script
python3 scripts/setup_infrastructure.py
```

This will create:
- DynamoDB tables (`TDeveloper-Tasks` and `TDeveloper-Projects`)
- S3 bucket for artifacts

### 5. Install as a Service

```bash
# Run the service installation script
sudo ./scripts/install_service.sh
```

This will:
- Create a systemd service for T-Developer
- Enable and start the service
- Configure logging

### 6. Verify Backend Deployment

```bash
# Check service status
sudo systemctl status tdeveloper

# Test the API
curl http://localhost:8000/health
```

## Frontend Deployment

### 1. Build the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Set API URL for production
echo "REACT_APP_API_URL=http://<EC2-PUBLIC-IP>:8000" > .env.production

# Build the frontend
npm run build
```

### 2. Create and Configure S3 Bucket

```bash
# Create S3 bucket
aws s3 mb s3://tdeveloper-frontend

# Configure for static website hosting
aws s3 website s3://tdeveloper-frontend --index-document index.html --error-document index.html

# Disable block public access
aws s3api put-public-access-block --bucket tdeveloper-frontend --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Set bucket policy for public read access
aws s3api put-bucket-policy --bucket tdeveloper-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::tdeveloper-frontend/*"
    }
  ]
}'
```

### 3. Deploy Frontend to S3

```bash
# Upload frontend build to S3
aws s3 sync build/ s3://tdeveloper-frontend/ --delete
```

### 4. Access the Frontend

The frontend will be available at:
```
http://tdeveloper-frontend.s3-website-<region>.amazonaws.com
```

## Monitoring and Maintenance

### Monitor the Deployment

```bash
# Run the monitoring script
./scripts/monitor_deployment.sh
```

### View Logs

```bash
# View backend logs
tail -f logs/tdeveloper.out.log
tail -f logs/tdeveloper.err.log
tail -f t-developer.log

# View systemd service logs
sudo journalctl -u tdeveloper -f
```

### Restart the Service

```bash
# Restart the backend service
sudo systemctl restart tdeveloper
```

## Troubleshooting

### Common Issues

1. **Backend not starting**:
   - Check logs: `sudo journalctl -u tdeveloper -f`
   - Verify environment variables in `.env`
   - Ensure Python dependencies are installed

2. **Frontend not connecting to backend**:
   - Check CORS configuration
   - Verify API URL in `.env.production`
   - Ensure security group allows traffic on port 8000

3. **DynamoDB or S3 errors**:
   - Verify IAM permissions
   - Check AWS region configuration
   - Ensure bucket and table names are correct

4. **GitHub integration issues**:
   - Verify GitHub token has correct permissions
   - Check repository name and owner
   - Ensure branch prefix is valid

5. **Slack integration issues**:
   - Verify Slack bot token and signing secret
   - Ensure bot is invited to the channel
   - Check Slack channel name format