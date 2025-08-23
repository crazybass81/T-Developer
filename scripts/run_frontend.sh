#!/bin/bash

# T-Developer v2 Frontend Runner
echo "🚀 Starting T-Developer v2 Frontend..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install streamlit pandas 2>/dev/null

# Export AWS region if not set
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# Run the Streamlit app
echo "✅ Starting Streamlit app..."
echo "=================================="

# Get IP address
IP_ADDR=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}' | cut -d'/' -f1)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "N/A")

echo "📍 Access the app at:"
echo "   Local:    http://localhost:8501"
echo "   Network:  http://$IP_ADDR:8501"
if [ "$PUBLIC_IP" != "N/A" ]; then
    echo "   Public:   http://$PUBLIC_IP:8501"
fi
echo "📍 Press Ctrl+C to stop the server"
echo "=================================="

streamlit run frontend/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --browser.gatherUsageStats false \
    --theme.primaryColor "#4CAF50" \
    --theme.backgroundColor "#FFFFFF" \
    --theme.secondaryBackgroundColor "#F0F2F6" \
    --theme.textColor "#262730"