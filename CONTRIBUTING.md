# 🤝 Contributing to AI Project Management Assistant

Thank you for your interest in contributing to the AI Project Management Assistant! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Code Standards](#-code-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Areas for Contribution](#-areas-for-contribution)
- [Architecture Guidelines](#-architecture-guidelines)

## 📜 Code of Conduct

This project adheres to a code of conduct adapted from the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

### Our Pledge

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Inclusive**: Welcome people of all backgrounds and experience levels
- **Be Collaborative**: Work together to build something amazing
- **Be Patient**: Help newcomers learn and grow

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Git** for version control
- **[uv](https://github.com/astral-sh/uv)** for package management
- **Redis** for local development
- **OpenAI API Key** for testing AI features

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/project-manager-assistant.git
   cd project-manager-assistant
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/project-manager-assistant.git
   ```

### Development Setup

1. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements-dev.txt
   ```

3. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start development services**:
   ```bash
   ./run.sh
   ```

## 🔄 Development Workflow

### Branch Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/feature-name`**: New features
- **`bugfix/issue-description`**: Bug fixes
- **`hotfix/critical-fix`**: Critical production fixes

### Workflow Steps

1. **Create feature branch**:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**:
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   pytest tests/
   black . && isort .
   mypy app/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/amazing-feature
   # Create PR on GitHub
   ```

## 📏 Code Standards

### Python Style Guide

- **PEP 8**: Follow Python's official style guide
- **Black**: Use Black formatter for consistent code style
- **isort**: Sort imports consistently
- **Line Length**: Maximum 88 characters (Black default)

### Type Hints

- **Required**: All functions must have type hints
- **Return Types**: Always specify return types
- **Complex Types**: Use `typing` module for complex types

```python
from typing import List, Dict, Optional, Union

def process_tasks(tasks: List[Task]) -> Dict[str, Any]:
    """Process a list of tasks and return results."""
    result: Dict[str, Any] = {}
    return result
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain complex logic and business rules
- **README Updates**: Update documentation for new features

```python
def extract_tasks(description: str, team: Team) -> TaskList:
    """Extract actionable tasks from project description.
    
    Args:
        description: Natural language project description
        team: Team information for context
        
    Returns:
        TaskList containing extracted tasks with metadata
        
    Raises:
        ValidationError: If description is invalid
        APIError: If LLM request fails
    """
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for API endpoints
├── e2e/           # End-to-end tests for full workflows
└── fixtures/      # Test data and fixtures
```

### Writing Tests

- **Test Coverage**: Aim for >90% code coverage
- **Test Names**: Descriptive test function names
- **Fixtures**: Use pytest fixtures for reusable test data
- **Mocking**: Mock external dependencies (OpenAI, Redis)

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_project_description():
    return "Build a simple todo application with user authentication"

@pytest.fixture  
def mock_openai_response():
    return {"choices": [{"message": {"content": "mocked response"}}]}

def test_task_extraction_with_valid_input(sample_project_description, mock_openai_response):
    """Test that task extraction works with valid project description."""
    with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
        result = extract_tasks(sample_project_description)
        assert len(result.tasks) > 0
        assert all(task.task_name for task in result.tasks)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_task_extraction.py

# Run tests with verbose output
pytest -v
```

## 📝 Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix  
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(agent): add risk assessment iteration logic
fix(api): handle timeout errors in task submission  
docs(readme): update installation instructions
test(integration): add tests for SSE progress streaming
```

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No merge conflicts

### PR Description Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass  
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: At least one maintainer reviews the PR
3. **Testing**: Reviewer tests functionality manually if needed
4. **Approval**: PR approved and merged by maintainer

## 🎯 Areas for Contribution

### 🧠 AI/ML Enhancements

- **New Agent Nodes**: Implement specialized analysis capabilities
- **Model Integration**: Support for different LLM providers (Anthropic, Cohere)
- **Prompt Engineering**: Improve prompt templates for better outputs
- **Fine-tuning**: Domain-specific model fine-tuning

### 🎨 Frontend Improvements

- **UI/UX**: Enhance Streamlit interface design
- **Visualization**: Better progress and result visualizations
- **Real-time Features**: Improve SSE implementation
- **Mobile Support**: Responsive design improvements

### 🛠️ Backend Features

- **API Enhancements**: New endpoints and functionality
- **Performance**: Optimization and caching improvements
- **Monitoring**: Logging, metrics, and health checks
- **Security**: Authentication and authorization features

### 🔌 Integrations

- **Project Management Tools**: Jira, Asana, Trello integration
- **Communication**: Slack, Teams notifications
- **File Storage**: Google Drive, Dropbox integration
- **Calendar**: Schedule integration with calendar apps

### 📚 Documentation

- **Tutorials**: Step-by-step guides
- **Examples**: Real-world use cases
- **API Docs**: Comprehensive API documentation
- **Video Content**: Demo videos and walkthroughs

## 🏗️ Architecture Guidelines

### Adding New Agent Nodes

1. **Create node function** in `app/agent/nodes/`:
   ```python
   def custom_analysis_node(state: AgentState) -> dict:
       """Custom analysis node implementation."""
       # Implementation here
       return {"custom_result": result}
   ```

2. **Add to graph** in `app/agent/graph.py`:
   ```python
   workflow.add_node("custom_analysis", create_tracked_node(
       custom_analysis_node,
       "custom_analysis", 
       "Custom Analysis Description"
   ))
   ```

3. **Update routing logic** if needed
4. **Add tests** for the new node
5. **Update documentation**

### Model Adapter Pattern

When adding new data types:

1. **Create simple model** for LLM interaction
2. **Create full model** for business logic
3. **Implement adapter** in `app/services/model_adapter.py`
4. **Add validation** and error handling
5. **Write comprehensive tests**

### API Endpoint Guidelines

- **RESTful design**: Follow REST principles
- **Error handling**: Comprehensive error responses
- **Validation**: Pydantic models for request/response
- **Documentation**: OpenAPI/Swagger documentation
- **Testing**: Unit and integration tests

## 🆘 Getting Help

### Community Support

- **GitHub Issues**: Ask questions and report bugs
- **Discussions**: Join community discussions
- **Discord/Slack**: Real-time chat (if available)

### Maintainer Contact

- Create an issue for technical questions
- Tag maintainers in PRs for review
- Follow up on stale PRs/issues

## 🏆 Recognition

Contributors will be recognized in:
- **README**: Contributors section
- **Releases**: Release notes acknowledgments  
- **Documentation**: Author credits

---

Thank you for contributing to the AI Project Management Assistant! Your efforts help make this project better for everyone. 🎉 