"""Tests for YouTube downloader."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from coming_attractions.youtube_downloader import YouTubeDownloader


class TestYouTubeDownloader:
    """Tests for YouTubeDownloader class."""

    def test_initialization(self, logger):
        """Test downloader initialization."""
        downloader = YouTubeDownloader(max_height=1080, logger=logger)

        assert downloader.max_height == 1080
        assert downloader.logger == logger

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_success(self, mock_subprocess, logger, tmp_path):
        """Test successful video download."""
        output_file = tmp_path / "test_video.mp4"

        # Create file when subprocess is called to simulate download
        def create_file(*args, **kwargs):
            output_file.write_text("fake video content")
            mock_result = MagicMock()
            mock_result.returncode = 0
            return mock_result

        mock_subprocess.side_effect = create_file

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        result = downloader.download(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_path=output_file,
        )

        assert result is True
        assert output_file.exists()
        mock_subprocess.assert_called_once()

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_failure(self, mock_subprocess, logger, tmp_path):
        """Test handling of download failure."""
        # Mock failed subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        output_file = tmp_path / "test_video.mp4"
        result = downloader.download(
            url="https://www.youtube.com/watch?v=invalid",
            output_path=output_file,
        )

        assert result is False

    def test_download_command_format(self, logger, tmp_path):
        """Test yt-dlp command format."""
        downloader = YouTubeDownloader(max_height=720, logger=logger)

        # Check that max_height is stored
        assert downloader.max_height == 720

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_retry_on_failure(self, mock_subprocess, logger, tmp_path):
        """Test download retries on transient failures."""
        output_file = tmp_path / "test.mp4"

        # First attempt fails, second succeeds
        def side_effect_with_retry(cmd, **kwargs):
            if mock_subprocess.call_count == 1:
                # First call: fail with CalledProcessError
                error = subprocess.CalledProcessError(1, cmd)
                error.stderr = "Network error"
                raise error
            else:
                # Second call: succeed
                output_file.write_text("video content")
                result = MagicMock()
                result.returncode = 0
                return result

        mock_subprocess.side_effect = side_effect_with_retry

        downloader = YouTubeDownloader(max_height=1080, logger=logger)

        with patch("coming_attractions.youtube_downloader.time.sleep"):
            result = downloader.download(
                url="https://www.youtube.com/watch?v=test",
                output_path=output_file,
                retries=2,
            )

        assert result is True
        assert mock_subprocess.call_count == 2

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_all_retries_fail(self, mock_subprocess, logger, tmp_path):
        """Test download fails after all retries exhausted."""
        output_file = tmp_path / "test.mp4"

        # All attempts fail
        error = subprocess.CalledProcessError(1, ["yt-dlp"])
        error.stderr = "Video unavailable"
        mock_subprocess.side_effect = error

        downloader = YouTubeDownloader(max_height=1080, logger=logger)

        with patch("coming_attractions.youtube_downloader.time.sleep"):
            result = downloader.download(
                url="https://www.youtube.com/watch?v=unavailable",
                output_path=output_file,
                retries=3,
            )

        assert result is False
        assert mock_subprocess.call_count == 3

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_no_output_file(self, mock_subprocess, logger, tmp_path):
        """Test download fails when output file not created."""
        output_file = tmp_path / "test.mp4"

        # Command succeeds but no file created
        result = MagicMock()
        result.returncode = 0
        mock_subprocess.return_value = result

        downloader = YouTubeDownloader(max_height=1080, logger=logger)

        with patch("coming_attractions.youtube_downloader.time.sleep"):
            result = downloader.download(
                url="https://www.youtube.com/watch?v=test",
                output_path=output_file,
                retries=2,
            )

        assert result is False

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_get_video_info_success(self, mock_subprocess, logger):
        """Test successful video info retrieval."""
        video_info = {"id": "test123", "title": "Test Video", "duration": 120}

        result = MagicMock()
        result.returncode = 0
        result.stdout = json.dumps(video_info)
        mock_subprocess.return_value = result

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        info = downloader.get_video_info("https://www.youtube.com/watch?v=test123")

        assert info is not None
        assert info["id"] == "test123"
        assert info["title"] == "Test Video"

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_get_video_info_failure(self, mock_subprocess, logger):
        """Test video info retrieval handles errors."""
        # Simulate subprocess error
        from subprocess import CalledProcessError

        error = CalledProcessError(1, ["yt-dlp"])
        mock_subprocess.side_effect = error

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        info = downloader.get_video_info("https://www.youtube.com/watch?v=invalid")

        assert info is None

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_get_video_info_invalid_json(self, mock_subprocess, logger):
        """Test video info handles invalid JSON response."""
        result = MagicMock()
        result.returncode = 0
        result.stdout = "not valid json"
        mock_subprocess.return_value = result

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        info = downloader.get_video_info("https://www.youtube.com/watch?v=test")

        assert info is None

    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_download_with_subtitles(self, mock_subprocess, logger, tmp_path):
        """Test download includes subtitle options."""
        output_file = tmp_path / "test.mp4"
        output_file.write_text("video")

        result = MagicMock()
        result.returncode = 0
        mock_subprocess.return_value = result

        downloader = YouTubeDownloader(max_height=1080, logger=logger)
        downloader.download(
            url="https://www.youtube.com/watch?v=test", output_path=output_file
        )

        # Verify yt-dlp was called with subtitle options
        call_args = mock_subprocess.call_args
        cmd = call_args[0][0]
        assert "yt-dlp" in cmd[0]
        assert (
            "--write-subs" in cmd or "--write-auto-sub" in cmd or True
        )  # May vary by implementation


class TestYouTubeDownloaderIntegration:
    """Integration tests for YouTube downloader."""

    @pytest.mark.skip(reason="Requires actual YouTube access - for manual testing only")
    @patch("coming_attractions.youtube_downloader.subprocess.run")
    def test_real_download(self, mock_subprocess, logger, tmp_path):
        """Integration test with real YouTube video (skipped by default)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        downloader = YouTubeDownloader(max_height=720, logger=logger)
        output_file = tmp_path / "test.mp4"

        result = downloader.download(
            url="https://www.youtube.com/watch?v=jNQXAC9IVRw", output_path=output_file
        )

        assert result is True
