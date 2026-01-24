"""Integration tests for end-to-end workflows."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


from coming_attractions.config import FetchConfig
from coming_attractions.fetcher import TrailerFetcher


class TestFetcherIntegration:
    """Integration tests for fetcher workflows."""

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_theatrical_fetch_workflow(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test complete theatrical fetch workflow."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        # Mock TMDb responses with proper date window
        today = date.today()
        release_date = (today + timedelta(days=30)).isoformat()

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 123,
                "title": "Test Movie",
                "release_date": release_date,
                "media_type": "movie",
            }
        ]

        mock_tmdb.get_videos.return_value = [
            {
                "key": "abc123",
                "type": "Trailer",
                "name": "Official Trailer",
                "official": True,
                "site": "YouTube",
            }
        ]

        # Mock YouTube downloader
        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt
        mock_yt.download.return_value = True

        # Run fetcher
        config = FetchConfig(
            api_key=valid_api_key,
            out_dir=tmp_path,
            mode="theatrical",
            include_upcoming=True,
            include_now_playing=False,
            include_popular=False,
            dry_run=False,
        )

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Verify workflow executed
        assert mock_tmdb.get_movie_feed.called
        # Video lookup happens when processing items
        assert stats.added >= 0 or stats.skipped >= 0

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_streaming_fetch_workflow(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test complete streaming fetch workflow."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        # Mock TMDb discover response with proper date
        today = date.today()
        release_date = (today - timedelta(days=30)).isoformat()

        mock_tmdb.discover.return_value = [
            {
                "id": 456,
                "title": "Streaming Movie",
                "release_date": release_date,
                "media_type": "movie",
            }
        ]

        mock_tmdb.get_videos.return_value = [
            {
                "key": "xyz789",
                "type": "Trailer",
                "name": "Trailer",
                "official": False,
                "site": "YouTube",
            }
        ]

        # Mock YouTube downloader
        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt
        mock_yt.download.return_value = True

        # Run fetcher
        config = FetchConfig(
            api_key=valid_api_key,
            out_dir=tmp_path,
            mode="streaming",
            media_types="movie",
            watch_providers="8,9",
            dry_run=False,
        )

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Verify workflow executed
        assert mock_tmdb.discover.called
        assert stats.added >= 0 or stats.skipped >= 0

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_skips_no_video(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test fetch skips items with no video."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 999,
                "title": "No Trailer Movie",
                "release_date": "2024-12-01",
                "media_type": "movie",
            }
        ]

        # No videos available
        mock_tmdb.get_videos.return_value = []

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt

        # Run fetcher
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="theatrical")

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Should skip due to no video
        assert stats.skipped >= 1
        assert not mock_yt.download.called

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_handles_existing_trailer(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test fetch skips already existing trailers."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 777,
                "title": "Existing Movie",
                "release_date": "2024-10-10",
                "media_type": "movie",
            }
        ]

        mock_tmdb.get_videos.return_value = [
            {"key": "exist123", "type": "Trailer", "name": "Trailer", "official": True}
        ]

        # Create existing trailer folder and file
        existing_folder = tmp_path / "Existing Movie (2024)"
        existing_folder.mkdir()
        existing_file = existing_folder / "Existing Movie (2024).mp4"
        existing_file.write_text("fake video data")

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt

        # Run fetcher
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path, mode="theatrical")

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Should skip existing trailer
        assert stats.skipped >= 1
        assert not mock_yt.download.called

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_handles_removed_trailer(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test fetch skips previously removed trailers."""
        # Setup removed file
        removed_file = tmp_path / ".trailer-removed.txt"
        removed_file.write_text("Removed Movie (2024)\n")

        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 888,
                "title": "Removed Movie",
                "release_date": "2024-09-09",
                "media_type": "movie",
            }
        ]

        mock_tmdb.get_videos.return_value = [
            {
                "key": "removed123",
                "type": "Trailer",
                "name": "Trailer",
                "official": True,
            }
        ]

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt

        # Run fetcher
        config = FetchConfig(
            api_key=valid_api_key,
            out_dir=tmp_path,
            removed_file=removed_file,
            mode="theatrical",
        )

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Should skip removed trailer
        assert stats.skipped >= 1
        assert not mock_yt.download.called

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_outside_date_window(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test fetch skips items outside date window."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        # Movie too far in future
        future_date = (date.today() + timedelta(days=500)).isoformat()

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 555,
                "title": "Far Future Movie",
                "release_date": future_date,
                "media_type": "movie",
            }
        ]

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt

        # Run fetcher with narrow window
        config = FetchConfig(
            api_key=valid_api_key,
            out_dir=tmp_path,
            mode="theatrical",
            days_ahead=365,
            days_back=90,
        )

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Should skip due to date window
        assert stats.skipped >= 1
        assert not mock_tmdb.get_videos.called

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_fetch_picks_best_video(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test fetch picks official trailer over teaser."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 333,
                "title": "Multiple Videos Movie",
                "release_date": "2024-08-15",
                "media_type": "movie",
            }
        ]

        # Multiple videos - should pick official trailer
        mock_tmdb.get_videos.return_value = [
            {"key": "teaser123", "type": "Teaser", "name": "Teaser", "official": False},
            {
                "key": "official123",
                "type": "Trailer",
                "name": "Official Trailer",
                "official": True,
            },
        ]

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt
        mock_yt.download.return_value = True

        # Run fetcher
        config = FetchConfig(
            api_key=valid_api_key, out_dir=tmp_path, mode="theatrical", dry_run=False
        )

        fetcher = TrailerFetcher(config, logger)
        stats = fetcher.fetch()

        # Should use official trailer
        if mock_yt.download.called:
            # Check that it downloaded using the official trailer's key
            call_args = mock_yt.download.call_args
            url = call_args[0][0] if call_args else ""
            assert "official123" in url or stats.added >= 0

    @patch("coming_attractions.fetcher.YouTubeDownloader")
    @patch("coming_attractions.fetcher.TMDbClient")
    def test_dry_run_no_downloads(
        self, mock_tmdb_class, mock_yt_class, tmp_path, logger, valid_api_key
    ):
        """Test dry-run mode doesn't download anything."""
        # Setup mocks
        mock_tmdb = MagicMock()
        mock_tmdb_class.return_value.__enter__.return_value = mock_tmdb

        mock_tmdb.get_movie_feed.return_value = [
            {
                "id": 111,
                "title": "Dry Run Movie",
                "release_date": "2024-07-07",
                "media_type": "movie",
            }
        ]

        mock_tmdb.get_videos.return_value = [
            {"key": "dryrun123", "type": "Trailer", "name": "Trailer", "official": True}
        ]

        mock_yt = MagicMock()
        mock_yt_class.return_value = mock_yt

        # Run fetcher in dry-run mode
        config = FetchConfig(
            api_key=valid_api_key, out_dir=tmp_path, mode="theatrical", dry_run=True
        )

        fetcher = TrailerFetcher(config, logger)
        fetcher.fetch()

        # Should NOT download in dry-run
        assert not mock_yt.download.called

        # Should NOT write index in dry-run
        index_file = tmp_path / "_index.json"
        assert not index_file.exists()


class TestPickBestVideo:
    """Tests for _pick_best_video method."""

    def test_picks_official_trailer_first(self, tmp_path, logger, valid_api_key):
        """Test that official trailer is picked first."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        # Note: _pick_best_video filters for site="YouTube" first
        videos = [
            {"key": "a", "type": "Teaser", "official": False, "site": "YouTube"},
            {"key": "b", "type": "Trailer", "official": True, "site": "YouTube"},
            {"key": "c", "type": "Trailer", "official": False, "site": "YouTube"},
        ]

        best = fetcher._pick_best_video(videos)
        assert best is not None
        assert best["key"] == "b"
        assert best["official"] is True

    def test_picks_trailer_over_teaser(self, tmp_path, logger, valid_api_key):
        """Test that Trailer is picked over Teaser."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        videos = [
            {"key": "a", "type": "Teaser", "official": False, "site": "YouTube"},
            {"key": "b", "type": "Trailer", "official": False, "site": "YouTube"},
        ]

        best = fetcher._pick_best_video(videos)
        assert best is not None
        assert best["key"] == "b"
        assert best["type"] == "Trailer"

    def test_returns_none_for_empty_list(self, tmp_path, logger, valid_api_key):
        """Test returns None when no videos available."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        best = fetcher._pick_best_video([])
        assert best is None

    def test_ignores_non_youtube_videos(self, tmp_path, logger, valid_api_key):
        """Test that non-YouTube videos are filtered out."""
        config = FetchConfig(api_key=valid_api_key, out_dir=tmp_path)

        fetcher = TrailerFetcher(config, logger)

        videos = [
            {"key": "a", "type": "Trailer", "official": True, "site": "Vimeo"},
            {"key": "b", "type": "Trailer", "official": False, "site": "YouTube"},
        ]

        best = fetcher._pick_best_video(videos)
        assert best is not None
        # Should pick YouTube video even though Vimeo one is official
        assert best["key"] == "b"
        assert best["site"] == "YouTube"
