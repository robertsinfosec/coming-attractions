"""Trailer fetching logic - downloads trailers from TMDb and YouTube."""

import json
import shutil
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from coming_attractions.config import FetchConfig
from coming_attractions.logger import Logger
from coming_attractions.models import FetchStats, MediaType, SkipReason, Trailer
from coming_attractions.tmdb_client import TMDbClient
from coming_attractions.utils import (
    load_removed_trailers,
    parse_release_date,
    sanitize_folder_name,
    validate_directory_writable,
)
from coming_attractions.youtube_downloader import YouTubeDownloader


class TrailerFetcher:
    """
    Fetches movie and TV trailers from TMDb and YouTube.
    
    Supports two modes:
    - Theatrical: upcoming, now_playing, popular movie feeds
    - Streaming: discover API with provider filters (movies and TV)
    """
    
    def __init__(self, config: FetchConfig, logger: Logger):
        """
        Initialize trailer fetcher.
        
        Args:
            config: Fetch configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.stats = FetchStats()
        self.removed_folders = load_removed_trailers(config.removed_file)
        self.expected_folders: Set[str] = set()
        self.seen_ids: Set[str] = set()
    
    def fetch(self) -> FetchStats:
        """
        Execute trailer fetch operation.
        
        Returns:
            Statistics about the fetch operation
        """
        # Validate output directory
        try:
            validate_directory_writable(self.config.out_dir)
        except ValueError as e:
            self.logger.error(str(e))
            raise
        
        # Initialize clients
        with TMDbClient(self.config.api_key, self.logger) as tmdb_client:
            downloader = YouTubeDownloader(self.config.max_height, self.logger)
            
            # Fetch movies/TV shows based on mode
            items = self._fetch_items(tmdb_client)
            
            self.logger.info(f"Found {len(items)} items from TMDb")
            
            # Process each item
            for item in items:
                self._process_item(item, tmdb_client, downloader)
            
            # Write index file
            if not self.config.dry_run:
                self._write_index()
            
            # Optional pruning
            if self.config.prune:
                self._prune_folders()
        
        # Print summary
        self._print_summary()
        
        return self.stats
    
    def _fetch_items(self, tmdb_client: TMDbClient) -> List[Dict[str, Any]]:
        """Fetch items based on configured mode."""
        items = []
        
        if self.config.mode in ("theatrical", "both"):
            items.extend(self._fetch_theatrical(tmdb_client))
        
        if self.config.mode in ("streaming", "both"):
            items.extend(self._fetch_streaming(tmdb_client))
        
        return items
    
    def _fetch_theatrical(self, tmdb_client: TMDbClient) -> List[Dict[str, Any]]:
        """Fetch theatrical movies from TMDb feeds."""
        items = []
        
        if self.config.include_upcoming:
            self.logger.info("Fetching upcoming movies...")
            feed_items = tmdb_client.get_movie_feed(
                "upcoming",
                self.config.region,
                self.config.max_pages,
            )
            for item in feed_items:
                item["media_type"] = "movie"
            items.extend(feed_items)
            self.logger.info(f"  Found {len(feed_items)} items", indent=2)
        
        if self.config.include_now_playing:
            self.logger.info("Fetching now playing movies...")
            feed_items = tmdb_client.get_movie_feed(
                "now_playing",
                self.config.region,
                self.config.max_pages,
            )
            for item in feed_items:
                item["media_type"] = "movie"
            items.extend(feed_items)
            self.logger.info(f"  Found {len(feed_items)} items", indent=2)
        
        if self.config.include_popular:
            self.logger.info("Fetching popular movies...")
            feed_items = tmdb_client.get_movie_feed(
                "popular",
                self.config.region,
                self.config.max_pages,
            )
            for item in feed_items:
                item["media_type"] = "movie"
            items.extend(feed_items)
            self.logger.info(f"  Found {len(feed_items)} items", indent=2)
        
        return items
    
    def _fetch_streaming(self, tmdb_client: TMDbClient) -> List[Dict[str, Any]]:
        """Fetch streaming content via discover API."""
        items = []
        
        # Parse media types
        media_types = [mt.strip() for mt in self.config.media_types.split(",") if mt.strip()]
        
        # Convert provider list format
        providers = self.config.watch_providers.replace(",", "|") if self.config.watch_providers else None
        
        # Calculate date window
        today = date.today()
        start_date = (today - timedelta(days=self.config.days_back)).isoformat()
        end_date = (today + timedelta(days=self.config.days_ahead)).isoformat()
        
        for media_type in media_types:
            if media_type not in ("movie", "tv"):
                self.logger.warning(f"Unknown media type '{media_type}', skipping")
                continue
            
            self.logger.info(f"Discovering {media_type}s from streaming providers...")
            discovered = tmdb_client.discover(
                media_type=media_type,
                region=self.config.region,
                start_date=start_date,
                end_date=end_date,
                watch_providers=providers,
                watch_region=self.config.watch_region,
                max_pages=self.config.max_pages,
            )
            items.extend(discovered)
            self.logger.info(f"  Found {len(discovered)} items", indent=2)
        
        return items
    
    def _process_item(
        self,
        item: Dict[str, Any],
        tmdb_client: TMDbClient,
        downloader: YouTubeDownloader,
    ) -> None:
        """Process a single item (movie or TV show)."""
        # Extract basic info
        tmdb_id = item.get("id")
        media_type = item.get("media_type", "movie")
        
        # Get title and release date based on media type
        if media_type == "movie":
            title = item.get("title") or ""
            release_date_str = item.get("release_date") or ""
        elif media_type == "tv":
            title = item.get("name") or ""
            release_date_str = item.get("first_air_date") or ""
        else:
            self.stats.increment_skip(SkipReason.MISSING_MEDIA_TYPE)
            return
        
        # Validate required fields
        if not tmdb_id:
            self.stats.increment_skip(SkipReason.NO_TITLE_OR_DATE)
            return
        
        # Check for duplicates (unique ID = media_type + tmdb_id)
        unique_id = f"{media_type}_{tmdb_id}"
        if unique_id in self.seen_ids:
            self.stats.increment_skip(SkipReason.DUPLICATE_TMDB_ID)
            return
        self.seen_ids.add(unique_id)
        
        # Validate title and date
        if not title or not release_date_str:
            self.stats.increment_skip(SkipReason.NO_TITLE_OR_DATE)
            return
        
        # Parse release date
        try:
            release_date = parse_release_date(release_date_str)
        except ValueError:
            self.stats.increment_skip(SkipReason.BAD_DATE)
            return
        
        # Check date window
        if not self._in_date_window(release_date):
            self.stats.increment_skip(SkipReason.OUT_OF_WINDOW)
            return
        
        # Get videos (trailers/teasers)
        try:
            videos = tmdb_client.get_videos(media_type, tmdb_id)
        except Exception as e:
            self.logger.debug(f"Failed to fetch videos for {title}: {e}")
            self.stats.increment_skip(SkipReason.NO_VIDEO)
            return
        
        # Pick best trailer
        video = self._pick_best_video(videos)
        if not video:
            self.stats.increment_skip(SkipReason.NO_VIDEO)
            return
        
        youtube_url = f"https://www.youtube.com/watch?v={video['key']}"
        
        # Generate folder name
        folder_name = self._generate_folder_name(title, release_date.year, media_type)
        
        # Check if previously removed
        if folder_name in self.removed_folders:
            self.logger.info(f"Skipping: removed. {folder_name}")
            self.stats.increment_skip(SkipReason.IN_REMOVED_LIST)
            return
        
        # Check if already exists
        folder_path = self.config.out_dir / folder_name
        output_path = folder_path / f"{folder_name}.mp4"
        
        if output_path.exists() and output_path.stat().st_size > 0:
            self.logger.info(f"Skipping: exists. {folder_name}")
            self.expected_folders.add(folder_name)
            self.stats.added += 1
            self.stats.increment_skip(SkipReason.ALREADY_EXISTS)
            return
        
        # Download trailer
        self._download_trailer(
            folder_name=folder_name,
            folder_path=folder_path,
            output_path=output_path,
            youtube_url=youtube_url,
            downloader=downloader,
            tmdb_id=tmdb_id,
            media_type=media_type,
        )
    
    def _in_date_window(self, release_date: date) -> bool:
        """Check if release date is within configured window."""
        today = date.today()
        start = today - timedelta(days=self.config.days_back)
        end = today + timedelta(days=self.config.days_ahead)
        return start <= release_date <= end
    
    def _pick_best_video(self, videos: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Pick best trailer from list of videos.
        
        Priority:
        1. Official YouTube Trailer
        2. Any YouTube Trailer
        3. Official YouTube Teaser
        4. Any YouTube Teaser
        """
        # Filter to YouTube trailers/teasers
        youtube_videos = [
            v for v in videos
            if v.get("site") == "YouTube"
            and v.get("key")
            and v.get("type") in ("Trailer", "Teaser")
        ]
        
        if not youtube_videos:
            return None
        
        # Score videos
        def score(v):
            s = 0
            if v.get("type") == "Trailer":
                s += 100
            if v.get("official") is True:
                s += 10
            return s
        
        # Sort by score (highest first) and return best
        youtube_videos.sort(key=score, reverse=True)
        return youtube_videos[0]
    
    def _generate_folder_name(self, title: str, year: int, media_type: str) -> str:
        """Generate sanitized folder name."""
        # Add [TV] suffix for TV shows
        if media_type == "tv":
            base_name = f"{title} ({year}) [TV]"
        else:
            base_name = f"{title} ({year})"
        
        return sanitize_folder_name(base_name)
    
    def _download_trailer(
        self,
        folder_name: str,
        folder_path: Path,
        output_path: Path,
        youtube_url: str,
        downloader: YouTubeDownloader,
        tmdb_id: int,
        media_type: str,
    ) -> None:
        """Download a trailer."""
        # Dry-run: just log
        if self.config.dry_run:
            self.logger.warning(f"[DRY-RUN] Would download: {folder_name}")
            self.logger.info(f"  YouTube URL: {youtube_url}", indent=2)
            self.expected_folders.add(folder_name)
            self.stats.added += 1
            return
        
        # Create folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Write TMDb ID sidecar
        tmdb_id_file = folder_path / ".tmdb_id"
        tmdb_id_file.write_text(f"{media_type}:{tmdb_id}\n", encoding="utf-8")
        
        # Log download
        self.logger.info(f"Downloading: {folder_name}")
        self.logger.info(f"  YouTube URL: {youtube_url}", indent=2)
        
        # Download
        success = downloader.download(youtube_url, output_path)
        
        if not success or not output_path.exists() or output_path.stat().st_size == 0:
            self.logger.warning("  Download produced no file, cleaning up.", indent=2)
            shutil.rmtree(folder_path, ignore_errors=True)
            self.stats.increment_skip(SkipReason.DOWNLOAD_FAILED)
            return
        
        self.logger.success(f"  Downloaded: {folder_name}", indent=2)
        self.expected_folders.add(folder_name)
        self.stats.added += 1
        
        # Sleep between downloads
        if self.config.sleep_between_downloads > 0:
            time.sleep(self.config.sleep_between_downloads)
    
    def _write_index(self) -> None:
        """Write index JSON file."""
        index_path = self.config.out_dir / "_index.json"
        
        index_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": self.config.mode,
            "region": self.config.region,
            "days_ahead": self.config.days_ahead,
            "now_playing_days_back": self.config.days_back,
            "max_pages": self.config.max_pages,
            "max_height": self.config.max_height,
            "feeds": {
                "upcoming": self.config.include_upcoming if self.config.mode in ("theatrical", "both") else False,
                "now_playing": self.config.include_now_playing if self.config.mode in ("theatrical", "both") else False,
                "popular": self.config.include_popular if self.config.mode in ("theatrical", "both") else False,
            },
            "streaming": {
                "enabled": self.config.mode in ("streaming", "both"),
                "media_types": self.config.media_types if self.config.mode in ("streaming", "both") else "",
                "watch_providers": self.config.watch_providers if self.config.mode in ("streaming", "both") else "",
                "watch_region": self.config.watch_region if self.config.mode in ("streaming", "both") else "",
            },
            "items": [],
        }
        
        # Write atomically
        temp_path = index_path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(index_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp_path.replace(index_path)
    
    def _prune_folders(self) -> None:
        """Remove folders not in expected set."""
        if self.config.dry_run:
            self.logger.warning("[DRY-RUN] Prune enabled but no folders will be removed")
            return
        
        for item in self.config.out_dir.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith("_"):
                continue
            if item.name not in self.expected_folders:
                shutil.rmtree(item, ignore_errors=True)
    
    def _print_summary(self) -> None:
        """Print operation summary."""
        self.logger.separator()
        if self.config.dry_run:
            self.logger.warning("DRY-RUN MODE - No downloads or changes were made")
            self.logger.separator()
        
        self.logger.info("Trailer Fetcher Summary")
        self.logger.separator()
        self.logger.info(f"Mode: {self.config.mode}")
        self.logger.info(f"Region: {self.config.region}")
        self.logger.info(f"Window: {self.config.days_back} days back, {self.config.days_ahead} days ahead")
        self.logger.info("")
        self.logger.success(f"Present/Downloaded: {self.stats.added}")
        self.logger.info(f"Skipped: {self.stats.skipped}")
        self.logger.info("")
        self.logger.info("Skip reasons:")
        for reason, count in self.stats.skip_reasons.items():
            if count > 0:
                self.logger.info(f"  {reason.replace('_', ' ').title()}: {count}", indent=2)
        self.logger.success("Trailer fetching complete.")
