#!/bin/bash

# Configuration
FRONTEND_BUCKET="tdeveloper-frontend"
REGION=$(aws configure get region)

# Check if bucket exists
echo "Checking if S3 bucket exists..."
if aws s3api head-bucket --bucket $FRONTEND_BUCKET 2>/dev/null; then
  echo "✅ S3 bucket $FRONTEND_BUCKET exists"
  
  # Check if website configuration is enabled
  echo "Checking website configuration..."
  WEBSITE_CONFIG=$(aws s3api get-bucket-website --bucket $FRONTEND_BUCKET 2>/dev/null || echo "")
  
  if [ -n "$WEBSITE_CONFIG" ]; then
    echo "✅ Website hosting is enabled"
    
    # Get website URL
    if [[ $REGION == "us-east-1" ]]; then
      WEBSITE_URL="http://${FRONTEND_BUCKET}.s3-website-${REGION}.amazonaws.com"
    else
      WEBSITE_URL="http://${FRONTEND_BUCKET}.s3-website.${REGION}.amazonaws.com"
    fi
    
    echo "Website URL: $WEBSITE_URL"
    
    # Check if index.html exists
    echo "Checking if index.html exists..."
    if aws s3 ls s3://$FRONTEND_BUCKET/index.html 2>/dev/null; then
      echo "✅ index.html exists"
      
      # Check if site is accessible
      echo "Checking if website is accessible..."
      HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $WEBSITE_URL)
      
      if [ "$HTTP_STATUS" == "200" ]; then
        echo "✅ Website is accessible (HTTP 200)"
      else
        echo "❌ Website returned HTTP status $HTTP_STATUS"
      fi
      
      # Check backend connectivity
      echo "Checking backend connectivity..."
      EC2_PUBLIC_DNS=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || echo "localhost")
      BACKEND_PORT=$(lsof -i -P | grep "uvicorn" | grep "LISTEN" | awk '{print $9}' | cut -d':' -f2 || echo "8000")
      BACKEND_URL="http://${EC2_PUBLIC_DNS}:${BACKEND_PORT}/health"
      
      echo "Backend URL: $BACKEND_URL"
      BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL)
      
      if [ "$BACKEND_STATUS" == "200" ]; then
        echo "✅ Backend is accessible (HTTP 200)"
      else
        echo "❌ Backend returned HTTP status $BACKEND_STATUS"
        echo "⚠️ Make sure your security group allows inbound traffic on port $BACKEND_PORT"
      fi
      
      echo ""
      echo "Frontend URL: $WEBSITE_URL"
      echo "Backend URL: $BACKEND_URL"
      echo ""
      echo "If the frontend cannot connect to the backend, check:"
      echo "1. EC2 security group allows inbound traffic on port $BACKEND_PORT"
      echo "2. Backend is running and accessible from the internet"
      echo "3. CORS settings in the backend allow requests from $WEBSITE_URL"
    else
      echo "❌ index.html does not exist. Deploy the frontend first."
    fi
  else
    echo "❌ Website hosting is not enabled. Run deploy_frontend.sh first."
  fi
else
  echo "❌ S3 bucket $FRONTEND_BUCKET does not exist. Run deploy_frontend.sh first."
fi