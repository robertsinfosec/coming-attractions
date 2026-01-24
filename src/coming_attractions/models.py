"""Data models for trailer management."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Dict, List


class MediaType(str, Enum):
    """Media type enumeration."""
    MOVIE = "movie"
    TV = "tv"


class SkipReason(str, Enum):
    """Reasons for skipping trailer download."""
    NO_TITLE_OR_DATE = "no_title_or_date"
    BAD_DATE = "bad_date"
    OUT_OF_WINDOW = "out_of_window"
    NO_VIDEO = "no_video"
    DOWNLOAD_FAILED = "download_failed"
    DUPLICATE_TMDB_ID = "duplicate_tmdb_id"
    MISSING_MEDIA_TYPE = "missing_media_type"
    IN_REMOVED_LIST = "in_removed_list"
    ALREADY_EXISTS = "already_exists"


@dataclass
class Trailer:
    """Represents a downloaded or to-be-downloaded trailer."""
    tmdb_id: int
    media_type: MediaType
    title: str
    release_date: date
    folder_name: str
    youtube_url: str
    youtube_key: str
    picked_type: str  # "Trailer" or "Teaser"
    official: bool
    video_name: str = ""
    file_path: str = ""


@dataclass
class FetchStats:
    """Statistics for a trailer fetch operation."""
    added: int = 0
    skipped: int = 0
    skip_reasons: Dict[str, int] = field(default_factory=lambda: {
        reason.value: 0 for reason in SkipReason
    })
    
    def increment_skip(self, reason: SkipReason) -> None:
        """Increment skip counter for given reason."""
        self.skipped += 1
        self.skip_reasons[reason.value] += 1


@dataclass
class PruneStats:
    """Statistics for a trailer prune operation."""
    theatrical_scanned: int = 0
    streaming_scanned: int = 0
    total_removed: int = 0
    new_removed_added: int = 0
    
    @property
    def total_scanned(self) -> int:
        """Total folders scanned."""
        return self.theatrical_scanned + self.streaming_scanned


@dataclass
class TitleFixStats:
    """Statistics for title fixing operation."""
    total: int = 0
    fixed: int = 0
    skipped: int = 0
    failed: int = 0


@dataclass
class IndexData:
    """Index file data structure."""
    generated_at: datetime
    mode: str
    region: str
    days_ahead: int
    now_playing_days_back: int
    max_pages: int
    max_height: int
    feeds: Dict[str, bool]
    streaming: Dict[str, str]
    items: List[Dict]
