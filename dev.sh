#!/bin/bash
# Development helper script for AliasConf

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)/src"

function show_help {
    echo -e "${BLUE}AliasConf Development Helper${NC}"
    echo "============================="
    echo ""
    echo "Usage: ./dev.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  test        Run tests (default: with coverage)"
    echo "  test-quick  Run tests without coverage"
    echo "  test-file   Run specific test file"
    echo "  format      Format code with black and isort"
    echo "  lint        Run linting with ruff"
    echo "  type        Run type checking with mypy"
    echo "  check       Run all checks (format, lint, type, test)"
    echo "  coverage    Generate HTML coverage report"
    echo "  clean       Clean temporary files"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh test"
    echo "  ./dev.sh test-file tests/test_basic.py"
    echo "  ./dev.sh check"
}

function run_tests {
    echo -e "${YELLOW}Running tests with coverage...${NC}"
    python3 -m pytest -v
}

function run_tests_quick {
    echo -e "${YELLOW}Running tests without coverage...${NC}"
    python3 -m pytest -v -o addopts=''
}

function run_test_file {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify a test file${NC}"
        echo "Usage: ./dev.sh test-file <path/to/test_file.py>"
        exit 1
    fi
    echo -e "${YELLOW}Running tests in $1...${NC}"
    python3 -m pytest -v -o addopts='' "$1"
}

function format_code {
    echo -e "${YELLOW}Formatting code...${NC}"
    
    # Check if black is installed
    if ! python3 -m black --version > /dev/null 2>&1; then
        echo -e "${RED}black is not installed. Install with: pip install black${NC}"
        exit 1
    fi
    
    # Check if isort is installed
    if ! python3 -m isort --version > /dev/null 2>&1; then
        echo -e "${RED}isort is not installed. Install with: pip install isort${NC}"
        exit 1
    fi
    
    echo "Running black..."
    python3 -m black src/ tests/
    
    echo "Running isort..."
    python3 -m isort src/ tests/
    
    echo -e "${GREEN}✓ Code formatting complete${NC}"
}

function run_lint {
    echo -e "${YELLOW}Running linter...${NC}"
    
    # Check if ruff is installed
    if ! python3 -m ruff --version > /dev/null 2>&1; then
        echo -e "${RED}ruff is not installed. Install with: pip install ruff${NC}"
        exit 1
    fi
    
    python3 -m ruff check src/ tests/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ No linting issues found${NC}"
    else
        echo -e "${RED}✗ Linting issues found${NC}"
        exit 1
    fi
}

function run_type_check {
    echo -e "${YELLOW}Running type checker...${NC}"
    
    # Check if mypy is installed
    if ! python3 -m mypy --version > /dev/null 2>&1; then
        echo -e "${RED}mypy is not installed. Install with: pip install mypy${NC}"
        exit 1
    fi
    
    python3 -m mypy src/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ No type errors found${NC}"
    else
        echo -e "${RED}✗ Type errors found${NC}"
        exit 1
    fi
}

function run_all_checks {
    echo -e "${BLUE}Running all checks...${NC}"
    echo "====================="
    
    format_code
    echo ""
    
    run_lint
    echo ""
    
    run_type_check
    echo ""
    
    run_tests
    
    echo ""
    echo -e "${BLUE}All checks complete!${NC}"
}

function generate_coverage {
    echo -e "${YELLOW}Generating HTML coverage report...${NC}"
    python3 -m pytest --cov=src/aliasconf --cov-report=html --cov-report=term
    echo -e "${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
}

function clean_files {
    echo -e "${YELLOW}Cleaning temporary files...${NC}"
    
    # Remove Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Remove pytest cache
    rm -rf .pytest_cache 2>/dev/null || true
    
    # Remove mypy cache
    rm -rf .mypy_cache 2>/dev/null || true
    
    # Remove coverage files
    rm -f .coverage 2>/dev/null || true
    rm -rf htmlcov 2>/dev/null || true
    
    # Remove build artifacts
    rm -rf build dist *.egg-info 2>/dev/null || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main script logic
case "$1" in
    test)
        run_tests
        ;;
    test-quick)
        run_tests_quick
        ;;
    test-file)
        run_test_file "$2"
        ;;
    format)
        format_code
        ;;
    lint)
        run_lint
        ;;
    type)
        run_type_check
        ;;
    check)
        run_all_checks
        ;;
    coverage)
        generate_coverage
        ;;
    clean)
        clean_files
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac