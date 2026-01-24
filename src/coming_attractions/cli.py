"""Click-based CLI interface for coming-attractions."""

import os
import sys
import time
from pathlib import Path
from typing import Optional

import click

from coming_attractions import __version__
from coming_attractions.config import (
    FetchConfig,
    PruneConfig,
    TitleFixConfig,
)
from coming_attractions.fetcher import TrailerFetcher
from coming_attractions.logger import Logger
from coming_attractions.pruner import TrailerPruner
from coming_attractions.title_fixer import TitleFixer


def _create_logger(debug: bool, timestamps: bool, log_file: Optional[str]) -> Logger:
    """Create logger instance from CLI options."""
    log_path = Path(log_file) if log_file else None
    return Logger(
        timestamps=timestamps,
        debug=debug,
        log_file=log_path,
    )


def _countdown_sleep(seconds: int, message: str = "Sleeping") -> None:
    """Display countdown timer while sleeping."""
    try:
        for remaining in range(seconds, 0, -1):
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            secs = remaining % 60

            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            print(f"\r⏳ {message}: {time_str} remaining", end="", flush=True)
            time.sleep(1)

        print("\r" + " " * 80 + "\r", end="", flush=True)  # Clear line
    except KeyboardInterrupt:
        print("\n")
        raise


# Environment variable helpers
def env_or_option(
    env_var: str, option_value: Optional[str], default: Optional[str] = None
) -> Optional[str]:
    """Get value from environment or CLI option, with precedence to CLI."""
    if option_value is not None:
        return option_value
    return os.environ.get(env_var, default)


def env_or_option_int(env_var: str, option_value: Optional[int], default: int) -> int:
    """Get integer value from environment or CLI option."""
    if option_value is not None:
        return option_value
    return int(os.environ.get(env_var, str(default)))


def env_or_option_bool(env_var: str, option_value: bool, default: bool = False) -> bool:
    """Get boolean value from environment or CLI option."""
    if option_value:
        return True
    env_val = os.environ.get(env_var, "").strip().lower()
    return env_val in ("1", "true", "yes") if env_val else default


@click.group()
@click.version_option(version=__version__, prog_name="coming-attractions")
@click.pass_context
def cli(ctx):
    """
    Coming Attractions - Automated Jellyfin Upcoming Movie Trailer Management.

    Fetches, manages, and maintains upcoming movie trailers for Jellyfin media servers.
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--api-key",
    envvar="TMDB_API_KEY",
    required=True,
    help="TMDb API key (required)",
)
@click.option(
    "--mode",
    type=click.Choice(["theatrical", "streaming", "both"]),
    default=lambda: os.environ.get("MODE", "both"),
    help="Fetch mode: theatrical, streaming, or both",
)
@click.option(
    "--region",
    default=lambda: os.environ.get("TMDB_REGION", "US"),
    help="Region code (ISO 3166-1 alpha-2)",
)
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("OUT_DIR", "/data/trailers")),
    help="Output directory for trailers",
)
@click.option(
    "--days-ahead",
    type=int,
    default=lambda: env_or_option_int("DAYS_AHEAD", None, 180),
    help="Days ahead for upcoming window",
)
@click.option(
    "--days-back",
    type=int,
    default=lambda: env_or_option_int("DAYS_BACK", None, 90),
    help="Days back for now playing window",
)
@click.option(
    "--max-pages",
    type=int,
    default=lambda: env_or_option_int("MAX_PAGES", None, 5),
    help="Maximum pages to fetch per feed",
)
@click.option(
    "--max-height",
    type=int,
    default=lambda: env_or_option_int("MAX_HEIGHT", None, 1080),
    help="Maximum video height for downloads",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=lambda: env_or_option_bool("DRY_RUN", False),
    help="Show what would be done without making changes",
)
@click.option(
    "--debug",
    is_flag=True,
    default=lambda: env_or_option_bool("DEBUG", False),
    help="Enable debug logging",
)
@click.option(
    "--timestamps",
    is_flag=True,
    default=lambda: env_or_option_bool("LOG_TIMESTAMPS", False),
    help="Add timestamps to log output",
)
@click.option(
    "--log-file",
    type=str,
    default=lambda: os.environ.get("LOG_FILE"),
    help="Log to file (with full timestamps)",
)
def fetch(
    api_key: str,
    mode: str,
    region: str,
    out_dir: Path,
    days_ahead: int,
    days_back: int,
    max_pages: int,
    max_height: int,
    dry_run: bool,
    debug: bool,
    timestamps: bool,
    log_file: Optional[str],
):
    """Fetch upcoming trailers from TMDb and YouTube."""
    with _create_logger(debug, timestamps, log_file) as logger:

        try:
            config = FetchConfig(
                api_key=api_key,
                mode=mode,
                region=region,
                out_dir=out_dir,
                days_ahead=days_ahead,
                days_back=days_back,
                max_pages=max_pages,
                max_height=max_height,
                dry_run=dry_run,
            )

            fetcher = TrailerFetcher(config, logger)
            fetcher.fetch()

            sys.exit(0)

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            if debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)



@cli.command()
@click.option(
    "--retention-years",
    type=int,
    default=lambda: env_or_option_int("RETENTION_YEARS", None, 2),
    help="Years to retain trailers",
)
@click.option(
    "--theatrical-dir",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("THEATRICAL_DIR", "./theatrical")),
    help="Theatrical trailers directory",
)
@click.option(
    "--streaming-dir",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("STREAMING_DIR", "./streaming")),
    help="Streaming trailers directory",
)
@click.option(
    "--removed-file",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("REMOVED_FILE", "./.trailer-removed.txt")),
    help="File tracking removed trailers",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=lambda: env_or_option_bool("DRY_RUN", False),
    help="Show what would be removed without removing",
)
@click.option(
    "--force",
    is_flag=True,
    help="Non-interactive mode (for automation)",
)
@click.option(
    "--debug",
    is_flag=True,
    default=lambda: env_or_option_bool("DEBUG", False),
    help="Enable debug logging",
)
@click.option(
    "--timestamps",
    is_flag=True,
    default=lambda: env_or_option_bool("LOG_TIMESTAMPS", False),
    help="Add timestamps to log output",
)
@click.option(
    "--log-file",
    type=str,
    default=lambda: os.environ.get("LOG_FILE"),
    help="Log to file (with full timestamps)",
)
def prune(
    retention_years: int,
    theatrical_dir: Path,
    streaming_dir: Path,
    removed_file: Path,
    dry_run: bool,
    force: bool,
    debug: bool,
    timestamps: bool,
    log_file: Optional[str],
):
    """Remove trailers older than retention period."""
    with _create_logger(debug, timestamps, log_file) as logger:
        try:
            config = PruneConfig(
                retention_years=retention_years,
                theatrical_dir=theatrical_dir,
                streaming_dir=streaming_dir,
                removed_file=removed_file,
                dry_run=dry_run,
                force=force,
            )

            pruner = TrailerPruner(config, logger)
            pruner.prune()

            sys.exit(0)

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            if debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)


@cli.command()
@click.option(
    "--root-dir",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("ROOT_DIR", "/data/trailers")),
    help="Root directory to scan for theatrical/ and streaming/ subdirectories",
)
@click.option(
    "--prefix",
    default="Trailer - ",
    help="Prefix to add to titles",
)
@click.option(
    "--debug",
    is_flag=True,
    default=lambda: env_or_option_bool("DEBUG", False),
    help="Enable debug logging",
)
@click.option(
    "--timestamps",
    is_flag=True,
    default=lambda: env_or_option_bool("LOG_TIMESTAMPS", False),
    help="Add timestamps to log output",
)
@click.option(
    "--log-file",
    type=str,
    default=lambda: os.environ.get("LOG_FILE"),
    help="Log to file (with full timestamps)",
)
def fix_titles(
    root_dir: Path,
    prefix: str,
    debug: bool,
    timestamps: bool,
    log_file: Optional[str],
):
    """Add 'Trailer - ' prefix to movie titles in NFO files."""
    with _create_logger(debug, timestamps, log_file) as logger:
        try:
            config = TitleFixConfig(
                root_dir=root_dir,
                prefix=prefix,
            )

            fixer = TitleFixer(config, logger)
            fixer.fix_titles()

            sys.exit(0)

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            if debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)


@cli.command()
@click.option(
    "--interval",
    default="12h",
    help="Interval between runs (e.g., 12h, 6h, 1d)",
)
@click.option(
    "--metadata-wait",
    type=int,
    default=lambda: env_or_option_int("METADATA_WAIT_SECONDS", None, 300),
    help="Seconds to wait for Jellyfin metadata population",
)
@click.option(
    "--retention-years",
    type=int,
    default=lambda: env_or_option_int("RETENTION_YEARS", None, 2),
    help="Years to retain trailers (for pruning)",
)
@click.option(
    "--api-key",
    envvar="TMDB_API_KEY",
    required=True,
    help="TMDb API key (required)",
)
@click.option(
    "--debug",
    is_flag=True,
    default=lambda: env_or_option_bool("DEBUG", False),
    help="Enable debug logging",
)
@click.option(
    "--timestamps",
    is_flag=True,
    default=lambda: env_or_option_bool("LOG_TIMESTAMPS", False),
    help="Add timestamps to log output",
)
@click.option(
    "--log-file",
    type=str,
    default=lambda: os.environ.get("LOG_FILE"),
    help="Log to file (with full timestamps)",
)
@click.pass_context
def daemon(
    ctx,
    interval: str,
    metadata_wait: int,
    retention_years: int,
    api_key: str,
    debug: bool,
    timestamps: bool,
    log_file: Optional[str],
):
    """Run continuous daemon mode with configured interval."""
    logger = _create_logger(debug, timestamps, log_file)

    # Parse interval
    interval_seconds = _parse_interval(interval)
    if interval_seconds is None:
        logger.error(
            f"Invalid interval format: {interval}. Use formats like '12h', '6h', '1d'"
        )
        sys.exit(1)

    logger.info(f"Starting daemon mode with {interval} ({interval_seconds}s) interval")
    logger.info(f"Metadata wait: {metadata_wait}s")
    logger.info(f"Retention: {retention_years} years")

    try:
        while True:
            logger.info("=" * 64)
            logger.info("Starting new daemon cycle")
            logger.info("=" * 64)

            # Step 1: Prune old trailers
            logger.info("Step 1: Pruning old trailers...")
            ctx.invoke(
                prune,
                retention_years=retention_years,
                theatrical_dir=Path("./theatrical"),
                streaming_dir=Path("./streaming"),
                removed_file=Path("./.trailer-removed.txt"),
                dry_run=False,
                force=True,
                debug=debug,
                timestamps=timestamps,
                log_file=log_file,
            )

            _countdown_sleep(5, "Waiting before fetching")

            # Step 2: Fetch theatrical trailers
            logger.info("Step 2: Fetching theatrical trailers...")
            ctx.invoke(
                fetch,
                api_key=api_key,
                mode="theatrical",
                region=os.environ.get("TMDB_REGION", "US"),
                out_dir=Path("/data/trailers/theatrical"),
                days_ahead=180,
                days_back=90,
                max_pages=5,
                max_height=1080,
                dry_run=False,
                debug=debug,
                timestamps=timestamps,
                log_file=log_file,
            )

            _countdown_sleep(metadata_wait, "Waiting for Jellyfin metadata")

            # Step 3: Fix theatrical titles
            logger.info("Step 3: Fixing theatrical titles...")
            ctx.invoke(
                fix_titles,
                root_dir=Path("/data/trailers/theatrical"),
                prefix="Trailer - ",
                debug=debug,
                timestamps=timestamps,
                log_file=log_file,
            )

            # Step 4: Fetch streaming trailers
            logger.info("Step 4: Fetching streaming trailers...")
            ctx.invoke(
                fetch,
                api_key=api_key,
                mode="streaming",
                region=os.environ.get("TMDB_REGION", "US"),
                out_dir=Path("/data/trailers/streaming"),
                days_ahead=180,
                days_back=90,
                max_pages=5,
                max_height=1080,
                dry_run=False,
                debug=debug,
                timestamps=timestamps,
                log_file=log_file,
            )

            _countdown_sleep(metadata_wait, "Waiting for Jellyfin metadata")

            # Step 5: Fix streaming titles
            logger.info("Step 5: Fixing streaming titles...")
            ctx.invoke(
                fix_titles,
                root_dir=Path("/data/trailers/streaming"),
                prefix="Trailer - ",
                debug=debug,
                timestamps=timestamps,
                log_file=log_file,
            )

            # Sleep until next cycle
            logger.success(f"Daemon cycle complete. Sleeping for {interval}...")
            _countdown_sleep(interval_seconds, "Next cycle in")

    except KeyboardInterrupt:
        logger.info("\nDaemon interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in daemon: {e}")
        if debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        logger.close()


def _parse_interval(interval_str: str) -> Optional[int]:
    """
    Parse interval string to seconds.

    Supports: 1h, 12h, 1d, 300s, 5m

    Returns:
        Seconds or None if invalid
    """
    import re

    match = re.match(r"^(\d+)([smhd])$", interval_str.lower())
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    return value * multipliers[unit]


if __name__ == "__main__":
    cli()
