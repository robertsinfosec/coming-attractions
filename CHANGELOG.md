# Changelog

**Navigation**: [Home](README.md) > [Documentation](README.md#documentation) > Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of unified Python application
- Click-based CLI with four commands: fetch, prune, fix-titles, daemon
- Pydantic configuration models with validation
- Centralized logging with color-coded output
- TMDb API client with retry logic and rate limiting
- YouTube downloader wrapper with quality control
- Trailer fetcher with theatrical/streaming/both modes
- Trailer pruner with retention policies
- NFO title fixer with atomic operations
- Daemon mode for automated scheduling
- Docker multi-arch support (amd64, arm64)
- GitHub Actions workflow for CI/CD
- Comprehensive test suite with fixtures
- Migration guide from old scripts
- Legacy compatibility wrappers
- Environment variable support for all options
- Dry-run mode for all commands

### Changed
- Migrated from three separate scripts (Python + Bash) to unified Python application
- Improved error handling with specific exception types
- Enhanced logging with timestamps and file output support
- Atomic file operations to prevent data corruption
- Better skip reason tracking and statistics
- Unicode normalization for folder names
- ISO 8601 date parsing and validation

### Deprecated
- Old scripts (trailer-fetcher.py, trailer-pruner.sh, trailer-title-fixer.sh)
  - Still available via legacy wrappers during migration period
  - Will be removed in version 2.0.0

### Fixed
- Race conditions in file operations (using atomic writes)
- Inconsistent error messages across scripts
- Missing validation for configuration values
- Inadequate logging in error scenarios

### Security
- Input validation for all user-provided values
- Path sanitization to prevent directory traversal
- API key redaction in logs

## [1.0.0] - 2024-XX-XX

### Added
- First stable release
- Complete refactoring of original scripts
- Backward compatibility with existing data structures
- Full test coverage (>80%)
- Comprehensive documentation

## Version History

### Version 1.0.0 (Initial Release)

This release represents the complete refactoring of the original script-based approach into a unified CLI application.

#### Major Features

- Unified CLI application replacing three separate scripts
- Backward compatibility with existing trailer directories and `.trailer-removed.txt`
- Docker support with multi-architecture builds
- Automated daemon mode for scheduled operations
- Comprehensive logging and error handling

#### Components

The application provides four main commands:
- `coming-attractions fetch`: Download movie trailers from YouTube
- `coming-attractions prune`: Remove old trailers based on retention policy
- `coming-attractions fix-titles`: Add prefix to NFO file titles
- `coming-attractions daemon`: Run all tasks on schedule

#### Requirements

System dependencies needed to run the application:
- Python 3.11+
- ffmpeg (for video downloads)
- TMDb API key (free registration)

#### Migration

Upgrade path from legacy scripts:
- Legacy compatibility wrappers provided
- Gradual migration path supported
- No data loss during migration
- Same directory structure maintained

## Comparison with Old Scripts

| Feature               | Old Scripts       | New Application                              |
| --------------------- | ----------------- | -------------------------------------------- |
| **Languages**         | Python + Bash     | Pure Python                                  |
| **CLI Framework**     | Argparse + Manual | Click                                        |
| **Configuration**     | Env vars only     | Env vars + CLI + Pydantic                    |
| **Logging**           | Print statements  | Centralized Logger                           |
| **Error Handling**    | Basic try/except  | Comprehensive with retry                     |
| **Testing**           | None              | 80%+ coverage                                |
| **Atomic Operations** | No                | Yes                                          |
| **Type Safety**       | Minimal           | Full type hints                              |
| **Daemon Mode**       | External cron     | Built-in scheduler                           |
| **Docker Support**    | DIY               | Official multi-arch images                   |
| **Documentation**     | README only       | README + MIGRATION + CONTRIBUTING + QUICKREF |
| **CI/CD**             | None              | GitHub Actions                               |

## Migration Path

Gradual migration from old scripts to new application.

### Phase 1: Preparation (Week 1)
- Install new application alongside old scripts
- Run validation and compatibility tests
- Test with dry-run mode

### Phase 2: Parallel Running (Week 2-3)
- Run new application in parallel with old scripts
- Compare outputs and verify correctness
- Use legacy wrappers for gradual migration

### Phase 3: Switchover (Week 4)
- Disable old scripts
- Enable new application for production
- Monitor closely for issues

### Phase 4: Cleanup (Week 5+)
- Remove old cron jobs
- Archive old scripts
- Update documentation

## Known Issues

None at this time.

## Planned Features

See [GitHub Issues](https://github.com/robertsinfosec/coming-attractions/issues) for planned features and enhancements.

### Potential Future Enhancements
- Web UI for management
- Email notifications for new trailers
- Integration with Plex/Jellyfin libraries
- Support for TV show trailers
- Advanced filtering (genres, ratings, languages)
- Batch operations for bulk management
- Prometheus metrics export
- Health check endpoints

**Note**: This project follows [Semantic Versioning](https://semver.org/). For the versions available, see the [tags on this repository](https://github.com/robertsinfosec/coming-attractions/tags).
