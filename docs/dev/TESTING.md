# Testing Guide

> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Setup](SETUP.md) | [Architecture](ARCHITECTURE.md) | [Codecov](CODECOV.md)

Complete guide for writing and running tests in Coming Attractions.

## Table of Contents

- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Code Coverage](#code-coverage)
- [Test Organization](#test-organization)
- [Best Practices](#best-practices)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)


## Running Tests

### Quick Test Run

```bash
cd src/
pytest
```

### With Coverage

```bash
cd src/
pytest --cov=coming_attractions --cov-report=term-missing
```

### Generate HTML Coverage Report

```bash
cd src/
pytest --cov=coming_attractions --cov-report=html
# Open htmlcov/index.html in your browser
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Single test file
pytest tests/test_utils.py

# Single test function
pytest tests/test_utils.py::test_sanitize_folder_name

# Tests matching pattern
pytest -k "test_prune"

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Using Makefile

If `make` is available:

```bash
cd src/

# Run all tests
make test

# With coverage report
make test-cov

# Clean coverage artifacts
make clean
```


## Writing Tests

### Test File Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_cli.py              # CLI command tests
├── test_fetcher.py          # Fetcher logic tests
├── test_pruner.py           # Pruner logic tests
├── test_title_fixer.py      # Title fixing tests
├── test_tmdb_client.py      # TMDb API tests (mocked)
├── test_utils.py            # Utility function tests
├── test_youtube_downloader.py  # YouTube download tests (mocked)
└── test_integration.py      # End-to-end integration tests
```

### Basic Test Pattern

```python
import pytest
from coming_attractions.utils import sanitize_folder_name

def test_sanitize_folder_name_removes_invalid_chars():
    """Test that invalid filesystem characters are removed."""
    result = sanitize_folder_name("Movie: The Title!")
    assert "/" not in result
    assert ":" not in result
    assert "Movie" in result
    assert result == "Movie The Title"
```

### Using Fixtures

Fixtures are defined in `conftest.py` and automatically available to all tests:

```python
import pytest

def test_something_with_temp_dir(tmp_path):
    """Test using pytest's built-in tmp_path fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"

def test_something_with_custom_fixture(mock_tmdb_client):
    """Test using custom fixture from conftest.py."""
    # mock_tmdb_client is pre-configured
    result = mock_tmdb_client.get_movie(123)
    assert result is not None
```

### Mocking External Dependencies

**Mock HTTP requests:**

```python
import pytest
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_api_call(mock_get):
    """Test HTTP request without hitting real API."""
    # Configure mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"title": "Test Movie"}
    mock_get.return_value = mock_response
    
    # Run test
    from coming_attractions.tmdb_client import TMDbClient
    client = TMDbClient(api_key="test_key")
    result = client.get_movie(123)
    
    # Verify
    assert result["title"] == "Test Movie"
    mock_get.assert_called_once()
```

**Mock file operations:**

```python
from unittest.mock import patch, mock_open

@patch('builtins.open', new_callable=mock_open, read_data='<movie><title>Test</title></movie>')
def test_nfo_parsing(mock_file):
    """Test NFO file parsing without real file."""
    from coming_attractions.title_fixer import parse_nfo
    result = parse_nfo('/fake/path/movie.nfo')
    assert result['title'] == 'Test'
```

**Mock subprocess/external commands:**

```python
@patch('subprocess.run')
def test_youtube_download(mock_run):
    """Test yt-dlp invocation without actually downloading."""
    mock_run.return_value = MagicMock(returncode=0)
    
    from coming_attractions.youtube_downloader import download_video
    success = download_video('https://youtube.com/watch?v=test', '/fake/path')
    
    assert success is True
    mock_run.assert_called_once()
```

### Testing Error Conditions

```python
import pytest

def test_handles_missing_file():
    """Test graceful handling of missing file."""
    from coming_attractions.utils import read_file
    
    result = read_file('/nonexistent/file.txt')
    assert result is None  # Should return None, not crash

def test_raises_on_invalid_input():
    """Test that invalid input raises expected exception."""
    from coming_attractions.config import Config
    
    with pytest.raises(ValueError, match="API key.*required"):
        Config(api_key="")  # Empty API key should raise
```

### Parametrized Tests

Test multiple inputs with one test function:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("Movie: Title", "Movie Title"),
    ("Show/Name", "Show Name"),
    ("Test|Pipe", "Test Pipe"),
    ("Normal Title", "Normal Title"),
])
def test_sanitize_various_chars(input, expected):
    """Test sanitization of various invalid characters."""
    from coming_attractions.utils import sanitize_folder_name
    assert sanitize_folder_name(input) == expected
```

### Testing CLI Commands

```python
from click.testing import CliRunner
from coming_attractions.cli import cli

def test_fetch_command_help():
    """Test fetch command help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ['fetch', '--help'])
    
    assert result.exit_code == 0
    assert 'TMDb API key' in result.output

def test_fetch_requires_api_key():
    """Test that fetch requires API key."""
    runner = CliRunner()
    result = runner.invoke(cli, ['fetch'])
    
    assert result.exit_code != 0
    assert 'TMDB_API_KEY' in result.output
```


## Code Coverage

### Understanding Coverage

Coverage measures what percentage of your code is executed during tests. Higher coverage generally means better tested code.

**Coverage is tracked via:**
- Terminal reports (run locally)
- HTML reports (browse locally)
- XML reports (uploaded to Codecov)
- Codecov dashboard (online, with trends)

### Viewing Coverage Locally

```bash
cd src/

# Terminal summary
pytest --cov=coming_attractions --cov-report=term

# Terminal with missing line numbers
pytest --cov=coming_attractions --cov-report=term-missing

# HTML (interactive, most detailed)
pytest --cov=coming_attractions --cov-report=html
open htmlcov/index.html

# XML (for Codecov)
pytest --cov=coming_attractions --cov-report=xml
```

### Coverage Badge

The README shows current coverage via Codecov badge:

[![codecov](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsinfosec/coming-attractions)

**Always refer to the live badge or Codecov dashboard for current numbers.**

### Coverage Goals

- **Target:** 80% overall coverage (per PRD)
- **Minimum:** No PR should decrease coverage
- **New code:** Should be ≥80% covered

**Check current coverage:**
- Visit [Codecov Dashboard](https://codecov.io/gh/robertsinfosec/coming-attractions)
- Click on branch or PR to see detailed breakdown

### Improving Coverage

1. **Identify gaps:**
   ```bash
   pytest --cov=coming_attractions --cov-report=html
   open htmlcov/index.html
   ```

2. **Focus on red/yellow files:**
   - Red = <60% coverage (priority)
   - Yellow = 60-79% coverage (needs work)
   - Green = 80-100% coverage (good!)

3. **Write tests for uncovered code:**
   - Look at "missing lines" in HTML report
   - Write tests that execute those lines
   - Verify with another coverage run

4. **Don't game coverage:**
   - Tests must have meaningful assertions
   - Cover both success and error paths
   - Test edge cases, not just happy path

See [Codecov Guide](CODECOV.md) for detailed coverage tracking setup.


## Test Organization

### Directory Structure

```
src/
├── coming_attractions/       # Source code
│   ├── __init__.py
│   ├── cli.py
│   ├── fetcher.py
│   └── ...
└── tests/                    # Test suite
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── test_cli.py           # Tests for cli.py
    ├── test_fetcher.py       # Tests for fetcher.py
    └── ...
```

### Naming Conventions

- **Test files:** `test_*.py` or `*_test.py`
- **Test functions:** `test_*`
- **Test classes:** `Test*`
- **Fixtures:** Descriptive names (`mock_tmdb_client`, `temp_trailer_dir`)

### Shared Fixtures (conftest.py)

Place reusable fixtures in `tests/conftest.py`:

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_trailer_dir(tmp_path):
    """Create temporary trailer directory structure."""
    theatrical = tmp_path / "theatrical"
    streaming = tmp_path / "streaming"
    theatrical.mkdir()
    streaming.mkdir()
    return tmp_path

@pytest.fixture
def mock_tmdb_client():
    """Create mock TMDb client."""
    from unittest.mock import MagicMock
    client = MagicMock()
    client.get_movie.return_value = {"title": "Test Movie", "id": 123}
    return client
```

These are automatically available to all tests.


## Best Practices

### 1. One Concept Per Test

❌ **Bad:** Testing multiple things in one test

```python
def test_everything():
    result1 = function1()
    assert result1 == expected1
    result2 = function2()
    assert result2 == expected2
    result3 = function3()
    assert result3 == expected3
```

✅ **Good:** Separate tests for each concept

```python
def test_function1():
    result = function1()
    assert result == expected1

def test_function2():
    result = function2()
    assert result == expected2

def test_function3():
    result = function3()
    assert result == expected3
```

### 2. Descriptive Test Names

❌ **Bad:** Vague names

```python
def test_fetch():
    ...

def test_error():
    ...
```

✅ **Good:** Clear, descriptive names

```python
def test_fetch_returns_trailers_for_valid_movie():
    ...

def test_fetch_handles_missing_release_date_gracefully():
    ...

def test_fetch_raises_value_error_on_invalid_api_key():
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_prune_removes_old_trailers():
    # Arrange: Set up test data
    trailer_dir = create_test_trailers(age_years=3)
    
    # Act: Execute function being tested
    result = prune_trailers(trailer_dir, retention_years=2)
    
    # Assert: Verify expected outcome
    assert result.removed_count == 1
    assert not trailer_dir.exists()
```

### 4. Mock External Dependencies

Always mock:
- HTTP requests (use `@patch('requests.get')`)
- File I/O (use `tmp_path` fixture or `mock_open`)
- External processes (use `@patch('subprocess.run')`)
- Time/dates (use `@patch('datetime.datetime.now')`)
- Random values (use `@patch('random.choice')`)

### 5. Test Both Success and Failure

```python
def test_download_success():
    """Test successful download."""
    result = download('https://valid.url')
    assert result is True

def test_download_network_error():
    """Test handling of network errors."""
    result = download('https://unreachable.url')
    assert result is False

def test_download_invalid_url():
    """Test handling of invalid URL format."""
    with pytest.raises(ValueError):
        download('not-a-url')
```

### 6. Use Fixtures for Common Setup

❌ **Bad:** Repeated setup in every test

```python
def test_one():
    dir = Path("/tmp/test")
    dir.mkdir()
    # ...

def test_two():
    dir = Path("/tmp/test")
    dir.mkdir()
    # ...
```

✅ **Good:** Shared fixture

```python
@pytest.fixture
def test_dir(tmp_path):
    return tmp_path / "test"

def test_one(test_dir):
    # test_dir is ready to use
    ...

def test_two(test_dir):
    # test_dir is ready to use
    ...
```

### 7. Keep Tests Fast

- Mock slow operations (network, file I/O)
- Use `tmp_path` instead of real directories
- Avoid `time.sleep()` in tests
- Run expensive tests separately with markers

```python
@pytest.mark.slow
def test_full_integration():
    """Slow integration test - run separately."""
    ...

# Run only fast tests:
pytest -m "not slow"

# Run only slow tests:
pytest -m slow
```


## Continuous Integration

### GitHub Actions

Every push and PR triggers automated testing via GitHub Actions.

**Workflow:** `.github/workflows/ci-cd.yml`

**What happens:**
1. Checkout code
2. Set up Python (3.11 and 3.12)
3. Install dependencies
4. Run linting (ruff)
5. Run tests with coverage
6. Upload coverage to Codecov
7. Build and publish Docker image (on main branch)

### Viewing CI Results

**On GitHub:**
1. Go to **Actions** tab
2. Click on workflow run
3. Expand "Run tests with coverage"
4. View test results and coverage report

**On Codecov:**
1. Visit [Codecov Dashboard](https://codecov.io/gh/robertsinfosec/coming-attractions)
2. Click on commit or PR
3. View detailed coverage breakdown

### PR Requirements

Before merging:
- ✅ All tests must pass
- ✅ Coverage must not decrease
- ✅ Linting must pass
- ✅ All checks must be green


## Troubleshooting

### Tests Failing Locally

**Check you're in the right directory:**

```bash
cd src/
pytest
```

**Ensure package is installed:**

```bash
pip install -e .
```

**Clear Python cache:**

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Import Errors

**Reinstall in editable mode:**

```bash
cd src/
pip install -e .
```

**Check Python version:**

```bash
python --version  # Should be 3.11+
```

### Coverage Report Not Generating

**Install pytest-cov:**

```bash
pip install pytest-cov
```

**Check pytest.ini configuration:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Mock Not Working

**Ensure correct import path:**

```python
# If module does: from requests import get
@patch('coming_attractions.fetcher.get')  # Patch where it's used

# If module does: import requests
@patch('requests.get')  # Patch at source
```

**Check mock is applied before function runs:**

```python
@patch('module.function')  # Decorator applies BEFORE test runs
def test_something(mock_func):
    ...
```

### Tests Pass Locally, Fail in CI

**Common causes:**
- File path differences (use `Path` objects)
- Environment variable differences (use fixtures to set)
- Timezone differences (mock `datetime.now()`)
- Different Python versions (test on 3.11 AND 3.12)

**Debug CI:**

```yaml
# Add to workflow for debugging
- name: Debug environment
  run: |
    pwd
    ls -la
    python --version
    pip list
```


## Pre-Commit Checklist

Before committing code:

- [ ] Run tests: `pytest`
- [ ] Check coverage hasn't decreased: `pytest --cov=coming_attractions`
- [ ] Lint code: `ruff check coming_attractions/ tests/`
- [ ] Format code (optional): `black coming_attractions/ tests/`
- [ ] All tests pass locally
- [ ] Added tests for new code
- [ ] Updated docstrings


## Additional Resources

- **pytest Documentation:** https://docs.pytest.org/
- **pytest-cov Documentation:** https://pytest-cov.readthedocs.io/
- **unittest.mock Guide:** https://docs.python.org/3/library/unittest.mock.html
- **Codecov Documentation:** https://docs.codecov.com/


> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Setup](SETUP.md) | [Architecture](ARCHITECTURE.md) | [Codecov](CODECOV.md)
