# Contributing to AE Trend Analyzer

Thank you for your interest in contributing to the AE Trend Analyzer! This document provides guidelines for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git
- Basic knowledge of pandas, Streamlit, and data analysis

### Setup Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/ae-trend-analyzer.git
   cd ae-trend-analyzer
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Activate (Mac/Linux)
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Test your setup**
   ```bash
   # Run in demo mode to verify setup
   python run_dashboard.py --sample
   ```

4. **Set up pre-commit hooks (optional but recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 🔄 Development Workflow

### Branching Strategy

- `master` - Main branch with stable releases
- `feature/feature-name` - Feature development
- `bugfix/issue-description` - Bug fixes
- `docs/improvement-description` - Documentation updates

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the [coding standards](#coding-standards)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run unit tests
   python -m pytest tests/
   
   # Test with sample data
   python run_dashboard.py --sample
   
   # Test ETL pipeline (if applicable)
   python run_etl.py --sample
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## 📤 Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git checkout master
   git pull upstream master
   git checkout your-feature-branch
   git rebase master
   ```

2. **Push your branch**
   ```bash
   git push origin your-feature-branch
   ```

3. **Create a Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link any related issues
   - Add screenshots for UI changes

### PR Requirements

- [ ] Code follows project coding standards
- [ ] Tests pass (`pytest tests/`)
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] Sample mode works (`python run_dashboard.py --sample`)

## 🎨 Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Organization

```python
# File structure for new modules
"""
Brief module description.

Longer description if needed.
"""

import standard_library
import third_party_packages

import local_modules

# Constants
CONSTANT_NAME = "value"

# Functions and classes
def function_name(param: type) -> return_type:
    """Brief function description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass
```

### Documentation

- Use Google-style docstrings
- Document all public functions and classes
- Include examples for complex functionality
- Update README.md for new features

## 🧪 Testing

### Test Structure

```
tests/
├── test_etl/           # ETL pipeline tests
├── test_analysis/      # Analysis module tests
├── test_app/          # Dashboard tests
└── conftest.py        # Test configuration
```

### Writing Tests

```python
import pytest
import pandas as pd

def test_function_name():
    """Test function with descriptive name."""
    # Arrange
    input_data = pd.DataFrame(...)
    expected_result = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_result
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_analysis/test_anomaly.py

# Run with coverage
python -m pytest --cov=src tests/

# Run tests in verbose mode
python -m pytest -v
```

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**
   - Inline comments for complex logic
   - Docstrings for all public functions
   - Type hints for better IDE support

2. **User Documentation**
   - README.md updates for new features
   - data/README.md for data structure changes
   - Command-line help text

3. **Developer Documentation**
   - CONTRIBUTING.md (this file)
   - Architecture decisions in comments
   - API documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation in sync with code

## 🐛 Issue Reporting

### Bug Reports

Please include:

- **Environment**: OS, Python version, package versions
- **Steps to reproduce**: Detailed steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error traceback if applicable
- **Sample data**: Minimal example that reproduces the issue

### Feature Requests

Please include:

- **Problem description**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other solutions you've considered
- **Use cases**: When would this be useful?

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority:high` - High priority issues

## 🔧 Development Tips

### Working with Large Data

- Always test with sample data first (`--sample` flag)
- Use chunked processing for large files
- Profile memory usage for optimization
- Consider data type optimization (int32 vs int64)

### Dashboard Development

- Test UI changes with different screen sizes
- Verify functionality with empty/minimal data
- Check performance with larger datasets
- Test error handling scenarios

### Anomaly Detection

- Validate algorithms with synthetic data
- Test edge cases (empty data, single points)
- Ensure graceful fallbacks when methods fail
- Document algorithm parameters and assumptions

## 🤝 Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Code Review**: Submit PRs for feedback

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- CITATION.cff file for academic contributions

## 📝 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to AE Trend Analyzer! 🎉
