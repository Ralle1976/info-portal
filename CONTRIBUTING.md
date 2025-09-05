# Contributing to QR-Info-Portal

Thank you for your interest in contributing to QR-Info-Portal! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Show empathy towards other community members

## 🔄 Development Process

We use GitHub Flow for our development process:

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes**
4. **Submit a Pull Request**

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-email-notifications`)
- `fix/` - Bug fixes (e.g., `fix/login-redirect-issue`)
- `docs/` - Documentation updates (e.g., `docs/update-api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/optimize-qr-generation`)

## 🛠️ Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/qr-info-portal.git
   cd qr-info-portal
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters (Black default)

### Code Quality

- Write meaningful variable and function names
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Keep functions focused and small
- Write unit tests for new features

### Example Code Style

```python
from typing import Optional, Dict
from datetime import datetime

def calculate_next_opening(
    current_time: datetime,
    schedule: Dict[str, List[str]],
    exceptions: Optional[List[Dict]] = None
) -> Optional[datetime]:
    """
    Calculate the next opening time based on schedule and exceptions.
    
    Args:
        current_time: Current timestamp
        schedule: Weekly schedule dictionary
        exceptions: List of exception dates and times
        
    Returns:
        Next opening datetime or None if no opening found
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_schedule.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the app structure in test files
- Use descriptive test names
- Test edge cases and error conditions

Example test:

```python
def test_status_calculation_with_exception():
    """Test status calculation when exception overlaps regular hours."""
    # Arrange
    schedule = {"mon": ["09:00-17:00"]}
    exception = {"date": "2025-01-01", "closed": True}
    
    # Act
    status = calculate_status(schedule, exception)
    
    # Assert
    assert status == "CLOSED"
    assert status.reason == "Holiday"
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Use Google-style docstrings
- Include usage examples in docstrings
- Keep documentation up-to-date with code changes

### Project Documentation

- Update README.md for significant changes
- Document new features in appropriate guide
- Add API endpoints to API documentation
- Include configuration options in reference

## 🎨 Frontend Guidelines

### CSS

- Use Tailwind CSS utility classes
- Follow component-based styling
- Ensure responsive design
- Test on multiple browsers

### JavaScript

- Use modern ES6+ syntax
- Keep JavaScript minimal (prefer HTMX)
- Document complex interactions
- Ensure accessibility (ARIA labels)

## 🔍 Code Review Process

### Before Submitting PR

- [ ] Run tests locally
- [ ] Update documentation
- [ ] Check code formatting
- [ ] Review your own changes
- [ ] Test on different browsers/devices

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Cross-browser testing done

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Closes #XXX
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, browser)
- Screenshots or error logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Mockups or examples (if applicable)

## 🌐 Translations

When adding or updating translations:

1. Update all language files (`de.json`, `en.json`, `th.json`)
2. Maintain consistent keys across files
3. Test translations in the UI
4. Consider text length in different languages

## 📦 Releasing

Releases are managed by maintainers:

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to production

## ❓ Getting Help

- Check existing documentation
- Search closed issues
- Ask in discussions
- Contact maintainers

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project statistics

Thank you for contributing to make QR-Info-Portal better! 🙏