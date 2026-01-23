# Style Guide

This document defines the coding standards and best practices for the Coming Attractions project.

## Table of Contents

- [General Principles](#general-principles)
- [Python Style](#python-style)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Git Workflow](#git-workflow)
- [Security](#security)

## General Principles

### Code Quality
- **Zero tolerance for technical debt** - Refactor as you go
- **No shortcuts** - Do it right the first time
- **Test everything** - Minimum 80% coverage
- **Document everything** - Code is read more than written
- **Review everything** - No code merges without review

### Best Practices
- **DRY (Don't Repeat Yourself)** - Extract common logic
- **SOLID principles** - Single responsibility, Open/closed, etc.
- **KISS (Keep It Simple)** - Simplest solution that works
- **YAGNI (You Aren't Gonna Need It)** - Don't over-engineer

## Python Style

### PEP 8 Compliance

We **strictly follow PEP 8**. Key points:

#### Naming Conventions
```python
# Modules: lowercase with underscores
import my_module

# Classes: PascalCase
class TrailerFetcher:
    pass

# Functions/variables: snake_case
def fetch_trailer(movie_id: int) -> Optional[str]:
    trailer_url = None
    return trailer_url

# Constants: UPPER_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"

# Private: leading underscore
def _internal_helper():
    pass
```

#### Spacing and Layout
```python
# Maximum line length: 100 characters (not 79 for modern screens)
# Indentation: 4 spaces (never tabs)
# Blank lines: 2 before top-level, 1 before methods

class MyClass:
    """Class docstring."""
    
    def __init__(self):
        self.value = 0
    
    def my_method(self):
        """Method docstring."""
        pass


def standalone_function():
    """Function docstring."""
    pass
```

#### Imports
```python
# Order: standard library, third-party, local
# Each section alphabetically sorted
# Absolute imports preferred

import sys
from pathlib import Path
from typing import List, Optional

import click
from pydantic import BaseModel

from coming_attractions.logger import Logger
from coming_attractions.models import Trailer
```

### Type Hints

**Required for all function signatures:**

```python
from typing import Optional, List, Dict, Any

def fetch_data(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """Fetch data from URL.
    
    Args:
        url: The URL to fetch from
        params: Optional query parameters
        timeout: Request timeout in seconds
        
    Returns:
        Response data if successful, None otherwise
    """
    pass
```

### Docstrings

**Google-style docstrings required for all public functions/classes:**

```python
def process_trailer(
    trailer: Trailer,
    output_dir: Path,
    dry_run: bool = False
) -> bool:
    """Process and download a trailer.
    
    Downloads the trailer video from YouTube, creates metadata files,
    and organizes the output into the specified directory structure.
    
    Args:
        trailer: The Trailer object to process
        output_dir: Directory to save trailer files
        dry_run: If True, simulate without downloading
        
    Returns:
        True if processing succeeded, False otherwise
        
    Raises:
        ValueError: If trailer is missing required fields
        PermissionError: If output_dir is not writable
        
    Example:
        >>> trailer = Trailer(title="Movie", release_date="2024-01-01")
        >>> process_trailer(trailer, Path("/data/trailers"))
        True
    """
    pass
```

### Error Handling

```python
# Good - Specific exceptions
try:
    data = fetch_api_data(url)
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise
except requests.Timeout:
    logger.warning("Request timed out, retrying...")
    # Retry logic
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Bad - Bare except
try:
    data = fetch_api_data(url)
except:  # ❌ Never do this!
    pass
```

### File Operations

**Always use atomic operations:**

```python
from pathlib import Path

def write_file_atomically(file_path: Path, content: str) -> None:
    """Write file using atomic operation (temp + rename).
    
    Args:
        file_path: Target file path
        content: Content to write
    """
    temp_file = file_path.with_suffix('.tmp')
    try:
        temp_file.write_text(content, encoding='utf-8')
        temp_file.rename(file_path)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()
        raise
```

### Logging

**Use centralized Logger, never print():**

```python
from coming_attractions.logger import Logger, LogLevel

logger = Logger(level=LogLevel.INFO)

# Good
logger.info("Processing 10 items")
logger.success("Download completed")
logger.warning("API rate limit approaching")
logger.error("Failed to parse response")

# Bad
print("Processing items")  # ❌ Never use print()
```

### Code Organization

**Functions should be focused and concise:**

```python
# Good - Single responsibility, ~20 lines
def validate_api_key(api_key: str) -> bool:
    """Validate TMDb API key format."""
    if not api_key:
        return False
    if len(api_key) != 32:
        return False
    if not api_key.isalnum():
        return False
    return True

# Bad - Too long, multiple responsibilities
def process_everything(data):  # ❌ 100+ line function
    # Parse data
    # Validate data
    # Transform data
    # Save to database
    # Send notifications
    # Generate reports
    pass  # This should be split into multiple functions!
```

## Project Structure

### Directory Layout

```
Root: GitHub metadata ONLY
├── README.md              # Project overview
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md          # Version history
├── STYLE_GUIDE.md        # This file
├── LICENSE               # License text
└── .gitignore            # Git ignore patterns

src/                      # ALL source code and configuration
├── coming_attractions/      # Main Python package
├── docker/               # Docker configuration
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── setup.py             # Package setup
├── requirements.txt     # Dependencies
├── pytest.ini           # Pytest config
└── Makefile            # Build automation

docs/                    # Documentation
├── PRD.md              # Product requirements
├── MIGRATION.md        # Migration guide
├── QUICKREF.md         # Quick reference
└── *.md                # Other docs

.github/                 # GitHub configuration
├── copilot-instructions.md
├── workflows/          # CI/CD workflows
├── ISSUE_TEMPLATE/     # Issue templates
└── PULL_REQUEST_TEMPLATE.md
```

### File Naming

- **Python modules**: `snake_case.py` (e.g., `trailer_fetcher.py`)
- **Test files**: `test_*.py` (e.g., `test_utils.py`)
- **Documentation**: `UPPERCASE.md` for root, `Title_Case.md` for docs/
- **Configuration**: Lowercase with extension (e.g., `pytest.ini`, `.dockerignore`)

## Documentation

### README Structure

Every significant directory should have a README explaining:
- Purpose of the directory
- How files are organized
- Key concepts or patterns used
- How to run/test the code

### Code Comments

```python
# Good - Explain WHY, not WHAT
# Use UTC to avoid timezone issues
timestamp = datetime.utcnow()

# Skip trailers already in removed file to avoid re-downloading
if folder_name in removed_trailers:
    continue

# Bad - Stating the obvious
# Increment counter
counter += 1  # ❌ Don't state the obvious

# Set x to 5
x = 5  # ❌ The code already says this
```

### Inline Documentation

```python
class TrailerFetcher:
    """Fetches movie trailers from TMDb and YouTube.
    
    This class handles the complete workflow of discovering upcoming
    movies from TMDb, finding their trailer videos, and downloading
    them to the appropriate directory structure.
    
    Attributes:
        api_key: TMDb API key for authentication
        mode: Fetch mode (theatrical, streaming, or both)
        config: Configuration object with all settings
    """
    
    def __init__(self, config: FetchConfig):
        """Initialize fetcher with configuration.
        
        Args:
            config: Validated configuration object
        """
        self.config = config
```

## Git Workflow

### Commit Messages

**Format:**
```
type: Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars).
Explain WHY the change was made, not what was changed
(the diff shows what changed).

- Bullet points are okay
- Reference issues: Fixes #123, Related to #456
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding/updating tests
- `refactor`: Code restructuring (no functional changes)
- `style`: Formatting, whitespace
- `chore`: Maintenance (dependencies, CI, etc.)
- `perf`: Performance improvement

**Examples:**
```
feat: Add support for custom trailer quality settings

Allows users to specify maximum resolution for downloads
instead of hardcoded 1080p. Useful for bandwidth-limited
environments.

Fixes #45
```

```
fix: Handle missing release dates in pruner

Some NFO files don't have releasedate field, causing
pruner to crash. Now falls back to premiered/aired/dateadded
in order of preference.

Fixes #67
```

### Branch Naming

```
feature/add-quality-settings
fix/pruner-missing-dates
docs/update-readme-structure
refactor/extract-api-client
```

## Security

### Never Commit Secrets

```python
# Good - Use environment variables
api_key = os.getenv("TMDB_API_KEY")

# Bad - Hardcoded secrets
api_key = "abc123..."  # ❌ NEVER!
```

### Input Validation

```python
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    """Configuration with validation."""
    
    api_key: str = Field(..., min_length=32, max_length=32)
    days_ahead: int = Field(default=365, ge=1, le=730)
    
    @field_validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric")
        return v
```

### Path Sanitization

```python
from unicodedata import normalize

def sanitize_folder_name(name: str) -> str:
    """Sanitize folder name for filesystem safety.
    
    Args:
        name: Raw folder name
        
    Returns:
        Sanitized folder name safe for all filesystems
    """
    # Normalize Unicode
    name = normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    
    # Remove invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '')
    
    # Limit length
    return name[:200]
```

## Testing

### Test Structure

```python
import pytest
from pathlib import Path
from coming_attractions.utils import sanitize_folder_name

class TestSanitizeFolderName:
    """Tests for folder name sanitization."""
    
    def test_removes_invalid_characters(self):
        """Test that invalid filesystem characters are removed."""
        result = sanitize_folder_name("Movie: The Title!")
        assert "/" not in result
        assert ":" not in result
    
    def test_limits_length(self):
        """Test that names are limited to 200 characters."""
        long_name = "a" * 300
        result = sanitize_folder_name(long_name)
        assert len(result) == 200
    
    def test_handles_unicode(self):
        """Test that Unicode is normalized to ASCII."""
        result = sanitize_folder_name("Café Müller")
        assert result == "Cafe Muller"
```

### Test Coverage

- **Minimum 80% coverage** for all new code
- **Test both success and failure paths**
- **Mock external dependencies** (API calls, file I/O)
- **Use fixtures** for common test setup

```python
@pytest.fixture
def temp_dir(tmp_path):
    """Provide isolated temporary directory."""
    yield tmp_path
    # Cleanup happens automatically

@pytest.fixture
def mock_logger():
    """Provide logger for testing."""
    from coming_attractions.logger import Logger, LogLevel
    return Logger(level=LogLevel.DEBUG)
```

## Code Review Checklist

Before submitting code for review:

- [ ] Follows PEP 8 style
- [ ] Has type hints on all functions
- [ ] Has docstrings on all public functions/classes
- [ ] No hardcoded values (use config/constants)
- [ ] Error handling is appropriate
- [ ] Logging uses Logger class, not print()
- [ ] Tests are included and pass
- [ ] Coverage is ≥80%
- [ ] Documentation is updated
- [ ] No secrets or sensitive data
- [ ] File operations are atomic
- [ ] Paths use Path objects, not strings
- [ ] Imports are organized properly

## Tools and Automation

### Recommended Tools

- **Black**: Code formatter (optional, but helpful)
- **ruff**: Fast linter for Python
- **mypy**: Static type checker
- **pytest**: Testing framework
- **pre-commit**: Git hooks for automation

### Running Checks

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/

# Test
pytest src/tests/ --cov=src/coming_attractions

# All at once
make lint format test
```

## Questions?

When in doubt:
1. Check this style guide
2. Look at existing code for patterns
3. Ask in PR review
4. Reference PEP 8: https://pep8.org/

**Remember: Quality over speed. Do it right the first time.**
