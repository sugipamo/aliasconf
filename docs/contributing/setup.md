# Contributing to AliasConf

Thank you for your interest in contributing to AliasConf! This guide will help you get started with development.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- pip or Poetry
- Make (optional, for using Makefile commands)

### Getting Started

1. **Fork and Clone the Repository**

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/aliasconf.git
cd aliasconf
```

2. **Create a Virtual Environment**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using Poetry
poetry shell
```

3. **Install Dependencies**

```bash
# Install in development mode
pip install -e ".[dev]"

# Or using Poetry
poetry install
```

4. **Run Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aliasconf --cov-report=html

# Run specific test file
pytest tests/test_manager.py
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write code following the project style guide
- Add tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code
black .
isort .

# Check code style
ruff check .

# Type checking
mypy src/

# Run all tests
pytest
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Follow conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `perf:` Performance improvements

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guide

### Python Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting
- **mypy**: Type checking

Configuration is in `pyproject.toml`.

### Code Examples

```python
# Good: Clear, typed, documented
from typing import Optional, Dict, Any

def get_config_value(
    path: str,
    default: Optional[Any] = None,
    type_hint: Optional[type] = None
) -> Any:
    """Get configuration value by path.
    
    Args:
        path: Dot-separated path to configuration value
        default: Default value if path not found
        type_hint: Expected type for conversion
        
    Returns:
        Configuration value or default
        
    Raises:
        ConfigNotFoundError: If path not found and no default
        ConfigValidationError: If type conversion fails
    """
    # Implementation
    pass
```

### Documentation Style

- Use Google-style docstrings
- Include type hints
- Provide examples in docstrings
- Keep line length under 88 characters

## Testing Guidelines

### Test Structure

```python
import pytest
from aliasconf import ConfigManager, ConfigNotFoundError

class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_basic_get(self):
        """Test basic get operation."""
        config = ConfigManager.from_dict({"key": "value"})
        assert config.get("key") == "value"
    
    def test_nested_get(self):
        """Test nested path access."""
        config = ConfigManager.from_dict({
            "parent": {"child": "value"}
        })
        assert config.get("parent.child") == "value"
    
    def test_missing_key_raises(self):
        """Test missing key raises appropriate error."""
        config = ConfigManager.from_dict({})
        with pytest.raises(ConfigNotFoundError):
            config.get("missing.key")
```

### Test Coverage

- Aim for >90% test coverage
- Test edge cases and error conditions
- Include integration tests
- Add performance tests for critical paths

## Documentation

### Adding Documentation

1. **API Documentation**: Update docstrings in code
2. **User Guides**: Add/update files in `docs/guide/`
3. **Examples**: Add to `docs/examples/`
4. **README**: Update if adding major features

### Building Documentation

```bash
# Build documentation locally
mkdocs serve

# View at http://localhost:8000
```

## Project Structure

```
aliasconf/
├── src/
│   └── aliasconf/          # Main package
│       ├── __init__.py
│       ├── manager.py      # ConfigManager class
│       ├── node.py         # ConfigNode class
│       ├── resolver.py     # Alias resolver
│       └── ...
├── tests/                  # Test files
│   ├── test_manager.py
│   ├── test_node.py
│   └── ...
├── docs/                   # Documentation
│   ├── index.md
│   ├── guide/
│   └── ...
├── pyproject.toml         # Project configuration
└── README.md
```

## Common Development Tasks

### Adding a New Feature

1. Create tests first (TDD approach)
2. Implement the feature
3. Ensure all tests pass
4. Add documentation
5. Update CHANGELOG.md

### Fixing a Bug

1. Write a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Add regression test if needed

### Improving Performance

1. Profile the code first
2. Write benchmarks
3. Implement optimization
4. Ensure benchmarks show improvement
5. Document the optimization

## Getting Help

- Check existing issues on GitHub
- Join our discussions
- Read the documentation
- Ask questions in pull requests

## Code of Conduct

Please follow our code of conduct in all interactions:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive criticism
- Assume good intentions

## Release Process

Maintainers handle releases:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. GitHub Actions handles PyPI deployment

## Thank You!

Your contributions make AliasConf better for everyone. We appreciate your time and effort!