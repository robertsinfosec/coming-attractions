"""Tests for TMDb client."""

import pytest
import responses
from requests.exceptions import RequestException

from coming_attractions.tmdb_client import TMDbClient


class TestTMDbClient:
    """Tests for TMDbClient class."""
    
    @responses.activate
    def test_successful_request(self, logger, sample_tmdb_response):
        """Test successful API request."""
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/upcoming",
            json=sample_tmdb_response,
            status=200,
        )
        
        client = TMDbClient("test_api_key", logger)
        result = client.get_movie_feed("upcoming", "US", max_pages=1)
        
        assert len(result) == 2
        assert result[0]["title"] == "Test Movie"
    
    @responses.activate
    def test_rate_limiting(self, logger, sample_tmdb_response):
        """Test handling of rate limiting (429 response)."""
        # First request returns 429
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/upcoming",
            status=429,
            headers={"Retry-After": "1"},
        )
        
        # Second request succeeds
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/upcoming",
            json=sample_tmdb_response,
            status=200,
        )
        
        client = TMDbClient("test_api_key", logger)
        result = client.get_movie_feed("upcoming", "US", max_pages=1)
        
        assert len(result) == 2
    
    @responses.activate
    def test_pagination(self, logger):
        """Test pagination across multiple pages."""
        # Page 1
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/upcoming",
            json={
                "results": [{"id": 1, "title": "Movie 1"}],
                "page": 1,
                "total_pages": 2,
            },
            status=200,
        )
        
        # Page 2
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/upcoming",
            json={
                "results": [{"id": 2, "title": "Movie 2"}],
                "page": 2,
                "total_pages": 2,
            },
            status=200,
        )
        
        client = TMDbClient("test_api_key", logger)
        result = client.get_movie_feed("upcoming", "US", max_pages=2)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
    
    @responses.activate
    def test_get_videos(self, logger, sample_videos_response):
        """Test fetching videos for a movie."""
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/movie/12345/videos",
            json=sample_videos_response,
            status=200,
        )
        
        client = TMDbClient("test_api_key", logger)
        result = client.get_videos("movie", 12345)
        
        assert len(result) == 2
        assert result[0]["type"] == "Trailer"
        assert result[0]["site"] == "YouTube"
    
    @responses.activate
    def test_discover(self, logger):
        """Test discover API."""
        responses.add(
            responses.GET,
            "https://api.themoviedb.org/3/discover/movie",
            json={
                "results": [
                    {"id": 1, "title": "Discovered Movie"},
                ],
                "page": 1,
                "total_pages": 1,
            },
            status=200,
        )
        
        client = TMDbClient("test_api_key", logger)
        result = client.discover(
            media_type="movie",
            region="US",
            start_date="2026-01-01",
            end_date="2026-12-31",
            max_pages=1,
        )
        
        assert len(result) == 1
        assert result[0]["media_type"] == "movie"
