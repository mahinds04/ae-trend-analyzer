# Contributing

Guidelines for contributing to the AE Trend Analyzer project.

## 🤝 Welcome Contributors!

Thank you for your interest in contributing to the AE Trend Analyzer! This project benefits from community contributions, whether you're fixing bugs, adding features, improving documentation, or sharing feedback.

## 📋 Quick Links

- **Main Repository**: [mahinds04/ae-trend-analyzer](https://github.com/mahinds04/ae-trend-analyzer)
- **Issues**: [Report bugs or request features](https://github.com/mahinds04/ae-trend-analyzer/issues)
- **Discussions**: [Community Q&A](https://github.com/mahinds04/ae-trend-analyzer/discussions)
- **Documentation**: [Wiki pages](https://github.com/mahinds04/ae-trend-analyzer/wiki)

## 🚀 Getting Started

### **1. Fork and Clone**

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ae-trend-analyzer.git
cd ae-trend-analyzer

# Add upstream remote
git remote add upstream https://github.com/mahinds04/ae-trend-analyzer.git
```

### **2. Set Up Development Environment**

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black isort flake8 pre-commit pytest

# Set up pre-commit hooks
pre-commit install
```

### **3. Verify Setup**

```bash
# Run tests
pytest -q

# Run smoke checks
python src/analysis/smoke_checks.py

# Test dashboard in sample mode
streamlit run src/app/streamlit_mvp.py -- --sample
```

## 🔄 Development Workflow

### **Branching Strategy**

- `master` - Stable release branch
- `feature/feature-name` - New feature development
- `bugfix/issue-description` - Bug fixes
- `docs/improvement-description` - Documentation updates

### **Making Changes**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run unit tests
   pytest tests/
   
   # Test with sample data
   streamlit run src/app/streamlit_mvp.py -- --sample
   
   # Run smoke checks
   python src/analysis/smoke_checks.py
   ```

4. **Code Quality Checks**
   ```bash
   # Format code
   black .
   isort .
   
   # Lint code
   flake8
   
   # Run all pre-commit hooks
   pre-commit run --all-files
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   
   # Use conventional commit format:
   # feat: new features
   # fix: bug fixes
   # docs: documentation changes
   # style: formatting changes
   # refactor: code restructuring
   # test: adding tests
   # chore: maintenance tasks
   ```

## 📤 Submitting Changes

### **Pull Request Process**

1. **Update Your Branch**
   ```bash
   git checkout master
   git pull upstream master
   git checkout your-feature-branch
   git rebase master
   ```

2. **Push Your Branch**
   ```bash
   git push origin your-feature-branch
   ```

3. **Create Pull Request**
   - Use clear, descriptive title
   - Fill out the PR template
   - Link any related issues
   - Add screenshots for UI changes

### **PR Requirements Checklist**

- [ ] Code follows project coding standards
- [ ] Tests pass (`pytest tests/`)
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] Sample mode works (`streamlit run src/app/streamlit_mvp.py -- --sample`)
- [ ] Pre-commit hooks pass
- [ ] Descriptive commit messages

## 🎨 Coding Standards

### **Python Style**

We follow **PEP 8** with some modifications enforced by our tools:

#### **Black Formatting**
```bash
# Format all Python files
black .

# Check formatting
black --check .
```

#### **Import Sorting with isort**
```bash
# Sort imports
isort .

# Check import order
isort --check-only .
```

Configuration in `pyproject.toml`:
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
```

#### **Linting with flake8**
```bash
flake8
```

Configuration in `.flake8`:
```ini
[flake8]
max-line-length = 88
ignore = E203, W503
exclude = .git, __pycache__, .venv
```

### **Documentation Standards**

#### **Function Docstrings**
```python
def process_faers_quarter(quarter_path: Path) -> pd.DataFrame:
    """
    Process a single FAERS quarter directory.
    
    Args:
        quarter_path: Path to quarter directory (e.g., faers_ascii_2024q1)
        
    Returns:
        DataFrame with standardized columns and processed events
        
    Raises:
        FileNotFoundError: If required files are missing
        ValueError: If data format is invalid
        
    Example:
        >>> quarter_df = process_faers_quarter(Path("data/raw/faers_ascii_2024q1"))
        >>> print(quarter_df.shape)
        (15000, 8)
    """
```

#### **Class Documentation**
```python
class DataProcessor:
    """
    Processes FAERS data with configurable options.
    
    Attributes:
        chunk_size: Number of rows to process at once
        encoding_fallbacks: List of encodings to try
        
    Example:
        >>> processor = DataProcessor(chunk_size=5000)
        >>> data = processor.load_quarter("data/raw/faers_ascii_2024q1")
    """
```

### **Type Hints**

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Union
from pathlib import Path
import pandas as pd

def load_data_file(
    file_path: Path, 
    encoding: str = "utf-8"
) -> pd.DataFrame:
    """Load data file with specified encoding."""
    
def process_multiple_files(
    file_paths: List[Path]
) -> Dict[str, pd.DataFrame]:
    """Process multiple files and return results."""
```

## 🧪 Testing Guidelines

### **Test Structure**

```
tests/
├── test_etl.py           # ETL pipeline tests
├── test_analysis.py      # Analysis function tests
├── test_dashboard.py     # Dashboard component tests
├── conftest.py          # Test configuration and fixtures
└── data/                # Test data files
    ├── sample_demo.txt
    ├── sample_drug.txt
    └── sample_reac.txt
```

### **Writing Tests**

#### **Unit Tests**
```python
import pytest
import pandas as pd
from src.etl.faers_loader import standardize_columns

def test_standardize_columns():
    """Test column name standardization."""
    # Arrange
    df = pd.DataFrame({
        'PRIMARYID': [1, 2, 3],
        'DRUGNAME': ['ASPIRIN', 'TYLENOL', 'ADVIL']
    })
    
    # Act
    result = standardize_columns(df, 'DRUG')
    
    # Assert
    assert 'case_id' in result.columns
    assert 'drug' in result.columns
    assert len(result) == 3

def test_data_loading_with_sample():
    """Test data loading in sample mode."""
    # Test implementation
    pass
```

#### **Integration Tests**
```python
def test_full_etl_pipeline():
    """Test complete ETL pipeline with sample data."""
    # Test implementation
    pass

def test_dashboard_startup():
    """Test dashboard can start without errors."""
    # Test implementation
    pass
```

### **Test Data**

- **Use small test datasets** to keep tests fast
- **Create realistic but minimal data** that covers edge cases
- **Store test data in `tests/data/`** directory
- **Don't commit large files** (use Git LFS if necessary)

### **Running Tests**

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_etl.py

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## 🎯 Contribution Areas

### **Code Contributions**

#### **High Priority**
- **Bug fixes**: Address issues in GitHub Issues
- **Performance improvements**: Optimize data processing
- **Error handling**: Improve robustness
- **Test coverage**: Add missing tests

#### **Medium Priority**
- **New features**: Enhance dashboard functionality
- **Data source integrations**: Add new data loaders
- **Visualization improvements**: New chart types
- **API development**: REST API for integration

#### **Nice to Have**
- **UI/UX improvements**: Dashboard aesthetics
- **Configuration options**: More customization
- **Export features**: Additional output formats
- **Deployment tools**: Docker, cloud deployment

### **Documentation Contributions**

#### **High Priority**
- **Fix errors**: Correct inaccuracies or broken links
- **Add examples**: More usage examples and tutorials
- **Improve clarity**: Simplify complex explanations
- **Update screenshots**: Current dashboard images

#### **Medium Priority**
- **New guides**: Advanced usage tutorials
- **Video content**: Screen recordings or presentations
- **Translation**: Documentation in other languages
- **FAQ updates**: Common questions and answers

### **Community Contributions**

#### **Issue Management**
- **Triage issues**: Categorize and prioritize
- **Reproduce bugs**: Verify and provide additional details
- **Answer questions**: Help other users
- **Test releases**: Validate new versions

#### **Outreach**
- **Blog posts**: Write about the project
- **Conference presentations**: Present at relevant events
- **Social media**: Share and promote the project
- **Academic papers**: Cite and reference the tool

## 📝 Commit Message Guidelines

### **Format**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **Types**

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting changes (no functional changes)
- **refactor**: Code restructuring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### **Examples**

```bash
feat(dashboard): add anomaly detection with Prophet forecasting

- Implement Prophet-based time series analysis
- Add anomaly detection to insights panel
- Include confidence intervals in visualization
- Handle missing data gracefully

Closes #42

fix(etl): handle encoding errors in FAERS file loading

- Add fallback encodings for problematic files
- Improve error messages for debugging
- Test with various file encodings

docs(wiki): update installation guide with Windows instructions

- Add Windows-specific virtual environment commands
- Include troubleshooting for common Windows issues
- Update screenshots with Windows terminal examples
```

## 🔍 Code Review Process

### **As a Contributor**

1. **Self-review your changes** before submitting
2. **Respond promptly** to reviewer feedback
3. **Make requested changes** or explain why not
4. **Keep discussions constructive** and professional

### **Review Criteria**

Reviewers will check for:

- **Functionality**: Does the code work as intended?
- **Code quality**: Is it readable and maintainable?
- **Testing**: Are there appropriate tests?
- **Documentation**: Are changes documented?
- **Performance**: Any performance implications?
- **Security**: No security vulnerabilities?

## 🌟 Recognition

### **Contributors**

All contributors are recognized in:
- **GitHub contributors page**
- **CONTRIBUTORS.md** file (if created)
- **Release notes** for significant contributions
- **Social media mentions** for major features

### **Types of Recognition**

- **Code contributions**: Bug fixes, features, improvements
- **Documentation**: Wiki pages, guides, examples
- **Testing**: Bug reports, testing new features
- **Community support**: Helping other users
- **Outreach**: Presentations, blog posts, papers

## 📞 Getting Help

### **Before Contributing**

- **Read existing documentation** thoroughly
- **Search issues and discussions** for similar topics
- **Test the application** to understand its functionality
- **Review existing code** to understand patterns

### **When You Need Help**

- **GitHub Discussions**: Ask questions about development
- **GitHub Issues**: Report bugs or unclear documentation
- **Email**: mahin.das.ml@gmail.com for direct support
- **Code reviews**: Get feedback on your approach

### **Community Guidelines**

Please follow our [Code of Conduct](https://github.com/mahinds04/ae-trend-analyzer/blob/master/CODE_OF_CONDUCT.md):

- **Be respectful** and inclusive
- **Provide constructive feedback**
- **Help others learn and grow**
- **Focus on the best solution** for the project

---

**Ready to contribute?** Start by exploring the codebase and picking an issue that interests you!