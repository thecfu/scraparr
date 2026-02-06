# Default recipe - show available commands
default:
    @just --list

# Run all checks (lint + test)
check: lint test

# Run pylint on source code
lint:
    uv run pylint --recursive=y src/scraparr

# Run tests with coverage
test:
    uv run pytest tests/ -v --cov=scraparr --cov-report=term-missing

# Run tests without coverage (faster)
test-quick:
    uv run pytest tests/ -v

# Install development dependencies
dev-install:
    uv sync --dev
