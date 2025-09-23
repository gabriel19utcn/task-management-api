#!/bin/bash

# System Integration Test script
echo "Setting up SI test environment..."

# Create virtual environment for SI tests
python3 -m venv si_test_venv
echo "✓ SI test virtual environment created"

# Activate virtual environment
source si_test_venv/bin/activate
echo "✓ SI test virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install SI test dependencies
echo "Installing SI test dependencies..."
pip install -r requirements-test.txt

echo "✓ SI test dependencies installed"

# Check if API is running
echo ""
echo "Checking if API is running..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✓ API is running"
else
    echo "❌ API is not running. Please start the API with: docker-compose up -d"
    deactivate
    rm -rf si_test_venv
    exit 1
fi

# Run behave tests
echo ""
echo "Running System Integration Tests..."
echo "=================================="
behave tests/si-tests/feature/ -v

# Store test exit code
test_exit_code=$?

# Deactivate virtual environment
deactivate
echo ""
echo "✓ SI test virtual environment deactivated"

# Remove virtual environment
rm -rf si_test_venv
echo "✓ SI test environment cleaned up"

echo ""
if [ $test_exit_code -eq 0 ]; then
    echo "All SI tests passed!"
else
    echo "Some SI tests failed!"
fi

exit $test_exit_code