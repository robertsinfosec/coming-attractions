"""Trailer pruning logic - removes old trailers based on retention policy."""

import re
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

from coming_attractions.config import PruneConfig
from coming_attractions.logger import Logger
from coming_attractions.models import PruneStats
from coming_attractions.utils import (
    add_to_removed_trailers,
    deduplicate_removed_trailers,
    load_removed_trailers,
)


class TrailerPruner:
    """
    Prunes old trailers based on retention policy.
    
    Scans theatrical and streaming directories for trailers older than
    the configured retention period and removes them.
    """
    
    def __init__(self, config: PruneConfig, logger: Logger):
        """
        Initialize trailer pruner.
        
        Args:
            config: Prune configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.stats = PruneStats()
        self.cutoff_date = self._calculate_cutoff_date()
        self.start_time = datetime.now()
    
    def _calculate_cutoff_date(self) -> date:
        """Calculate cutoff date based on retention years."""
        today = date.today()
        return today - timedelta(days=365 * self.config.retention_years)
    
    def prune(self) -> PruneStats:
        """
        Execute pruning operation.
        
        Returns:
            Statistics about the prune operation
        """
        # Validate at least one directory exists
        if not self.config.theatrical_dir.exists() and not self.config.streaming_dir.exists():
            self.logger.error(
                f"Neither {self.config.theatrical_dir} nor "
                f"{self.config.streaming_dir} exists. Nothing to process."
            )
            raise ValueError("No valid directories to process")
        
        # Track counts before
        removed_before = len(load_removed_trailers(self.config.removed_file))
        
        self.logger.info(f"Trailer pruning run started at {self.start_time.isoformat()}")
        self.logger.info(f"Retention policy: {self.config.retention_years} years")
        self.logger.info(f"Cutoff date: {self.cutoff_date}")
        
        # Process each directory
        if self.config.theatrical_dir.exists():
            self.logger.info(f"Scanning '{self.config.theatrical_dir}'...")
            self._process_directory(self.config.theatrical_dir, "theatrical")
        else:
            self.logger.warning(f"Directory '{self.config.theatrical_dir}' missing, skipping.")
        
        if self.config.streaming_dir.exists():
            self.logger.info(f"Scanning '{self.config.streaming_dir}'...")
            self._process_directory(self.config.streaming_dir, "streaming")
        else:
            self.logger.warning(f"Directory '{self.config.streaming_dir}' missing, skipping.")
        
        # Deduplicate removed file
        if not self.config.dry_run:
            deduplicate_removed_trailers(self.config.removed_file)
        
        # Track counts after
        removed_after = len(load_removed_trailers(self.config.removed_file))
        self.stats.new_removed_added = removed_after - removed_before
        
        # Print summary
        self._print_summary(removed_before, removed_after)
        
        return self.stats
    
    def _process_directory(self, directory: Path, category: str) -> None:
        """Process all folders in a directory."""
        for folder in directory.iterdir():
            if not folder.is_dir():
                continue
            
            self._process_folder(folder, category)
    
    def _process_folder(self, folder: Path, category: str) -> None:
        """Process a single trailer folder."""
        folder_name = folder.name
        
        self.logger.info(f"Attempting to evaluate folder '{folder_name}'...")
        
        # Update category stats
        if category == "theatrical":
            self.stats.theatrical_scanned += 1
        else:
            self.stats.streaming_scanned += 1
        
        # Look for movie.nfo
        nfo_path = folder / "movie.nfo"
        if not nfo_path.exists():
            self.logger.warning(
                f"  No movie.nfo found in '{folder_name}'. "
                f"Manual intervention required.",
                indent=2,
            )
            return
        
        # Extract effective date
        effective_date = self._extract_effective_date(nfo_path)
        
        if effective_date is None:
            self.logger.warning(
                f"  No usable dates found in movie.nfo for '{folder_name}'. "
                f"Manual intervention required.",
                indent=2,
            )
            return
        
        self.logger.info(
            f"  Effective date: {effective_date} (cutoff: {self.cutoff_date})",
            indent=2,
        )
        
        # Check if older than cutoff
        if effective_date < self.cutoff_date:
            self.logger.info(
                f"  Folder '{folder_name}' exceeds retention window. Removing...",
                indent=2,
            )
            
            if self.config.dry_run:
                self.logger.warning(
                    f"  [DRY-RUN] Would remove '{folder_name}' (not actually removed)",
                    indent=2,
                )
                self.stats.total_removed += 1
            else:
                # Add to removed list
                add_to_removed_trailers(self.config.removed_file, folder_name)
                
                # Remove folder
                try:
                    shutil.rmtree(folder)
                    self.logger.success(f"  Removed '{folder_name}'", indent=2)
                    self.stats.total_removed += 1
                except (OSError, PermissionError) as e:
                    self.logger.error(f"  Failed to remove '{folder_name}': {e}", indent=2)
        else:
            self.logger.info(
                f"  Folder '{folder_name}' is within retention window. Keeping.",
                indent=2,
            )
    
    def _extract_effective_date(self, nfo_path: Path) -> Optional[date]:
        """
        Extract effective date from movie.nfo file.
        
        Priority:
        1. <releasedate> or <premiered>
        2. <aired>
        3. <dateadded>
        
        Args:
            nfo_path: Path to movie.nfo file
        
        Returns:
            date object or None if no valid date found
        """
        self.logger.debug(f"Extracting effective date from: {nfo_path}")
        
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
        except ET.ParseError:
            self.logger.debug(f"XML validation failed for: {nfo_path}")
            self.logger.warning(
                f"  Invalid or corrupted movie.nfo for '{nfo_path.parent.name}'. "
                f"Manual intervention required.",
                indent=2,
            )
            return None
        
        # Try releasedate first
        releasedate_elem = root.find("releasedate")
        if releasedate_elem is not None and releasedate_elem.text:
            date_str = releasedate_elem.text.strip()
            if date_str:
                parsed = self._parse_date(date_str)
                if parsed:
                    self.logger.debug(f"Using releasedate: {parsed}")
                    return parsed
        
        # Try premiered
        premiered_elem = root.find("premiered")
        if premiered_elem is not None and premiered_elem.text:
            date_str = premiered_elem.text.strip()
            if date_str:
                parsed = self._parse_date(date_str)
                if parsed:
                    self.logger.debug(f"Using premiered: {parsed}")
                    return parsed
        
        # Try aired
        aired_elem = root.find("aired")
        if aired_elem is not None and aired_elem.text:
            date_str = aired_elem.text.strip()
            if date_str:
                parsed = self._parse_date(date_str)
                if parsed:
                    self.logger.debug(f"Using aired: {parsed}")
                    return parsed
        
        # Try dateadded (extract just the date part)
        dateadded_elem = root.find("dateadded")
        if dateadded_elem is not None and dateadded_elem.text:
            date_str = dateadded_elem.text.strip().split()[0]  # Take only date part
            if date_str:
                parsed = self._parse_date(date_str)
                if parsed:
                    self.logger.debug(f"Using dateadded: {parsed}")
                    return parsed
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse date string (YYYY-MM-DD format).
        
        Args:
            date_str: Date string to parse
        
        Returns:
            date object or None if invalid
        """
        # Validate format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            self.logger.debug(f"Invalid date format: {date_str}")
            return None
        
        try:
            year, month, day = map(int, date_str.split("-"))
            return date(year, month, day)
        except ValueError:
            self.logger.debug(f"Invalid date values: {date_str}")
            return None
    
    def _print_summary(self, removed_before: int, removed_after: int) -> None:
        """Print operation summary."""
        end_time = datetime.now()
        elapsed = int((end_time - self.start_time).total_seconds())
        
        self.logger.separator()
        if self.config.dry_run:
            self.logger.warning("DRY-RUN MODE - No changes were made")
            self.logger.separator()
        
        self.logger.info("Trailer pruning summary")
        self.logger.info(f"Started:  {self.start_time.isoformat()}")
        self.logger.info(f"Finished: {end_time.isoformat()}")
        self.logger.info(f"Elapsed:  {elapsed}s")
        self.logger.info("")
        self.logger.info(f"Theatrical folders scanned: {self.stats.theatrical_scanned}")
        self.logger.info(f"Streaming folders scanned:  {self.stats.streaming_scanned}")
        self.logger.info(f"Total folders scanned:      {self.stats.total_scanned}")
        self.logger.info("")
        
        if self.stats.total_removed == 0:
            self.logger.info("No trailers met the removal criteria this run. Nothing was deleted.")
        else:
            self.logger.success(f"Folders removed this run: {self.stats.total_removed}")
        
        self.logger.info("")
        self.logger.info(f"Removed list before run: {removed_before}")
        self.logger.info(f"New titles added:        {self.stats.new_removed_added}")
        self.logger.info(f"Removed list after run:  {removed_after}")
        self.logger.info("")
        self.logger.success("Trailer pruning run complete.")
