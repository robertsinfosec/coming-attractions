# GitHub Copilot Instructions

## Project Overview

This is **Coming Attractions**, a professional Python application for automated movie trailer management. It fetches trailers from TMDb/YouTube, enforces retention policies, and maintains metadata for media server integration.

## Code Quality Standards

### Python Code
- **Always follow PEP 8** - Use proper naming, spacing, and structure
- **Type hints required** - All function signatures must include type hints
- **Docstrings required** - Use Google-style docstrings for all public functions/classes
- **No technical debt** - Refactor as you go, never leave TODO comments without GitHub issues
- **Minimum 80% test coverage** - Write tests for all new code

### Project Structure
```
Root: GitHub metadata only (README, CONTRIBUTING, CHANGELOG, STYLE_GUIDE, LICENSE, .gitignore)
src/: ALL source code and configuration
  - coming_attractions/: Python package
  - docker/: Docker configuration
  - scripts/: Utility scripts
  - tests/: Test suite
  - setup.py, requirements.txt, pytest.ini, Makefile
docs/: All non-standard documentation
.github/: GitHub-specific configs, workflows, templates
```

### Import Organization
```python
# 1. Standard library (alphabetical)
import sys
from pathlib import Path
from typing import List, Optional

# 2. Third-party packages (alphabetical)
import click
from pydantic import BaseModel

# 3. Local modules (alphabetical)
from coming_attractions.logger import Logger
from coming_attractions.models import Trailer
```

### Error Handling
- Use specific exception types, never bare `except:`
- Provide helpful error messages with context
- Always clean up resources (use context managers)
- Log errors with appropriate level (error/warning/debug)

### Logging
- Use centralized Logger class from `coming_attractions.logger`
- Color-coded prefixes: `[*]` info, `[+]` success, `[-]` error, `[!]` warning
- Include context in log messages
- Never log sensitive data (API keys, credentials)

### Testing
- Place all tests in `src/tests/`
- Use pytest with fixtures from `conftest.py`
- Mock external dependencies (HTTP calls, file I/O)
- Test both success and failure cases
- Use descriptive test names: `test_fetch_handles_missing_release_date`

### File Operations
- **Always use atomic operations** (temp file + rename)
- Validate paths before writing
- Use Path objects, not string concatenation
- Handle encoding explicitly (UTF-8)

### Configuration
- Use Pydantic models for validation
- Support environment variables AND CLI arguments
- Provide sensible defaults
- Document all configuration options

### CLI Commands
- Use Click framework
- Consistent option naming: `--option-name` (kebab-case)
- Provide help text for all options
- Support dry-run mode where applicable

### Docker
- Multi-stage builds for smaller images
- Non-root user in containers
- Health checks where appropriate
- Multi-architecture support (amd64, arm64)

## Common Patterns

### Logging Pattern
```python
logger = Logger(level=LogLevel.INFO)
logger.info("Starting process")
try:
    result = do_something()
    logger.success(f"Completed: {result}")
except ValueError as e:
    logger.error(f"Validation failed: {e}")
    return False
```

### Atomic File Write Pattern
```python
temp_file = target_file.with_suffix('.tmp')
try:
    temp_file.write_text(content)
    temp_file.rename(target_file)
except Exception as e:
    if temp_file.exists():
        temp_file.unlink()
    raise
```

### Pydantic Config Pattern
```python
class MyConfig(BaseModel):
    api_key: str = Field(..., min_length=32)
    max_items: int = Field(default=100, ge=1, le=1000)
    
    @field_validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric")
        return v
```

## What NOT to Do

- ❌ Don't put source code or config files in repo root
- ❌ Don't use print() - use Logger
- ❌ Don't hardcode paths - use Path objects and configuration
- ❌ Don't ignore errors - handle or propagate them
- ❌ Don't leave commented-out code
- ❌ Don't use mutable default arguments
- ❌ Don't mix tabs and spaces (use 4 spaces)
- ❌ Don't write functions longer than 50 lines
- ❌ Don't exceed 100 characters per line

## Markdown Documentation Standards

All markdown files must follow professional formatting standards:

### Required Practices

1. **Use real headers, not bold text**: Never use `**Header:**` as a simulated section header. Use proper `####` markdown headers instead.

2. **Add section descriptions**: Every header needs at least one sentence explaining what the section contains.

3. **Blank lines everywhere**: All headings, code blocks, lists, and tables MUST have blank lines above and below.

4. **No horizontal rules**: Never use `---` separators. Headers provide sufficient visual separation.

5. **No emoji in headers**: Keep section headers professional without decorative emoji.

6. **Use GitHub admonitions**: For callouts, use `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, etc.

### Examples

**CORRECT:**
```markdown
### Configuration Options

The following environment variables control behavior.

| Variable | Description |
...
```

**INCORRECT:**
```markdown
### Configuration Options
---
**Environment Variables:**
...
```

See STYLE_GUIDE.md for complete documentation standards.

## Git Commit Messages

Format:
```
type: Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars).
- Bullet points okay
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

## When Suggesting Changes

1. **Read existing code first** - Understand current patterns
2. **Follow existing style** - Match what's already there
3. **Test your suggestions** - Provide test cases
4. **Update documentation** - Keep docs in sync with code
5. **Consider backward compatibility** - Don't break existing functionality
6. **Update path references** - Remember src/ structure
7. **Think about edge cases** - Handle errors gracefully

## Repository Philosophy

- **GitHub-first**: Follow GitHub conventions and standards
- **Quality over speed**: Take time to do it right
- **No technical debt**: Refactor as you go
- **Test everything**: No untested code in production
- **Document everything**: Code is read more than written
- **Security first**: Validate inputs, sanitize outputs, protect secrets

## Helpful Resources

- PEP 8: https://pep8.org/
- Click Docs: https://click.palletsprojects.com/
- Pydantic Docs: https://docs.pydantic.dev/
- pytest Docs: https://docs.pytest.org/
- Project README: See root README.md
- Style Guide: See root STYLE_GUIDE.md
