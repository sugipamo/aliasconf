# Testing Guide for AliasConf

This guide explains how to set up and run tests for the AliasConf project.

## Environment Setup Issues and Solutions

### Problem: System Python Environment
The system uses an externally-managed Python environment that prevents direct package installation. This is a security feature in modern Linux distributions.

### Solution 1: Using PYTHONPATH (Quick Method)
The easiest way to run tests without setting up a virtual environment:

```bash
# Set PYTHONPATH to include the src directory
export PYTHONPATH=/home/cphelper/project-cph/aliasconf/src

# Run tests
python3 -m pytest -v
```

### Solution 2: Using the Test Runner Script
We've created a convenient script that handles the environment setup:

```bash
# Run all tests with coverage
./run_tests.sh

# Run specific test file
./run_tests.sh tests/test_basic.py

# Run without coverage
./run_tests.sh --no-cov

# Generate HTML coverage report
./run_tests.sh --html

# Set custom coverage threshold
./run_tests.sh --fail-under 60
```

### Solution 3: Virtual Environment (Recommended for Development)
If you have python3-venv installed:

```bash
# Install venv support (if needed)
sudo apt install python3-venv

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Test Structure

The test suite is organized into four main files:

1. **test_basic.py** - Basic functionality tests
   - Configuration creation and loading
   - Alias resolution
   - Type conversion
   - Error handling

2. **test_edge_cases.py** - Edge case and boundary tests
   - Circular references
   - Unicode handling
   - Performance limits
   - Error conditions

3. **test_integration.py** - Integration and real-world scenarios
   - Multi-file configurations
   - Environment variable integration
   - Migration scenarios
   - Concurrent access

4. **test_performance.py** - Performance benchmarks
   - Load time tests
   - Memory efficiency
   - Cache performance
   - Scalability limits

## Running Specific Tests

```bash
# Run a specific test file
./run_tests.sh tests/test_basic.py

# Run a specific test class
./run_tests.sh tests/test_basic.py::TestBasicFunctionality

# Run a specific test method
./run_tests.sh tests/test_basic.py::TestBasicFunctionality::test_alias_resolution

# Run tests matching a pattern
./run_tests.sh -k "alias"
```

## Code Coverage

The project is configured to require 80% code coverage. Current coverage is around 60%.

To view detailed coverage:

```bash
# Generate HTML coverage report
./run_tests.sh --html

# Open the report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
```

## Common Issues and Solutions

### Issue: ModuleNotFoundError for 'aliasconf'
**Solution**: Make sure PYTHONPATH is set correctly or use the run_tests.sh script.

### Issue: pytest-asyncio warning
**Solution**: This is a deprecation warning and doesn't affect test execution. It can be safely ignored.

### Issue: Coverage failing
**Solution**: The project requires 80% coverage. You can temporarily lower this requirement:
```bash
./run_tests.sh --fail-under 60
```

## CI/CD Integration

The project uses GitHub Actions for continuous integration. The workflow:
- Runs on multiple Python versions (3.8-3.12)
- Tests on Ubuntu, Windows, and macOS
- Enforces code quality with ruff, black, isort, and mypy
- Requires 80% test coverage

## Development Workflow

1. Make your changes
2. Run the test suite: `./run_tests.sh`
3. Check code formatting: `black src/ tests/`
4. Run type checking: `mypy src/`
5. Run linting: `ruff check src/ tests/`

## Adding New Tests

When adding new features, ensure you:
1. Add corresponding tests in the appropriate test file
2. Maintain the 80% coverage requirement
3. Follow the existing test patterns and naming conventions
4. Use the fixtures defined in conftest.py when appropriate