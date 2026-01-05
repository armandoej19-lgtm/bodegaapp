.PHONY: help install dev-install test lint format clean run backup build dist

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help:
	@echo "Bodega App - Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  $(GREEN)install$(NC)      - Install production dependencies"
	@echo "  $(GREEN)dev-install$(NC)  - Install development dependencies"
	@echo "  $(GREEN)test$(NC)         - Run tests"
	@echo "  $(GREEN)lint$(NC)         - Run code linting"
	@echo "  $(GREEN)format$(NC)       - Format code with black"
	@echo "  $(GREEN)clean$(NC)        - Clean temporary files"
	@echo "  $(GREEN)run$(NC)          - Run the application"
	@echo "  $(GREEN)backup$(NC)       - Create database backup"
	@echo "  $(GREEN)build$(NC)        - Build distribution packages"
	@echo "  $(GREEN)dist$(NC)         - Create distribution"

install:
	@echo "$(YELLOW)Installing production dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev-install: install
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	pip install pytest pytest-cov black flake8 mypy
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

test:
	@echo "$(YELLOW)Running tests...$(NC)"
	python -m pytest tests/ -v --cov=src --cov-report=term-missing
	@echo "$(GREEN)✓ Tests completed$(NC)"

lint:
	@echo "$(YELLOW)Running code linting...$(NC)"
	flake8 src/ tests/ scripts/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports
	@echo "$(GREEN)✓ Linting completed$(NC)"

format:
	@echo "$(YELLOW)Formatting code...$(NC)"
	black src/ tests/ scripts/
	@echo "$(GREEN)✓ Code formatted$(NC)"

clean:
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

run:
	@echo "$(YELLOW)Starting Bodega App...$(NC)"
	python run.py

backup:
	@echo "$(YELLOW)Creating database backup...$(NC)"
	python scripts/backup_database.py

build:
	@echo "$(YELLOW)Building distribution...$(NC)"
	python setup.py sdist bdist_wheel
	@echo "$(GREEN)✓ Build completed$(NC)"

dist: clean build
	@echo "$(GREEN)✓ Distribution packages created in dist/ directory$(NC)"

# Alias for common tasks
all: clean install test lint