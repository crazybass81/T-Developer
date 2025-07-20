#!/bin/bash
set -e

# Configuration
FRONTEND_BUCKET="tdeveloper-frontend"

# Get EC2 public DNS for backend URL
EC2_PUBLIC_DNS=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || echo "localhost")

# Detect backend port by finding the running backend process
BACKEND_PORT=$(lsof -i -P | grep "uvicorn" | grep "LISTEN" | awk '{print $9}' | cut -d':' -f2)
if [ -z "$BACKEND_PORT" ]; then
  # Default port if backend not detected
  BACKEND_PORT=8000
  echo "Backend not detected, using default port $BACKEND_PORT"
fi

# Set backend URL for S3 hosting
BACKEND_URL="http://${EC2_PUBLIC_DNS}:${BACKEND_PORT}"
echo "Using backend URL: $BACKEND_URL"

# Allow user to override backend URL
if [ ! -z "$1" ]; then
  BACKEND_URL="$1"
  echo "Overriding backend URL with: $BACKEND_URL"
fi

# Verify backend is accessible
echo "Verifying backend is accessible..."
if curl -s "${BACKEND_URL}/health" > /dev/null; then
  echo "✅ Backend is accessible"
else
  echo "⚠️ Warning: Backend at $BACKEND_URL is not accessible"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment aborted"
    exit 1
  fi
fi

echo "Building frontend for production..."
cd ~/T-Developer/frontend

# Set environment variables for the build
echo "REACT_APP_API_URL=${BACKEND_URL}" > .env.production
echo "REACT_APP_EC2_PUBLIC_DNS=${EC2_PUBLIC_DNS}" >> .env.production

# Build with production environment
npm run build

echo "Creating S3 bucket for frontend hosting..."
aws s3 mb s3://${FRONTEND_BUCKET} || true

echo "Configuring bucket for static website hosting..."
aws s3 website s3://${FRONTEND_BUCKET} --index-document index.html --error-document index.html

echo "Setting bucket policy for public access..."
aws s3api put-bucket-policy --bucket ${FRONTEND_BUCKET} --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::'${FRONTEND_BUCKET}'/*"
    }
  ]
}'

echo "Uploading frontend build to S3..."
aws s3 sync build/ s3://${FRONTEND_BUCKET}/ --acl public-read

echo "Frontend deployed successfully!"
echo "Website URL: http://${FRONTEND_BUCKET}.s3-website-$(aws configure get region).amazonaws.com"