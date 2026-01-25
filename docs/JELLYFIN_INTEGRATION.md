# Jellyfin Integration Guide

> **Navigation:** [Home](../README.md) | [User Guide](USER_GUIDE.md) | [Docker Guide](DOCKER.md) | [Contributing](../CONTRIBUTING.md)

Complete guide for integrating Coming Attractions trailers with Jellyfin media server.

## Table of Contents

- [Overview](#overview)
- [What This Is vs. Trailerfin](#what-this-is-vs-trailerfin)
- [Setup Instructions](#setup-instructions)
- [Directory Structure](#directory-structure)
- [Library Configuration](#library-configuration)
- [Metadata Generation](#metadata-generation)
- [Title Prefixes](#title-prefixes)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

Coming Attractions creates separate Jellyfin libraries for **upcoming trailers** - movies and TV shows not yet released or recently available on streaming platforms. This is different from associating trailers with existing media in your library.

**What you get:**
- Separate "Theatrical Trailers" library for upcoming theatrical releases
- Separate "Streaming Trailers" library for upcoming streaming content
- Automatic metadata (NFO files) for proper display
- "Trailer - " prefix to distinguish from actual movies
- "Recently Added" sections showing newest trailers

## What This Is vs. Trailerfin

### Coming Attractions (This Project)

**Purpose:** Show trailers for **upcoming** movies and TV shows

- **Content:** Trailers for movies/shows **not yet released**
- **Libraries:** Separate "Theatrical Trailers" and "Streaming Trailers" libraries
- **Use Case:** "What's coming to theaters?" or "What's new on Netflix next month?"
- **Display:** Standalone trailer library with "Trailer - " prefix

#### Example

How Coming Attractions appears in Jellyfin:

```
Your Jellyfin Libraries:
- Movies (your existing collection)
- TV Shows (your existing collection)
- Theatrical Trailers ← Coming Attractions
- Streaming Trailers ← Coming Attractions
```

### Trailerfin

**Purpose:** Associate trailers with **existing** media in your library

- **Content:** Trailers for movies/shows **you already have**
- **Libraries:** Uses your existing "Movies" and "TV Shows" libraries
- **Use Case:** "Show me the trailer for this movie I already own"
- **Display:** Trailer button appears on existing movie/show pages

#### Example

How Trailerfin appears in Jellyfin:

```
In your "Movies" library:
- The Matrix (1999)
  [▶ Play] [🎬 Trailer] ← Trailerfin adds this button
```

### Can You Use Both?

Yes! They serve different purposes:

- **Trailerfin:** Enhances existing media with trailer buttons
- **Coming Attractions:** Separate libraries for upcoming content

## Setup Instructions

### Step 1: Prepare Directory Structure

Coming Attractions creates this structure automatically:

```
/data/trailers/
├── theatrical/
│   ├── Movie Title (2026)/
│   │   ├── Movie Title (2026).mp4
│   │   └── movie.nfo
│   └── Another Movie (2026)/
│       └── ...
└── streaming/
    ├── Show Name (2026) [TV]/
    │   ├── Show Name (2026) [TV].mp4
    │   └── movie.nfo
    └── Streaming Movie (2026)/
        └── ...
```

If using Docker, ensure Jellyfin can access this directory (see [Docker Guide](DOCKER.md#integration-with-jellyfin)).

### Step 2: Add Libraries in Jellyfin

Create separate libraries for theatrical and streaming trailers.

#### Theatrical Trailers Library

Steps to create theatrical trailers library:

1. **Jellyfin Dashboard** → **Libraries** → **Add Library**
2. **Content type:** Movies
3. **Display name:** `Theatrical Trailers` (or your preference)
4. **Folders:**
   - Click **+** (Add folder)
   - Enter: `/data/trailers/theatrical` (or your path)
   - Click **OK**
5. **Library settings:**
   - ✅ Enable **NFO** metadata provider
   - ✅ Enable **Trailers** (optional - won't apply to these since they ARE trailers)
   - ⚙️ Configure other settings as desired
6. Click **OK** to create library

#### Streaming Trailers Library

Repeat the same steps:

1. **Content type:** Movies (yes, even for TV show trailers)
2. **Display name:** `Streaming Trailers`
3. **Folder:** `/data/trailers/streaming`
4. ✅ Enable **NFO** metadata provider
5. Click **OK**

> **Note:** Use "Movies" content type even for TV trailers because they're individual video files, not series with episodes.

### Step 3: Scan Libraries

After adding libraries:

1. **Dashboard** → **Libraries**
2. Find your new trailer libraries
3. Click **Scan Library** on each

Jellyfin will detect trailer folders and read NFO metadata.

## Directory Structure

Understand how Coming Attractions organizes trailer files and metadata.

### How Coming Attractions Organizes Files

Each trailer gets its own folder named: `Title (Year)` or `Title (Year) [TV]`

```
/data/trailers/theatrical/
├── Dune Part Three (2026)/
│   ├── Dune Part Three (2026).mp4      ← Video file
│   └── movie.nfo                        ← Metadata
├── Avatar 4 (2026)/
│   ├── Avatar 4 (2026).mp4
│   └── movie.nfo
└── Blade Runner 2099 (2027)/
    ├── Blade Runner 2099 (2027).mp4
    └── movie.nfo
```

### NFO File Format

Example `movie.nfo`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>Trailer - Dune Part Three</title>
  <originaltitle>Dune Part Three</originaltitle>
  <year>2026</year>
  <plot>Third installment of the Dune saga...</plot>
  <trailer>https://www.youtube.com/watch?v=...</trailer>
  <genre>Science Fiction</genre>
  <genre>Adventure</genre>
</movie>
```

Jellyfin reads this file to display metadata.

## Library Configuration

Optimize your Jellyfin library settings for best trailer display and performance.

### Recommended Settings

**Dashboard** → **Libraries** → [Your Trailer Library] → **Manage Library**

#### Display Settings

Basic library display configuration:

- **Display name:** `Theatrical Trailers` or `Streaming Trailers`
- **Language:** English (or your preference)
- **Country:** United States (or your region)

#### Library Settings

Feature toggles for the library:

- ✅ **Enable chapter image extraction:** Optional
- ✅ **Extract chapter images during library scan:** Optional
- ⚠️ **Automatically refresh metadata:** Disabled (Coming Attractions manages metadata)

#### Metadata Downloaders

Ensure NFO is **first** in the list:

1. **NFO** (drag to top)
2. TheMovieDb
3. The Open Movie Database

This ensures Jellyfin reads Coming Attractions' NFO files first.

#### Image Fetchers

Image source priority:

- TheMovieDb
- The Open Movie Database
- Fanart
- Screen Grabber

## Metadata Generation

Coming Attractions automatically generates NFO metadata files for proper Jellyfin display.

### Automatic Metadata

Coming Attractions generates NFO files automatically during fetch:

```bash
coming-attractions fetch --mode theatrical
```

Creates:
```
/data/trailers/theatrical/Movie (2026)/
├── Movie (2026).mp4
└── movie.nfo  ← Auto-generated
```

### Metadata Wait Time (Daemon Mode)

When running in daemon mode, there's a wait period after fetching to allow Jellyfin to detect new files:

```yaml
environment:
  - METADATA_WAIT_SECONDS=300  # Wait 5 minutes (default)
```

**Workflow:**

Steps performed in each daemon cycle:

1. Coming Attractions downloads trailer
2. Jellyfin detects new file (via library scan or real-time monitoring)
3. Jellyfin generates NFO (if auto-refresh enabled)
4. Wait period ends
5. Coming Attractions runs `fix-titles` to add "Trailer - " prefix

**Adjust wait time if:**

When to change the default wait time:

- You have a slow NAS: Increase to `600` (10 minutes)
- You disabled auto-refresh: Decrease to `60` (1 minute)
- You manually scan libraries: Set to `0`

## Title Prefixes

Understand why and how to add prefixes to distinguish trailers from actual movies.

### Why Prefix Titles?

Without prefixes, you can't tell trailers apart from actual movies:

**Search for "Dune Part Three":**

- `Dune Part Three` ← Is this the movie or the trailer? 🤔
- `Dune Part Three` ← Can't tell!

With prefixes:
- `Dune Part Three` ← The actual movie ✅
- `Trailer - Dune Part Three` ← Clearly the trailer ✅

### Adding Prefixes

Run `fix-titles` after fetching:

```bash
coming-attractions fix-titles --root-dir /data/trailers/theatrical
```

This updates NFO files:

```xml
<title>Dune Part Three</title>
```

Becomes:

```xml
<title>Trailer - Dune Part Three</title>
```

### Custom Prefixes

You can customize the prefix:

```bash
coming-attractions fix-titles \
  --root-dir /data/trailers \
  --prefix "Coming Soon - "
```

Results in: `Coming Soon - Dune Part Three`

### Automatic Prefixing (Daemon Mode)

Daemon mode handles this automatically:

```bash
coming-attractions daemon --interval 12h
```

1. Fetches trailers
2. Waits for metadata
3. **Automatically runs fix-titles**
4. Sleeps until next cycle

## Examples

See how Coming Attractions trailers appear in Jellyfin's user interface.

### Example: Jellyfin Home Screen

With Coming Attractions configured, your Jellyfin home screen shows:

```
Recently added in Theatrical Trailers:
[Trailer - Dune Part Three]
[Trailer - Avatar 4]
[Trailer - Blade Runner 2099]

Recently added in Streaming Trailers:
[Trailer - Stranger Things S5]
[Trailer - The Witcher S4]
[Trailer - Wednesday S2]

Recently added in Movies:
[The Matrix]
[Inception]
[Interstellar]
```

Clear separation between upcoming trailers and your existing library!

### Example: Trailer Detail Page

Click a trailer in Jellyfin:

**Title:** `Trailer - Dune Part Three`
**Year:** 2026
**Genre:** Science Fiction, Adventure
**Plot:** Third installment of the Dune saga...

**Buttons:**

Available playback options:

1. **▶ Play** ← Plays the trailer video
2. **🎬 Trailer** ← May appear if Trailerfin found a different trailer

> Button 1 plays the Coming Attractions trailer (downloaded file)
> Button 2 (if present) plays Trailerfin's online trailer

## Troubleshooting

Common Jellyfin integration issues and their solutions.

### Jellyfin Doesn't Show Trailers

**Problem:** Libraries are empty after scanning.

**Solutions:**

1. **Verify directory structure:**
   ```bash
   ls -la /data/trailers/theatrical/
   ```
   
   Should show folders like `Movie (2026)/`

2. **Check file structure:**
   ```bash
   ls -la "/data/trailers/theatrical/Movie (2026)/"
   ```
   
   Should contain `.mp4` and `.nfo` files

3. **Verify Jellyfin can access the directory:**
   
   **For Docker:**
   ```yaml
   volumes:
     - /data/trailers/theatrical:/media/trailers:ro
   ```
   
   **Test access:**
   ```bash
   docker exec jellyfin ls -la /media/trailers
   ```

4. **Check permissions:**
   ```bash
   # Ensure Jellyfin user can read files
   chmod -R 755 /data/trailers
   ```

5. **Force library scan:**
   
   Dashboard → Libraries → [Trailer Library] → Scan Library

### NFO Files Not Being Read

**Problem:** Metadata is blank or incorrect.

**Solutions:**

1. **Check NFO provider is enabled:**
   
   Dashboard → Libraries → [Library] → Manage Library → Metadata Downloaders
   
   Ensure **NFO** is first in the list.

2. **Verify NFO file exists:**
   ```bash
   cat "/data/trailers/theatrical/Movie (2026)/movie.nfo"
   ```
   
   Should show XML content.

3. **Check NFO file format:**
   
   Must be valid XML with `<movie>` root element.

4. **Refresh metadata:**
   
   Right-click trailer → **Refresh Metadata** → **Replace all metadata**

### Trailers Have No Prefix

**Problem:** Titles don't show "Trailer - " prefix.

**Solutions:**

1. **Run fix-titles:**
   ```bash
   coming-attractions fix-titles --root-dir /data/trailers
   ```

2. **Verify NFO was updated:**
   ```bash
   grep "<title>" "/data/trailers/theatrical/Movie (2026)/movie.nfo"
   ```
   
   Should show: `<title>Trailer - Movie</title>`

3. **Refresh Jellyfin metadata:**
   
   Right-click trailer → **Refresh Metadata** → **Replace all metadata**

4. **For daemon mode, check metadata wait time:**
   ```yaml
   environment:
     - METADATA_WAIT_SECONDS=300
   ```
   
   May need to increase if Jellyfin is slow to generate NFO.

### Duplicate Entries

**Problem:** Same trailer appears multiple times.

**Solutions:**

1. **Check for duplicate folders:**
   ```bash
   ls -la /data/trailers/theatrical/ | grep "Movie (2026)"
   ```
   
   Remove duplicates.

2. **Check removed trailers file:**
   ```bash
   cat /data/trailers/.trailer-removed.txt
   ```
   
   Ensures Coming Attractions won't re-download.

3. **Clear Jellyfin library and rescan:**
   
   Dashboard → Libraries → [Library] → **Remove** → Re-add library → Scan

### TV Show Trailers Not Displaying Correctly

**Problem:** TV trailers show as movies or have wrong metadata.

**Solution:**

This is expected. TV show trailers are individual video files, not episodes of a series. Coming Attractions adds `[TV]` suffix to folder names:

```
Stranger Things S5 (2025) [TV]/
├── Stranger Things S5 (2025) [TV].mp4
└── movie.nfo
```

Jellyfin treats these as "movies" (individual videos) in your Streaming Trailers library. The `[TV]` suffix helps you identify which are TV shows.

### Real-Time Library Updates Not Working

**Problem:** New trailers don't appear until manual scan.

**Solutions:**

1. **Enable real-time monitoring (Linux):**
   
   Dashboard → Libraries → [Library] → Manage Library
   
   ✅ Enable **Real time monitoring**

2. **For Docker, may need host network mode:**
   ```yaml
   network_mode: host
   ```

3. **Or use scheduled scans:**
   
   Dashboard → Scheduled Tasks → **Scan Media Library**
   
   Set to run every 15-30 minutes.

### Performance Issues

**Problem:** Library scans are slow or Jellyfin is sluggish.

**Solutions:**

1. **Disable chapter image extraction:**
   
   Dashboard → Libraries → [Library] → Manage Library
   
   ❌ Disable **Extract chapter images during library scan**

2. **Limit video quality:**
   
   Trailers don't need 4K. Set Coming Attractions to 1080p:
   ```yaml
   environment:
     - MAX_HEIGHT=1080
   ```

3. **Increase metadata wait time (daemon):**
   
   Reduce scan frequency:
   ```yaml
   environment:
     - METADATA_WAIT_SECONDS=600  # 10 minutes
   ```

4. **Run Coming Attractions during off-hours:**
   
   Schedule daemon for low-traffic times:
   ```bash
   coming-attractions daemon --interval 24h  # Once daily
   ```

### Getting Help

For issues not covered here:

- Check [User Guide - Troubleshooting](USER_GUIDE.md#troubleshooting)
- Check [Docker Guide - Troubleshooting](DOCKER.md#troubleshooting)
- 🐛 [Report bugs](https://github.com/robertsinfosec/coming-attractions/issues)
- 💬 [Discussions](https://github.com/robertsinfosec/coming-attractions/discussions)

> **Navigation:**** [Home](../README.md) | [User Guide](USER_GUIDE.md) | [Docker Guide](DOCKER.md) | [Contributing](../CONTRIBUTING.md)
