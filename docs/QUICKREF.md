# Quick Reference Guide

Quick reference for common tasks with Coming Attractions.

## Installation

```bash
# Clone repository
git clone https://github.com/robertsinfosec/coming-attractions.git
cd coming-attractions

# Install
pip install -e .

# Verify
coming-attractions --version
```

## Common Commands

### Fetch Trailers

```bash
# Fetch theatrical trailers
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode theatrical \
  --out-dir /data/trailers/theatrical

# Fetch streaming trailers
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode streaming \
  --out-dir /data/trailers/streaming

# Fetch both types
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode both \
  --out-dir /data/trailers/upcoming

# Dry run (simulate without downloading)
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode theatrical \
  --dry-run
```

### Prune Old Trailers

```bash
# Prune trailers older than 2 years
coming-attractions prune \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming \
  --retention-years 2 \
  --force

# Dry run (see what would be deleted)
coming-attractions prune \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming \
  --retention-years 2 \
  --dry-run
```

### Fix NFO Titles

```bash
# Add "Trailer - " prefix to titles
coming-attractions fix-titles \
  --root-dir /data/trailers \
  --prefix "Trailer - "

# Custom prefix
coming-attractions fix-titles \
  --root-dir /data/trailers \
  --prefix "Preview: "
```

### Daemon Mode

```bash
# Run daemon with default 12h interval
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 12h

# Custom metadata wait time (default: 300s / 5min)
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 12h \
  --metadata-wait 600

# Custom retention period
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 6h \
  --retention-years 3
```

## Environment Variables

Instead of command-line options, set environment variables:

```bash
# Fetch settings
export TMDB_API_KEY=your_api_key_here
export MODE=theatrical
export OUT_DIR=/data/trailers/theatrical
export DAYS_AHEAD=365
export DAYS_BACK=90

# Prune settings
export RETENTION_YEARS=2
export THEATRICAL_DIR=/data/trailers/theatrical
export STREAMING_DIR=/data/trailers/streaming

# Daemon settings
export METADATA_WAIT_SECONDS=300  # Wait 5 minutes for Jellyfin metadata (default)
export LOG_TIMESTAMPS=1
export DEBUG=0

# Run commands
coming-attractions fetch
coming-attractions prune --force
coming-attractions fix-titles
```

## Docker

### Quick Start

```bash
# Build image
docker build -t coming-attractions:latest .

# Run fetch
docker run --rm \
  -v /path/to/data:/data \
  -e TMDB_API_KEY=YOUR_KEY \
  coming-attractions:latest fetch \
  --mode theatrical \
  --out-dir /data/trailers

# Run daemon
docker run -d \
  --name coming-attractions \
  -v /path/to/data:/data \
  -e TMDB_API_KEY=YOUR_KEY \
  coming-attractions:latest daemon \
  --mode theatrical \
  --out-dir /data/trailers \
  --fetch-interval 12h
```

### Docker Compose

```yaml
version: '3.8'

services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    container_name: coming-attractions
    restart: unless-stopped
    volumes:
      - /path/to/trailers:/data/trailers
      - ./config:/config
    environment:
      - TZ=America/New_York
      - TMDB_API_KEY=your_api_key_here
      - TMDB_REGION=US
      - RETENTION_YEARS=2
      - DAYS_AHEAD=365
      - DAYS_BACK=180
      - MAX_HEIGHT=1080
      - METADATA_WAIT_SECONDS=300  # Wait 5 min for Jellyfin metadata
      - LOG_TIMESTAMPS=1
    command: daemon --interval 12h
```

## Cron Examples

```bash
# Fetch theatrical trailers twice daily at 6am and 6pm
0 6,18 * * * /path/to/venv/bin/coming-attractions fetch --api-key YOUR_KEY --mode theatrical --out-dir /data/theatrical

# Fetch streaming trailers daily at 8am
0 8 * * * /path/to/venv/bin/coming-attractions fetch --api-key YOUR_KEY --mode streaming --out-dir /data/streaming

# Prune old trailers daily at 2am
0 2 * * * /path/to/venv/bin/coming-attractions prune --theatrical-dir /data/theatrical --streaming-dir /data/streaming --retention-years 2 --force

# Fix titles daily at 3am
0 3 * * * /path/to/venv/bin/coming-attractions fix-titles --root-dir /data/trailers
```

## Logging

```bash
# Enable debug logging
coming-attractions fetch --debug

# Log to file
coming-attractions fetch --log-file /var/log/coming-attractions.log

# Add timestamps
coming-attractions fetch --timestamps

# Combine options
coming-attractions fetch \
  --debug \
  --timestamps \
  --log-file /var/log/coming-attractions.log
```

## Configuration File

Create `.env` file in project root:

```env
# Required
TMDB_API_KEY=your_api_key_here

# Fetch settings
MODE=theatrical
OUT_DIR=/data/trailers/theatrical
DAYS_AHEAD=365
DAYS_BACK=90
MAX_PAGES=10
MAX_HEIGHT=1080

# Prune settings
RETENTION_YEARS=2
THEATRICAL_DIR=/data/trailers/theatrical
STREAMING_DIR=/data/trailers/streaming
REMOVED_FILE=./.trailer-removed.txt

# Title fixer settings
ROOT_DIR=/data/trailers
PREFIX=Trailer - 

# Logging
DEBUG=0
LOG_TIMESTAMPS=0
LOG_FILE=/var/log/coming-attractions.log

# Daemon intervals
FETCH_INTERVAL=12h
PRUNE_INTERVAL=1d
FIX_INTERVAL=1d
```

Then run without arguments:

```bash
coming-attractions fetch
coming-attractions prune --force
coming-attractions fix-titles
coming-attractions daemon
```

## Troubleshooting

### Command not found

```bash
# Check installation
pip list | grep coming-attractions

# Reinstall
pip install -e .

# Check PATH
which coming-attractions
```

### Import errors

```bash
# Verify Python version (requires 3.11+)
python --version

# Check dependencies
pip install -e .
```

### API errors

```bash
# Test API key
curl "https://api.themoviedb.org/3/movie/550?api_key=YOUR_KEY"

# Check rate limiting
coming-attractions fetch --debug
```

### Permission errors

```bash
# Check directory permissions
ls -la /data/trailers/

# Fix permissions
chmod -R u+rw /data/trailers/
```

### Video download errors

```bash
# Check ffmpeg installation
ffmpeg -version

# Update yt-dlp
pip install --upgrade yt-dlp

# Test download manually
yt-dlp --format 'bv*[height<=1080]+ba/b' 'https://youtube.com/watch?v=VIDEO_ID'
```

## Getting Help

```bash
# Main help
coming-attractions --help

# Command-specific help
coming-attractions fetch --help
coming-attractions prune --help
coming-attractions fix-titles --help
coming-attractions daemon --help

# Version
coming-attractions --version
```

## Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Fetch aliases
alias ft-fetch-theatrical='coming-attractions fetch --mode theatrical'
alias ft-fetch-streaming='coming-attractions fetch --mode streaming'
alias ft-fetch-both='coming-attractions fetch --mode both'

# Dry run aliases
alias ft-dry-fetch='coming-attractions fetch --dry-run'
alias ft-dry-prune='coming-attractions prune --dry-run'

# Maintenance aliases
alias ft-prune='coming-attractions prune --force'
alias ft-fix='coming-attractions fix-titles'

# Docker aliases
alias ft-docker='docker run --rm -v /data:/data -e TMDB_API_KEY=$TMDB_API_KEY coming-attractions:latest'
```

## Migration from Old Scripts

```bash
# Old: python trailer-fetcher.py
# New: coming-attractions fetch

# Old: ./trailer-pruner.sh --prune --force
# New: coming-attractions prune --force

# Old: ./trailer-title-fixer.sh /data/trailers
# New: coming-attractions fix-titles --root-dir /data/trailers

# Use legacy wrappers for gradual migration
python legacy_fetch.py
python legacy_prune.py --prune --dry-run
python legacy_title_fixer.py /data/trailers
```
