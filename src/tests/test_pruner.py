"""Tests for pruner."""

import pytest
from pathlib import Path
from datetime import date, timedelta

from coming_attractions.pruner import TrailerPruner
from coming_attractions.config import PruneConfig


class TestTrailerPruner:
    """Tests for TrailerPruner class."""
    
    def test_prune_old_trailer(self, temp_trailer_dir, sample_nfo_xml, logger):
        """Test pruning a trailer older than retention period."""
        # Create old trailer
        folder = temp_trailer_dir["theatrical"] / "Old Movie (2020)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        
        # Modify NFO to have old date
        old_nfo = sample_nfo_xml.replace("2026-12-25", "2020-01-01")
        nfo_path.write_text(old_nfo)
        
        # Create removed file
        removed_file = temp_trailer_dir["root"] / ".trailer-removed.txt"
        
        # Run pruner
        config = PruneConfig(
            retention_years=2,
            theatrical_dir=temp_trailer_dir["theatrical"],
            streaming_dir=temp_trailer_dir["streaming"],
            removed_file=removed_file,
            dry_run=False,
        )
        pruner = TrailerPruner(config, logger)
        stats = pruner.prune()
        
        # Verify folder was removed
        assert not folder.exists()
        assert stats.total_removed == 1
        
        # Verify added to removed file
        content = removed_file.read_text()
        assert "Old Movie (2020)" in content
    
    def test_keep_recent_trailer(self, temp_trailer_dir, sample_nfo_xml, logger):
        """Test keeping a recent trailer within retention period."""
        # Create recent trailer
        folder = temp_trailer_dir["theatrical"] / "Recent Movie (2026)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        nfo_path.write_text(sample_nfo_xml)
        
        removed_file = temp_trailer_dir["root"] / ".trailer-removed.txt"
        
        # Run pruner
        config = PruneConfig(
            retention_years=2,
            theatrical_dir=temp_trailer_dir["theatrical"],
            streaming_dir=temp_trailer_dir["streaming"],
            removed_file=removed_file,
            dry_run=False,
        )
        pruner = TrailerPruner(config, logger)
        stats = pruner.prune()
        
        # Verify folder still exists
        assert folder.exists()
        assert stats.total_removed == 0
    
    def test_dry_run_mode(self, temp_trailer_dir, sample_nfo_xml, logger):
        """Test dry-run mode doesn't remove files."""
        # Create old trailer
        folder = temp_trailer_dir["theatrical"] / "Old Movie (2020)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        old_nfo = sample_nfo_xml.replace("2026-12-25", "2020-01-01")
        nfo_path.write_text(old_nfo)
        
        removed_file = temp_trailer_dir["root"] / ".trailer-removed.txt"
        
        # Run pruner in dry-run mode
        config = PruneConfig(
            retention_years=2,
            theatrical_dir=temp_trailer_dir["theatrical"],
            streaming_dir=temp_trailer_dir["streaming"],
            removed_file=removed_file,
            dry_run=True,
        )
        pruner = TrailerPruner(config, logger)
        stats = pruner.prune()
        
        # Verify folder still exists
        assert folder.exists()
        assert stats.total_removed == 1  # Count shows what would be removed
        
        # Verify NOT added to removed file in dry-run
        assert not removed_file.exists() or removed_file.read_text() == ""
    
    def test_missing_nfo(self, temp_trailer_dir, logger):
        """Test handling folder without NFO."""
        # Create folder without NFO
        folder = temp_trailer_dir["theatrical"] / "No NFO (2020)"
        folder.mkdir()
        
        removed_file = temp_trailer_dir["root"] / ".trailer-removed.txt"
        
        # Run pruner
        config = PruneConfig(
            retention_years=2,
            theatrical_dir=temp_trailer_dir["theatrical"],
            streaming_dir=temp_trailer_dir["streaming"],
            removed_file=removed_file,
            dry_run=False,
        )
        pruner = TrailerPruner(config, logger)
        stats = pruner.prune()
        
        # Verify folder still exists (not removed without NFO)
        assert folder.exists()
        assert stats.total_removed == 0
    
    def test_invalid_nfo(self, temp_trailer_dir, logger):
        """Test handling corrupted NFO."""
        # Create folder with invalid NFO
        folder = temp_trailer_dir["theatrical"] / "Invalid NFO (2020)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        nfo_path.write_text("This is not valid XML")
        
        removed_file = temp_trailer_dir["root"] / ".trailer-removed.txt"
        
        # Run pruner
        config = PruneConfig(
            retention_years=2,
            theatrical_dir=temp_trailer_dir["theatrical"],
            streaming_dir=temp_trailer_dir["streaming"],
            removed_file=removed_file,
            dry_run=False,
        )
        pruner = TrailerPruner(config, logger)
        stats = pruner.prune()
        
        # Verify folder still exists (not removed with invalid NFO)
        assert folder.exists()
        assert stats.total_removed == 0
