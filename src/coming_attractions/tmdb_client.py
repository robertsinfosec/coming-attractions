"""TMDb API client with retry logic and rate limiting."""

import time
from typing import Any, Dict, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from coming_attractions.logger import Logger


class TMDbClient:
    """
    TMDb API client with automatic retry and rate limiting.
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting handling (429 responses)
    - Request timeout handling
    - Debug logging
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, api_key: str, logger: Logger):
        """
        Initialize TMDb client.
        
        Args:
            api_key: TMDb API key
            logger: Logger instance for output
        """
        self.api_key = api_key
        self.logger = logger
        self.session = requests.Session()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.RequestException)),
        reraise=True,
    )
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic.
        
        Args:
            endpoint: API endpoint (relative to BASE_URL)
            params: Query parameters
        
        Returns:
            JSON response as dictionary
        
        Raises:
            requests.exceptions.RequestException: On request failure
        """
        # Build full URL
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        # Add API key to params
        request_params = dict(params or {})
        request_params["api_key"] = self.api_key
        
        self.logger.debug(f"TMDb API request: {endpoint}")
        if params:
            self.logger.debug(f"  Params: {params}")
        
        try:
            response = self.session.get(url, params=request_params, timeout=30)
            
            self.logger.debug(f"  Response status: {response.status_code}")
            
            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                self.logger.warning(
                    f"  Rate limited by TMDb. Waiting {retry_after}s...",
                    indent=2,
                )
                time.sleep(retry_after)
                # Retry the request
                response = self.session.get(url, params=request_params, timeout=30)
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.Timeout:
            self.logger.warning("  Request timeout. Retrying...", indent=2)
            raise
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"  Request failed: {e}. Retrying...", indent=2)
            raise
    
    def get_movie_feed(
        self,
        feed: str,
        region: str,
        max_pages: int = 1,
    ) -> list[Dict[str, Any]]:
        """
        Fetch movies from a TMDb feed (upcoming, now_playing, popular).
        
        Args:
            feed: Feed name (upcoming, now_playing, or popular)
            region: Region code (ISO 3166-1 alpha-2)
            max_pages: Maximum pages to fetch
        
        Returns:
            List of movie dictionaries
        """
        items = []
        page = 1
        
        while page <= max_pages:
            data = self._make_request(
                f"movie/{feed}",
                {"region": region, "page": page},
            )
            
            results = data.get("results", [])
            items.extend(results)
            
            total_pages = int(data.get("total_pages", page))
            if page >= total_pages:
                break
            
            page += 1
        
        return items
    
    def discover(
        self,
        media_type: str,
        region: str,
        start_date: str,
        end_date: str,
        watch_providers: Optional[str] = None,
        watch_region: Optional[str] = None,
        max_pages: int = 1,
    ) -> list[Dict[str, Any]]:
        """
        Fetch content via TMDb discover API.
        
        Args:
            media_type: "movie" or "tv"
            region: Region code for releases
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            watch_providers: Pipe-separated provider IDs (e.g., "8|9|337")
            watch_region: Region for streaming availability
            max_pages: Maximum pages to fetch
        
        Returns:
            List of media dictionaries with media_type annotation
        """
        items = []
        page = 1
        
        # Determine date field based on media type
        if media_type == "movie":
            date_gte = "primary_release_date.gte"
            date_lte = "primary_release_date.lte"
        else:  # tv
            date_gte = "first_air_date.gte"
            date_lte = "first_air_date.lte"
        
        # Build base params
        params = {
            "page": page,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "with_original_language": "en",
            date_gte: start_date,
            date_lte: end_date,
        }
        
        # Add provider filters if specified
        if watch_providers and watch_region:
            params["watch_region"] = watch_region
            params["with_watch_providers"] = watch_providers
            params["with_watch_monetization_types"] = "flatrate"
        
        while page <= max_pages:
            params["page"] = page
            data = self._make_request(f"discover/{media_type}", params)
            
            results = data.get("results", [])
            
            # Annotate each item with media_type
            for item in results:
                item["media_type"] = media_type
            
            items.extend(results)
            
            total_pages = int(data.get("total_pages", page))
            if page >= total_pages:
                break
            
            page += 1
        
        return items
    
    def get_videos(self, media_type: str, tmdb_id: int) -> list[Dict[str, Any]]:
        """
        Get videos (trailers, teasers) for a movie or TV show.
        
        Args:
            media_type: "movie" or "tv"
            tmdb_id: TMDb ID
        
        Returns:
            List of video dictionaries
        """
        data = self._make_request(f"{media_type}/{tmdb_id}/videos")
        return data.get("results", [])
    
    def close(self) -> None:
        """Close session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
