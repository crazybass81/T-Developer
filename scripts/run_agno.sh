#!/bin/bash

# T-Developer v2 Agno Example Runner Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project root directory (one level up from scripts)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "🚀 Running T-Developer v2 Agno Manager Example..."
echo "================================================"
echo "Project directory: $PROJECT_DIR"
echo ""
echo "This example will demonstrate:"
echo "  1. Creating agent specifications from requirements"
echo "  2. Checking for duplicates (DD-Gate)"
echo "  3. Generating implementation code with Claude"
echo "  4. Registering new agents"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r backend/requirements.txt

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run Agno example
echo ""
echo "================================================"
echo "Running Agno Manager Example..."
echo "================================================"
echo ""

python examples/use_agno.py