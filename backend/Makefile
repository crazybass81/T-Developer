.PHONY: help install dev-install format lint type-check test security clean build run docker-up docker-down

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

format: ## Format code with Black and isort
	black src tests
	isort src tests

lint: ## Run linting checks
	flake8 src tests
	pylint src

type-check: ## Run type checking with mypy
	mypy src

test: ## Run all tests
	pytest tests -v --cov=src --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests -v -m unit

test-integration: ## Run integration tests only
	pytest tests -v -m integration

test-e2e: ## Run end-to-end tests only
	pytest tests -v -m e2e

security: ## Run security checks
	bandit -r src
	safety check -r requirements.txt
	safety check -r requirements-dev.txt

clean: ## Clean build artifacts and cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist htmlcov .coverage coverage.xml

build: clean ## Build the project
	python setup.py sdist bdist_wheel

run: ## Run the development server
	uvicorn src.main_api:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-clean: docker-down ## Clean Docker resources
	docker-compose down -v
	docker system prune -f

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

setup-hooks: ## Install git hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

check-all: format lint type-check security test ## Run all checks

ci: ## Run CI pipeline checks
	make format
	make lint
	make type-check
	make security
	make test

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-rollback: ## Rollback last migration
	alembic downgrade -1

db-reset: ## Reset database
	alembic downgrade base
	alembic upgrade head

agent-test: ## Test specific agent
	@read -p "Enter agent name (e.g., nl_input): " agent; \
	pytest tests/agents/test_$$agent.py -v

agent-run: ## Run specific agent standalone
	@read -p "Enter agent name (e.g., nl_input): " agent; \
	python -m src.agents.$$agent.main

benchmark: ## Run performance benchmarks
	python scripts/benchmark.py

profile: ## Profile application performance
	python -m cProfile -o profile.stats src/main_api.py
	python -m pstats profile.stats

docs: ## Generate documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

deploy-dev: ## Deploy to development environment
	./scripts/deploy.sh development

deploy-staging: ## Deploy to staging environment
	./scripts/deploy.sh staging

deploy-prod: ## Deploy to production environment
	@echo "⚠️  Production deployment requires confirmation"
	@read -p "Are you sure? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		./scripts/deploy.sh production; \
	fi

monitoring-start: ## Start monitoring stack
	docker-compose -f docker-compose.monitoring.yml up -d

monitoring-stop: ## Stop monitoring stack
	docker-compose -f docker-compose.monitoring.yml down