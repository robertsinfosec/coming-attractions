# src/ Directory

This directory contains ALL source code and configuration for the Coming Attractions project.

## Structure

```
src/
├── coming_attractions/      # Main Python package
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point
│   ├── cli.py           # Click CLI commands
│   ├── logger.py        # Centralized logging
│   ├── models.py        # Data models and enums
│   ├── config.py        # Pydantic configuration
│   ├── utils.py         # Shared utilities
│   ├── tmdb_client.py   # TMDb API client
│   ├── youtube_downloader.py  # yt-dlp wrapper
│   ├── fetcher.py       # Trailer fetching logic
│   ├── pruner.py        # Retention policy
│   └── title_fixer.py   # NFO title updates
│
├── docker/              # Docker configuration
│   ├── Dockerfile       # Multi-stage build
│   ├── docker-compose.yml  # Example deployment
│   └── .dockerignore    # Docker ignore patterns
│
├── scripts/             # Utility scripts
│   ├── legacy_fetch.py  # Legacy compatibility wrapper
│   ├── legacy_prune.py  # Legacy compatibility wrapper
│   ├── legacy_title_fixer.py  # Legacy compatibility wrapper
│   ├── validate_migration.py  # Migration validator
│   ├── test_compatibility.py  # Compatibility tester
│   └── check_project.py  # Project completeness checker
│
├── tests/               # Test suite
│   ├── conftest.py      # Shared fixtures
│   ├── test_utils.py    # Utility tests
│   ├── test_title_fixer.py
│   ├── test_pruner.py
│   └── test_tmdb_client.py
│
├── setup.py             # Package setup configuration
├── requirements.txt     # Python dependencies
├── pytest.ini           # Pytest configuration
├── Makefile             # Build automation
└── .env.example         # Example environment variables
```

## Development Workflow

### Initial Setup

```bash
cd src/
pip install -e .          # Install in development mode
pip install -e ".[dev]"   # With dev dependencies
```

### Running Tests

```bash
cd src/
make test                 # Run all tests
make test-cov             # With coverage report
make lint                 # Run linter
make format               # Format code
```

### Building Docker

```bash
cd src/
make docker-build         # Build image
make docker-run           # Test run
```

### Running the Application

```bash
# From anywhere after install
coming-attractions --help

# Or directly from src/
python -m coming_attractions --help
```

## Running Utility Scripts

All utility scripts are now in `src/scripts/`:

```bash
# Check project completeness
python src/scripts/check_project.py

# Validate migration from old scripts
python src/scripts/validate_migration.py \
  --theatrical-dir /path/to/theatrical \
  --streaming-dir /path/to/streaming

# Test compatibility with old scripts
python src/scripts/test_compatibility.py

# Legacy compatibility wrappers
python src/scripts/legacy_fetch.py
python src/scripts/legacy_prune.py --prune --dry-run
python src/scripts/legacy_title_fixer.py /path/to/trailers
```

## Path References

All source code and configuration is under `src/`. When referencing paths in documentation or code:

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
