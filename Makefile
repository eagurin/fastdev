.PHONY: help install install-dev test lint format clean build serve

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install FastDEV
	pip install -e .

install-dev:  ## Install FastDEV with development dependencies
	pip install -e ".[dev,analysis,monitoring]"

test:  ## Run tests
	pytest tests/ -v --cov=fastdev --cov-report=term-missing

lint:  ## Run all linters
	black --check src/ tests/
	isort --check-only src/ tests/
	ruff check src/ tests/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

serve:  ## Start FastDEV server
	fastdev serve

dev-serve:  ## Start FastDEV server with verbose output
	fastdev serve --verbose
