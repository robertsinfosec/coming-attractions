"""Configuration models using Pydantic for type-safe validation."""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class FetchConfig(BaseModel):
    """Configuration for trailer fetching."""

    api_key: str = Field(..., min_length=32, description="TMDb API key")
    mode: Literal["theatrical", "streaming", "both"] = Field(
        default="both", description="Fetch mode: theatrical, streaming, or both"
    )
    region: str = Field(
        default="US",
        pattern=r"^[A-Z]{2}$",
        description="Region code (ISO 3166-1 alpha-2)",
    )
    out_dir: Path = Field(
        default=Path("/data/trailers"),
        description="Output directory for trailers (theatrical/ and streaming/ created inside)",
    )

    # Date window configuration
    days_ahead: int = Field(
        default=180, ge=1, le=365, description="Days ahead for upcoming window"
    )
    days_back: int = Field(
        default=90, ge=0, le=365, description="Days back for now playing window"
    )

    # Pagination and quality
    max_pages: int = Field(
        default=5, ge=1, le=20, description="Maximum pages to fetch per feed"
    )
    max_height: int = Field(
        default=1080, ge=480, le=4320, description="Maximum video height for downloads"
    )

    # Theatrical mode settings
    include_upcoming: bool = Field(
        default=True, description="Include upcoming feed (theatrical mode)"
    )
    include_now_playing: bool = Field(
        default=True, description="Include now playing feed (theatrical mode)"
    )
    include_popular: bool = Field(
        default=True, description="Include popular feed (theatrical mode)"
    )

    # Streaming mode settings
    media_types: str = Field(
        default="movie,tv", description="Media types for streaming (comma-separated)"
    )
    watch_providers: str = Field(
        default="8,9,337,384,15,350,531,386,37,43",
        description="Streaming provider IDs (comma-separated)",
    )
    watch_region: str = Field(
        default="US",
        pattern=r"^[A-Z]{2}$",
        description="Region for streaming availability",
    )

    # Operational settings
    sleep_between_downloads: float = Field(
        default=0.25, ge=0, description="Sleep seconds between downloads"
    )
    prune: bool = Field(default=False, description="Remove folders not in current run")
    dry_run: bool = Field(
        default=False, description="Show what would be done without making changes"
    )

    # Tracking
    removed_file: Path = Field(
        default=Path("/data/trailers/.trailer-removed.txt"),
        description="File tracking removed trailers (stored in trailer root directory)",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if not v or not v.strip():
            raise ValueError("TMDB_API_KEY cannot be empty")
        return v.strip()

    @field_validator("out_dir", "removed_file", mode="before")
    @classmethod
    def expand_path(cls, v):
        """Expand environment variables and user home in paths."""
        if isinstance(v, str):
            return Path(os.path.expandvars(os.path.expanduser(v)))
        return v


class PruneConfig(BaseModel):
    """Configuration for trailer pruning."""

    retention_years: int = Field(
        default=2, ge=1, description="Years to retain trailers"
    )
    theatrical_dir: Path = Field(
        default=Path("./theatrical"), description="Theatrical trailers directory"
    )
    streaming_dir: Path = Field(
        default=Path("./streaming"), description="Streaming trailers directory"
    )
    removed_file: Path = Field(
        default=Path("/data/trailers/.trailer-removed.txt"),
        description="File tracking removed trailers (stored in trailer root directory)",
    )
    dry_run: bool = Field(
        default=False, description="Show what would be removed without removing"
    )
    force: bool = Field(
        default=False, description="Non-interactive mode (auto-install dependencies)"
    )

    @field_validator("theatrical_dir", "streaming_dir", "removed_file", mode="before")
    @classmethod
    def expand_path(cls, v):
        """Expand environment variables and user home in paths."""
        if isinstance(v, str):
            return Path(os.path.expandvars(os.path.expanduser(v)))
        return v


class TitleFixConfig(BaseModel):
    """Configuration for title fixing."""

    root_dir: Path = Field(
        default=Path("/data/trailers"),
        description="Root directory to scan for theatrical/ and streaming/ subdirectories",
    )
    prefix: str = Field(default="Trailer - ", description="Prefix to add to titles")
    nfo_name: str = Field(default="movie.nfo", description="NFO filename to process")

    @field_validator("root_dir", mode="before")
    @classmethod
    def expand_path(cls, v):
        """Expand environment variables and user home in paths."""
        if isinstance(v, str):
            return Path(os.path.expandvars(os.path.expanduser(v)))
        return v


class DaemonConfig(BaseModel):
    """Configuration for daemon mode."""

    interval_hours: int = Field(
        default=12, ge=1, le=168, description="Hours between daemon runs"  # Max 1 week
    )
    metadata_wait_seconds: int = Field(
        default=300,  # 5 minutes
        ge=0,
        description="Seconds to wait for Jellyfin metadata population",
    )
    retention_years: int = Field(
        default=2, ge=1, description="Years to retain trailers (for pruning)"
    )
