"""YouTube downloader wrapper using yt-dlp."""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional

from coming_attractions.logger import Logger


class YouTubeDownloader:
    """
    YouTube video downloader using yt-dlp.

    Features:
    - Quality-controlled downloads (max height limit)
    - Automatic video+audio merge to MP4
    - Retry logic for transient failures
    - Progress suppression for clean output
    """

    def __init__(self, max_height: int, logger: Logger):
        """
        Initialize YouTube downloader.

        Args:
            max_height: Maximum video height (e.g., 1080, 720)
            logger: Logger instance for output
        """
        self.max_height = max_height
        self.logger = logger

    def download(
        self,
        url: str,
        output_path: Path,
        retries: int = 3,
    ) -> bool:
        """
        Download YouTube video to specified path.

        Args:
            url: YouTube video URL
            output_path: Destination file path (should end in .mp4)
            retries: Number of retry attempts on failure

        Returns:
            True if download successful, False otherwise

        Notes:
            - Prefers MP4 video + M4A audio merge
            - Falls back to best MP4, then best available
            - Requires ffmpeg for audio/video merge
        """
        # Build yt-dlp format string
        # Priority:
        # 1. Best video (mp4, height <= max) + best audio (m4a)
        # 2. Best single mp4 file
        # 3. Best available format
        fmt = (
            f"bv*[ext=mp4][height<={self.max_height}]+ba[ext=m4a]/" f"b[ext=mp4]/" f"b"
        )

        # Build command
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-progress",
            "--quiet",
            "--no-warnings",
            "--merge-output-format",
            "mp4",
            "--no-part",
            "-f",
            fmt,
            "-o",
            str(output_path),
            url,
        ]

        # Retry loop
        for attempt in range(retries):
            try:
                self.logger.debug(f"yt-dlp attempt {attempt + 1}/{retries}")

                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                # Verify file was created and is non-empty
                if output_path.exists() and output_path.stat().st_size > 0:
                    self.logger.debug(
                        f"  Downloaded {output_path.stat().st_size} bytes"
                    )
                    return True
                else:
                    error_msg = "  Download produced no output file"
                    if attempt < retries - 1:
                        self.logger.warning(error_msg, indent=2)
                        wait_time = 2**attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(error_msg, indent=2)
                        return False

            except subprocess.CalledProcessError as e:
                stderr = e.stderr.strip() if e.stderr else ""

                if attempt < retries - 1:
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"  Download attempt {attempt + 1} failed. "
                        f"Retrying in {wait_time}s...",
                        indent=2,
                    )
                    if stderr:
                        self.logger.warning(f"  Error: {stderr}", indent=2)
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    if stderr:
                        self.logger.error(f"  Download failed: {stderr}", indent=2)
                    else:
                        self.logger.error(
                            "  Download failed with no error message", indent=2
                        )
                    return False

        return False

    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Get video metadata without downloading.

        Args:
            url: YouTube video URL

        Returns:
            Video info dictionary or None on error
        """
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--quiet",
            url,
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )

            return json.loads(result.stdout)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None
