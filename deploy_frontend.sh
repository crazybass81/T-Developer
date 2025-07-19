#!/bin/bash
set -e

# Configuration
FRONTEND_BUCKET="tdeveloper-frontend"
BACKEND_URL="http://your-backend-url:8001"  # Change this to your actual backend URL

echo "Building frontend for production..."
cd ~/T-Developer/frontend
REACT_APP_API_URL="${BACKEND_URL}" npm run build

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