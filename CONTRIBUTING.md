# Contributing to Project Manager AI Assistant

Thank you for your interest in contributing to Project Manager AI Assistant! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include details about your configuration and environment

### Suggesting Enhancements

If you have a suggestion for a new feature or improvement, please:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead

### Pull Requests

- Fork the repo and create your branch from `main`
- If you've added code that should be tested, add tests
- If you've changed APIs, update the documentation
- Ensure the test suite passes
- Make sure your code lints
- Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- OpenAI API Key (for testing)

### Local Development

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/project-manager-assistant.git
   cd project-manager-assistant
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

6. **Run the application**
   ```bash
   # Backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Frontend (in another terminal)
   streamlit run streamlit_app/app.py --server.port 8501
   ```

### Database Setup

If you're working on features that require database changes:

```bash
# Run migrations
alembic upgrade head

# Create test database
pytest --create-db
```

## Coding Standards

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- Maximum line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use docstrings for all public functions and classes
- Follow Google-style docstrings

### Code Formatting

We use [Black](https://black.readthedocs.io/) for code formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Import Organization

We use [isort](https://pycqa.github.io/isort/) for import organization:

```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

### Linting

We use [flake8](https://flake8.pycqa.org/) for linting:

```bash
# Run linter
flake8 app/ streamlit_app/ tests/
```

### Type Checking

We use [mypy](http://mypy-lang.org/) for static type checking:

```bash
# Run type checker
mypy app/ streamlit_app/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov=streamlit_app

# Run specific test file
pytest tests/test_api.py

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Write tests for all new features
- Aim for at least 80% code coverage
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

Example test structure:

```python
import pytest
from app.services.project_service import ProjectService

class TestProjectService:
    @pytest.fixture
    def project_service(self):
        return ProjectService()
    
    def test_generate_project_plan(self, project_service):
        # Arrange
        project_description = "Test project"
        team_members = []
        
        # Act
        result = project_service.generate_plan(project_description, team_members)
        
        # Assert
        assert result is not None
        assert "tasks" in result
```

### Integration Tests

For integration tests that require external services:

```python
@pytest.mark.integration
def test_openai_integration():
    # Tests that require OpenAI API
    pass
```

Run integration tests separately:

```bash
pytest -m integration
```

## Pull Request Process

### Before Submitting

1. **Ensure your code follows the style guidelines**
   ```bash
   black .
   isort .
   flake8 app/ streamlit_app/ tests/
   mypy app/ streamlit_app/
   ```

2. **Run the test suite**
   ```bash
   pytest
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add docstrings for new functions
   - Update API documentation if APIs changed

4. **Check for security issues**
   ```bash
   bandit -r app/ streamlit_app/
   ```

### Pull Request Guidelines

- Use a clear and descriptive title
- Include a summary of the changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all CI checks pass

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
```

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

### Release Checklist

1. **Update version numbers**
   - Update `__version__` in main modules
   - Update `pyproject.toml` if applicable

2. **Update changelog**
   - Add entries to `CHANGELOG.md`
   - Include all significant changes

3. **Create release branch**
   ```bash
   git checkout -b release/v1.2.0
   ```

4. **Run full test suite**
   ```bash
   pytest
   pytest --cov=app --cov=streamlit_app
   ```

5. **Create pull request**
   - Merge to main
   - Create GitHub release
   - Tag the release

## Plugin Development

### Creating a New Plugin

1. **Create plugin directory**
   ```
   app/plugins/your_plugin/
   ├── __init__.py
   ├── plugin.py
   ├── config.py
   └── tests/
   ```

2. **Implement plugin interface**
   ```python
   from app.plugins.base import BasePlugin
   
   class YourPlugin(BasePlugin):
       name = "your_plugin"
       version = "1.0.0"
       
       def initialize(self, config):
           # Plugin initialization
           pass
       
       def execute(self, data):
           # Plugin execution logic
           pass
   ```

3. **Add tests**
   ```python
   def test_your_plugin():
       plugin = YourPlugin()
       result = plugin.execute(test_data)
       assert result is not None
   ```

4. **Update documentation**
   - Add plugin documentation
   - Include usage examples
   - Document configuration options

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the docs folder for detailed guides
- **Email**: For security issues or private matters

## Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor hall of fame

Thank you for contributing to Project Manager AI Assistant! 