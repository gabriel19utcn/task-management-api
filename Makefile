.PHONY: test unit-test si-test lint format clean

unit-test:
	./run_tests.sh

si-test:
	./run_si_tests.sh

lint:
	flake8 app/ tests/ --max-line-length=88

format:
	@echo "Formatting code..."
	black app/ tests/ --line-length 88
	isort app/ tests/ --profile black
	@echo "✓ Code formatted"

format-check:
	@echo "Checking code formatting..."
	black app/ tests/ --line-length 88 --check
	isort app/ tests/ --profile black --check-only
	@echo "✓ Format check completed"

pre-commit: format-check lint test

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f test.db
	rm -rf .pytest_cache test_venv si_test_venv
