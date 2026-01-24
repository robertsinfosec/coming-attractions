"""Pytest configuration and shared fixtures."""


import pytest

from coming_attractions.logger import Logger


@pytest.fixture
def logger():
    """Provide a logger instance for tests."""
    return Logger(timestamps=False, debug=True, log_file=None)


@pytest.fixture
def valid_api_key():
    """Provide a valid-length API key for testing (32 characters)."""
    return "a" * 32  # TMDb API keys are 32 characters


@pytest.fixture
def temp_trailer_dir(tmp_path):
    """Create a temporary trailer directory structure."""
    theatrical = tmp_path / "theatrical"
    streaming = tmp_path / "streaming"
    theatrical.mkdir()
    streaming.mkdir()

    return {
        "root": tmp_path,
        "theatrical": theatrical,
        "streaming": streaming,
    }


@pytest.fixture
def sample_nfo_xml():
    """Sample NFO XML content."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>Test Movie</title>
    <originaltitle>Test Movie</originaltitle>
    <sorttitle>Test Movie</sorttitle>
    <premiered>2026-12-25</premiered>
    <releasedate>2026-12-25</releasedate>
    <year>2026</year>
    <plot>A test movie for unit tests.</plot>
    <runtime>120</runtime>
    <mpaa>PG-13</mpaa>
    <dateadded>2026-01-01 12:00:00</dateadded>
</movie>"""


@pytest.fixture
def sample_nfo_no_dates():
    """Sample NFO without date fields."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>Test Movie</title>
    <plot>A test movie without dates.</plot>
</movie>"""


@pytest.fixture
def sample_nfo_prefixed():
    """Sample NFO with prefixed title."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>Trailer - Test Movie</title>
    <premiered>2026-12-25</premiered>
</movie>"""


@pytest.fixture
def sample_tmdb_response():
    """Sample TMDb API response."""
    return {
        "results": [
            {
                "id": 12345,
                "title": "Test Movie",
                "release_date": "2026-12-25",
                "overview": "A test movie",
                "vote_average": 7.5,
            },
            {
                "id": 67890,
                "title": "Another Test",
                "release_date": "2026-06-15",
                "overview": "Another test",
                "vote_average": 8.0,
            },
        ],
        "page": 1,
        "total_pages": 1,
        "total_results": 2,
    }


@pytest.fixture
def sample_videos_response():
    """Sample TMDb videos response."""
    return {
        "results": [
            {
                "key": "test_video_key",
                "site": "YouTube",
                "type": "Trailer",
                "official": True,
                "name": "Official Trailer",
            },
            {
                "key": "test_teaser_key",
                "site": "YouTube",
                "type": "Teaser",
                "official": False,
                "name": "Teaser",
            },
        ]
    }
