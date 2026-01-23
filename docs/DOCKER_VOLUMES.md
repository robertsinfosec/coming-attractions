# Docker Volume Mapping Guide

## Directory Structure

Your setup will create the following structure:

```
/opt/media/nas-data/trailers/           # Your host directory
├── .trailer-removed.txt                # Tracking file (auto-created)
├── theatrical/                         # Theatrical releases (auto-created)
│   ├── Movie Name (2026)/
│   │   ├── movie.mp4
│   │   └── movie.nfo
│   └── Another Movie (2026)/
│       ├── movie.mp4
│       └── movie.nfo
└── streaming/                          # Streaming releases (auto-created)
    ├── Show Name (2026) [TV]/
    │   ├── movie.mp4
    │   └── movie.nfo
    └── Streaming Movie (2026)/
        ├── movie.mp4
        └── movie.nfo
```

## Docker Compose Example

### For Your Jellyfin/Servarr Setup

```yaml
version: '3.8'

services:
  coming-attractions:
    image: ghcr.io/robertsinfosec/coming-attractions:latest
    container_name: coming-attractions
    restart: unless-stopped
    
    environment:
      - TMDB_API_KEY=your_tmdb_api_key_here
      - TZ=America/New_York
      - MODE=both
      - RETENTION_YEARS=2
      - LOG_TIMESTAMPS=1
    
    volumes:
      # Single volume mount - everything lives here
      - /opt/media/nas-data/trailers:/data/trailers
    
    command: daemon --interval 12h

  # Your existing Jellyfin setup
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    volumes:
      # Point Jellyfin to the same trailer directory
      - /opt/media/nas-data/trailers:/data/trailers:ro  # Read-only for safety
      # ... your other volumes
```

## How It Works

### 1. Container Startup
- Container starts with working directory: `/data/trailers`
- This maps to your host: `/opt/media/nas-data/trailers/`

### 2. First Run
The app will automatically create:
- `/data/trailers/theatrical/` → `/opt/media/nas-data/trailers/theatrical/`
- `/data/trailers/streaming/` → `/opt/media/nas-data/trailers/streaming/`
- `/data/trailers/.trailer-removed.txt` → `/opt/media/nas-data/trailers/.trailer-removed.txt`

### 3. Ongoing Operations

**Fetch Command:**
```bash
# Inside container: /data/trailers
# On host: /opt/media/nas-data/trailers
docker exec coming-attractions fetch --mode theatrical
```

Downloads trailers to:
- Container: `/data/trailers/theatrical/Movie Name (2026)/`
- Host: `/opt/media/nas-data/trailers/theatrical/Movie Name (2026)/`

**Prune Command:**
```bash
docker exec coming-attractions prune --retention-years 2
```

When a trailer is removed:
1. Deletes: `/data/trailers/theatrical/Old Movie (2020)/`
2. Updates: `/data/trailers/.trailer-removed.txt` with "Old Movie (2020)"
3. Next fetch skips this movie (won't re-download)

### 4. Jellyfin Integration

Point Jellyfin libraries to:
- **Theatrical Trailers**: `/data/trailers/theatrical` (read-only mount recommended)
- **Streaming Trailers**: `/data/trailers/streaming` (read-only mount recommended)

Jellyfin will automatically:
- Detect new trailer folders
- Read `movie.nfo` for metadata
- Display with "Trailer - Movie Name" titles

## Environment Variables

All path-related variables default to `/data/trailers` structure:

```yaml
environment:
  # These are the defaults (usually don't need to change):
  - OUT_DIR=/data/trailers                          # Base directory
  - THEATRICAL_DIR=/data/trailers/theatrical         # Auto-created
  - STREAMING_DIR=/data/trailers/streaming           # Auto-created
  - REMOVED_FILE=/data/trailers/.trailer-removed.txt # Tracking file
  
  # Only override if you need custom structure:
  # - OUT_DIR=/custom/path
  # - REMOVED_FILE=/custom/path/.my-removed-list.txt
```

## Volume Permissions

The container runs as non-root user (`uid 1000`). Ensure your host directory is writable:

```bash
# On your host
sudo chown -R 1000:1000 /opt/media/nas-data/trailers
chmod -R 755 /opt/media/nas-data/trailers
```

Or use Docker Compose user directive:

```yaml
services:
  coming-attractions:
    user: "1000:1000"  # Match your host user
    # ... rest of config
```

## Complete Example

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
      - TMDB_API_KEY=${TMDB_API_KEY}
      
      # Recommended
      - TZ=America/New_York
      - MODE=both
      - RETENTION_YEARS=2
      - DAYS_AHEAD=180
      - MAX_HEIGHT=1080
      
      # Optional logging
      - LOG_TIMESTAMPS=1
      - LOG_FILE=/data/trailers/coming-attractions.log
    
    volumes:
      # Single mount point - everything in one place
      - /opt/media/nas-data/trailers:/data/trailers
    
    command: daemon --interval 12h
```

Then create `.env` file:
```bash
TMDB_API_KEY=your_api_key_here
```

Start with:
```bash
docker-compose up -d
```

## Verifying Setup

```bash
# Check container logs
docker logs coming-attractions

# Check trailer directory structure
ls -la /opt/media/nas-data/trailers/

# Expected output:
# drwxr-xr-x  trailers trailers theatrical/
# drwxr-xr-x  trailers trailers streaming/
# -rw-r--r--  trailers trailers .trailer-removed.txt

# Run manual fetch to test
docker exec coming-attractions fetch --mode theatrical --dry-run

# Check what would be pruned
docker exec coming-attractions prune --dry-run
```

## Summary

✅ **One Volume Mount**: `/opt/media/nas-data/trailers:/data/trailers`  
✅ **Auto-Created Subdirectories**: `theatrical/`, `streaming/`  
✅ **Tracking File**: `.trailer-removed.txt` in trailer root  
✅ **No Separate Config Volume**: Everything in one place  
✅ **Jellyfin Compatible**: Point to subdirectories, read NFO files  
✅ **Permission Safe**: Runs as non-root user (uid 1000)

This matches your expected setup perfectly! 🎯
