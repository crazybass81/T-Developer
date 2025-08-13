#!/bin/bash

set -e

echo "🚀 Setting up T-Developer development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_status "Python version $PYTHON_VERSION is compatible"
else
    print_error "Python version $PYTHON_VERSION is not compatible. Required: >= $REQUIRED_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
print_status "pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-dev.txt
print_status "Dependencies installed"

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
print_status "Pre-commit hooks installed"

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p data/cache
mkdir -p data/uploads
mkdir -p data/downloads
print_status "Directories created"

# Set up environment variables
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
DEBUG=True

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database Configuration
DATABASE_URL=postgresql://tdeveloper:tdeveloper123@localhost:5432/t_developer
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Application Settings
LOG_LEVEL=DEBUG
MAX_WORKERS=4
REQUEST_TIMEOUT=300

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF
    print_status ".env file created (please update with your credentials)"
else
    print_warning ".env file already exists"
fi

# Initialize database
echo "Setting up database..."
if command -v docker &> /dev/null; then
    docker-compose up -d postgres redis
    sleep 5
    print_status "Database services started"
else
    print_warning "Docker not found. Please install Docker or set up PostgreSQL and Redis manually"
fi

# Run database migrations
echo "Running database migrations..."
if [ -d "alembic" ]; then
    alembic upgrade head
    print_status "Database migrations completed"
else
    print_warning "Alembic not configured yet"
fi

# Run initial tests
echo "Running initial tests..."
pytest tests/test_health.py -v || print_warning "No health tests found yet"

# Generate initial documentation
echo "Building documentation..."
if [ -f "mkdocs.yml" ]; then
    mkdocs build
    print_status "Documentation built"
else
    print_warning "MkDocs not configured yet"
fi

echo ""
echo "✨ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Update .env file with your credentials"
echo "3. Start the development server: make run"
echo "4. Run tests: make test"
echo "5. View documentation: make docs-serve"
echo ""
echo "For more commands, run: make help"
