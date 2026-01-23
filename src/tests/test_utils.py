"""Tests for utility functions."""

from datetime import date

import pytest

from coming_attractions.utils import (
    add_to_removed_trailers,
    format_duration,
    load_removed_trailers,
    parse_release_date,
    sanitize_folder_name,
)


class TestSanitizeFolderName:
    """Tests for folder name sanitization."""

    def test_basic_sanitization(self):
        assert sanitize_folder_name("Movie Title (2026)") == "Movie Title (2026)"

    def test_removes_invalid_chars(self):
        assert sanitize_folder_name("Movie: The Sequel") == "Movie The Sequel"
        assert sanitize_folder_name("Movie/Title") == "MovieTitle"
        assert sanitize_folder_name("Movie<>Title") == "MovieTitle"

    def test_handles_unicode(self):
        assert sanitize_folder_name("Café") == "Café"
        assert sanitize_folder_name("日本") == "日本"

    def test_strips_dots_and_spaces(self):
        assert sanitize_folder_name("  Movie  ") == "Movie"
        assert sanitize_folder_name("...Movie...") == "Movie"
        assert sanitize_folder_name("  ...Movie...  ") == "Movie"

    def test_handles_empty_input(self):
        assert sanitize_folder_name("") == "Unknown"
        assert sanitize_folder_name("   ") == "Unknown"

    def test_truncates_long_names(self):
        long_name = "A" * 300
        result = sanitize_folder_name(long_name, max_length=200)
        assert len(result.encode("utf-8")) <= 200

    def test_handles_control_characters(self):
        # Control characters are removed, whitespace is collapsed to single space
        assert sanitize_folder_name("Movie\x00Title") == "MovieTitle"
        assert sanitize_folder_name("Movie\nTitle") == "Movie Title"  # \n becomes space
        assert sanitize_folder_name("Movie\tTitle") == "Movie Title"  # \t becomes space


class TestParseReleaseDate:
    """Tests for date parsing."""

    def test_valid_date(self):
        assert parse_release_date("2026-12-25") == date(2026, 12, 25)
        assert parse_release_date("2020-01-01") == date(2020, 1, 1)

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_release_date("25-12-2026")
        with pytest.raises(ValueError):
            parse_release_date("2026/12/25")
        with pytest.raises(ValueError):
            parse_release_date("invalid")

    def test_invalid_values(self):
        with pytest.raises(ValueError):
            parse_release_date("2026-13-01")  # Invalid month
        with pytest.raises(ValueError):
            parse_release_date("2026-12-32")  # Invalid day

    def test_empty_input(self):
        with pytest.raises(ValueError):
            parse_release_date("")
        with pytest.raises(ValueError):
            parse_release_date(None)


class TestRemovedTrailers:
    """Tests for removed trailers tracking."""

    def test_load_nonexistent_file(self, tmp_path):
        removed_file = tmp_path / ".trailer-removed.txt"
        result = load_removed_trailers(removed_file)
        assert result == set()

    def test_load_existing_file(self, tmp_path):
        removed_file = tmp_path / ".trailer-removed.txt"
        removed_file.write_text("Movie 1 (2020)\nMovie 2 (2021)\n")

        result = load_removed_trailers(removed_file)
        assert result == {"Movie 1 (2020)", "Movie 2 (2021)"}

    def test_add_to_removed(self, tmp_path):
        removed_file = tmp_path / ".trailer-removed.txt"

        assert add_to_removed_trailers(removed_file, "Movie 1 (2020)")
        assert add_to_removed_trailers(removed_file, "Movie 2 (2021)")

        result = load_removed_trailers(removed_file)
        assert result == {"Movie 1 (2020)", "Movie 2 (2021)"}

    def test_add_duplicate(self, tmp_path):
        removed_file = tmp_path / ".trailer-removed.txt"

        add_to_removed_trailers(removed_file, "Movie 1 (2020)")
        add_to_removed_trailers(removed_file, "Movie 1 (2020)")

        result = load_removed_trailers(removed_file)
        assert result == {"Movie 1 (2020)"}


class TestFormatDuration:
    """Tests for duration formatting."""

    def test_seconds_only(self):
        assert format_duration(45) == "45s"
        assert format_duration(0) == "0s"

    def test_minutes(self):
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3599) == "59m 59s"

    def test_hours(self):
        assert format_duration(3600) == "1h"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(9015) == "2h 30m 15s"
