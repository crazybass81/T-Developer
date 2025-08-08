# T-Developer Lambda Deployment Makefile

.PHONY: help build deploy test clean validate logs

# Default environment
ENV ?= development
REGION ?= us-east-1
STACK_NAME = t-developer-lambda-stack-$(ENV)

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(GREEN)T-Developer Lambda Deployment Commands$(NC)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Usage: make [command] ENV=[development|staging|production]"
	@echo "Example: make deploy ENV=production"

install: ## Install dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	pip install -r ../../requirements.txt
	pip install aws-sam-cli
	@echo "$(GREEN)Dependencies installed$(NC)"

validate: ## Validate SAM template
	@echo "$(YELLOW)Validating SAM template...$(NC)"
	sam validate --template template.yaml
	@echo "$(GREEN)Template is valid$(NC)"

build: validate ## Build SAM application
	@echo "$(YELLOW)Building SAM application for $(ENV)...$(NC)"
	sam build \
		--template template.yaml \
		--config-env $(ENV) \
		--parallel \
		--cached
	@echo "$(GREEN)Build completed$(NC)"

deploy: build ## Deploy to AWS
	@echo "$(YELLOW)Deploying to $(ENV) environment...$(NC)"
	sam deploy \
		--stack-name $(STACK_NAME) \
		--config-env $(ENV) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--no-confirm-changeset \
		--no-fail-on-empty-changeset
	@echo "$(GREEN)Deployment completed$(NC)"

test-local: ## Test functions locally
	@echo "$(YELLOW)Starting local testing...$(NC)"
	./local-test.sh

test-deployed: ## Test deployed functions
	@echo "$(YELLOW)Testing deployed functions in $(ENV)...$(NC)"
	@for agent in nl-input ui-selection parser component-decision match-rate search generation assembly download; do \
		echo "Testing $$agent agent..."; \
		aws lambda invoke \
			--function-name t-developer-$$agent-agent-$(ENV) \
			--payload '{"body": {"test": true}}' \
			--cli-binary-format raw-in-base64-out \
			response.json > /dev/null 2>&1; \
		if grep -q "statusCode.*200" response.json; then \
			echo "$(GREEN)✓ $$agent test passed$(NC)"; \
		else \
			echo "$(RED)✗ $$agent test failed$(NC)"; \
			cat response.json; \
		fi; \
		rm -f response.json; \
	done

logs: ## View logs for a specific function
	@read -p "Enter agent name (nl-input, ui-selection, etc.): " agent; \
	aws logs tail /aws/lambda/t-developer-$$agent-agent-$(ENV) --follow

metrics: ## View CloudWatch metrics
	@echo "$(YELLOW)Fetching metrics for $(ENV)...$(NC)"
	@aws cloudwatch get-metric-statistics \
		--namespace AWS/Lambda \
		--metric-name Invocations \
		--dimensions Name=FunctionName,Value=t-developer-nl-input-agent-$(ENV) \
		--start-time $$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S') \
		--end-time $$(date -u '+%Y-%m-%dT%H:%M:%S') \
		--period 300 \
		--statistics Sum

delete: ## Delete the stack
	@echo "$(RED)WARNING: This will delete the $(STACK_NAME) stack$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		aws cloudformation delete-stack --stack-name $(STACK_NAME); \
		echo "$(YELLOW)Waiting for stack deletion...$(NC)"; \
		aws cloudformation wait stack-delete-complete --stack-name $(STACK_NAME); \
		echo "$(GREEN)Stack deleted$(NC)"; \
	else \
		echo "Deletion cancelled"; \
	fi

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf .aws-sam
	rm -rf layers/common/python
	rm -f response.json
	rm -f env.json
	@echo "$(GREEN)Cleaned$(NC)"

status: ## Check stack status
	@echo "$(YELLOW)Checking stack status for $(ENV)...$(NC)"
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--query 'Stacks[0].StackStatus' \
		--output text 2>/dev/null || echo "Stack not found"

outputs: ## Show stack outputs
	@echo "$(YELLOW)Stack outputs for $(ENV):$(NC)"
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
		--output table

update-code: ## Quick update function code only
	@read -p "Enter agent name to update: " agent; \
	echo "$(YELLOW)Updating $$agent agent code...$(NC)"; \
	cd ../../src/agents/production/$$agent && \
	zip -r function.zip . -x "*.pyc" -x "__pycache__/*" && \
	aws lambda update-function-code \
		--function-name t-developer-$$agent-agent-$(ENV) \
		--zip-file fileb://function.zip && \
	rm function.zip && \
	echo "$(GREEN)Code updated$(NC)"

monitor: ## Open CloudWatch dashboard
	@echo "$(YELLOW)Opening CloudWatch dashboard...$(NC)"
	@aws cloudwatch put-dashboard \
		--dashboard-name T-Developer-$(ENV) \
		--dashboard-body file://cloudwatch-dashboard.json 2>/dev/null || true
	@echo "Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$(REGION)#dashboards:name=T-Developer-$(ENV)"

all: install validate build deploy test-deployed ## Full deployment pipeline

.DEFAULT_GOAL := help