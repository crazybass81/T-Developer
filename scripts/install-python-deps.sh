#!/bin/bash
# scripts/install-python-deps.sh

echo "🐍 Installing Python dependencies with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create/activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

source .venv/bin/activate

# Install dependencies
echo "Installing requirements..."
uv pip install -r requirements.txt

# Install layer dependencies
if [ -f "layers/python-common/requirements.txt" ]; then
    echo "Installing layer dependencies..."
    uv pip install -r layers/python-common/requirements.txt
fi

echo "✅ Python dependencies installed successfully!"