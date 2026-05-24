.PHONY: help install dev prod run test lint format type-check clean setup

# Variables
PYTHON := python3
PIP := pip3

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Context-Aware Question Generator$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make setup      # Initial setup"
	@echo "  make dev        # Run development server"
	@echo "  make test       # Run tests"
	@echo "  make lint       # Check code style"

# ============================================================================
# Setup & Installation
# ============================================================================

setup: install ## Initial project setup (install dependencies)
	@echo "$(GREEN)✓ Project setup complete!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  cp .env.example .env"
	@echo "  make dev"

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: install ## Install dependencies including dev tools
	@echo "$(BLUE)Installing development tools...$(NC)"
	$(PIP) install black ruff mypy
	@echo "$(GREEN)✓ Dev tools installed$(NC)"

# ============================================================================
# Running the Application
# ============================================================================

dev: ## Run development server (with auto-reload)
	@echo "$(BLUE)Starting development server...$(NC)"
	@echo "$(GREEN)Open http://localhost:8000/docs in your browser$(NC)"
	$(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

prod: ## Run production server (no auto-reload)
	@echo "$(BLUE)Starting production server...$(NC)"
	$(PYTHON) -m uvicorn src.main:app --host 0.0.0.0 --port 8000

run: dev ## Alias for dev target

# ============================================================================
# Testing
# ============================================================================

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-phase1: ## Run Phase 1 tests
	@echo "$(BLUE)Running Phase 1 tests...$(NC)"
	$(PYTHON) -m pytest tests/test_config.py -v

test-phase2: ## Run Phase 2 tests
	@echo "$(BLUE)Running Phase 2 tests...$(NC)"
	$(PYTHON) -m pytest tests/test_mcp_integration.py -v

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Run linter (ruff)
	@echo "$(BLUE)Linting code...$(NC)"
	$(PYTHON) -m ruff check src/ tests/

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	$(PYTHON) -m black src/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Type checking...$(NC)"
	$(PYTHON) -m mypy src/
	@echo "$(GREEN)✓ Type check complete$(NC)"

quality: lint format type-check ## Run all code quality checks

# ============================================================================
# Utility
# ============================================================================

clean: ## Clean up generated files and cache
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.egg-info' -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache build dist
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

verify: ## Verify health check and MCPs
	@echo "$(BLUE)Verifying systems...$(NC)"
	@echo "$(GREEN)Waiting for server to be ready...$(NC)"
	@sleep 2
	@echo "$(GREEN)✓ Health check:$(NC)"
	@curl -s http://localhost:8000/health | $(PYTHON) -m json.tool || echo "Server not running"
	@echo ""
	@echo "$(GREEN)✓ MCPs:$(NC)"
	@curl -s http://localhost:8000/mcps | $(PYTHON) -m json.tool || echo "Server not running"

shell: ## Open Python shell with project context
	@echo "$(BLUE)Starting Python shell...$(NC)"
	$(PYTHON)

env-setup: ## Setup environment file from template
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(BLUE)Edit .env with your configuration$(NC)"; \
		echo "$(GREEN)✓ .env created$(NC)"; \
	else \
		echo "$(GREEN)✓ .env already exists$(NC)"; \
	fi

check: ## Run all checks (lint, type-check, test)
	@echo "$(BLUE)Running all checks...$(NC)"
	$(MAKE) lint
	$(MAKE) type-check
	@echo "$(GREEN)✓ All checks passed$(NC)"

update: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

# ============================================================================
# Docker (optional)
# ============================================================================

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t context-aware-question-generator .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run application in Docker
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 8000:8000 -v $(PWD)/output:/app/output context-aware-question-generator

docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker ps -q --filter "ancestor=context-aware-question-generator" | xargs docker stop 2>/dev/null || true
	@echo "$(GREEN)✓ Containers stopped$(NC)"

# ============================================================================
# Defaults
# ============================================================================

.DEFAULT_GOAL := help
