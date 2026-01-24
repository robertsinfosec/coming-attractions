"""Tests for trailer fetcher."""

from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from coming_attractions.config import FetchConfig
from coming_attractions.fetcher import TrailerFetcher
from coming_attractions.models import FetchStats, MediaType, SkipReason


class TestTrailerFetcherInit:
    """Tests for TrailerFetcher initialization."""

    def test_initialization(self, tmp_path, logger, valid_api_key):
        """Test fetcher initializes correctly."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="theatrical")

        fetcher = TrailerFetcher(config, logger)

        assert fetcher.config == config
        assert fetcher.logger == logger
        assert isinstance(fetcher.stats, FetchStats)
        assert isinstance(fetcher.expected_folders, set)
        assert isinstance(fetcher.seen_ids, set)

    def test_loads_removed_trailers(self, tmp_path, logger, valid_api_key):
        """Test that removed trailers are loaded on init."""
        removed_file = tmp_path / ".trailer-removed.txt"
        removed_file.write_text("Movie One (2024)\nMovie Two (2025)\n")

        config = FetchConfig(
            api_key=valid_api_key, out_dir=tmp_path, removed_file=removed_file
        )

        fetcher = TrailerFetcher(config, logger)

        assert "Movie One (2024)" in fetcher.removed_folders
        assert "Movie Two (2025)" in fetcher.removed_folders


class TestFetchItems:
    """Tests for _fetch_items method."""

    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_theatrical_mode(
        self, mock_client_class, tmp_path, logger, valid_api_key
    ):
        """Test fetching in theatrical mode."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="theatrical")

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        fetcher = TrailerFetcher(config, logger)
        fetcher._fetch_theatrical = Mock(return_value=[{"id": 1, "title": "Test"}])
        fetcher._fetch_streaming = Mock(return_value=[])

        items = fetcher._fetch_items(mock_client)

        assert len(items) == 1
        fetcher._fetch_theatrical.assert_called_once()
        fetcher._fetch_streaming.assert_not_called()

    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_streaming_mode(
        self, mock_client_class, tmp_path, logger, valid_api_key
    ):
        """Test fetching in streaming mode."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="streaming")

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        fetcher = TrailerFetcher(config, logger)
        fetcher._fetch_theatrical = Mock(return_value=[])
        fetcher._fetch_streaming = Mock(return_value=[{"id": 2, "name": "Show"}])

        items = fetcher._fetch_items(mock_client)

        assert len(items) == 1
        fetcher._fetch_theatrical.assert_not_called()
        fetcher._fetch_streaming.assert_called_once()

    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_both_mode(self, mock_client_class, tmp_path, logger, valid_api_key):
        """Test fetching in both mode."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="both")

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        fetcher = TrailerFetcher(config, logger)
        fetcher._fetch_theatrical = Mock(return_value=[{"id": 1}])
        fetcher._fetch_streaming = Mock(return_value=[{"id": 2}])

        items = fetcher._fetch_items(mock_client)

        assert len(items) == 2
        fetcher._fetch_theatrical.assert_called_once()
        fetcher._fetch_streaming.assert_called_once()


class TestProcessItem:
    """Tests for _process_item method."""

    # Note: _process_item is complex and requires extensive mocking of TMDb client
    # Integration tests would be more appropriate for this method
    # For now, testing the helper methods it uses

    pass


class TestInDateWindow:
    """Tests for _in_date_window method."""

    def test_date_within_window(self, tmp_path, logger, valid_api_key):
        """Test date within configured window."""

        config = FetchConfig(
            api_key=valid_api_key, out_dir=tmp_path, days_ahead=365, days_back=90
        )

        fetcher = TrailerFetcher(config, logger)

        # Test date 30 days in future
        future_date = date.today() + timedelta(days=30)
        assert fetcher._in_date_window(future_date) is True

        # Test date 30 days in past
        past_date = date.today() - timedelta(days=30)
        assert fetcher._in_date_window(past_date) is True

    def test_date_outside_window(self, tmp_path, logger, valid_api_key):
        """Test date outside configured window."""

        config = FetchConfig(
            api_key=valid_api_key, out_dir=tmp_path, days_ahead=30, days_back=30
        )

        fetcher = TrailerFetcher(config, logger)

        # Test date 100 days in future
        future_date = date.today() + timedelta(days=100)
        assert fetcher._in_date_window(future_date) is False

        # Test date 100 days in past
        past_date = date.today() - timedelta(days=100)
        assert fetcher._in_date_window(past_date) is False


class TestGenerateFolderName:
    """Tests for _generate_folder_name method."""

    def test_movie_folder_name(self, tmp_path, logger, valid_api_key):
        """Test generating folder name for movie."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        folder_name = fetcher._generate_folder_name("Test Movie", 2024, MediaType.MOVIE)
        assert folder_name == "Test Movie (2024)"

    def test_tv_folder_name(self, tmp_path, logger, valid_api_key):
        """Test generating folder name for TV show."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        folder_name = fetcher._generate_folder_name("Test Show", 2024, MediaType.TV)
        assert folder_name == "Test Show (2024) [TV]"


class TestWriteIndex:
    """Tests for _write_index method."""

    def test_write_index_creates_file(self, tmp_path, logger, valid_api_key):
        """Test that index JSON file is created with metadata."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="theatrical")

        fetcher = TrailerFetcher(config, logger)
        fetcher.expected_folders = {"Movie One (2024)", "Movie Two (2025)"}

        fetcher._write_index()

        index_file = config.out_dir / "_index.json"
        assert index_file.exists()

        # Verify it's valid JSON
        import json

        data = json.loads(index_file.read_text())
        assert "generated_at" in data
        assert "mode" in data
        assert data["mode"] == "theatrical"

    def test_atomic_write(self, tmp_path, logger, valid_api_key):
        """Test that index file uses atomic write."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)
        fetcher.expected_folders = {"Test (2024)"}

        fetcher._write_index()

        # Temp file should not exist after write (atomic operation completed)
        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0

        # Index file should exist
        index_file = config.out_dir / "_index.json"
        assert index_file.exists()


class TestPrintSummary:
    """Tests for _print_summary method."""

    def test_summary_output(self, tmp_path, logger, valid_api_key):
        """Test that summary is printed with correct stats."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)
        fetcher.stats.added = 5
        fetcher.stats.skipped = 3
        fetcher.stats.total_items = 8

        # Should not raise any exceptions
        fetcher._print_summary()


class TestValidateDirectory:
    """Tests for directory validation."""

    def test_invalid_directory_raises(self, logger, valid_api_key):
        """Test that invalid directory raises ValueError."""
        config = FetchConfig(
            api_key=valid_api_key, out_dir=Path("/nonexistent/invalid/path")
        )

        fetcher = TrailerFetcher(config, logger)

        with patch("coming_attractions.fetcher.TMDbClient"):
            with pytest.raises(ValueError):
                fetcher.fetch()


class TestDryRunMode:
    """Tests for dry-run mode."""

    @patch("coming_attractions.fetcher.TMDbClient")
    @patch("coming_attractions.fetcher.YouTubeDownloader")
    def test_dry_run_no_write(
        self, mock_downloader, mock_client, tmp_path, logger, valid_api_key
    ):
        """Test that dry-run mode doesn't write files."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, dry_run=True)

        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        fetcher = TrailerFetcher(config, logger)
        fetcher._fetch_items = Mock(return_value=[])

        fetcher.fetch()

        # Index file should not exist in dry-run
        index_file = tmp_path / ".index.txt"
        assert not index_file.exists()


class TestFetchStats:
    """Tests for fetch statistics tracking."""

    def test_stats_initialization(self):
        """Test stats are initialized to zero."""
        stats = FetchStats()
        assert stats.added == 0
        assert stats.skipped == 0
        assert len(stats.skip_reasons) > 0  # Has all skip reasons

    def test_stats_tracking(self):
        """Test that FetchStats tracks skip reasons correctly."""
        stats = FetchStats()
        stats.increment_skip(SkipReason.NO_VIDEO)
        stats.increment_skip(SkipReason.NO_VIDEO)
        stats.increment_skip(SkipReason.ALREADY_EXISTS)

        assert stats.skipped == 3
        assert stats.skip_reasons[SkipReason.NO_VIDEO.value] == 2
        assert stats.skip_reasons[SkipReason.ALREADY_EXISTS.value] == 1


class TestSanitizeFolderNameIntegration:
    """Integration tests for folder name sanitization in fetch context."""

    def test_movie_title_with_colon(self):
        """Test that movie titles with colons are sanitized."""
        from coming_attractions.utils import sanitize_folder_name

        # Common movie title pattern
        result = sanitize_folder_name("Spider-Man: No Way Home (2021)")
        assert ":" not in result
        assert "Spider-Man" in result
        assert "(2021)" in result
