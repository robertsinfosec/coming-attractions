# src/ Directory

This directory contains ALL source code and configuration for the Coming Attractions project.

For detailed architecture and design patterns, see **[Architecture Guide](../docs/dev/ARCHITECTURE.md)**.

## Quick Reference

```
src/
├── coming_attractions/      # Main Python package
├── docker/                  # Docker configuration
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── setup.py                 # Package configuration
├── requirements.txt         # Dependencies
├── pytest.ini               # Test configuration
└── Makefile                 # Build automation
```

## For Developers

- **[Setup Guide](../docs/dev/SETUP.md)** - Development environment setup
- **[Testing Guide](../docs/dev/TESTING.md)** - Writing and running tests
- **[Architecture Guide](../docs/dev/ARCHITECTURE.md)** - Complete project structure and design patterns
- **[Style Guide](../STYLE_GUIDE.md)** - Code quality standards

## Path References

All source code and configuration is under `src/`. When referencing paths:

- **Package imports**: `from coming_attractions.logger import Logger`
- **Setup**: `pip install -e src/`
- **Docker build**: `docker build -f src/docker/Dockerfile .`
- **Tests**: Run from `src/` directory

## Why This Structure?

Following GitHub-first best practices:
- **Root directory**: Only GitHub metadata (README, LICENSE, etc.)
- **src/ directory**: All source code and configuration
- **docs/ directory**: All documentation
- **.github/ directory**: GitHub-specific configs

This keeps the repository organized and makes it clear what's metadata vs. actual project code.
