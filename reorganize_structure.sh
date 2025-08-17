#!/bin/bash
# Reorganize T-Developer project structure

echo "📦 Reorganizing T-Developer project structure..."

# 1. Move test scripts to scripts/tests/
echo "Moving test scripts..."
mkdir -p scripts/tests
mv test_evolution_with_ai.py scripts/tests/ 2>/dev/null || true
mv run_real_evolution.py scripts/tests/ 2>/dev/null || true

# 2. Move documentation to proper locations
echo "Organizing documentation..."
mkdir -p docs/project
mv integration_plan.md docs/project/ 2>/dev/null || true
mv SYSTEM_STATUS.md docs/project/ 2>/dev/null || true
mv MVP_USAGE.md docs/project/ 2>/dev/null || true
mv AGENT_ARCHITECTURE.md docs/architecture/ 2>/dev/null || true
mv MASTER_PLAN.md docs/00_planning/ 2>/dev/null || true

# 3. Clean up coverage reports
echo "Cleaning coverage reports..."
rm -rf htmlcov 2>/dev/null || true
rm -rf backend/htmlcov 2>/dev/null || true

# 4. Move API configs  
echo "Organizing API configs..."
mkdir -p config/api
mv api_endpoint.txt config/api/ 2>/dev/null || true

# 5. Move shell scripts
echo "Organizing shell scripts..."
mkdir -p scripts/shell
mv start_ui.sh scripts/shell/ 2>/dev/null || true
mv tdev scripts/shell/ 2>/dev/null || true

# 6. Create organized structure info
cat > PROJECT_STRUCTURE.md << 'EOF'
# T-Developer Project Structure

```
T-DeveloperMVP/
├── backend/                 # Backend server & agents
│   ├── main.py              # FastAPI server
│   ├── agent_manager.py     # Agent orchestration
│   ├── evolution_engine.py  # Evolution orchestration
│   ├── packages/            # Core packages
│   │   ├── agents/          # Agent implementations
│   │   ├── learning/        # Learning system
│   │   ├── performance/     # Performance optimization
│   │   ├── sandbox/         # Sandbox environment
│   │   └── ...
│   ├── tests/               # Backend tests
│   └── references/          # Reference materials
│
├── frontend/                # React frontend
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   └── package.json
│
├── scripts/                 # Utility scripts
│   ├── tests/               # Test scripts
│   ├── shell/               # Shell scripts
│   └── *.py                 # Python utilities
│
├── config/                  # Configuration files
│   ├── api/                 # API configs
│   ├── k6-scripts/          # Load test scripts
│   └── *.yaml               # Config files
│
├── docs/                    # Documentation
│   ├── 00_planning/         # Planning docs
│   ├── architecture/        # Architecture docs
│   ├── implementation/      # Implementation guides
│   ├── operations/          # Operations docs
│   ├── project/             # Project management
│   └── reference/           # API references
│
├── lambda_handlers/         # AWS Lambda handlers
├── infrastructure/          # Infrastructure configs
├── blueprints/              # Service blueprints
├── schemas/                 # Data schemas
├── examples/                # Example code
│
├── README.md                # Project overview
├── CLAUDE.md                # AI assistant guide
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Python project config
└── docker-compose.yml       # Docker setup
```

## Key Directories

### Backend (`/backend`)
- Core application server and agent implementations
- All business logic and API endpoints
- Tests colocated with source code

### Frontend (`/frontend`)
- React-based web interface
- Redux state management
- WebSocket integration

### Scripts (`/scripts`)
- Deployment scripts
- Testing utilities
- Development tools

### Documentation (`/docs`)
- Comprehensive project documentation
- Architecture decisions
- Implementation guides

### Configuration (`/config`)
- Environment configs
- Test scenarios
- Policy definitions
EOF

echo "✅ Reorganization complete!"
echo "📄 Created PROJECT_STRUCTURE.md for reference"

# Show summary
echo ""
echo "Summary of changes:"
echo "- Test scripts moved to scripts/tests/"
echo "- Documentation organized in docs/"
echo "- Coverage reports cleaned up"
echo "- Shell scripts moved to scripts/shell/"
echo "- Created PROJECT_STRUCTURE.md"