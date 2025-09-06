# OpenBioCure-Ingestion Makefile

PYTHON_VERSION := 3
VENV_DIR := .venv
CORELIB_PATH ?= ../OpenBioCure-Lib
CORELIB_NAME := openbiocure-corelib

TEST_DIR := tests
UNIT_TEST_DIR := $(TEST_DIR)/unit
INTEGRATION_TEST_DIR := $(TEST_DIR)/integration
CONNECTOR_TEST_DIR := $(TEST_DIR)/connectors

PYTEST := $(VENV_DIR)/bin/pytest
PYTEST_ARGS := -v

BLACK := $(VENV_DIR)/bin/black
ISORT := $(VENV_DIR)/bin/isort
FLAKE8 := $(VENV_DIR)/bin/flake8
MYPY := $(VENV_DIR)/bin/mypy

SRC_DIRS := obc_ingestion obc_connector_sdk connectors tests

DOCS_DIR := docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build

DOCKER_IMAGE := OpenBioCure-ingestion
DOCKER_TAG := latest

DB_NAME := OpenBioCure
DB_USER := postgres
DB_PASSWORD := postgres
DB_PORT := 5432

.PHONY: help
help:
	@echo "OpenBioCure-Ingestion Makefile"
	@echo "---------------------------"
	@echo "Environment setup:"
	@echo "  venv                 Create virtual environment"
	@echo "  setup-dev            Set up complete development environment"
	@echo ""
	@echo "CoreLib management:"
	@echo "  install-corelib      Install CoreLib from local path"
	@echo "  update-corelib       Update CoreLib to specific version"
	@echo "                       Usage: make update-corelib VERSION=3.1.0"
	@echo "  check-corelib-version Check installed CoreLib version"
	@echo "  verify-corelib-compatibility Verify CoreLib compatibility"
	@echo ""
	@echo "Testing:"
	@echo "  test                 Run all tests"
	@echo "  test-unit            Run unit tests"
	@echo "  test-integration     Run integration tests"
	@echo "  test-connectors      Run connector tests"
	@echo "  coverage             Run tests with coverage report"
	@echo ""
	@echo "Code quality:"
	@echo "  format               Format code with black and isort"
	@echo "  check-format         Check code formatting"
	@echo "  lint                 Run linters"
	@echo "  quality-check        Run all code quality checks"
	@echo ""
	@echo "Run components:"
	@echo "  run-scheduler        Run the scheduler"
	@echo "  run-worker           Run a worker"
	@echo "  list-connectors      List connectors"
	@echo "  test-connector       Test a specific connector (CONNECTOR=pubmed)"
	@echo ""
	@echo "Docs:"
	@echo "  docs                 Build documentation"
	@echo "  docs-serve           Serve documentation locally"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build         Build Docker image"
	@echo "  docker-run           Run Docker container"
	@echo ""
	@echo "Database:"
	@echo "  db-start             Start local development database"
	@echo "  db-stop              Stop local development database"
	@echo ""
	@echo "Build:"
	@echo "  build                Build package"
	@echo "  clean                Clean build artifacts"

venv:
	python$(PYTHON_VERSION) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

install-deps: venv
	$(VENV_DIR)/bin/pip install -U pip setuptools wheel
	$(VENV_DIR)/bin/pip install -e .

install-dev-deps: install-deps
	$(VENV_DIR)/bin/pip install -e ".[dev]"

install-corelib:
	@if [ ! -d "$(CORELIB_PATH)" ]; then \
		echo "Error: CoreLib path $(CORELIB_PATH) does not exist"; \
		echo "Specify the correct path with: make install-corelib CORELIB_PATH=/path/to/corelib"; \
		exit 1; \
	fi
	$(VENV_DIR)/bin/pip install -e "$(CORELIB_PATH)"
	@echo "Installed CoreLib from $(CORELIB_PATH)"

update-corelib:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION parameter required"; \
		echo "Usage: make update-corelib VERSION=3.1.0"; \
		exit 1; \
	fi
	@if ! echo "$(VERSION)" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$$'; then \
		echo "Error: Invalid version format. Expected format: X.Y.Z or X.Y.Z-suffix"; \
		exit 1; \
	fi
	@echo "Backing up current CoreLib installation..."
	@mkdir -p .backups
	@$(VENV_DIR)/bin/pip freeze | grep "$(CORELIB_NAME)" > .backups/corelib-$(shell date +%Y%m%d%H%M%S).txt || true
	@if [ ! -d "$(CORELIB_PATH)" ]; then \
		echo "Error: CoreLib path $(CORELIB_PATH) does not exist"; \
		echo "Specify the correct path with: make update-corelib VERSION=$(VERSION) CORELIB_PATH=/path/to/corelib"; \
		exit 1; \
	fi
	@echo "Checking out version $(VERSION) in $(CORELIB_PATH)..."
	@(cd "$(CORELIB_PATH)" && git fetch && git checkout v$(VERSION))
	@echo "Updating CoreLib to version $(VERSION)..."
	$(VENV_DIR)/bin/pip install -e "$(CORELIB_PATH)"
	@echo "CoreLib updated to version $(VERSION)"

check-corelib-version:
	@echo "Installed CoreLib versions:"
	@$(VENV_DIR)/bin/pip freeze | grep "$(CORELIB_NAME)"

verify-corelib-compatibility: check-corelib-version
	@echo "Verifying CoreLib compatibility..."
	@$(VENV_DIR)/bin/python -c "from openbiocure_corelib import version; print(f'CoreLib version: {version.__version__}')"
	@echo "Compatibility check completed"

setup-dev: install-dev-deps install-corelib
	@echo "Development environment setup complete"

test: test-unit test-integration test-connectors

test-unit:
	$(PYTEST) $(PYTEST_ARGS) $(UNIT_TEST_DIR)

test-integration:
	$(PYTEST) $(PYTEST_ARGS) $(INTEGRATION_TEST_DIR)

test-connectors:
	$(PYTEST) $(PYTEST_ARGS) $(CONNECTOR_TEST_DIR)

test-smoke:
	$(PYTEST) $(PYTEST_ARGS) -m smoke $(TEST_DIR)

test-regression:
	$(PYTEST) $(PYTEST_ARGS) -m regression $(TEST_DIR)

test-no-network:
	$(PYTEST) $(PYTEST_ARGS) -m "not network" $(TEST_DIR)

test-runner:
	python $(TEST_DIR)/test_runner.py

coverage:
	$(PYTEST) $(PYTEST_ARGS) --cov=obc_connector_sdk --cov=obc_ingestion --cov-report=term --cov-report=html $(TEST_DIR)
	@echo "Coverage report available at htmlcov/index.html"

format:
	$(BLACK) $(SRC_DIRS)
	$(ISORT) $(SRC_DIRS)

check-format:
	$(BLACK) --check $(SRC_DIRS)
	$(ISORT) --check-only $(SRC_DIRS)

lint:
	# $(FLAKE8) $(SRC_DIRS)
	# $(MYPY) $(SRC_DIRS)

quality-check: check-format lint

run-scheduler:
	$(VENV_DIR)/bin/OpenBioCure-ingestion scheduler run

run-worker:
	$(VENV_DIR)/bin/OpenBioCure-ingestion worker start

list-connectors:
	$(VENV_DIR)/bin/OpenBioCure-ingestion ingest list-connectors

test-connector:
	@if [ -z "$(CONNECTOR)" ]; then \
		echo "Error: CONNECTOR parameter required"; \
		echo "Usage: make test-connector CONNECTOR=pubmed"; \
		exit 1; \
	fi
	$(VENV_DIR)/bin/OpenBioCure-ingestion connector test $(CONNECTOR)

docs:
	$(VENV_DIR)/bin/sphinx-build -b html $(DOCS_DIR) $(DOCS_BUILD_DIR)
	@echo "Documentation built at $(DOCS_BUILD_DIR)/index.html"

docs-serve: docs
	$(VENV_DIR)/bin/python -m http.server --directory $(DOCS_BUILD_DIR)

build:
	$(VENV_DIR)/bin/python -m build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf $(DOCS_BUILD_DIR)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	docker run -it --rm $(DOCKER_IMAGE):$(DOCKER_TAG)

db-start:
	docker run -d --name OpenBioCure-db \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-p $(DB_PORT):5432 \
		postgres:14
	@echo "Database running on port $(DB_PORT)"

db-stop:
	docker stop OpenBioCure-db
	docker rm OpenBioCure-db
