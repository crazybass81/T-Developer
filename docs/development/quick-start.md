# 🚀 AI Autonomous Evolution System - Quick Start

## Overview

Start the T-Developer AI Autonomous Evolution System that achieves 85% AI autonomy through genetic algorithms and meta-learning.

## Prerequisites

- **Python 3.11+** (3.12 recommended)
- **UV Package Manager** (ultra-fast Python package management)
- **Docker & Docker Compose**
- **AWS Account** with Bedrock, ECS, and Parameter Store access
- **32GB RAM** (for evolution testing)
- **Linux/macOS** (WSL2 for Windows)

## 🧬 Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/t-developer-evolution.git
cd t-developer-evolution
```

### 2. Install UV Package Manager
```bash
# Install UV (replaces pip for ultra-fast installs)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

### 3. Setup Python Environment
```bash
cd backend

# Create virtual environment with UV
uv venv
source .venv/bin/activate

# Install dependencies (ultra-fast with UV)
uv pip install -r requirements.txt
uv pip install -r requirements-evolution.txt
```

### 4. AWS Configuration
```bash
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Key, Region (us-east-1), and output format

# Set evolution-specific environment variables
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-opus
export EVOLUTION_MODE=enabled
export AI_AUTONOMY_LEVEL=0.85
export MEMORY_CONSTRAINT_KB=6.5
export INSTANTIATION_TARGET_US=3
```

### 5. Initialize Evolution Database
```bash
# Run migrations for evolution tracking
cd backend
alembic upgrade head

# Initialize evolution checkpoints
python src/evolution/initialize_checkpoints.py
```

## 🧬 Start the Evolution System

### Quick Start (Development Mode)
```bash
# Start all services with Docker Compose
docker-compose -f docker-compose.evolution.yml up -d

# Initialize the evolution engine
cd backend
python src/evolution/engine.py --init

# Start the autonomous evolution
python src/main_evolution.py
```

### Production Start (ECS Fargate)
```bash
# Deploy to AWS ECS
./infrastructure/aws/deploy-evolution.sh

# Monitor deployment
aws ecs describe-services --cluster t-developer-evolution

# Start evolution monitoring
python src/monitoring/evolution_monitor.py --production
```

## 🎮 First Evolution Cycle

### 1. Initialize First Generation
```python
# backend/scripts/start_first_evolution.py
from src.evolution.engine import EvolutionEngine
from src.evolution.fitness import FitnessEvaluator

# Initialize evolution engine
engine = EvolutionEngine(
    autonomy_level=0.85,
    memory_constraint_kb=6.5,
    instantiation_target_us=3
)

# Create first generation of agents
first_gen = engine.create_initial_generation(
    population_size=100,
    agent_types=['nl_input', 'parser', 'generation']
)

# Start evolution
engine.evolve(generations=10, target_fitness=0.95)
```

### 2. Monitor Evolution Progress
```bash
# Real-time evolution monitoring
python src/monitoring/evolution_dashboard.py

# Check fitness scores
curl http://localhost:8000/api/v1/evolution/fitness

# View generation statistics
curl http://localhost:8000/api/v1/evolution/stats
```

### 3. Validate Evolution Safety
```bash
# Run safety checks
python src/security/evolution_safety_validator.py --validate-all

# Check for malicious patterns
python src/security/malicious_evolution_detector.py --scan-latest

# Verify checkpoints
python src/evolution/checkpoint_manager.py --verify
```

## 📊 Evolution Dashboard

### Access the Dashboard
```bash
# Start the monitoring dashboard
python src/monitoring/start_dashboard.py

# Open in browser
open http://localhost:8000/evolution
```

### Key Metrics to Monitor
- **AI Autonomy**: Current autonomy percentage (target: 85%)
- **Fitness Score**: Generation fitness (improves 5% per generation)
- **Memory Usage**: Per-agent memory (must stay < 6.5KB)
- **Instantiation Speed**: Agent creation time (target < 3μs)
- **Evolution Safety**: Safety score (must be 100%)
- **Cost Reduction**: Automated optimization savings (target 30%+)

## 🧪 Test the System

### Run Evolution Tests
```bash
cd backend

# Unit tests for evolution components
pytest tests/evolution/ -v

# Integration tests for genetic algorithms
pytest tests/integration/test_genetic_algorithms.py -v

# Performance benchmarks
pytest tests/performance/test_evolution_performance.py -v --benchmark

# Safety validation tests
pytest tests/security/test_evolution_safety.py -v
```

### Validate Constraints
```bash
# Memory constraint validation (6.5KB)
python tests/performance/validate_memory_constraint.py

# Instantiation speed test (3μs)
python tests/performance/validate_instantiation_speed.py

# AI autonomy validation (85%)
python tests/evolution/validate_autonomy_level.py
```

## 🛡️ Security & Safety

### Enable All Safety Features
```bash
# Activate evolution safety framework
export EVOLUTION_SAFETY=strict

# Enable prompt injection defense
export PROMPT_DEFENSE=enabled

# Activate PII detection
export PII_DETECTION=auto

# Start with safety monitoring
python src/main_evolution.py --safety-mode
```

### Emergency Controls
```bash
# Stop evolution immediately
python src/evolution/emergency_stop.py

# Rollback to last safe checkpoint
python src/evolution/rollback.py --to-last-safe

# Reset to initial state
python src/evolution/reset_evolution.py --confirm
```

## 📈 Performance Optimization

### Optimize Memory Usage
```bash
# Analyze current memory usage
python src/optimization/memory_analyzer.py

# Apply memory optimizations
python src/optimization/memory_optimizer.py --target 6.5KB
```

### Speed Optimization
```bash
# Profile instantiation speed
python src/optimization/speed_profiler.py

# Apply speed optimizations
python src/optimization/speed_optimizer.py --target 3us
```

## 🔧 Troubleshooting

### Common Issues

1. **Evolution Not Starting**
   ```bash
   # Check evolution engine status
   python src/evolution/check_status.py
   
   # View logs
   tail -f logs/evolution.log
   ```

2. **Memory Constraint Violations**
   ```bash
   # Reset memory allocations
   python src/evolution/reset_memory.py
   
   # Reduce agent complexity
   export AGENT_COMPLEXITY=minimal
   ```

3. **Safety Violations**
   ```bash
   # View safety report
   python src/security/safety_report.py
   
   # Reset safety framework
   python src/security/reset_safety.py
   ```

## 📚 Next Steps

1. **Read the Full Documentation**
   - [AI-DRIVEN-EVOLUTION.md](../../AI-DRIVEN-EVOLUTION.md) - 80-day implementation plan
   - [Evolution Safety Framework](../security/evolution-safety-framework.md)
   - [Performance Optimization](../architecture/performance-optimization-strategy.md)

2. **Configure Production Settings**
   - Set up AWS ECS Fargate
   - Configure Bedrock AgentCore
   - Enable production monitoring

3. **Join the Evolution**
   - Monitor daily improvements
   - Contribute to fitness functions
   - Help improve safety constraints

---

**System**: AI Autonomous Evolution  
**Autonomy**: 85%  
**Status**: Ready to Evolve

> "Launch the evolution and watch AI create itself"