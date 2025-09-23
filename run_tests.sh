#!/bin/bash

# Shell script to create venv, install dependencies, run tests, and cleanup
echo "Setting up test environment..."

# Create virtual environment
python3 -m venv test_venv
echo "✓ Virtual environment created"

# Activate virtual environment
source test_venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install testing dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt

echo "✓ Dependencies installed"

# Run the tests
echo ""
echo "Running unit tests..."
echo "===================="
python -m pytest tests/unit-tests/ -v

# Store test exit code
test_exit_code=$?

# Deactivate virtual environment
deactivate
echo ""
echo "✓ Virtual environment deactivated"

# Remove virtual environment
rm -rf test_venv
echo "✓ Test environment cleaned up"

echo ""
if [ $test_exit_code -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed!"
fi

exit $test_exit_code