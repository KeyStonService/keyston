# SynergyMesh Governance Framework - Makefile
# Version: 1.0.0
# Last Updated: 2025-12-10

.PHONY: help install test lint format validate docs clean deploy

# Default target
help:
	@echo "SynergyMesh Governance Framework - Available Commands"
	@echo "======================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install Python dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Quality & Validation:"
	@echo "  make test             Run all tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make lint             Run code linters"
	@echo "  make format           Format code with black"
	@echo "  make validate         Validate governance configurations"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             Build documentation"
	@echo "  make docs-serve       Serve documentation locally"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start governance services"
	@echo "  make docker-down      Stop governance services"
	@echo "  make docker-logs      View service logs"
	@echo ""
	@echo "Development:"
	@echo "  make run-dashboard    Run governance dashboard"
	@echo "  make run-cli          Run governance CLI"
	@echo "  make clean            Clean build artifacts"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy           Deploy governance framework"
	@echo "  make deploy-test      Deploy to test environment"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-watch:
	pytest-watch tests/

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 tools/ tests/ --max-line-length=100
	@echo "Running pylint..."
	pylint tools/ tests/ --disable=C0111
	@echo "Running mypy..."
	mypy tools/ tests/ --ignore-missing-imports

format:
	black tools/ tests/ --line-length=100

format-check:
	black tools/ tests/ --check --line-length=100

# Validation
validate:
	@echo "Validating YAML configurations..."
	python tools/governance-cli.py validate --all
	@echo "Validating schemas..."
	python tools/governance-cli.py validate --schemas
	@echo "Checking dependencies..."
	python tools/governance-cli.py validate --dependencies

# Documentation
docs:
	cd docs && sphinx-build -b html . _build/html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

docs-clean:
	rm -rf docs/_build

# Docker Operations
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Development
run-dashboard:
	python tools/governance-dashboard.py

run-cli:
	python tools/governance-cli.py

run-validator:
	python tools/governance-cli.py validate --all --verbose

# Reports
report-assessment:
	python tools/governance-cli.py report --type assessment --output reports/

report-compliance:
	python tools/governance-cli.py report --type compliance --output reports/

report-metrics:
	python tools/governance-cli.py report --type metrics --output reports/

report-all:
	make report-assessment
	make report-compliance
	make report-metrics

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf docs/_build

clean-all: clean docker-clean

# Deployment
deploy-test:
	@echo "Deploying to test environment..."
	# Add deployment commands here

deploy:
	@echo "Deploying governance framework..."
	@echo "1. Validating configurations..."
	make validate
	@echo "2. Running tests..."
	make test
	@echo "3. Building Docker images..."
	make docker-build
	@echo "4. Starting services..."
	make docker-up
	@echo "Deployment complete!"

# Monitoring
monitor-start:
	docker-compose --profile monitoring up -d

monitor-stop:
	docker-compose --profile monitoring down

# Integration
integration-coordinator:
	python integration/integration-coordinator.py

integration-test:
	pytest tests/test_integration.py -v

# Utility targets
check-all: format-check lint test validate

setup: install validate
	@echo "Setup complete! Run 'make help' to see available commands."

.DEFAULT_GOAL := help
