#!/bin/bash
# Install Agno Framework + Agent Squad

echo "🔧 Installing T-Developer AI Frameworks..."

# Install Agno Framework (Open Source)
echo "📦 Installing Agno Framework..."
pip install agno
pip install agno[all]  # All extensions

# Install Agent Squad (Open Source)  
echo "📦 Installing Agent Squad..."
npm install -g agent-squad
npm install agent-squad[aws]

# Verify installations
echo "✅ Verifying installations..."
python -c "import agno; print(f'Agno version: {agno.__version__}')"
node -e "console.log('Agent Squad:', require('agent-squad').version)"

echo "🚀 Frameworks installed successfully!"
echo "📋 Architecture: Agno + Agent Squad + Bedrock AgentCore"