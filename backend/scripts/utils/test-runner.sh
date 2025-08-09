#!/bin/bash

# T-Developer Test Runner Script

set -e

echo "🧪 T-Developer Test Suite"
echo "========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if npm is available
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

# Parse command line arguments
TEST_TYPE=${1:-"all"}
COVERAGE=${2:-"false"}

case $TEST_TYPE in
    "unit")
        print_status "Running unit tests..."
        if [ "$COVERAGE" = "true" ]; then
            npm run test:unit -- --coverage
        else
            npm run test:unit
        fi
        ;;
    "integration")
        print_status "Running integration tests..."
        npm run test:integration
        ;;
    "e2e")
        print_status "Running E2E tests..."
        print_warning "Make sure test services are running"
        npm run test:e2e
        ;;
    "all")
        print_status "Running all tests..."
        
        print_status "1/3 - Unit tests"
        npm run test:unit
        
        print_status "2/3 - Integration tests"
        npm run test:integration
        
        print_status "3/3 - E2E tests"
        npm run test:e2e
        
        if [ "$COVERAGE" = "true" ]; then
            print_status "Generating coverage report..."
            npm run test:coverage
        fi
        ;;
    "watch")
        print_status "Running tests in watch mode..."
        npm run test:watch
        ;;
    *)
        echo "Usage: $0 [unit|integration|e2e|all|watch] [coverage]"
        echo ""
        echo "Examples:"
        echo "  $0 unit          # Run unit tests only"
        echo "  $0 all coverage  # Run all tests with coverage"
        echo "  $0 watch         # Run tests in watch mode"
        exit 1
        ;;
esac

print_status "Tests completed!"