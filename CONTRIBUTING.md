# Contributing to Coming Attractions

Thank you for your interest in contributing to Coming Attractions! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project follows a code of conduct that all contributors are expected to uphold. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/coming-attractions.git
   cd coming-attractions
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/robertsinfosec/coming-attractions.git
   ```

## Development Setup

### Using VS Code Dev Container (Recommended)

The project includes a Dev Container configuration for a consistent development environment:

1. Install [VS Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project in VS Code
3. When prompted, click "Reopen in Container"
4. The container will build and set up the development environment automatically

### Manual Setup

If you prefer not to use Dev Containers:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   make install-dev
   # Or manually:
   pip install -e ".[dev]"
   ```

3. **Verify installation**:
   ```bash
   coming-attractions --help
   pytest --version
   ```

## Making Changes

### Branch Naming

Create a descriptive branch for your changes:

```bash
git checkout -b feature/add-new-filter
git checkout -b fix/pruner-crash
git checkout -b docs/update-readme
```

### Commit Messages

Write clear, descriptive commit messages:

```
type: Short description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123" or "Related to #456"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

Examples:
```
feat: Add --exclude-genres option to fetch command

fix: Handle missing release dates in pruner

docs: Update Docker deployment instructions
```

## Testing

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# With coverage
make test-cov
```

### Writing Tests

1. Place tests in `tests/` directory
2. Name test files `test_*.py`
3. Use descriptive test names: `test_fetch_handles_missing_trailer`
4. Use fixtures from `conftest.py`
5. Aim for >80% code coverage

Example test:

```python
def test_sanitize_folder_name_removes_invalid_chars(utils_module):
    """Test that invalid filesystem characters are removed."""
    result = utils_module.sanitize_folder_name("Movie: The Title!")
    assert result == "Movie The Title"
    assert "/" not in result
```

### Running Specific Tests

```bash
# Single test file
pytest tests/test_utils.py

# Single test function
pytest tests/test_utils.py::test_sanitize_folder_name

# With verbose output
pytest -v tests/
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   make test
   ```

3. **Check code quality** (if tools installed):
   ```bash
   make lint
   make format
   ```

4. **Update documentation** if you changed:
   - CLI commands or options
   - Configuration options
   - API or behavior

### Submitting

1. **Push to your fork**:
   ```bash
   git push origin feature/your-branch
   ```

2. **Create Pull Request** on GitHub
3. **Fill out PR template** completely
4. **Link related issues**: "Fixes #123"

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, a maintainer will merge

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Organization

```python
# Order of imports:
# 1. Standard library
# 2. Third-party packages
# 3. Local modules

import sys
from pathlib import Path
from typing import List, Optional

import click
from pydantic import BaseModel

from coming_attractions.logger import Logger
```

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings:

```python
def fetch_trailer(api_key: str, movie_id: int) -> Optional[str]:
    """Fetch trailer URL for a movie.
    
    Args:
        api_key: TMDb API key
        movie_id: TMDb movie ID
        
    Returns:
        Trailer URL if found, None otherwise
        
    Raises:
        ValueError: If api_key is invalid
    """
    pass
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Clean up resources (use context managers)

```python
try:
    with open(file_path) as f:
        data = f.read()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return None
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    return None
```

## Project Structure

```
coming-attractions/
├── src/
│   └── coming_attractions/      # Main package
│       ├── cli.py             # CLI interface
│       ├── fetcher.py         # Fetch logic
│       ├── pruner.py          # Prune logic
│       └── ...
├── tests/                     # Test suite
├── docs/                      # Documentation (if any)
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Docker Compose example
└── setup.py                   # Package configuration
```

## Getting Help

- **Issues**: Check [existing issues](https://github.com/robertsinfosec/coming-attractions/issues)
- **Discussions**: Start a discussion for questions
- **Documentation**: Read the [README](README.md) and [MIGRATION](MIGRATION.md) guide

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
