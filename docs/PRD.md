# Product Requirements Document (PRD)

## Coming Attractions - Automated Movie Trailer Management System

**Version**: 1.0  
**Status**: Active Development  
**Last Updated**: January 23, 2026  
**Owner**: robertsinfosec  

---

## Executive Summary

Coming Attractions is a Python-based automation system that discovers, downloads, and manages movie trailers for home media servers. It integrates with The Movie Database (TMDb) API for content discovery and YouTube for video downloads, maintaining a well-organized library with automated retention policies.

### Problem Statement

Home media server enthusiasts want to automatically populate their libraries with trailers for upcoming theatrical and streaming releases. Manually searching, downloading, and organizing trailers is time-consuming and error-prone. Existing solutions are either proprietary, platform-specific, or lack proper metadata management.

### Solution

A professional, open-source Python application that:
- Automatically discovers upcoming movie releases via TMDb API
- Downloads high-quality trailers from YouTube
- Generates proper metadata (NFO files) for media server integration
- Enforces retention policies to remove outdated trailers
- Maintains consistent naming and organization
- Runs as a daemon for hands-off automation

---

## Objectives and Goals

### Primary Objectives

1. **Automation**: Zero-touch trailer management for home media servers
2. **Quality**: Professional-grade code following Python best practices (PEP 8)
3. **Reliability**: Robust error handling, retry logic, atomic operations
4. **Compatibility**: Works with existing Plex/Jellyfin/Emby/Kodi installations
5. **Maintainability**: Well-documented, tested, and extensible codebase

### Success Metrics

- **Code Quality**: ≥80% test coverage, zero PEP 8 violations
- **Reliability**: <1% failure rate for valid trailer downloads
- **Performance**: Process 100+ trailers in <10 minutes
- **Usability**: Setup time <15 minutes for new users
- **Community**: Active GitHub repository with documentation and examples

### Non-Goals (Out of Scope)

- TV show trailers (may be added in v2.0)
- Video encoding/transcoding (rely on source quality)
- Media server API integration (use filesystem monitoring instead)
- Web UI (CLI and daemon mode sufficient for v1.0)
- Support for non-YouTube video sources (future enhancement)

---

## User Personas

### Primary: Alex - Home Lab Enthusiast

**Background**: Runs Plex server at home with 10TB media library  
**Technical Level**: Intermediate (comfortable with Docker, command-line)  
**Needs**:
- Automatic trailer updates without manual intervention
- Integration with existing Plex library structure
- Low maintenance overhead
- Quality control (1080p preferred, no 4K waste)

**Pain Points**:
- Manually searching for trailers takes hours per month
- Inconsistent naming breaks Plex metadata matching
- Forgot to remove old trailers, wasting disk space
- Previous bash scripts were fragile and hard to debug

### Secondary: Sam - Self-Hosting Advocate

**Background**: Open-source enthusiast running Jellyfin on Raspberry Pi  
**Technical Level**: Advanced (writes Python, contributes to FOSS)  
**Needs**:
- Complete control over scheduling and configuration
- Clear, documented codebase for customization
- Docker support for easy deployment
- ARM64 compatibility for Pi

**Pain Points**:
- Proprietary solutions don't respect privacy
- Existing tools lack proper error handling
- No visibility into what's happening (logging)
- Can't contribute improvements back to community

### Tertiary: Jordan - DevOps Professional

**Background**: Runs media center as part of homelab learning environment  
**Technical Level**: Expert (Kubernetes, CI/CD, monitoring)  
**Needs**:
- Containerized deployment with health checks
- Prometheus metrics (future)
- Structured logging for aggregation
- GitOps-friendly configuration

**Pain Points**:
- Scripts don't fit into modern DevOps workflows
- No observability (metrics, traces)
- Hard to troubleshoot in production
- Can't use existing monitoring infrastructure

---

## Features and Requirements

### Must-Have (MVP - v1.0)

#### Feature 1: Trailer Discovery and Download

**Description**: Fetch upcoming movie trailers from TMDb and download from YouTube

**Requirements**:
- FR-1.1: Support TMDb API for movie discovery
- FR-1.2: Filter by release date window (configurable days ahead/back)
- FR-1.3: Filter by region (default: US)
- FR-1.4: Support three modes: theatrical, streaming, both
- FR-1.5: Select best available trailer (official trailer > trailer > teaser)
- FR-1.6: Download up to 1080p quality (configurable max)
- FR-1.7: Generate NFO files with metadata (title, plot, release date, etc.)
- FR-1.8: Skip existing folders to avoid re-downloading
- FR-1.9: Track skipped trailers with reason codes
- FR-1.10: Dry-run mode for testing

**Acceptance Criteria**:
- Successfully fetches theatrical releases for US region
- Downloads official trailers when available
- Creates proper NFO file structure
- Skips already-downloaded trailers
- Handles API errors gracefully (retry with exponential backoff)

#### Feature 2: Retention Policy Enforcement

**Description**: Automatically remove trailers after movies release

**Requirements**:
- FR-2.1: Configurable retention period (default: 2 years post-release)
- FR-2.2: Extract release date from NFO files (4 fallback methods)
- FR-2.3: Support both theatrical and streaming directories
- FR-2.4: Maintain audit log of removed trailers
- FR-2.5: Atomic updates to removal tracking file
- FR-2.6: Force mode with confirmation to prevent accidents
- FR-2.7: Dry-run mode to preview deletions
- FR-2.8: Report disk space freed

**Acceptance Criteria**:
- Correctly identifies trailers past retention date
- Removes trailers only after confirmation (unless --force)
- Updates .trailer-removed.txt atomically
- Handles missing NFO files gracefully
- Reports accurate statistics

#### Feature 3: NFO Title Standardization

**Description**: Add consistent prefix to trailer titles in NFO files

**Requirements**:
- FR-3.1: Configurable title prefix (default: "Trailer - ")
- FR-3.2: Recursive directory scanning
- FR-3.3: XML-safe updates with validation
- FR-3.4: Atomic file writes (temp + rename)
- FR-3.5: Skip already-prefixed titles
- FR-3.6: Preserve XML structure and encoding
- FR-3.7: Report statistics (updated, skipped, errors)

**Acceptance Criteria**:
- Adds prefix to unprefixed titles
- Skips titles already prefixed
- Maintains valid XML structure
- No data corruption or truncation
- Handles malformed XML gracefully

#### Feature 4: CLI Interface

**Description**: Professional command-line interface using Click

**Requirements**:
- FR-4.1: Four commands: fetch, prune, fix-titles, daemon
- FR-4.2: Consistent option naming (kebab-case)
- FR-4.3: Environment variable support for all options
- FR-4.4: Help text for all commands and options
- FR-4.5: Debug logging flag
- FR-4.6: Dry-run support where applicable
- FR-4.7: Color-coded output ([*] info, [+] success, [-] error, [!] warning)
- FR-4.8: Optional log file output
- FR-4.9: Optional timestamps in logs

**Acceptance Criteria**:
- All commands accessible via `coming-attractions <command>`
- Help text is clear and complete
- Environment variables override defaults
- CLI options override environment variables
- Output is readable and informative

#### Feature 5: Daemon Mode

**Description**: Run all operations on a schedule for automation

**Requirements**:
- FR-5.1: Configurable intervals for each task (e.g., 12h, 6h, 1d)
- FR-5.2: Enable/disable individual tasks
- FR-5.3: Countdown display between runs
- FR-5.4: Graceful shutdown (SIGTERM, SIGINT)
- FR-5.5: Continuous operation with error recovery
- FR-5.6: All CLI options available in daemon mode
- FR-5.7: Log output for each run

**Acceptance Criteria**:
- Runs fetch/prune/fix on schedule
- Handles errors without crashing
- Shuts down cleanly on signal
- Logs all operations
- Resumes after temporary failures

### Should-Have (v1.1)

- FR-6: Prometheus metrics export
- FR-7: Email notifications for errors
- FR-8: Genre/rating filtering
- FR-9: Multiple language support
- FR-10: Bandwidth throttling

### Could-Have (v2.0)

- FR-11: Web UI for management
- FR-12: TV show trailer support
- FR-13: Direct Plex/Jellyfin API integration
- FR-14: Custom trailer sources (beyond YouTube)
- FR-15: Advanced scheduling (cron expressions)

### Won't-Have

- FR-X1: Video transcoding/re-encoding
- FR-X2: Subtitle downloading
- FR-X3: Social features (sharing, ratings)
- FR-X4: Blockchain/NFT integration

---

## Technical Requirements

### Architecture

**Design Principles**:
- Modular design (separate concerns: API, download, metadata, CLI)
- Dependency injection (pass config/logger to classes)
- Atomic operations (file writes are temp + rename)
- Fail-fast validation (Pydantic models)
- Comprehensive logging (debug/info/warning/error levels)

**Technology Stack**:
- **Language**: Python 3.11+ (type hints, dataclasses)
- **CLI Framework**: Click 8.1.7+
- **Config Validation**: Pydantic 2.5.0+
- **HTTP Client**: requests 2.31.0+
- **Retry Logic**: tenacity 8.2.3+
- **Video Download**: yt-dlp (latest)
- **Testing**: pytest + responses
- **Containerization**: Docker (multi-stage, multi-arch)

**System Architecture**:
```
┌─────────────────┐
│   CLI (Click)   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Config  │ (Pydantic validation)
    └────┬─────┘
         │
    ┌────▼──────────────────────────┐
    │  Business Logic Layer         │
    ├───────────┬───────────┬───────┤
    │  Fetcher  │  Pruner   │ Fixer │
    └─────┬─────┴─────┬─────┴───┬───┘
          │           │         │
    ┌─────▼───┐  ┌────▼────┐  ┌▼──────┐
    │ TMDb API│  │ File I/O│  │XML Ops│
    └─────┬───┘  └────┬────┘  └┬──────┘
          │           │         │
    ┌─────▼───────────▼─────────▼───┐
    │   YouTube (yt-dlp)            │
    └───────────────────────────────┘
```

### Performance Requirements

- **PR-1**: Process 100 trailers in ≤10 minutes (avg 6s each)
- **PR-2**: API rate limit compliance (40 requests/10 seconds for TMDb)
- **PR-3**: Memory usage ≤512MB during normal operation
- **PR-4**: Startup time ≤2 seconds
- **PR-5**: Graceful degradation on slow networks

### Reliability Requirements

- **RR-1**: Retry failed API calls up to 3 times with exponential backoff
- **RR-2**: Atomic file operations prevent data corruption
- **RR-3**: Validate all inputs (Pydantic, path checks)
- **RR-4**: Handle missing/malformed data gracefully
- **RR-5**: No data loss on crash (atomic writes, journaling)

### Security Requirements

- **SR-1**: Never log API keys or credentials
- **SR-2**: Validate all external inputs (API responses, file paths)
- **SR-3**: Sanitize folder names to prevent path traversal
- **SR-4**: Run as non-root user in Docker
- **SR-5**: Use GitHub Advanced Security (CodeQL, Dependabot, Secret Scanning)

### Testing Requirements

- **TR-1**: Minimum 80% code coverage
- **TR-2**: Unit tests for all utilities and business logic
- **TR-3**: Integration tests for API clients (mocked)
- **TR-4**: Fixtures for common test scenarios
- **TR-5**: CI/CD runs tests on every PR

### Documentation Requirements

- **DR-1**: README with quickstart guide
- **DR-2**: Migration guide from old scripts
- **DR-3**: API documentation (docstrings)
- **DR-4**: Style guide (PEP 8 compliance)
- **DR-5**: Contributing guidelines
- **DR-6**: Changelog (semantic versioning)

---

## User Stories

### Epic 1: Setup and Configuration

**US-1.1**: As a new user, I want to install the application with pip so I can start using it quickly.  
**AC**: `pip install -e .` works, `coming-attractions --help` shows usage

**US-1.2**: As a user, I want to configure via environment variables so I don't expose secrets in command history.  
**AC**: All options available as env vars, `.env.example` provided

**US-1.3**: As a user, I want clear error messages when configuration is invalid so I can fix issues quickly.  
**AC**: Pydantic validation errors are readable, suggest fixes

### Epic 2: Trailer Discovery

**US-2.1**: As a user, I want to fetch upcoming theatrical releases so my Plex library stays current.  
**AC**: Fetch command downloads trailers for US theatrical releases in next 365 days

**US-2.2**: As a user, I want to filter by release date window so I control how far ahead to look.  
**AC**: `--days-ahead` and `--days-back` options work correctly

**US-2.3**: As a user, I want to skip existing trailers so I don't waste bandwidth.  
**AC**: Existing folders are detected and skipped, logged appropriately

**US-2.4**: As a user, I want to see why trailers were skipped so I can troubleshoot issues.  
**AC**: Statistics show counts for each skip reason (no trailer, outside window, etc.)

### Epic 3: Trailer Cleanup

**US-3.1**: As a user, I want to automatically remove old trailers so I don't waste disk space.  
**AC**: Prune command removes trailers >2 years after release

**US-3.2**: As a user, I want to preview deletions before committing so I can verify correctness.  
**AC**: Dry-run mode shows what would be deleted without actually deleting

**US-3.3**: As a user, I want to track removed trailers so I don't re-download them.  
**AC**: .trailer-removed.txt is updated atomically with all deletions

### Epic 4: Automation

**US-4.1**: As a user, I want to run the application on a schedule so I don't have to remember.  
**AC**: Daemon mode runs fetch/prune/fix on configurable intervals

**US-4.2**: As a user, I want the daemon to recover from errors so temporary issues don't stop automation.  
**AC**: Daemon continues running after API errors, network issues, etc.

**US-4.3**: As a user, I want to stop the daemon gracefully so I don't corrupt data.  
**AC**: SIGTERM/SIGINT trigger clean shutdown, finish current operation

### Epic 5: Container Deployment

**US-5.1**: As a user, I want to run in Docker so I have a consistent environment.  
**AC**: Official Docker images available for amd64 and arm64

**US-5.2**: As a user, I want Docker Compose support so I can integrate with my homelab stack.  
**AC**: docker-compose.yml provided with examples

**US-5.3**: As a user, I want the container to run as non-root so it's more secure.  
**AC**: Dockerfile uses non-root user, works with rootless Docker

---

## Dependencies and Integrations

### External APIs

1. **TMDb API** (themoviedb.org)
   - **Purpose**: Movie discovery, metadata
   - **Authentication**: API key (free tier)
   - **Rate Limits**: 40 requests/10 seconds
   - **Dependency Level**: Critical (core functionality)

2. **YouTube** (via yt-dlp)
   - **Purpose**: Video downloads
   - **Authentication**: None (public videos)
   - **Rate Limits**: Soft limits, handled by yt-dlp
   - **Dependency Level**: Critical (core functionality)

### Media Servers (Indirect)

- **Plex**: Via filesystem monitoring (no direct API)
- **Jellyfin**: Via filesystem monitoring
- **Emby**: Via filesystem monitoring
- **Kodi**: Via NFO file support

### Development Tools

- **GitHub Actions**: CI/CD automation
- **CodeQL**: Security scanning
- **Dependabot**: Dependency updates
- **Docker Hub/GHCR**: Container registry

---

## Risks and Mitigations

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TMDb API changes | Medium | High | Version API calls, monitor changelogs, retry logic |
| YouTube blocks yt-dlp | Medium | Critical | Keep yt-dlp updated, consider alternative sources v2.0 |
| Rate limiting | High | Medium | Respect limits, exponential backoff, queue requests |
| Disk space exhaustion | Low | Medium | Retention policies, monitoring, user alerts |
| Data corruption | Low | High | Atomic operations, backups, validation |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User misconfiguration | High | Low | Validation, good defaults, clear error messages |
| Network failures | High | Low | Retry logic, timeout handling, graceful degradation |
| Dependency vulnerabilities | Medium | Medium | Dependabot, regular updates, security scanning |
| Breaking changes in updates | Medium | Medium | Semantic versioning, changelog, migration guides |

---

## Timeline and Milestones

### Phase 1: MVP (Complete)

- ✅ Core Python package structure
- ✅ CLI with 4 commands
- ✅ Fetcher, pruner, title fixer
- ✅ Basic tests
- ✅ Docker support
- ✅ Documentation

### Phase 2: Quality & Security (In Progress)

- 🔄 Repository reorganization (GitHub-first structure)
- 🔄 GitHub Advanced Security setup
- 🔄 Enhanced documentation (PRD, style guide)
- ⏳ Test coverage to 80%+
- ⏳ CI/CD improvements
- ⏳ Migration from old scripts validation

### Phase 3: v1.0 Release

- ⏳ Beta testing with users
- ⏳ Bug fixes and polish
- ⏳ Performance optimization
- ⏳ Release announcement
- ⏳ Public GitHub repository

### Phase 4: v1.1 Enhancements

- ⏳ Prometheus metrics
- ⏳ Email notifications
- ⏳ Advanced filtering
- ⏳ Community feedback integration

---

## Open Questions

1. **Q**: Should we support authentication for private YouTube playlists?  
   **A**: Defer to v2.0 - complexity not worth it for MVP

2. **Q**: How to handle trailers >1080p (4K, 8K)?  
   **A**: Make max resolution configurable, default 1080p for bandwidth

3. **Q**: Support for non-English trailers?  
   **A**: Yes via TMDb language parameter, document in v1.1

4. **Q**: What about trailers split across multiple videos?  
   **A**: Download first video only for MVP, consider playlist support v2.0

5. **Q**: Integration with Sonarr/Radarr?  
   **A**: Future consideration - would require API integration

---

## Approval and Sign-off

**Document Status**: Draft  
**Approved By**: TBD  
**Date**: TBD  

---

## Appendix

### Glossary

- **NFO**: XML metadata file used by media servers (Kodi format)
- **TMDb**: The Movie Database - open movie metadata API
- **yt-dlp**: YouTube downloader CLI tool (youtube-dl fork)
- **Retention Policy**: Rules for when to delete old trailers
- **Atomic Operation**: File write that completes fully or not at all
- **Daemon Mode**: Background process running continuously

### References

- TMDb API Docs: https://developers.themoviedb.org/
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- Click Docs: https://click.palletsprojects.com/
- Pydantic Docs: https://docs.pydantic.dev/
- PEP 8: https://pep8.org/

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-23 | robertsinfosec | Initial PRD creation |
