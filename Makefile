# HerpAI-Ingestion Makefile

# Variables
PYTHON := python3
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
VENV_ACTIVATE := $(VENV_BIN)/activate
PYTHON_VERSION := 3.9
PACKAGE_NAME := herpai-ingestion
GITHUB_USERNAME := openbiocure
GITHUB_REPO := HerpAI-Ingestion

# Test and coverage settings
TESTS_DIR := tests
COVERAGE_OPTIONS := --cov=herpai_ingestion --cov=herpai_connector_sdk --cov=connectors --cov-report=term-missing
TEST_OPTIONS := -v -ra --strict-markers

# Linting settings
FLAKE8_OPTIONS := --max-line-length=88 --extend-ignore=E203
MYPY_OPTIONS := --ignore-missing-imports --strict
BLACK_OPTIONS := --line-length=88
ISORT_OPTIONS := --profile black

# OS specific commands
ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV_NAME)/Scripts
	VENV_ACTIVATE := $(VENV_BIN)/activate
	PYTHON := python
	# Handle path separators for Windows
	SEP := \\
else
	SEP := /
endif

# Define command prefix to activate virtualenv before running commands
VENV_RUN := . $(VENV_ACTIVATE) &&

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: all clean test lint format help venv install dev-install build publish check init ci ci-test docs examples

# Default target
all: help

##@ General
help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "$(BLUE)Usage:$(NC)\n  make $(GREEN)<target>$(NC)\n\n$(BLUE)Targets:$(NC)\n"} \
		/^[a-zA-Z0-9_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Development Environment
venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(GREEN)Virtual environment created at $(VENV_NAME)/$(NC)"
	@echo "$(YELLOW)To activate, run: source $(VENV_ACTIVATE)$(NC)"

install: check-venv ## Install package in development mode
	@echo "$(BLUE)Installing package...$(NC)"
	$(VENV_RUN) pip install -e .
	@echo "$(GREEN)Installation complete.$(NC)"

dev-install: check-venv ## Install package with development dependencies
	@echo "$(BLUE)Installing package with development dependencies...$(NC)"
	$(VENV_RUN) pip install -e ".[dev]"
	@echo "$(GREEN)Development installation complete.$(NC)"

init: dev-install ## Initialize development environment with pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	$(VENV_RUN) pre-commit install
	@echo "$(GREEN)Development environment initialized.$(NC)"

##@ Testing
test: check-venv ## Run all tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	$(VENV_RUN) pytest $(TESTS_DIR) $(TEST_OPTIONS) $(COVERAGE_OPTIONS)

test-unit: check-venv ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(VENV_RUN) pytest tests/unit $(TEST_OPTIONS)

test-integration: check-venv ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(VENV_RUN) pytest tests/integration $(TEST_OPTIONS)

test-e2e: check-venv ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	$(VENV_RUN) pytest tests/e2e $(TEST_OPTIONS)

test-connectors: check-venv ## Run connector tests
	@echo "$(BLUE)Running connector tests...$(NC)"
	$(VENV_RUN) pytest tests/connectors $(TEST_OPTIONS)

##@ Code Quality
lint: check-venv ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	$(VENV_RUN) flake8 $(FLAKE8_OPTIONS) .
	$(VENV_RUN) mypy $(MYPY_OPTIONS) .
	$(VENV_RUN) black --check $(BLACK_OPTIONS) .
	$(VENV_RUN) isort --check-only $(ISORT_OPTIONS) .

format: check-venv ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_RUN) black $(BLACK_OPTIONS) .
	$(VENV_RUN) isort $(ISORT_OPTIONS) .

check: lint test ## Run all quality checks (linting and tests)
	@echo "$(GREEN)All checks passed!$(NC)"

##@ Examples
run-examples: check-venv ## Run all examples
	@echo "$(BLUE)Running examples...$(NC)"
	$(VENV_RUN) python examples/basic/01_basic_ingestion.py

##@ Documentation
docs: check-venv ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	$(VENV_RUN) sphinx-build -b html docs/source docs/build/html
	@echo "$(GREEN)Documentation built at docs/build/html/index.html$(NC)"

##@ CI/CD
ci: clean venv dev-install ci-test lint ## Run CI pipeline locally
	@echo "$(GREEN)CI pipeline completed!$(NC)"

ci-test: check-venv ## Run tests in CI mode
	@echo "$(BLUE)Running tests in CI mode...$(NC)"
	CI=true $(VENV_RUN) pytest $(TESTS_DIR) $(TEST_OPTIONS) $(COVERAGE_OPTIONS)

##@ Building and Publishing
build: check-venv ## Build package distributions
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_RUN) pip install --upgrade build
	$(VENV_RUN) python -m build
	@echo "$(GREEN)Package built successfully.$(NC)"

publish-test: build ## Publish package to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	$(VENV_RUN) pip install --upgrade twine
	$(VENV_RUN) python -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)Package published to TestPyPI.$(NC)"

publish: build ## Publish package to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	$(VENV_RUN) pip install --upgrade twine
	$(VENV_RUN) python -m twine upload dist/*
	@echo "$(GREEN)Package published to PyPI.$(NC)"

##@ Maintenance
clean: ## Clean up build artifacts and virtual environment
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV_NAME)/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "$(GREEN)Cleanup complete.$(NC)"

# Helper targets
check-venv: ## Check if virtual environment exists, create if it doesn't
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Virtual environment not found. Creating one...$(NC)"; \
		$(MAKE) venv; \
	fi

##@ Dependencies
update-corelib: check-venv ## Uninstall and reinstall openbiocure-corelib from local dist, pass VERSION=x.y.z
	@echo "$(BLUE)Updating openbiocure-corelib to version $(VERSION)...$(NC)"
	$(VENV_RUN) pip uninstall -y openbiocure-corelib
	$(VENV_RUN) pip install /Users/mohammad_shehab/develop/HerpAI-Lib/dist/openbiocure_corelib-$(VERSION)-py3-none-any.whl
	@echo "$(GREEN)openbiocure-corelib updated to version $(VERSION).$(NC)"
