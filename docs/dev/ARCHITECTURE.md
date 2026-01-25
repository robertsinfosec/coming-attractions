# Architecture Guide

> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Setup](SETUP.md) | [Testing](TESTING.md) | [Style Guide](../../STYLE_GUIDE.md)

Complete architectural overview of the Coming Attractions project.

## Table of Contents

- [Project Structure](#project-structure)
- [Module Overview](#module-overview)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Key Decisions](#key-decisions)
- [Extension Points](#extension-points)


## Project Structure

### Repository Layout

```
coming-attractions/
├── .devcontainer/           # VS Code Dev Container configuration
├── .github/                 # GitHub-specific files
│   ├── copilot-instructions.md
│   └── workflows/
│       └── ci-cd.yml        # CI/CD pipeline
├── docs/                    # User documentation
│   ├── dev/                 # Developer documentation
│   │   ├── SETUP.md
│   │   ├── TESTING.md
│   │   ├── ARCHITECTURE.md  # This file
│   │   └── CODECOV.md
│   ├── images/              # Screenshots
│   ├── DOCKER.md
│   ├── JELLYFIN_INTEGRATION.md
│   ├── USER_GUIDE.md
│   └── PRD.md               # Product Requirements
├── src/                     # ALL source code
│   ├── coming_attractions/  # Python package
│   ├── docker/              # Docker configuration
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Test suite
│   ├── setup.py
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Makefile
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── STYLE_GUIDE.md
```

### Why This Structure?

**Root level = GitHub metadata only**
- README, LICENSE, CONTRIBUTING, etc.
- Standard location for repo-wide documentation
- First thing visitors see

**src/ = ALL source code**
- Keeps root clean
- Separates code from documentation
- Allows for future multi-package projects
- Follows modern Python packaging best practices

**docs/ = Non-code documentation**
- User guides, integration docs, etc.
- Separate from code to avoid clutter
- dev/ subdirectory for developer-specific docs

**tests/ inside src/**
- Co-located with source code
- Makes relative imports simpler
- Natural discovery by pytest


## Module Overview

### Core Application (`src/coming_attractions/`)

```
coming_attractions/
├── __init__.py           # Package initialization, version
├── __main__.py           # Entry point (python -m coming_attractions)
├── cli.py                # Click CLI commands (fetch, prune, daemon, fix-titles)
├── config.py             # Pydantic configuration models
├── logger.py             # Centralized logging with color prefixes
├── models.py             # Data classes and enums
├── utils.py              # Shared utilities (path sanitization, etc.)
├── tmdb_client.py        # TMDb API client
├── youtube_downloader.py # yt-dlp wrapper
├── fetcher.py            # Trailer fetching orchestration
├── pruner.py             # Trailer retention and cleanup
└── title_fixer.py        # NFO title prefix management
```

### Module Responsibilities

#### `__init__.py`
- Package metadata (`__version__`)
- Public API exports

#### `__main__.py`
- Entry point for `python -m coming_attractions`
- Delegates to `cli.main()`

#### `cli.py`
- Click command definitions
- Argument parsing and validation
- Delegates to business logic modules

#### `config.py`
- Pydantic models for configuration
- Environment variable mapping
- Validation rules

#### `logger.py`
- Centralized logging
- Color-coded prefixes: `[*]` `[+]` `[-]` `[!]`
- Console and file output

#### `models.py`
- Data classes (Trailer, Movie, etc.)
- Enums (Mode, LogLevel, etc.)
- Immutable data structures

#### `utils.py`
- Shared utility functions
- Path sanitization
- File operations
- Date/time helpers

#### `tmdb_client.py`
- TMDb API client
- HTTP request handling
- Response parsing
- Error handling

#### `youtube_downloader.py`
- yt-dlp wrapper
- Video quality selection
- Download progress
- ffmpeg integration

#### `fetcher.py`
- Orchestrates trailer fetching
- Discovers movies from TMDb
- Downloads trailers via YouTube
- Generates NFO metadata
- Tracks removed trailers

#### `pruner.py`
- Implements retention policy
- Scans trailer directories
- Calculates trailer age
- Removes old trailers
- Updates removed tracker

#### `title_fixer.py`
- Parses NFO files
- Adds "Trailer - " prefix
- Atomic file updates


## Data Flow

### Fetch Command Flow

```
User runs: coming-attractions fetch --api-key KEY --mode theatrical

1. cli.py
   ├─> Parse arguments
   ├─> Validate API key
   └─> Call fetcher.fetch_trailers()

2. fetcher.py
   ├─> Initialize TMDbClient
   ├─> Discover movies (upcoming, now_playing, popular)
   │   └─> tmdb_client.py makes API requests
   ├─> For each movie:
   │   ├─> Check if already exists (skip if present)
   │   ├─> Check if previously removed (skip if removed)
   │   ├─> Search for trailer on YouTube
   │   ├─> Download via youtube_downloader.py
   │   │   └─> yt-dlp downloads video+audio, merges with ffmpeg
   │   ├─> Generate NFO metadata
   │   └─> Save to trailer directory
   └─> Return summary stats

3. logger.py
   └─> Log progress, successes, errors
```

### Prune Command Flow

```
User runs: coming-attractions prune --retention-years 2

1. cli.py
   ├─> Parse arguments
   └─> Call pruner.prune_trailers()

2. pruner.py
   ├─> Scan theatrical directory
   ├─> Scan streaming directory
   ├─> For each trailer folder:
   │   ├─> Parse year from folder name "Movie (2026)"
   │   ├─> Calculate age: current_year - release_year
   │   └─> If age > retention_years:
   │       ├─> Delete folder
   │       └─> Add to .trailer-removed.txt
   └─> Return pruned count

3. logger.py
   └─> Log removals and summary
```

### Daemon Command Flow

```
User runs: coming-attractions daemon --interval 12h

1. cli.py
   └─> Call daemon loop

2. daemon.py (in cli.py)
   └─> Loop forever:
       ├─> Prune old trailers
       ├─> Fetch theatrical trailers
       ├─> Wait for Jellyfin metadata (METADATA_WAIT_SECONDS)
       ├─> Fix theatrical titles
       ├─> Fetch streaming trailers
       ├─> Wait for Jellyfin metadata
       ├─> Fix streaming titles
       ├─> Sleep for interval
       └─> Repeat
```

### Fix-Titles Command Flow

```
User runs: coming-attractions fix-titles --root-dir /data/trailers

1. cli.py
   └─> Call title_fixer.fix_titles()

2. title_fixer.py
   ├─> Recursively find all movie.nfo files
   ├─> For each NFO:
   │   ├─> Parse XML
   │   ├─> Check if title already has prefix
   │   ├─> If not, add "Trailer - " prefix
   │   ├─> Write to temp file
   │   └─> Atomic rename (temp → original)
   └─> Return count of files modified

3. logger.py
   └─> Log progress and summary
```


## Design Patterns

### Dependency Injection

Instead of hard-coding dependencies, pass them as arguments:

```python
# fetcher.py
def fetch_trailers(
    api_key: str,
    out_dir: Path,
    tmdb_client: TMDbClient = None,  # Injectable
    youtube_downloader: YouTubeDownloader = None,  # Injectable
):
    if tmdb_client is None:
        tmdb_client = TMDbClient(api_key)
    if youtube_downloader is None:
        youtube_downloader = YouTubeDownloader()
    # ...
```

#### Benefits

- Easy to test (inject mocks)
- Flexible (swap implementations)
- Clear dependencies

### Pydantic for Configuration

```python
# config.py
from pydantic import BaseModel, Field

class FetchConfig(BaseModel):
    api_key: str = Field(..., min_length=32)
    mode: Mode = Mode.BOTH
    days_ahead: int = Field(default=180, ge=1, le=3650)
    
    @field_validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric")
        return v
```

**Benefits:**
- Automatic validation
- Type safety
- Environment variable mapping
- Clear error messages

### Atomic File Operations

```python
# title_fixer.py
def update_nfo(nfo_path: Path, new_content: str):
    temp_file = nfo_path.with_suffix('.tmp')
    try:
        temp_file.write_text(new_content, encoding='utf-8')
        temp_file.rename(nfo_path)  # Atomic on POSIX
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise
```

**Benefits:**
- No partial writes
- Failure safe
- Concurrent access safe

### Separation of Concerns

Each module has a single responsibility:

- **tmdb_client.py** - TMDb API only
- **youtube_downloader.py** - YouTube downloads only
- **fetcher.py** - Orchestration (uses both above)
- **cli.py** - CLI interface only
- **pruner.py** - Retention policy only

**Benefits:**
- Easy to understand
- Easy to test
- Easy to modify
- Reusable components

### Logging Strategy

Centralized logger with consistent prefixes:

```python
# logger.py
class Logger:
    def info(self, msg: str):
        print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")
    
    def success(self, msg: str):
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")
    
    def error(self, msg: str):
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {msg}")
    
    def warning(self, msg: str):
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")
```

**Benefits:**
- Consistent output
- Easy to grep logs
- Visual distinction
- Centralized control


## Key Decisions

### Why Python 3.11+?

- **Type hints improvements** - Better generics, `Self` type
- **Performance** - 10-25% faster than 3.10
- **Error messages** - Much clearer tracebacks
- **Pattern matching** - For complex logic

### Why Click for CLI?

- **Automatic help generation** - `--help` for free
- **Type conversion** - Automatic int/path conversion
- **Environment variable support** - Built-in
- **Testing support** - `CliRunner` for tests
- **Composability** - Easy to add commands

### Why Pydantic for Config?

- **Validation** - Automatic input validation
- **Type safety** - Runtime type checking
- **Environment vars** - Automatic mapping
- **Error messages** - Clear validation errors
- **Serialization** - JSON/dict conversion built-in

### Why NFO Files?

- **Jellyfin/Emby/Kodi standard** - Expected format
- **Human-readable** - XML, easy to debug
- **Self-contained** - Metadata with video
- **Portable** - Works across media servers

### Why Atomic Operations?

- **Reliability** - No partial writes
- **Concurrency** - Safe with multiple processes
- **Recovery** - Failed ops don't corrupt files
- **Production-ready** - Enterprise-grade reliability

### Why src/ Directory?

- **Clean root** - GitHub metadata only
- **Packaging** - Modern Python packaging
- **Scalability** - Room for multiple packages
- **Clarity** - Clear separation of concerns

### Why Removed Tracker?

**Problem:** After pruning old trailers, next fetch would re-download them.

**Solution:** `.trailer-removed.txt` tracks removed trailers.

```
Movie Title (2020)
Another Movie (2019)
```

**Benefits:**
- Prevents re-downloads
- Persistent across restarts
- Simple text format
- Git-ignorable


## Extension Points

### Adding New Commands

1. **Define command in cli.py:**
   ```python
   @cli.command()
   @click.option('--new-option', help='Description')
   def new_command(new_option: str):
       """New command description."""
       # Implementation
   ```

2. **Add business logic module:**
   ```python
   # src/coming_attractions/new_module.py
   def do_new_thing(option: str):
       # Logic here
   ```

3. **Add tests:**
   ```python
   # src/tests/test_new_module.py
   def test_new_thing():
       # Tests here
   ```

### Adding New Streaming Providers

1. **Update provider list in config.py:**
   ```python
   DEFAULT_WATCH_PROVIDERS = [8, 9, 337, 384, 15, 350, 531, 386, 37, 43, 999]  # Add 999
   ```

2. **Find TMDb provider ID:**
   ```bash
   curl "https://api.themoviedb.org/3/watch/providers/movie?api_key=KEY"
   ```

3. **Update documentation** (USER_GUIDE.md, README.md)

### Adding New Fetch Modes

1. **Add to Mode enum (models.py):**
   ```python
   class Mode(str, Enum):
       THEATRICAL = "theatrical"
       STREAMING = "streaming"
       BOTH = "both"
       NEW_MODE = "new_mode"  # New
   ```

2. **Implement in fetcher.py:**
   ```python
   if mode == Mode.NEW_MODE:
       # New fetch logic
   ```

3. **Add tests**

### Adding New NFO Fields

1. **Update NFO template in fetcher.py:**
   ```python
   nfo_content = f"""<?xml version="1.0" encoding="UTF-8"?>
   <movie>
       <title>{title}</title>
       <year>{year}</year>
       <new_field>{new_data}</new_field>
   </movie>
   """
   ```

2. **Update title_fixer.py if needed** (preserve new field)

### Supporting New Media Servers

Currently supports Jellyfin/Emby/Plex via NFO files. To add new server:

1. **Research metadata format** (NFO, JSON, database?)
2. **Create new metadata module** (e.g., `kodi_metadata.py`)
3. **Add option to select format** (env var or CLI flag)
4. **Generate appropriate metadata**

### Adding Webhooks/Notifications

**Idea:** Notify when new trailers are added.

1. **Create notification module:**
   ```python
   # src/coming_attractions/notifier.py
   def send_notification(message: str, webhook_url: str):
       requests.post(webhook_url, json={"text": message})
   ```

2. **Add config option:**
   ```python
   WEBHOOK_URL = os.getenv("WEBHOOK_URL")
   ```

3. **Call in fetcher.py after downloads:**
   ```python
   if new_trailers and WEBHOOK_URL:
       notifier.send_notification(f"Downloaded {len(new_trailers)} trailers", WEBHOOK_URL)
   ```


## Code Organization Best Practices

### Imports

Always organize imports:

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

### Functions

Keep functions focused and small:

```python
# Good: Single responsibility
def sanitize_folder_name(name: str) -> str:
    """Remove invalid filesystem characters from name."""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

# Good: Clear purpose
def parse_year_from_folder(folder_name: str) -> Optional[int]:
    """Extract year from folder name like 'Movie (2026)'."""
    match = re.search(r'\((\d{4})\)', folder_name)
    return int(match.group(1)) if match else None
```

### Error Handling

Be specific and informative:

```python
# Good
try:
    data = fetch_from_api(movie_id)
except requests.HTTPError as e:
    logger.error(f"API request failed for movie {movie_id}: {e}")
    return None
except requests.Timeout:
    logger.warning(f"API timeout for movie {movie_id}, retrying...")
    return retry_fetch(movie_id)
```

### Type Hints

Use type hints everywhere:

```python
from typing import List, Optional, Dict
from pathlib import Path

def fetch_trailers(
    api_key: str,
    mode: Mode,
    out_dir: Path,
    days_ahead: int = 180,
) -> Dict[str, int]:
    """Fetch trailers and return statistics.
    
    Args:
        api_key: TMDb API key
        mode: Fetch mode (theatrical, streaming, both)
        out_dir: Output directory for trailers
        days_ahead: Days ahead to fetch
        
    Returns:
        Dictionary with download statistics
    """
    # Implementation
```


## Further Reading

- [Setup Guide](SETUP.md) - Development environment setup
- [Testing Guide](TESTING.md) - Writing and running tests
- [Style Guide](../../STYLE_GUIDE.md) - Code quality standards
- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute
- [PRD](../PRD.md) - Product requirements


> **Navigation:** [Home](../../README.md) | [Contributing](../../CONTRIBUTING.md) | [Setup](SETUP.md) | [Testing](TESTING.md) | [Style Guide](../../STYLE_GUIDE.md)
