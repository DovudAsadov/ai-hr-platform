# Contributing to AI HR Platform

First off, thank you for considering contributing to AI HR Platform! 🎉

It's people like you that make AI HR Platform such a great tool for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@aihrplatform.com](mailto:contact@aihrplatform.com).

### Our Pledge

We pledge to make participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Getting Started

### Issues

Issues are a great way to start contributing:

- **Bug Reports**: Found a bug? Please check if it's already reported in our [Issues](https://github.com/yourusername/ai-hr-platform/issues)
- **Feature Requests**: Have an idea? We'd love to hear it!
- **Questions**: Need help? Ask in our [Discussions](https://github.com/yourusername/ai-hr-platform/discussions)

### Good First Issues

Look for issues labeled `good first issue` or `help wanted`. These are perfect for newcomers!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Setup Steps

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/ai-hr-platform.git
   cd ai-hr-platform
   ```

2. **Set up Development Environment**
   ```bash
   # Install in development mode
   pip install -e ".[dev]"
   
   # Or use the setup script
   python scripts/setup_dev.py
   ```

3. **Configure Environment**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- **Bug Fixes**: Fix issues in the codebase
- **New Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **UI/UX**: Improve user interfaces

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

2. **Make Your Changes**
   - Write clear, concise code
   - Follow our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run the full test suite
   pytest
   
   # Run specific tests
   pytest tests/test_your_feature.py
   
   # Check code quality
   make check
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the pull request template
   - Link any related issues

## Pull Request Process

### Before Submitting

- [ ] Tests pass (`pytest`)
- [ ] Code quality checks pass (`make check`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### Pull Request Guidelines

1. **Clear Title**: Use a descriptive title that explains what the PR does
2. **Description**: Provide a detailed description of your changes
3. **Link Issues**: Reference any related issues using `Fixes #123`
4. **Screenshots**: Include screenshots for UI changes
5. **Testing**: Describe how you tested your changes

### Review Process

1. **Automated Checks**: CI/CD pipeline will run tests and quality checks
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any feedback or requested changes
4. **Approval**: Once approved, your PR will be merged

## Style Guidelines

### Python Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning

### Code Standards

- **PEP 8**: Follow Python's style guide
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Write docstrings for all public functions
- **Comments**: Use comments to explain complex logic
- **Naming**: Use descriptive variable and function names

### Example Code

```python
from typing import Dict, Any, Optional

def analyze_resume(
    resume_text: str, 
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze a resume and return structured feedback.
    
    Args:
        resume_text: The text content of the resume
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If resume_text is empty or invalid
    """
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")
    
    # Analysis logic here
    return {"status": "success", "analysis": "..."}
```

## Testing

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
import pytest
from ai_hr_platform.core import ResumeAnalyzer

class TestResumeAnalyzer:
    def test_analyze_valid_resume(self):
        """Test analyzing a valid resume."""
        analyzer = ResumeAnalyzer()
        result = analyzer.process("Sample resume text")
        assert result["status"] == "success"
    
    def test_analyze_empty_resume(self):
        """Test analyzing an empty resume."""
        analyzer = ResumeAnalyzer()
        with pytest.raises(ValueError):
            analyzer.process("")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_hr_platform

# Run specific test file
pytest tests/test_core.py

# Run tests matching a pattern
pytest -k "test_analyze"
```

## Documentation

### Types of Documentation

- **Code Documentation**: Docstrings and comments
- **User Documentation**: README, usage guides
- **API Documentation**: Function and class references
- **Contributing Documentation**: This file!

### Writing Documentation

- Use clear, concise language
- Include code examples
- Update documentation when changing code
- Use proper markdown formatting

## Community

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Email**: [contact@aihrplatform.com](mailto:contact@aihrplatform.com)

### Communication Guidelines

- Be respectful and inclusive
- Use clear, descriptive titles
- Provide context and examples
- Search before posting

## Recognition

Contributors are recognized in several ways:

- **Contributors List**: All contributors are listed in our README
- **Release Notes**: Significant contributions are mentioned in releases
- **Special Thanks**: Outstanding contributions get special recognition

## Questions?

Don't hesitate to ask questions! We're here to help:

- Open an issue with the `question` label
- Start a discussion in GitHub Discussions
- Email us at [contact@aihrplatform.com](mailto:contact@aihrplatform.com)

Thank you for contributing to AI HR Platform! 🚀