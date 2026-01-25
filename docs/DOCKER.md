# Docker Guide

> **Navigation:** [Home](../README.md) | [User Guide](USER_GUIDE.md) | [Jellyfin Integration](JELLYFIN_INTEGRATION.md) | [Contributing](../CONTRIBUTING.md)

Complete guide for running Coming Attractions in Docker.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Compose (Recommended)](#docker-compose-recommended)
- [Docker Run](#docker-run)
- [Directory Structure](#directory-structure)
- [Volume Mapping](#volume-mapping)
- [Environment Variables](#environment-variables)
- [Multi-Architecture Support](#multi-architecture-support)
- [Volume Permissions](#volume-permissions)
- [Integration with Jellyfin](#integration-with-jellyfin)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)


## Quick Start

The fastest way to get started with Coming Attractions:

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
      - MODE=both
      - RETENTION_YEARS=2
      - DAYS_AHEAD=180
      - DAYS_BACK=90
      - MAX_HEIGHT=1080
      - METADATA_WAIT_SECONDS=300
      - LOG_TIMESTAMPS=1
    volumes:
      - /path/to/trailers:/data/trailers
    command: daemon --interval 12h
```

Create `.env` file:

```env
TMDB_API_KEY=your_api_key_here
```

Start:

```bash
docker-compose up -d
```

## Docker Compose (Recommended)

### Complete Example

Full-featured Docker Compose configuration:

```yaml
version: '3.8'

services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    container_name: coming-attractions
    restart: unless-stopped
    user: "1000:1000"  # Optional: match your host UID/GID
    
    environment:
      # Required
      - TZ=America/New_York
      - TMDB_API_KEY=${TMDB_API_KEY}
      
      # Fetch settings
      - MODE=both
      - TMDB_REGION=US
      - DAYS_AHEAD=180
      - DAYS_BACK=90
      - MAX_PAGES=5
      - MAX_HEIGHT=1080
      
      # Streaming providers (Netflix, Prime, Disney+, HBO Max, Hulu, Apple TV+, Paramount+, Peacock, Showtime, Starz)
      - MEDIA_TYPES=movie,tv
      - WATCH_PROVIDERS=8,9,337,384,15,350,531,386,37,43
      - WATCH_REGION=US
      
      # Retention
      - RETENTION_YEARS=2
      
      # Logging
      - LOG_TIMESTAMPS=1
      - DEBUG=0
      - LOG_FILE=/data/trailers/coming-attractions.log
      
      # Daemon
      - METADATA_WAIT_SECONDS=300  # Wait 5 min for Jellyfin
    
    volumes:
      # Single mount - everything stored here
      - /opt/media/trailers:/data/trailers
    
    command: daemon --interval 12h
    
    healthcheck:
      test: ["CMD", "pgrep", "-f", "coming-attractions"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### With Existing Jellyfin Setup

If you already run Jellyfin via Docker Compose, add Coming Attractions to the same file:

```yaml
version: '3.8'

services:
  # Your existing Jellyfin service
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    volumes:
      - /opt/media/config:/config
      - /opt/media/cache:/cache
      - /opt/media/movies:/media/movies
      - /opt/media/tv:/media/tv
      # Add trailer directories (read-only for safety)
      - /opt/media/trailers/theatrical:/media/trailers-theatrical:ro
      - /opt/media/trailers/streaming:/media/trailers-streaming:ro
    ports:
      - 8096:8096
  
  # Add Coming Attractions
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    container_name: coming-attractions
    restart: unless-stopped
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - TZ=America/New_York
      - MODE=both
      - RETENTION_YEARS=2
      - LOG_TIMESTAMPS=1
    volumes:
      # Same trailer directory Jellyfin uses (read-write)
      - /opt/media/trailers:/data/trailers
    command: daemon --interval 12h
    depends_on:
      - jellyfin
```

## Docker Run

If you prefer `docker run` over Docker Compose:

### Daemon Mode

Run continuously in the background:

```bash
docker run -d \
  --name coming-attractions \
  --restart unless-stopped \
  -e TZ=America/New_York \
  -e TMDB_API_KEY=your_api_key_here \
  -e MODE=both \
  -e RETENTION_YEARS=2 \
  -e LOG_TIMESTAMPS=1 \
  -v /opt/media/trailers:/data/trailers \
  ghcr.io/robertsinfosec/coming-attractions:latest \
  daemon --interval 12h
```

### One-Time Fetch

Run a single fetch operation:

```bash
docker run --rm \
  -e TMDB_API_KEY=your_api_key_here \
  -v /opt/media/trailers:/data/trailers \
  ghcr.io/robertsinfosec/coming-attractions:latest \
  fetch --mode theatrical --out-dir /data/trailers/theatrical
```

### One-Time Prune

Remove old trailers once:

```bash
docker run --rm \
  -v /opt/media/trailers:/data/trailers \
  ghcr.io/robertsinfosec/coming-attractions:latest \
  prune --retention-years 2 --force
```

### Fix Titles

Add trailer prefix to NFO files:

```bash
docker run --rm \
  -v /opt/media/trailers:/data/trailers \
  ghcr.io/robertsinfosec/coming-attractions:latest \
  fix-titles --root-dir /data/trailers
```

## Directory Structure

### Container Paths

Inside the container, Coming Attractions expects:

```
/data/trailers/                    # Base directory
├── .trailer-removed.txt           # Tracking file (auto-created)
├── theatrical/                    # Theatrical releases (auto-created)
│   ├── Movie Name (2026)/
│   │   ├── Movie Name (2026).mp4
│   │   └── movie.nfo
│   └── Another Movie (2026)/
│       ├── Another Movie (2026).mp4
│       └── movie.nfo
└── streaming/                     # Streaming releases (auto-created)
    ├── Show Name (2026) [TV]/
    │   ├── Show Name (2026) [TV].mp4
    │   └── movie.nfo
    └── Streaming Movie (2026)/
        ├── Streaming Movie (2026).mp4
        └── movie.nfo
```

### Host Paths

Map your host directory to `/data/trailers`:

```yaml
volumes:
  - /opt/media/trailers:/data/trailers
```

This creates the same structure on your host:

```
/opt/media/trailers/               # Your host directory
├── .trailer-removed.txt
├── theatrical/
│   └── ...
└── streaming/
    └── ...
```

## Volume Mapping

### Single Volume (Recommended)

Mount one parent directory and let the app create subdirectories:

```yaml
volumes:
  - /opt/media/trailers:/data/trailers
```

#### Advantages

Benefits of single volume approach:

- Simplest configuration
- App manages subdirectories
- Tracking file (.trailer-removed.txt) in one place
- Easy to back up

### Custom Paths

If you need custom paths:

```yaml
environment:
  - OUT_DIR=/data/trailers
  - THEATRICAL_DIR=/data/trailers/theatrical
  - STREAMING_DIR=/data/trailers/streaming
  - REMOVED_FILE=/data/trailers/.trailer-removed.txt

volumes:
  - /opt/media/trailers:/data/trailers
```

### Read-Only Mounts

For Jellyfin, mount trailer directories as read-only:

```yaml
volumes:
  # Jellyfin - read-only
  - /opt/media/trailers/theatrical:/media/trailers-theatrical:ro
  - /opt/media/trailers/streaming:/media/trailers-streaming:ro
```

This prevents Jellyfin from accidentally modifying trailer files.

## Environment Variables

All environment variables from the [User Guide](USER_GUIDE.md#environment-variables) are supported. Key variables for Docker:

| Variable                | Description                                   | Default |
| ----------------------- | --------------------------------------------- | ------- |
| `TMDB_API_KEY`          | **Required.** TMDb API key                    | -       |
| `TZ`                    | Timezone (e.g., `America/New_York`)           | `UTC`   |
| `MODE`                  | Fetch mode: `theatrical`, `streaming`, `both` | `both`  |
| `RETENTION_YEARS`       | Years to retain trailers                      | `2`     |
| `METADATA_WAIT_SECONDS` | Wait for Jellyfin metadata (daemon)           | `300`   |
| `LOG_TIMESTAMPS`        | Add timestamps to logs                        | `0`     |
| `DEBUG`                 | Enable debug logging                          | `0`     |

See [User Guide - Environment Variables](USER_GUIDE.md#environment-variables) for the complete list.

## Multi-Architecture Support

Coming Attractions supports multiple architectures out of the box:

| Platform            | Architecture   | Supported | Notes                   |
| ------------------- | -------------- | --------- | ----------------------- |
| Intel/AMD PC        | `linux/amd64`  | ✅         | Standard desktop/server |
| Raspberry Pi 4/5    | `linux/arm64`  | ✅         | 64-bit Raspberry Pi OS  |
| Raspberry Pi 3      | `linux/arm/v7` | ✅         | 32-bit Raspberry Pi OS  |
| Raspberry Pi Zero 2 | `linux/arm64`  | ✅         | 64-bit capable          |
| Apple Silicon Mac   | `linux/arm64`  | ✅         | Via Docker Desktop      |
| Intel Mac           | `linux/amd64`  | ✅         | Via Docker Desktop      |

### Automatic Detection

Docker automatically pulls the correct image for your architecture:

```bash
docker pull ghcr.io/robertsinfosec/coming-attractions:latest
```

No configuration needed!

### Manual Architecture Selection

If you need to force a specific architecture:

```bash
docker pull --platform linux/arm64 ghcr.io/robertsinfosec/coming-attractions:latest
```

## Volume Permissions

### Understanding Permissions

The container runs as user `uid 1000` by default. Ensure your host directory is writable by this user.

### Fix Permissions (Linux)

Steps to fix ownership and permissions:

```bash
# Check current ownership
ls -la /opt/media/trailers/

# Fix ownership (replace 1000:1000 with your UID:GID)
sudo chown -R 1000:1000 /opt/media/trailers

# Fix permissions
chmod -R 755 /opt/media/trailers
```

### Custom User ID

To run as a different user, set the `user` directive:

```yaml
services:
  coming-attractions:
    user: "1001:1001"  # Your UID:GID
    # ...
```

Or via `docker run`:

```bash
docker run -d \
  --user 1001:1001 \
  # ...
```

### Find Your UID/GID

How to find your user and group IDs:

```bash
# On your host
id
# Output: uid=1000(myuser) gid=1000(myuser) ...
```

Use these values in the `user` directive.

## Integration with Jellyfin

### Same Docker Network

If Jellyfin and Coming Attractions are in the same `docker-compose.yml`:

```yaml
services:
  jellyfin:
    # ...
    volumes:
      - /opt/media/trailers/theatrical:/media/trailers-theatrical:ro
      - /opt/media/trailers/streaming:/media/trailers-streaming:ro
  
  coming-attractions:
    # ...
    volumes:
      - /opt/media/trailers:/data/trailers
    depends_on:
      - jellyfin
```

### Separate Docker Compose Files

If they're in separate files, use a shared volume path:

**Jellyfin's `docker-compose.yml`:**

```yaml
services:
  jellyfin:
    volumes:
      - /opt/media/trailers/theatrical:/media/trailers-theatrical:ro
      - /opt/media/trailers/streaming:/media/trailers-streaming:ro
```

**Coming Attractions' `docker-compose.yml`:**

```yaml
services:
  coming-attractions:
    volumes:
      - /opt/media/trailers:/data/trailers
```

Both point to the same host directory: `/opt/media/trailers`.

### Metadata Wait Time

The daemon waits for Jellyfin to detect new files and generate NFO metadata before adding the "Trailer - " prefix. Adjust if needed:

```yaml
environment:
  - METADATA_WAIT_SECONDS=300  # 5 minutes (default)
  # - METADATA_WAIT_SECONDS=600  # 10 minutes (slower NAS)
```

See [Jellyfin Integration Guide](JELLYFIN_INTEGRATION.md) for library setup.

## Examples

### Minimal Configuration

Simplest possible configuration:

```yaml
services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
    volumes:
      - ./trailers:/data/trailers
    command: daemon --interval 12h
```

### Theatrical Only

Fetch only theatrical trailers:

```yaml
services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - MODE=theatrical
      - DAYS_AHEAD=365
      - MAX_HEIGHT=2160  # 4K
    volumes:
      - ./trailers:/data/trailers
    command: daemon --interval 24h
```

### Streaming Only

Fetch only streaming trailers:

```yaml
services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - MODE=streaming
      - MEDIA_TYPES=movie,tv
      - WATCH_PROVIDERS=8,9,337  # Netflix, Prime, Disney+
    volumes:
      - ./trailers:/data/trailers
    command: daemon --interval 12h
```

### Debug Mode

Enable debug logging and dry-run:

```yaml
services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - DEBUG=1
      - LOG_TIMESTAMPS=1
      - LOG_FILE=/data/trailers/debug.log
    volumes:
      - ./trailers:/data/trailers
    command: fetch --mode both --dry-run
```

### Custom Retention

Change trailer retention period:

```yaml
services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - RETENTION_YEARS=3  # Keep trailers for 3 years
    volumes:
      - ./trailers:/data/trailers
    command: daemon --interval 12h
```

## Troubleshooting

### Container Won't Start

**Check logs:**

```bash
docker logs coming-attractions
```

**Common issues:**

- Missing `TMDB_API_KEY`
- Volume permission errors
- Invalid command syntax

### Permission Denied Errors

**Problem:** Can't write to `/data/trailers`

**Solution:**

```bash
# Check container user
docker exec coming-attractions id
# Output: uid=1000 gid=1000

# Fix host permissions
sudo chown -R 1000:1000 /opt/media/trailers
chmod -R 755 /opt/media/trailers
```

Or run as your user:

```yaml
services:
  coming-attractions:
    user: "$(id -u):$(id -g)"
```

### No Trailers Downloaded

**Check logs:**

```bash
docker logs coming-attractions --tail 100
```

**Enable debug:**

```yaml
environment:
  - DEBUG=1
  - LOG_TIMESTAMPS=1
```

Restart and check logs:

```bash
docker-compose restart
docker logs -f coming-attractions
```

### Container Keeps Restarting

**Check exit code:**

```bash
docker ps -a | grep coming-attractions
```

**View logs:**

```bash
docker logs coming-attractions
```

**Common causes:**

- Invalid API key
- Syntax error in command
- Missing required environment variables

### Jellyfin Doesn't See Trailers

**Check volume mounts:**

```bash
# Inside Jellyfin container
docker exec jellyfin ls -la /media/trailers-theatrical
```

**Verify paths match:**

```yaml
# Coming Attractions writes to:
volumes:
  - /opt/media/trailers:/data/trailers

# Jellyfin reads from:
volumes:
  - /opt/media/trailers/theatrical:/media/trailers-theatrical:ro
```

**Refresh Jellyfin library:**

Dashboard → Libraries → Scan Library

See [Jellyfin Integration Guide](JELLYFIN_INTEGRATION.md).

### Update Container

```bash
# Pull latest image
docker pull ghcr.io/robertsinfosec/coming-attractions:latest

# Restart (Docker Compose)
docker-compose down
docker-compose up -d

# Or restart (docker run)
docker stop coming-attractions
docker rm coming-attractions
# Run your docker run command again
```

### View Real-Time Logs

```bash
# Follow logs
docker logs -f coming-attractions

# Last 100 lines
docker logs coming-attractions --tail 100

# Since 1 hour ago
docker logs coming-attractions --since 1h
```

### Execute Commands Manually

```bash
# Fetch theatrical
docker exec coming-attractions \
  coming-attractions fetch --mode theatrical

# Prune old trailers
docker exec coming-attractions \
  coming-attractions prune --retention-years 2 --force

# Fix titles
docker exec coming-attractions \
  coming-attractions fix-titles
```

### Access Container Shell

```bash
docker exec -it coming-attractions /bin/bash
```

Then run commands directly:

```bash
coming-attractions --help
ls -la /data/trailers
cat /data/trailers/.trailer-removed.txt
```

## Building Locally

To build the Docker image yourself:

```bash
# Clone repository
git clone https://github.com/robertsinfosec/coming-attractions.git
cd coming-attractions

# Build for your architecture
docker build -t coming-attractions:local -f src/docker/Dockerfile .

# Build multi-arch (requires buildx)
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t coming-attractions:multi \
  -f src/docker/Dockerfile \
  .

# Run locally built image
docker run --rm \
  -e TMDB_API_KEY=your_key \
  -v ./data:/data/trailers \
  coming-attractions:local \
  fetch --mode theatrical --dry-run
```

> **Navigation:**** [Home](../README.md) | [User Guide](USER_GUIDE.md) | [Jellyfin Integration](JELLYFIN_INTEGRATION.md) | [Contributing](../CONTRIBUTING.md)
