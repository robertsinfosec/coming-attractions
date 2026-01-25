# User Guide

> **Navigation:** [Home](../README.md) | [Docker Guide](DOCKER.md) | [Jellyfin Integration](JELLYFIN_INTEGRATION.md) | [Contributing](../CONTRIBUTING.md)

Complete user guide for Coming Attractions - automated movie trailer management.

## Table of Contents

- [Installation](#installation)
- [Commands](#commands)
  - [fetch - Download Trailers](#fetch---download-trailers)
  - [prune - Remove Old Trailers](#prune---remove-old-trailers)
  - [fix-titles - Add Trailer Prefix](#fix-titles---add-trailer-prefix)
  - [daemon - Continuous Operation](#daemon---continuous-operation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration File (.env)](#configuration-file-env)
  - [TMDb API Key](#tmdb-api-key)
  - [Streaming Providers](#streaming-providers)
- [Usage Patterns](#usage-patterns)
  - [One-Time Fetch](#one-time-fetch)
  - [Scheduled Automation (Cron)](#scheduled-automation-cron)
  - [Daemon Mode](#daemon-mode-1)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)


## Installation

### Option 1: Install from Source

```bash
# Clone repository
git clone https://github.com/robertsinfosec/coming-attractions.git
cd coming-attractions

# Install package
cd src/
pip install -e .

# Verify installation
coming-attractions --version
coming-attractions --help
```

### Option 2: Docker

See the [Docker Guide](DOCKER.md) for complete Docker and Docker Compose instructions.

## Commands

### `fetch` - Download Trailers

Fetch upcoming movie and TV show trailers from TMDb and YouTube.

#### Syntax

Command line syntax:

```bash
coming-attractions fetch [OPTIONS]
```

#### Options

| Option         | Type    | Description                                                   | Environment Variable |
| -------------- | ------- | ------------------------------------------------------------- | -------------------- |
| `--api-key`    | TEXT    | **Required.** TMDb API key                                    | `TMDB_API_KEY`       |
| `--mode`       | CHOICE  | Fetch mode: `theatrical`, `streaming`, or `both`              | `MODE`               |
| `--region`     | TEXT    | Region code (ISO 3166-1 alpha-2, e.g., `US`, `GB`)            | `TMDB_REGION`        |
| `--out-dir`    | PATH    | Output directory for trailers                                 | `OUT_DIR`            |
| `--days-ahead` | INTEGER | Days ahead for upcoming releases window                       | `DAYS_AHEAD`         |
| `--days-back`  | INTEGER | Days back for now playing/recent releases                     | `DAYS_BACK`          |
| `--max-pages`  | INTEGER | Maximum pages per TMDb feed                                   | `MAX_PAGES`          |
| `--max-height` | INTEGER | Maximum video height (480, 720, 1080, 2160, 4320)             | `MAX_HEIGHT`         |
| `--dry-run`    | FLAG    | Preview what would be downloaded without actually downloading | `DRY_RUN`            |
| `--debug`      | FLAG    | Enable debug logging                                          | `DEBUG`              |
| `--timestamps` | FLAG    | Add timestamps to log output                                  | `LOG_TIMESTAMPS`     |
| `--log-file`   | PATH    | Write logs to file                                            | `LOG_FILE`           |

#### Examples

Common usage examples:

**Fetch theatrical trailers for the US:**

```bash
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode theatrical \
  --region US \
  --out-dir /data/trailers/theatrical \
  --days-ahead 180 \
  --days-back 90
```

**Fetch streaming content (movies and TV shows):**

```bash
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode streaming \
  --out-dir /data/trailers/streaming
```

**Fetch both theatrical and streaming:**

```bash
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode both \
  --out-dir /data/trailers
```

**Preview what would be downloaded (dry-run):**

```bash
coming-attractions fetch \
  --api-key YOUR_API_KEY \
  --mode theatrical \
  --dry-run
```

**Using environment variables:**

```bash
export TMDB_API_KEY=your_api_key_here
export MODE=theatrical
export OUT_DIR=/data/trailers/theatrical
export DAYS_AHEAD=365
export DAYS_BACK=180

coming-attractions fetch
```

#### Output Structure

How trailers are organized on disk:

```
/data/trailers/
├── theatrical/
│   ├── Dune Part Three (2026)/
│   │   ├── Dune Part Three (2026).mp4
│   │   └── movie.nfo
│   └── Another Movie (2025)/
│       ├── Another Movie (2025).mp4
│       └── movie.nfo
└── streaming/
    ├── Show Name (2026) [TV]/
    │   ├── Show Name (2026) [TV].mp4
    │   └── movie.nfo
    └── Streaming Movie (2026)/
        ├── Streaming Movie (2026).mp4
        └── movie.nfo
```

### `prune` - Remove Old Trailers

Remove trailers older than the specified retention period and track removed items to prevent re-downloading.

#### Syntax

Command line syntax:

```bash
coming-attractions prune [OPTIONS]
```

#### Options

| Option              | Type    | Description                           | Environment Variable |
| ------------------- | ------- | ------------------------------------- | -------------------- |
| `--retention-years` | INTEGER | Years to retain trailers (default: 2) | `RETENTION_YEARS`    |
| `--theatrical-dir`  | PATH    | Theatrical trailers directory         | `THEATRICAL_DIR`     |
| `--streaming-dir`   | PATH    | Streaming trailers directory          | `STREAMING_DIR`      |
| `--removed-file`    | PATH    | Tracking file for removed trailers    | `REMOVED_FILE`       |
| `--dry-run`         | FLAG    | Preview what would be removed         | `DRY_RUN`            |
| `--force`           | FLAG    | Non-interactive mode (auto-confirm)   | -                    |
| `--debug`           | FLAG    | Enable debug logging                  | `DEBUG`              |
| `--timestamps`      | FLAG    | Add timestamps to log output          | `LOG_TIMESTAMPS`     |
| `--log-file`        | PATH    | Write logs to file                    | `LOG_FILE`           |

#### Examples

Common usage examples:

**Preview what would be removed:**

```bash
coming-attractions prune \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming \
  --retention-years 2 \
  --dry-run
```

**Remove trailers older than 2 years:**

```bash
coming-attractions prune \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming \
  --retention-years 2 \
  --force
```

**Custom retention period (3 years):**

```bash
coming-attractions prune \
  --retention-years 3 \
  --force
```

#### How It Works

Pruning process steps:

1. Scans directories for trailer folders
2. Parses release year from folder name (e.g., "Movie Title (2023)")
3. Calculates age: `current_year - release_year`
4. If age > retention period, marks for deletion
5. Removes folder and updates `.trailer-removed.txt`
6. Prevents re-downloading by checking removed list on next fetch

### `fix-titles` - Add Trailer Prefix

Adds "Trailer - " prefix to NFO file titles to distinguish trailers from actual movies in media servers.

#### Syntax

Command line syntax:

```bash
coming-attractions fix-titles [OPTIONS]
```

#### Options

| Option         | Type | Description                           | Environment Variable |
| -------------- | ---- | ------------------------------------- | -------------------- |
| `--root-dir`   | PATH | Root directory to scan for NFO files  | `ROOT_DIR`           |
| `--prefix`     | TEXT | Prefix to add (default: "Trailer - ") | `PREFIX`             |
| `--debug`      | FLAG | Enable debug logging                  | `DEBUG`              |
| `--timestamps` | FLAG | Add timestamps to log output          | `LOG_TIMESTAMPS`     |
| `--log-file`   | PATH | Write logs to file                    | `LOG_FILE`           |

#### Examples

Common usage examples:

**Add "Trailer - " prefix to theatrical titles:**

```bash
coming-attractions fix-titles \
  --root-dir /data/trailers/theatrical
```

**Custom prefix:**

```bash
coming-attractions fix-titles \
  --root-dir /data/trailers/theatrical \
  --prefix "Coming Soon - "
```

#### Why This Matters

Importance of title prefixes:

Without prefixes, when you search for "Super Great Movie" in Jellyfin:
- You see: `Super Great Movie` (the actual movie)
- You see: `Super Great Movie` (the trailer) ← **Can't tell them apart!**

With prefixes:
- You see: `Super Great Movie` (the actual movie)
- You see: `Trailer - Super Great Movie` (clearly the trailer) ✅

### `daemon` - Continuous Operation

Run the complete trailer management workflow on a schedule.

#### Syntax

Command line syntax:

```bash
coming-attractions daemon [OPTIONS]
```

#### Options

| Option              | Type    | Description                                          | Environment Variable    |
| ------------------- | ------- | ---------------------------------------------------- | ----------------------- |
| `--interval`        | TEXT    | Interval between runs (e.g., `12h`, `6h`, `1d`)      | `DAEMON_INTERVAL`       |
| `--metadata-wait`   | INTEGER | Seconds to wait for Jellyfin metadata (default: 300) | `METADATA_WAIT_SECONDS` |
| `--retention-years` | INTEGER | Retention for pruning (default: 2)                   | `RETENTION_YEARS`       |
| `--api-key`         | TEXT    | **Required.** TMDb API key                           | `TMDB_API_KEY`          |
| `--debug`           | FLAG    | Enable debug logging                                 | `DEBUG`                 |
| `--timestamps`      | FLAG    | Add timestamps to log output                         | `LOG_TIMESTAMPS`        |
| `--log-file`        | PATH    | Write logs to file                                   | `LOG_FILE`              |

#### Workflow

Each daemon cycle performs these steps:

1. **Prune** old trailers (retention policy)
2. **Fetch** theatrical trailers
3. **Wait** for Jellyfin metadata (default: 5 minutes)
4. **Fix** theatrical titles (add "Trailer - " prefix)
5. **Fetch** streaming trailers
6. **Wait** for Jellyfin metadata
7. **Fix** streaming titles
8. **Sleep** for configured interval
9. **Repeat**

#### Examples

**Run every 12 hours:**

```bash
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 12h
```

**Custom metadata wait time:**

```bash
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 6h \
  --metadata-wait 600  # 10 minutes
```

**With logging:**

```bash
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 12h \
  --timestamps \
  --log-file /var/log/coming-attractions.log
```


## Configuration

### Environment Variables

All CLI options can be set via environment variables. This is especially useful for Docker deployments.

| Variable                | Description                                   | Default                            |
| ----------------------- | --------------------------------------------- | ---------------------------------- |
| `TMDB_API_KEY`          | **Required.** TMDb API key                    | -                                  |
| `MODE`                  | Fetch mode: `theatrical`, `streaming`, `both` | `both`                             |
| `TMDB_REGION`           | Region code (ISO 3166-1 alpha-2)              | `US`                               |
| `OUT_DIR`               | Output directory                              | `/data/trailers`                   |
| `DAYS_AHEAD`            | Days ahead for upcoming window                | `180`                              |
| `DAYS_BACK`             | Days back for now playing                     | `90`                               |
| `MAX_PAGES`             | Max pages per feed                            | `5`                                |
| `MAX_HEIGHT`            | Max video height (480-4320)                   | `1080`                             |
| `RETENTION_YEARS`       | Years to retain trailers                      | `2`                                |
| `THEATRICAL_DIR`        | Theatrical trailers directory                 | `./theatrical`                     |
| `STREAMING_DIR`         | Streaming trailers directory                  | `./streaming`                      |
| `REMOVED_FILE`          | Removed trailers tracking file                | `./.trailer-removed.txt`           |
| `MEDIA_TYPES`           | Streaming media types (`movie`, `tv`)         | `movie,tv`                         |
| `WATCH_PROVIDERS`       | Streaming provider IDs (comma-separated)      | `8,9,337,384,15,350,531,386,37,43` |
| `WATCH_REGION`          | Streaming region                              | `US`                               |
| `DRY_RUN`               | Enable dry-run mode (`0` or `1`)              | `0`                                |
| `DEBUG`                 | Enable debug logging (`0` or `1`)             | `0`                                |
| `LOG_TIMESTAMPS`        | Add timestamps to logs (`0` or `1`)           | `0`                                |
| `LOG_FILE`              | Log file path                                 | -                                  |
| `METADATA_WAIT_SECONDS` | Jellyfin metadata wait (daemon)               | `300`                              |

### Configuration File (.env)

Create a `.env` file in your project directory:

```env
# Required
TMDB_API_KEY=your_api_key_here

# Fetch settings
MODE=both
OUT_DIR=/data/trailers
DAYS_AHEAD=180
DAYS_BACK=90
MAX_PAGES=5
MAX_HEIGHT=1080

# Prune settings
RETENTION_YEARS=2
THEATRICAL_DIR=/data/trailers/theatrical
STREAMING_DIR=/data/trailers/streaming
REMOVED_FILE=/data/trailers/.trailer-removed.txt

# Title fixer settings
ROOT_DIR=/data/trailers
PREFIX=Trailer - 

# Daemon settings
DAEMON_INTERVAL=12h
METADATA_WAIT_SECONDS=300

# Logging
DEBUG=0
LOG_TIMESTAMPS=1
LOG_FILE=/var/log/coming-attractions.log
```

Then run commands without arguments:

```bash
coming-attractions fetch
coming-attractions prune --force
coming-attractions fix-titles
coming-attractions daemon
```

### TMDb API Key

How to obtain a free TMDb API key:

Get your free API key from [The Movie Database (TMDb)](https://www.themoviedb.org/settings/api):

1. Create a TMDb account at https://www.themoviedb.org/signup
2. Go to **Settings** → **API**
3. Click **Create` or **Request an API Key**
4. Choose **Developer** option
5. Fill out the form (use `Personal` or `Educational` for hobby projects)
6. Copy the **API Key (v3 auth)** value
7. Set as environment variable: `export TMDB_API_KEY=your_key_here`

### Streaming Providers

Default streaming provider configuration:

| Provider           | TMDb ID |
| ------------------ | ------- |
| Netflix            | 8       |
| Amazon Prime Video | 9       |
| Disney+            | 337     |
| HBO Max            | 384     |
| Hulu               | 15      |
| Apple TV+          | 350     |
| Paramount+         | 531     |
| Peacock            | 386     |
| Showtime           | 37      |
| Starz              | 43      |

#### Finding Provider IDs

How to find provider IDs for other regions:

```bash
# Get movie providers
curl "https://api.themoviedb.org/3/watch/providers/movie?api_key=YOUR_KEY"

# Get TV providers
curl "https://api.themoviedb.org/3/watch/providers/tv?api_key=YOUR_KEY"
```

Then set `WATCH_PROVIDERS` to a comma-separated list:

```bash
export WATCH_PROVIDERS=8,9,337,384,15  # Netflix, Prime, Disney+, HBO Max, Hulu
```

## Usage Patterns

### One-Time Fetch

For manual, one-time trailer downloads:

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

# Prune old ones
coming-attractions prune \
  --theatrical-dir /data/trailers/theatrical \
  --streaming-dir /data/trailers/streaming \
  --retention-years 2 \
  --force

# Fix titles
coming-attractions fix-titles \
  --root-dir /data/trailers
```

### Scheduled Automation (Cron)

For scheduled automation using cron:

```bash
# Edit crontab
crontab -e
```

Add these entries:

```cron
# Fetch theatrical trailers twice daily (6am and 6pm)
0 6,18 * * * /usr/local/bin/coming-attractions fetch --api-key YOUR_KEY --mode theatrical --out-dir /data/theatrical >> /var/log/fetch.log 2>&1

# Fetch streaming trailers daily at 8am
0 8 * * * /usr/local/bin/coming-attractions fetch --api-key YOUR_KEY --mode streaming --out-dir /data/streaming >> /var/log/fetch.log 2>&1

# Prune old trailers weekly (Sunday at 2am)
0 2 * * 0 /usr/local/bin/coming-attractions prune --theatrical-dir /data/theatrical --streaming-dir /data/streaming --retention-years 2 --force >> /var/log/prune.log 2>&1

# Fix titles daily at 3am
0 3 * * * /usr/local/bin/coming-attractions fix-titles --root-dir /data/trailers >> /var/log/fix.log 2>&1
```

**Important:** Use full paths in cron jobs (`/usr/local/bin/coming-attractions`, not just `coming-attractions`).

### Daemon Mode

For continuous, hands-off automation (recommended for Docker):

```bash
coming-attractions daemon \
  --api-key YOUR_API_KEY \
  --interval 12h \
  --metadata-wait 300 \
  --retention-years 2 \
  --timestamps \
  --log-file /var/log/coming-attractions.log
```

This runs indefinitely, executing the full workflow every 12 hours.

## Logging

### Log Prefixes

Console and log file output use color-coded prefixes:

- `[*]` - Informational (cyan)
- `[+]` - Success (green)
- `[-]` - Error (red)
- `[!]` - Warning (yellow)

### Example Output

Sample console output from fetch command:

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
[+] Present/Downloaded: 150
[*] Skipped: 130
[*] Skip reasons:
[*]   Out Of Window: 63
[*]   No Video Available: 45
[+] Trailer fetching complete.
```

### Logging Options

Options for controlling log output:

**Enable debug logging:**

```bash
coming-attractions fetch --debug
```

**Log to file:**

```bash
coming-attractions fetch --log-file /var/log/coming-attractions.log
```

**Add timestamps:**

```bash
coming-attractions fetch --timestamps
```

**Combine all logging options:**

```bash
coming-attractions fetch \
  --debug \
  --timestamps \
  --log-file /var/log/coming-attractions.log
```

## Troubleshooting

### "TMDB_API_KEY is required"

**Problem:** Command fails with "TMDB_API_KEY is required" error.

**Solution:**
- Set environment variable: `export TMDB_API_KEY=your_key_here`
- Or pass via CLI: `--api-key your_key`
- Get a free key from [TMDb](https://www.themoviedb.org/settings/api)

### "Directory is not writable"

**Problem:** Permission denied when writing trailers.

**Solution:**

```bash
# Check directory permissions
ls -la /data/trailers/

# Fix ownership
sudo chown -R $USER:$USER /data/trailers/

# Fix permissions
chmod -R 755 /data/trailers/
```

For Docker, see [Docker Guide - Volume Permissions](DOCKER.md#volume-permissions).

### "Download failed"

**Problem:** YouTube downloads fail.

**Solution:**

1. **Check internet connectivity:**
   ```bash
   ping youtube.com
   ```

2. **Verify yt-dlp is installed:**
   ```bash
   yt-dlp --version
   ```

3. **Update yt-dlp:**
   ```bash
   pip install --upgrade yt-dlp
   ```

4. **Enable debug mode:**
   ```bash
   coming-attractions fetch --debug
   ```

5. **Test download manually:**
   ```bash
   yt-dlp --format 'bv*[height<=1080]+ba/b' 'https://youtube.com/watch?v=VIDEO_ID'
   ```

### "No trailers found"

**Problem:** Fetch command returns zero results.

**Solution:**

1. **Check date window settings:**
   ```bash
   # Increase window
   coming-attractions fetch --days-ahead 365 --days-back 180
   ```

2. **Verify region code:**
   ```bash
   # Try different region
   coming-attractions fetch --region GB  # United Kingdom
   ```

3. **Enable debug to see API responses:**
   ```bash
   coming-attractions fetch --debug
   ```

4. **Check TMDb API status:**
   - Visit https://www.themoviedb.org/
   - Check for service outages

### "Jellyfin not showing trailers"

**Problem:** Trailers don't appear in Jellyfin library.

**Solution:**

1. **Run fix-titles to add "Trailer - " prefix:**
   ```bash
   coming-attractions fix-titles --root-dir /data/trailers/theatrical
   ```

2. **Check NFO files contain metadata:**
   ```bash
   cat "/data/trailers/theatrical/Movie Title (2026)/movie.nfo"
   ```

3. **Refresh library metadata in Jellyfin:**
   - Dashboard → Libraries → [Your Library] → Scan Library

4. **Ensure "Trailers" metadata provider is enabled:**
   - Dashboard → Libraries → [Your Library] → Manage Library
   - Check "Trailers" under metadata providers

5. **Verify directory structure:**
   ```
   /data/trailers/theatrical/
   └── Movie Title (2026)/
       ├── Movie Title (2026).mp4  ✅ Video file
       └── movie.nfo              ✅ Metadata file
   ```

See [Jellyfin Integration Guide](JELLYFIN_INTEGRATION.md) for detailed setup.

### "Command not found"

**Problem:** `coming-attractions: command not found`

**Solution:**

1. **Check installation:**
   ```bash
   pip list | grep coming-attractions
   ```

2. **Reinstall package:**
   ```bash
   cd coming-attractions/src/
   pip install -e .
   ```

3. **Check PATH:**
   ```bash
   which coming-attractions
   ```

4. **For cron jobs, use full path:**
   ```bash
   which coming-attractions  # Get full path
   # Use: /usr/local/bin/coming-attractions in crontab
   ```

### "Import errors"

**Problem:** Module import errors when running commands.

**Solution:**

1. **Verify Python version (requires 3.11+):**
   ```bash
   python --version
   ```

2. **Check dependencies:**
   ```bash
   cd coming-attractions/src/
   pip install -e .
   ```

3. **Reinstall from scratch:**
   ```bash
   pip uninstall coming-attractions
   cd coming-attractions/src/
   pip install -e .
   ```

### Enable Debug Mode

For any issue, enable debug mode to see detailed output:

```bash
coming-attractions fetch --debug --timestamps
```

This shows:
- API requests and responses
- File operations
- Download progress
- Error stack traces

### Getting Help

Command help and support resources:

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

For issues not covered here:
- 🐛 [Report bugs](https://github.com/robertsinfosec/coming-attractions/issues)
- 💬 [Discussions](https://github.com/robertsinfosec/coming-attractions/discussions)
- 📖 [Documentation](https://github.com/robertsinfosec/coming-attractions)


> **Navigation:** [Home](../README.md) | [Docker Guide](DOCKER.md) | [Jellyfin Integration](JELLYFIN_INTEGRATION.md) | [Contributing](../CONTRIBUTING.md)
