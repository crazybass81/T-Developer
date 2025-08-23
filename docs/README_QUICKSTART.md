# 🚀 T-Developer v2 Quick Start Guide

## 📋 Prerequisites

1. **AWS Account with Bedrock Access**
   - Enable AWS Bedrock in your AWS account
   - Request access to Claude models in Bedrock
   - Configure AWS credentials:
     ```bash
     export AWS_ACCESS_KEY_ID=your_key
     export AWS_SECRET_ACCESS_KEY=your_secret
     export AWS_DEFAULT_REGION=us-east-1
     ```

2. **Python 3.9+**
   ```bash
   python3 --version
   ```

## 🎯 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

### 2. Run the Web UI

```bash
# Make script executable (first time only)
chmod +x run_ui.sh

# Start the UI
./run_ui.sh
```

The UI will open automatically at: **http://localhost:8501**

### 3. Use the UI

1. **Enter Project Path**: 
   - Single file: `/path/to/file.py`
   - Directory: `/path/to/project/`

2. **Enter Requirements**:
   ```
   Analyze this code for:
   - Security vulnerabilities
   - Performance bottlenecks
   - Code quality issues
   - Missing error handling
   ```

3. **Click "Analyze Project"**

## 🎮 Command Line Examples

### Analyze a Single File

```python
python examples/analyze_code.py
```

### Custom Analysis

```python
import asyncio
from backend.packages.memory import MemoryHub
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents import AgentTask

async def analyze():
    # Initialize
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    agent = CodeAnalysisAgent(memory_hub=memory_hub)
    
    # Create task
    task = AgentTask(
        intent="analyze_code",
        inputs={
            "file_path": "/path/to/your/code.py",
            "analysis_type": "security"
        }
    )
    
    # Execute
    result = await agent.execute(task)
    print(result.data)
    
    # Cleanup
    await memory_hub.shutdown()

# Run
asyncio.run(analyze())
```

## 🏗️ Project Structure

```
T-Developer-v2/
├── backend/
│   ├── packages/
│   │   ├── memory/        # Memory Hub (5 contexts)
│   │   └── agents/        # Agent system
│   └── requirements.txt
├── frontend/
│   └── app.py            # Streamlit UI
├── examples/
│   └── analyze_code.py   # Example usage
└── run_ui.sh            # UI launcher
```

## 🔧 Configuration

Edit `.env` file:

```env
# AWS Configuration
AWS_DEFAULT_REGION=us-east-1

# Memory Configuration
MEMORY_STORAGE_PATH=/tmp/t-developer/memory

# Agent Configuration
AGENT_TIMEOUT_SECONDS=300

# Feature Flags
ENABLE_AUTO_EVOLUTION=true
```

## 📊 Features

- **🤖 Real AI Analysis**: Uses Claude via AWS Bedrock
- **💾 Memory System**: 5 context types (O/A/S/U/OBS)
- **🔄 Evolution Ready**: Self-improvement capabilities
- **🎨 Web UI**: Simple, intuitive interface
- **📈 History Tracking**: Remembers previous analyses

## 🆘 Troubleshooting

### AWS Credentials Error
```bash
# Check credentials
aws sts get-caller-identity

# Configure if needed
aws configure
```

### Bedrock Access Error
1. Go to AWS Console → Bedrock
2. Request model access for Claude
3. Wait for approval (usually instant)

### Port Already in Use
```bash
# Change port in run_ui.sh
streamlit run frontend/app.py --server.port 8502
```

## 📚 Next Steps

1. **Add More Agents**: Extend `BaseAgent` for new capabilities
2. **Customize Analysis**: Modify `CodeAnalysisAgent` prompts
3. **Integrate with CI/CD**: Use the API programmatically
4. **Enable Auto-Evolution**: Implement evolution workflows

## 📝 License

MIT License - See LICENSE file

---

**Built with ❤️ for autonomous development**