"""Tests for title fixer."""

import pytest
from pathlib import Path
from xml.etree import ElementTree as ET

from coming_attractions.title_fixer import TitleFixer
from coming_attractions.config import TitleFixConfig


class TestTitleFixer:
    """Tests for TitleFixer class."""
    
    def test_fix_unprefixed_title(self, temp_trailer_dir, sample_nfo_xml, logger):
        """Test fixing a title without prefix."""
        # Create trailer folder with NFO
        folder = temp_trailer_dir["theatrical"] / "Test Movie (2026)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        nfo_path.write_text(sample_nfo_xml)
        
        # Run fixer
        config = TitleFixConfig(root_dir=temp_trailer_dir["theatrical"])
        fixer = TitleFixer(config, logger)
        stats = fixer.fix_titles()
        
        # Verify stats
        assert stats.total == 1
        assert stats.fixed == 1
        assert stats.skipped == 0
        assert stats.failed == 0
        
        # Verify NFO was updated
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        title = root.find("title").text
        assert title == "Trailer - Test Movie"
    
    def test_skip_prefixed_title(self, temp_trailer_dir, sample_nfo_prefixed, logger):
        """Test skipping already prefixed title."""
        # Create trailer folder with prefixed NFO
        folder = temp_trailer_dir["theatrical"] / "Test Movie (2026)"
        folder.mkdir()
        nfo_path = folder / "movie.nfo"
        nfo_path.write_text(sample_nfo_prefixed)
        
        # Run fixer
        config = TitleFixConfig(root_dir=temp_trailer_dir["theatrical"])
        fixer = TitleFixer(config, logger)
        stats = fixer.fix_titles()
        
        # Verify stats
        assert stats.total == 1
        assert stats.fixed == 0
        assert stats.skipped == 1
        assert stats.failed == 0
    
    def test_skip_no_nfo(self, temp_trailer_dir, logger):
        """Test skipping folder without NFO."""
        # Create trailer folder without NFO
        folder = temp_trailer_dir["theatrical"] / "Test Movie (2026)"
        folder.mkdir()
        
        # Run fixer
        config = TitleFixConfig(root_dir=temp_trailer_dir["theatrical"])
        fixer = TitleFixer(config, logger)
        stats = fixer.fix_titles()
        
        # Verify stats
        assert stats.total == 1
        assert stats.fixed == 0
        assert stats.skipped == 1
        assert stats.failed == 0
    
    def test_empty_directory(self, temp_trailer_dir, logger):
        """Test handling empty directory."""
        config = TitleFixConfig(root_dir=temp_trailer_dir["theatrical"])
        fixer = TitleFixer(config, logger)
        stats = fixer.fix_titles()
        
        assert stats.total == 0
        assert stats.fixed == 0
        assert stats.skipped == 0
        assert stats.failed == 0
    
    def test_invalid_directory(self, tmp_path, logger):
        """Test error on invalid directory."""
        config = TitleFixConfig(root_dir=tmp_path / "nonexistent")
        fixer = TitleFixer(config, logger)
        
        with pytest.raises(ValueError):
            fixer.fix_titles()
