.PHONY: help install install-dev test test-unit test-integration test-cov lint format clean docker-build docker-run

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run all tests
	pytest

test-unit:  ## Run unit tests only
	pytest -m "not integration"

test-integration:  ## Run integration tests only
	pytest -m integration

test-cov:  ## Run tests with coverage report
	pytest --cov=coming_attractions --cov-report=term-missing --cov-report=html

lint:  ## Run linting checks (requires ruff)
	@echo "Note: Install ruff for linting: pip install ruff"
	@command -v ruff >/dev/null 2>&1 && ruff check coming_attractions/ tests/ || echo "Ruff not installed, skipping"

format:  ## Format code (requires black)
	@echo "Note: Install black for formatting: pip install black"
	@command -v black >/dev/null 2>&1 && black coming_attractions/ tests/ || echo "Black not installed, skipping"

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

docker-build:  ## Build Docker image
	docker build -f docker/Dockerfile -t coming-attractions:latest ..

docker-run:  ## Run Docker container (interactive)
	docker run -it --rm \
		-v $${PWD}/data:/data \
		-e TMDB_API_KEY=$${TMDB_API_KEY} \
		coming-attractions:latest --help
