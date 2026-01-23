# Development Guide

## Running Tests

### Quick Test Run
```bash
cd src
pytest
```

### With Coverage Report
```bash
cd src
pytest --cov=coming_attractions --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
cd src
pytest --cov=coming_attractions --cov-report=html
# Open htmlcov/index.html in your browser
```

### Generate XML Coverage for Codecov
```bash
cd src
pytest --cov=coming_attractions --cov-report=xml
```

## Code Coverage

Current coverage: **58%** (Target: 80%)

### Coverage by Module
- `models.py`: 100% ✅
- `__init__.py`: 100% ✅
- `utils.py`: 87% ✅
- `config.py`: 84% ✅
- `title_fixer.py`: 81% ✅
- `tmdb_client.py`: 79% ✅
- `pruner.py`: 68%
- `logger.py`: 67%
- `youtube_downloader.py`: 57%
- `cli.py`: 51%
- `fetcher.py`: 9% ⚠️
- `__main__.py`: 0% ⚠️

### Improving Coverage

Priority areas for additional tests:
1. **fetcher.py** - Core functionality, needs comprehensive integration tests
2. **cli.py** - Command-line interface tests
3. **__main__.py** - Entry point testing

## Linting and Type Checking

### Lint with ruff
```bash
cd src
ruff check coming_attractions/ tests/
```

### Type check with mypy
```bash
cd src
mypy coming_attractions/ --ignore-missing-imports
```

### Auto-format with black (optional)
```bash
cd src
black coming_attractions/ tests/
```

## Continuous Integration

GitHub Actions workflows:
- **CI** (`.github/workflows/ci.yml`) - Runs tests, linting, and uploads coverage to Codecov
- **Build** (`.github/workflows/build.yml`) - Builds and publishes Docker images
- **Security** (`.github/workflows/security.yml`) - CodeQL security scanning

### Codecov Integration

Coverage reports are automatically uploaded to Codecov on every push and PR.

To view coverage:
1. Visit https://codecov.io/gh/robertsinfosec/coming-attractions
2. View detailed reports by file, function, and line
3. See coverage trends over time

### Setting Up Codecov (First Time)

1. Go to https://codecov.io and sign in with GitHub
2. Enable the `coming-attractions` repository
3. Copy the upload token
4. Add it as a repository secret: `CODECOV_TOKEN`

## Testing Best Practices

1. **Write tests first** - TDD approach when adding new features
2. **Mock external dependencies** - API calls, file I/O, network requests
3. **Test edge cases** - Empty inputs, invalid data, error conditions
4. **Use fixtures** - Leverage `conftest.py` for reusable test setup
5. **Descriptive names** - Test function names should describe what they test

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_cli.py          # CLI command tests
├── test_fetcher.py      # Fetcher integration tests
├── test_pruner.py       # Pruner logic tests
├── test_title_fixer.py  # Title fixing tests
├── test_tmdb_client.py  # TMDb API tests (mocked)
├── test_utils.py        # Utility function tests
└── test_youtube_downloader.py  # YouTube download tests
```

### Example Test

```python
import pytest
from coming_attractions.utils import sanitize_folder_name

class TestSanitizeFolderName:
    def test_removes_invalid_chars(self):
        """Test that invalid filesystem characters are removed."""
        result = sanitize_folder_name("Movie: The Title!")
        assert "/" not in result
        assert ":" not in result
        assert "Movie" in result
```

## Pre-Commit Checklist

Before committing:
- [ ] Tests pass: `pytest`
- [ ] Coverage hasn't decreased: `pytest --cov=coming_attractions --cov-report=term`
- [ ] No lint errors: `ruff check coming_attractions/ tests/`
- [ ] Code is formatted: `black coming_attractions/ tests/` (optional)
- [ ] Type hints are correct: `mypy coming_attractions/` (optional)

## Troubleshooting

### Tests failing with import errors
```bash
# Reinstall package in editable mode
cd src
pip install -e .
```

### Coverage report not generating
```bash
# Make sure pytest-cov is installed
pip install pytest-cov
```

### Codecov upload failing
```bash
# Check that CODECOV_TOKEN is set in GitHub secrets
# Manually upload for testing:
bash <(curl -s https://codecov.io/bash) -t YOUR_TOKEN
```
