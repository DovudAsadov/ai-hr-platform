.PHONY: help install test lint format clean build docs

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build package"
	@echo "  docs        Generate documentation"
	@echo "  dev         Install in development mode"
	@echo "  pre-commit  Install pre-commit hooks"

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

pre-commit:
	pre-commit install

test:
	pytest tests/ -v --cov=ai_hr_platform

lint:
	flake8 ai_hr_platform/
	mypy ai_hr_platform/ --ignore-missing-imports
	bandit -r ai_hr_platform/

format:
	black ai_hr_platform/
	isort ai_hr_platform/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	@echo "Documentation is in docs/ directory"
	@echo "Open docs/README.md to get started"

check:
	@echo "Running all checks..."
	@$(MAKE) lint
	@$(MAKE) test
	@echo "All checks passed!"