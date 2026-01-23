"""Title fixing logic - adds 'Trailer - ' prefix to NFO titles."""

import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from coming_attractions.config import TitleFixConfig
from coming_attractions.logger import Logger
from coming_attractions.models import TitleFixStats


class TitleFixer:
    """
    Fixes trailer titles by adding 'Trailer - ' prefix.
    
    Scans directory for movie.nfo files and updates <title> elements
    to include the configured prefix for proper Jellyfin display.
    """
    
    def __init__(self, config: TitleFixConfig, logger: Logger):
        """
        Initialize title fixer.
        
        Args:
            config: Title fix configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.stats = TitleFixStats()
    
    def fix_titles(self) -> TitleFixStats:
        """
        Execute title fixing operation.
        
        Returns:
            Statistics about the fix operation
        """
        # Validate root directory exists
        if not self.config.root_dir.exists():
            self.logger.error(f"Root directory does not exist: {self.config.root_dir}")
            raise ValueError(f"Root directory does not exist: {self.config.root_dir}")
        
        self.logger.info("Trailer title fixer starting...")
        self.logger.debug(
            f"Root='{self.config.root_dir}' Prefix='{self.config.prefix}'"
        )
        
        # Gather all subdirectories
        folders = [
            f for f in self.config.root_dir.iterdir()
            if f.is_dir()
        ]
        
        if not folders:
            self.logger.warning("No subfolders found under root. Nothing to do.")
            return self.stats
        
        self.logger.debug(f"Discovered {len(folders)} trailer folders.")
        
        # Process each folder
        for folder in folders:
            self._process_folder(folder)
        
        # Print summary
        self._print_summary()
        
        return self.stats
    
    def _process_folder(self, folder: Path) -> None:
        """Process a single trailer folder."""
        self.stats.total += 1
        
        nfo_path = folder / self.config.nfo_name
        
        # Check NFO exists
        if not nfo_path.exists():
            self.stats.skipped += 1
            self.logger.debug(f"No movie.nfo; skipping: {folder}")
            return
        
        # Extract current title
        current_title = self._extract_title(nfo_path)
        
        if current_title is None:
            self.stats.skipped += 1
            self.logger.debug(f"Could not extract <title>; skipping: {nfo_path}")
            return
        
        # Check if already prefixed
        if current_title.startswith(self.config.prefix):
            self.stats.skipped += 1
            self.logger.debug(f"Already prefixed; skipping: {nfo_path}")
            return
        
        # Update title
        self.logger.info(f"Processing: {folder.name}")
        self.logger.debug(f"  NFO path: {nfo_path}")
        self.logger.debug(f"  Current title: '{current_title}'")
        
        success = self._update_title(nfo_path, current_title)
        
        if success:
            new_title = f"{self.config.prefix}{current_title}"
            self.logger.success(f"  Updated title: '{new_title}'", indent=2)
            self.stats.fixed += 1
        else:
            self.logger.error(f"  Failed to update title", indent=2)
            self.stats.failed += 1
    
    def _extract_title(self, nfo_path: Path) -> str | None:
        """
        Extract title from NFO file.
        
        Args:
            nfo_path: Path to movie.nfo file
        
        Returns:
            Title string or None if not found/invalid
        """
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            title_elem = root.find("title")
            if title_elem is not None and title_elem.text:
                return title_elem.text.strip()
            
            return None
        
        except ET.ParseError:
            return None
    
    def _update_title(self, nfo_path: Path, current_title: str) -> bool:
        """
        Update title in NFO file with prefix.
        
        Uses atomic write pattern: temp file + rename.
        
        Args:
            nfo_path: Path to movie.nfo file
            current_title: Current title text
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse XML
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            # Find and update title element
            title_elem = root.find("title")
            if title_elem is None:
                return False
            
            new_title = f"{self.config.prefix}{current_title}"
            title_elem.text = new_title
            
            # Write to temp file
            temp_path = nfo_path.with_suffix(f".tmp.{os.getpid()}")
            try:
                # Write with declaration and proper encoding
                tree.write(
                    temp_path,
                    encoding="utf-8",
                    xml_declaration=True,
                )
                
                # Verify the write succeeded and contains expected title
                verify_title = self._extract_title(temp_path)
                if verify_title != new_title:
                    self.logger.debug(f"  Sanity check failed: expected '{new_title}', got '{verify_title}'")
                    return False
                
                # Atomic rename
                temp_path.replace(nfo_path)
                return True
            
            finally:
                # Clean up temp file if it still exists
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)
        
        except (ET.ParseError, OSError, IOError) as e:
            self.logger.debug(f"  Update failed: {e}")
            return False
    
    def _print_summary(self) -> None:
        """Print operation summary."""
        self.logger.info("")
        self.logger.separator()
        self.logger.info("Trailer Title Fixer Summary")
        self.logger.separator()
        self.logger.info(f"Total folders:    {self.stats.total}")
        self.logger.success(f"Fixed:            {self.stats.fixed}")
        self.logger.info(f"Skipped:          {self.stats.skipped}")
        
        if self.stats.failed > 0:
            self.logger.error(f"Failed:           {self.stats.failed}")
            self.logger.warning(
                f"Completed with {self.stats.failed} error(s). "
                f"Check logs above for details."
            )
        else:
            self.logger.success("All operations completed successfully.")
