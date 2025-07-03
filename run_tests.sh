#!/bin/bash
# Script to run pytest with proper environment setup

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running AliasConf Test Suite${NC}"
echo "================================"

# Set PYTHONPATH to include the src directory
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)/src"

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Please install it with: pip install pytest pytest-cov"
    exit 1
fi

# Parse command line arguments
PYTEST_ARGS=""
COVERAGE_REPORT="term-missing"
FAIL_UNDER="80"
NO_COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)
            NO_COVERAGE=true
            shift
            ;;
        --html)
            COVERAGE_REPORT="html"
            shift
            ;;
        --fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

# Build pytest command
if [ "$NO_COVERAGE" = true ]; then
    # Override the addopts from pyproject.toml to disable coverage
    PYTEST_CMD="python3 -m pytest -v -o addopts='' $PYTEST_ARGS"
else
    PYTEST_CMD="python3 -m pytest -v --cov=src/aliasconf --cov-report=$COVERAGE_REPORT --cov-fail-under=$FAIL_UNDER $PYTEST_ARGS"
fi

echo -e "Running: ${GREEN}$PYTEST_CMD${NC}"
echo "================================"

# Run pytest
$PYTEST_CMD

# Capture exit code
EXIT_CODE=$?

# Display result
echo "================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed successfully!${NC}"
else
    echo -e "${RED}✗ Tests failed or coverage requirement not met${NC}"
fi

exit $EXIT_CODE