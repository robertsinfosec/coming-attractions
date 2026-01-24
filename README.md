# Coming Attractions

**Automated Jellyfin Upcoming Movie Trailer Management**

A professional Python application for fetching, managing, and maintaining upcoming movie trailers for Jellyfin media servers. Automatically downloads trailers from TMDb and YouTube, manages retention policies, and fixes metadata for proper Jellyfin display.

[![CI/CD](https://github.com/robertsinfosec/coming-attractions/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/robertsinfosec/coming-attractions/actions/workflows/ci-cd.yml)
[![tests](https://img.shields.io/github/actions/workflow/status/robertsinfosec/coming-attractions/ci-cd.yml?branch=main&label=tests&logo=githubactions&logoColor=white)](https://github.com/robertsinfosec/coming-attractions/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/robertsinfosec/coming-attractions/branch/main/graph/badge.svg?token=80%25)](https://codecov.io/gh/robertsinfosec/coming-attractions)
[![CodeQL](https://github.com/robertsinfosec/coming-attractions/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/robertsinfosec/coming-attractions/security/code-scanning)
[![Docker Build](https://github.com/robertsinfosec/coming-attractions/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/robertsinfosec/coming-attractions/pkgs/container/coming-attractions)
[![ghcr.io](https://img.shields.io/badge/ghcr.io-published-blue?logo=docker&logoColor=white)](https://github.com/robertsinfosec/coming-attractions/pkgs/container/coming-attractions)
[![python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://github.com/robertsinfosec/coming-attractions/blob/main/src/setup.py)
[![license](https://img.shields.io/github/license/robertsinfosec/coming-attractions?label=license&logo=opensourceinitiative&logoColor=white&color=MIT)](https://github.com/robertsinfosec/coming-attractions/blob/main/LICENSE)
[![last commit](https://img.shields.io/github/last-commit/robertsinfosec/coming-attractions?label=last%20commit&logo=git&logoColor=white&color=today)](https://github.com/robertsinfosec/coming-attractions/commits/main)
[![issues](https://img.shields.io/github/issues/robertsinfosec/coming-attractions?label=issues&logo=github&logoColor=white&color=0%20open)](https://github.com/robertsinfosec/coming-attractions/issues)
[![pull requests](https://img.shields.io/github/issues-pr/robertsinfosec/coming-attractions?label=pull%20requests&logo=github&logoColor=white&color=0%20open)](https://github.com/robertsinfosec/coming-attractions/pulls)
[![dependabot](https://img.shields.io/badge/dependabot-enabled-025E8C?logo=dependabot&logoColor=white)](https://github.com/robertsinfosec/coming-attractions/security/dependabot)

## Features

✨ **Dual Mode Operation**
- **Theatrical Mode**: Upcoming, now playing, and popular movies from TMDb feeds
- **Streaming Mode**: Discover movies and TV shows from specific streaming providers
- **Both Mode**: Run theatrical and streaming fetches together

🎬 **Smart Trailer Selection**
- Prioritizes official trailers over teasers
- One trailer per title (highest quality)
- Configurable video quality (up to 4K)
- Automatic video+audio merge via ffmpeg

🗄️ **Intelligent Management**
- Configurable retention policies (default: 2 years)
- Automatic cleanup of old trailers
- Tracks removed trailers to prevent re-downloading
- Atomic file operations for reliability

🏷️ **Jellyfin Integration**
- Automatic "Trailer - " prefix for proper display
- NFO metadata generation
- TV show detection with [TV] suffix
- Compatible with existing Jellyfin libraries

🐳 **Production Ready**
- Daemon mode with configurable intervals
- Comprehensive logging (console + file)
- Dry-run mode for testing
- Environment variable support

🌍 **Multi-Platform Support**
- Works seamlessly on AMD/Intel and ARM processors
- Native support for Raspberry Pi (all models)
- Compatible with macOS via Docker Desktop (Intel & Apple Silicon)
- Automatic architecture detection - no configuration needed

## Quick Start

### Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    container_name: coming-attractions
    restart: unless-stopped
    environment:
      - TZ=America/New_York
      - TMDB_API_KEY=${TMDB_API_KEY}  # Required
      - TMDB_REGION=US
      - RETENTION_YEARS=2
      - DAYS_AHEAD=180
      - DAYS_BACK=90
      - MAX_HEIGHT=1080
      - METADATA_WAIT_SECONDS=300  # Wait 5 min for Jellyfin metadata (default)
      - LOG_TIMESTAMPS=1
    volumes:
      - /path/to/trailers:/data/trailers
      - ./config:/config
    command: daemon --interval 12h
```

### Standalone CLI

```bash
# Install from src directory
pip install -e src/

# Fetch trailers
coming-attractions fetch \
  --api-key $TMDB_API_KEY \
  --mode theatrical \
  --out-dir /data/trailers/theatrical \
  --days-ahead 180

# Prune old trailers
coming-attractions prune \
  --retention-years 2 \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming

# Fix titles
coming-attractions fix-titles \
  --root-dir /data/trailers/theatrical

# Run daemon
coming-attractions daemon --interval 12h
```

## Commands

### `fetch` - Download Trailers

Fetch trailers from TMDb and YouTube.

```bash
coming-attractions fetch [OPTIONS]

Options:
  --api-key TEXT              TMDb API key (required) [env: TMDB_API_KEY]
  --mode [theatrical|streaming|both]  Fetch mode [env: MODE]
  --region TEXT               Region code (ISO 3166-1) [env: TMDB_REGION]
  --out-dir PATH              Output directory [env: OUT_DIR]
  --days-ahead INTEGER        Days ahead for upcoming [env: DAYS_AHEAD]
  --days-back INTEGER         Days back for now playing [env: DAYS_BACK]
  --max-pages INTEGER         Max pages per feed [env: MAX_PAGES]
  --max-height INTEGER        Max video height [env: MAX_HEIGHT]
  --dry-run                   Show what would happen [env: DRY_RUN]
  --debug                     Enable debug logging [env: DEBUG]
  --timestamps                Add timestamps to output [env: LOG_TIMESTAMPS]
  --log-file TEXT             Log to file [env: LOG_FILE]
```

**Examples:**

```bash
# Fetch theatrical trailers for US region
coming-attractions fetch \
  --api-key abc123 \
  --mode theatrical \
  --region US \
  --out-dir /data/trailers/theatrical

# Fetch streaming content (movies + TV)
MODE=streaming \
MEDIA_TYPES=movie,tv \
WATCH_PROVIDERS=8,9,337 \
coming-attractions fetch --api-key abc123

# Dry-run to preview
coming-attractions fetch --api-key abc123 --dry-run
```

### `prune` - Remove Old Trailers

Remove trailers older than retention period.

```bash
coming-attractions prune [OPTIONS]

Options:
  --retention-years INTEGER   Years to retain [env: RETENTION_YEARS]
  --theatrical-dir PATH       Theatrical directory [env: THEATRICAL_DIR]
  --streaming-dir PATH        Streaming directory [env: STREAMING_DIR]
  --removed-file PATH         Removed trailers file [env: REMOVED_FILE]
  --dry-run                   Show what would be removed [env: DRY_RUN]
  --force                     Non-interactive mode
  --debug                     Enable debug logging [env: DEBUG]
  --timestamps                Add timestamps [env: LOG_TIMESTAMPS]
  --log-file TEXT             Log to file [env: LOG_FILE]
```

**Examples:**

```bash
# Preview what would be removed (dry-run)
coming-attractions prune --retention-years 2 --dry-run

# Remove trailers older than 3 years
coming-attractions prune --retention-years 3

# Non-interactive (for cron)
coming-attractions prune --retention-years 2 --force
```

### `fix-titles` - Add Trailer Prefix

Add "Trailer - " prefix to titles in NFO files.

```bash
coming-attractions fix-titles [OPTIONS]

Options:
  --root-dir PATH             Root directory to scan [env: ROOT_DIR]
  --prefix TEXT               Prefix to add (default: "Trailer - ")
  --debug                     Enable debug logging [env: DEBUG]
  --timestamps                Add timestamps [env: LOG_TIMESTAMPS]
  --log-file TEXT             Log to file [env: LOG_FILE]
```

**Examples:**

```bash
# Fix theatrical titles
coming-attractions fix-titles --root-dir /data/trailers/theatrical

# Custom prefix
coming-attractions fix-titles --prefix "Coming Soon - "
```

### `daemon` - Continuous Operation

Run complete workflow on interval.

```bash
coming-attractions daemon [OPTIONS]

Options:
  --interval TEXT             Interval (e.g., 12h, 6h, 1d)
  --metadata-wait INTEGER     Wait for Jellyfin metadata [env: METADATA_WAIT_SECONDS]
  --retention-years INTEGER   Retention for pruning [env: RETENTION_YEARS]
  --api-key TEXT              TMDb API key [env: TMDB_API_KEY]
  --debug                     Enable debug logging [env: DEBUG]
  --timestamps                Add timestamps [env: LOG_TIMESTAMPS]
  --log-file TEXT             Log to file [env: LOG_FILE]
```

**Workflow:**
1. Prune old trailers (retention policy)
2. Fetch theatrical trailers
3. **Wait for Jellyfin metadata** (default: 5 min) - Allows Jellyfin to detect new files and generate NFO metadata
4. Fix theatrical titles (adds "Trailer - " prefix to NFO files)
5. Fetch streaming trailers
6. **Wait for Jellyfin metadata** (default: 5 min)
7. Fix streaming titles
8. Sleep for configured interval
9. Repeat

**Examples:**

```bash
# Run every 12 hours
coming-attractions daemon --interval 12h

# Run every 6 hours with custom metadata wait
coming-attractions daemon --interval 6h --metadata-wait 600

# Run daily
coming-attractions daemon --interval 1d
```

## Environment Variables

All CLI options can be set via environment variables:

| Variable                | Description                             | Default                            |
| ----------------------- | --------------------------------------- | ---------------------------------- |
| `TMDB_API_KEY`          | **Required.** TMDb API key              | -                                  |
| `MODE`                  | Fetch mode: theatrical, streaming, both | `both`                             |
| `TMDB_REGION`           | Region code (ISO 3166-1 alpha-2)        | `US`                               |
| `OUT_DIR`               | Output directory                        | `/data/trailers`                   |
| `DAYS_AHEAD`            | Days ahead for upcoming window          | `180`                              |
| `DAYS_BACK`             | Days back for now playing               | `90`                               |
| `MAX_PAGES`             | Max pages per feed                      | `5`                                |
| `MAX_HEIGHT`            | Max video height (480-4320)             | `1080`                             |
| `RETENTION_YEARS`       | Years to retain trailers                | `2`                                |
| `THEATRICAL_DIR`        | Theatrical trailers directory           | `./theatrical`                     |
| `STREAMING_DIR`         | Streaming trailers directory            | `./streaming`                      |
| `REMOVED_FILE`          | Removed trailers tracking file          | `./.trailer-removed.txt`           |
| `MEDIA_TYPES`           | Streaming media types (movie,tv)        | `movie,tv`                         |
| `WATCH_PROVIDERS`       | Streaming provider IDs                  | `8,9,337,384,15,350,531,386,37,43` |
| `WATCH_REGION`          | Streaming region                        | `US`                               |
| `DRY_RUN`               | Enable dry-run mode                     | `0`                                |
| `DEBUG`                 | Enable debug logging                    | `0`                                |
| `LOG_TIMESTAMPS`        | Add timestamps to logs                  | `0`                                |
| `LOG_FILE`              | Log file path                           | -                                  |
| `METADATA_WAIT_SECONDS` | Jellyfin metadata wait (daemon)         | `300`                              |

## Configuration

### TMDb API Key

Get your free API key from [TMDb](https://www.themoviedb.org/settings/api):

1. Create a TMDb account
2. Go to Settings → API
3. Request an API key (choose "Developer")
4. Copy the API Key (v3 auth)

### Streaming Providers

Default providers (major US platforms):
- Netflix (8)
- Prime Video (9)
- Disney+ (337)
- HBO Max (384)
- Hulu (15)
- Apple TV+ (350)
- Paramount+ (531)
- Peacock (386)
- Showtime (37)
- Starz (43)

Find provider IDs: `https://api.themoviedb.org/3/watch/providers/movie?api_key=YOUR_KEY`

### Jellyfin Integration

1. **Create trailer libraries:**
   ```
   /data/trailers/
   ├── theatrical/
   │   └── Movie Title (2026)/
   │       ├── Movie Title (2026).mp4
   │       └── movie.nfo
   └── streaming/
       └── Movie Title (2026)/
           ├── Movie Title (2026).mp4
           └── movie.nfo
   ```

2. **Add libraries in Jellyfin:**
   - Type: "Movies"
   - Path: `/data/trailers/theatrical`
   - Content type: "Movies"
   - Enable "Trailers" metadata provider

3. **Configure trailer display:**
   - Settings → Playback → "Play trailers before movies"
   - Choose "From trailers folder"

## Output Format

### Console Output

```
[*] Fetching upcoming movies...
[*]   Found 150 items
[*] Downloading: Dune Part Three (2026)
[*]   YouTube URL: https://youtube.com/watch?v=...
[+]   Downloaded: Dune Part Three (2026)
[*] Skipping: exists. Another Movie (2025)

[*] ────────────────────────────────────────────────────────────────
[*] Trailer Fetcher Summary
[*] ────────────────────────────────────────────────────────────────
[*] Mode: theatrical
[*] Region: US
[*] Window: 90 days back, 180 days ahead
[*] 
[+] Present/Downloaded: 150
[*] Skipped: 130
[*] 
[*] Skip reasons:
[*]   Out Of Window: 63
[*]   No Video Available: 45
[*]   Download Failed: 2
[+] Trailer fetching complete.
```

### Log Prefixes

- `[*]` - Informational (cyan)
- `[+]` - Success (green)
- `[-]` - Error (red)
- `[!]` - Warning (yellow)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/robertsinfosec/coming-attractions.git
cd coming-attractions

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest --cov=coming_attractions
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=coming_attractions --cov-report=html

# Specific test file
pytest tests/test_utils.py

# Verbose
pytest -v
```

### Building Docker Image

```bash
# Build locally
docker build -t coming-attractions:local .

# Build multi-arch
docker buildx build --platform linux/amd64,linux/arm64 -t coming-attractions:latest .

# Run locally
docker run --rm \
  -e TMDB_API_KEY=your_key \
  -v $(pwd)/data:/data/trailers \
  coming-attractions:local fetch --mode theatrical
```

## Troubleshooting

### Common Issues

**"TMDB_API_KEY is required"**
- Set environment variable: `export TMDB_API_KEY=your_key`
- Or pass via CLI: `--api-key your_key`

**"Directory is not writable"**
- Check permissions on output directory
- Docker: Ensure volume mount has correct permissions
- Try: `chmod 777 /data/trailers`

**"Download failed"**
- Check internet connectivity
- Verify yt-dlp is installed: `yt-dlp --version`
- Check YouTube URL is accessible
- Enable debug mode: `--debug`

**"No trailers found"**
- Check date window settings (--days-ahead, --days-back)
- Verify region code (--region US)
- Enable debug to see API responses: `--debug`
- Check TMDb API status

**Jellyfin not showing trailers**
- Run `fix-titles` command to add "Trailer - " prefix
- Check NFO files contain correct metadata
- Refresh library metadata in Jellyfin
- Ensure "Trailers" provider is enabled

### Debug Mode

Enable verbose logging:

```bash
coming-attractions fetch --api-key abc123 --debug
```

Log to file:

```bash
coming-attractions fetch --api-key abc123 --log-file /tmp/trailers.log
```

Add timestamps:

```bash
coming-attractions fetch --api-key abc123 --timestamps
```

### Dry-Run Mode

Preview changes without modifying anything:

```bash
# Preview fetch
coming-attractions fetch --api-key abc123 --dry-run

# Preview prune
coming-attractions prune --retention-years 2 --dry-run
```

## Architecture

```
coming_attractions/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point
├── cli.py                # Click CLI commands
├── config.py             # Pydantic configuration models
├── logger.py             # Centralized logging
├── models.py             # Data classes
├── utils.py              # Shared utilities
├── tmdb_client.py        # TMDb API client
├── youtube_downloader.py # yt-dlp wrapper
├── fetcher.py            # Trailer fetching logic
├── pruner.py             # Trailer pruning logic
└── title_fixer.py        # Title fixing logic
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [STYLE_GUIDE.md](STYLE_GUIDE.md) for complete guidelines.

**Quick Start:**
1. Fork the repository
2. Create a feature branch
3. Make your changes following the style guide
4. Add tests (minimum 80% coverage)
5. Submit a pull request

## Documentation

- **[README.md](README.md)** - This file (project overview)
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Code quality standards (PEP 8)
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/PRD.md](docs/PRD.md)** - Product Requirements Document
- **[docs/MIGRATION.md](docs/MIGRATION.md)** - Migration from old scripts
- **[docs/QUICKREF.md](docs/QUICKREF.md)** - Quick reference guide
- **[src/README.md](src/README.md)** - Source directory structure

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TMDb](https://www.themoviedb.org/) for movie metadata API
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloads
- [Jellyfin](https://jellyfin.org/) for media server platform

## Support

- 🐛 [Report bugs](https://github.com/robertsinfosec/coming-attractions/issues)
- 💡 [Request features](https://github.com/robertsinfosec/coming-attractions/issues)
- 📖 [Documentation](https://github.com/robertsinfosec/coming-attractions)
- 💬 [Discussions](https://github.com/robertsinfosec/coming-attractions/discussions)

---

![Alt](https://repobeats.axiom.co/api/embed/b8e996332fcb25fbecb1e9daeccee596a2128a8e.svg "Repobeats analytics image")
