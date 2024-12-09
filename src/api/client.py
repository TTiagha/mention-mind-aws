"""
MentionMind API client implementation
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT_CALLS,
    DEFAULT_RATE_LIMIT_PERIOD,
    DEFAULT_TIMEOUT,
    ENDPOINT_MENTIONS,
)
from .exceptions import APIError, ValidationError
from .mention_processor import MentionProcessor
from .token_manager import TokenManager

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter implementation"""

    def __init__(
        self,
        calls: int = DEFAULT_RATE_LIMIT_CALLS,
        period: float = DEFAULT_RATE_LIMIT_PERIOD,
    ):
        self.calls = calls
        self.period = period
        self.timestamps: List[float] = []

    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits"""
        now = time.time()
        self.timestamps = [ts for ts in self.timestamps if now - ts <= self.period]

        if len(self.timestamps) >= self.calls:
            sleep_time = self.timestamps[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.timestamps.append(now)


class MentionMindClient:
    """Client for interacting with the MentionMind API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        rate_limit_calls: int = DEFAULT_RATE_LIMIT_CALLS,
        rate_limit_period: float = DEFAULT_RATE_LIMIT_PERIOD,
    ) -> None:
        """
        Initialize the MentionMind API client

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_calls: Number of calls allowed per period
            rate_limit_period: Period for rate limiting in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries  # Store max_retries as instance variable

        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "POST",
            ],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Initialize components
        self.token_manager = TokenManager(self.session, self.base_url)
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_period)
        self.mention_processor = MentionProcessor()  # Initialize MentionProcessor

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request with rate limiting and error handling

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body data

        Returns:
            Dict[str, Any]: API response data

        Raises:
            APIError: If the API request fails
        """
        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.token_manager.get_auth_headers(self.api_key)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=self.timeout,
            )

            if not response.ok:
                raise APIError(
                    f"API request failed: {response.text}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None,
                )

            # Return empty dict for successful empty responses (e.g., DELETE)
            if not response.text:
                return {}

            result = response.json()
            if not isinstance(result, dict):
                return {"data": result}
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if isinstance(e, requests.exceptions.HTTPError):
                raise APIError(
                    f"API request failed: {str(e)}",
                    status_code=e.response.status_code,
                    response=e.response.json() if e.response.text else None,
                )
            raise APIError(f"API request failed: {str(e)}")

    def get_mentions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        process: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch mentions from the API

        Args:
            start_date: ISO format date string (YYYY-MM-DD)
            end_date: ISO format date string (YYYY-MM-DD)
            limit: Maximum number of mentions to return
            process: Whether to process the mentions through the mention processor

        Returns:
            List[Dict[str, Any]]: List of mention objects

        Raises:
            ValidationError: If parameters are invalid
            APIError: If the API request fails
        """
        # Validate parameters
        if start_date and not self._is_valid_date(start_date):
            raise ValidationError("start_date must be in YYYY-MM-DD format")
        if end_date and not self._is_valid_date(end_date):
            raise ValidationError("end_date must be in YYYY-MM-DD format")

        params = {
            "limit": str(limit),  # Convert to string for API
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = self._make_request("GET", ENDPOINT_MENTIONS, params=params)
        mentions = cast(List[Dict[str, Any]], response.get("mentions", []))

        if process:
            processed_mentions = self.mention_processor.process_mentions(mentions)
            return processed_mentions
        return mentions

    def remove_mention(self, mention_id: str, project_id: Optional[str] = None) -> bool:
        """
        Remove a mention by its ID

        Args:
            mention_id: ID of the mention to remove
            project_id: Optional project ID

        Returns:
            bool: True if successful

        Raises:
            ValidationError: If mention_id is empty
            APIError: If the API request fails
        """
        if not mention_id:
            raise ValidationError("mention_id is required")

        data = {"mention_id": mention_id}
        if project_id:
            data["project_id"] = project_id

        self._make_request(
            method="POST", endpoint=f"{ENDPOINT_MENTIONS}/remove", json=data
        )
        return True

    def remove_all_mentions(self, project_id: str) -> bool:
        """
        Remove all mentions for a project

        Args:
            project_id: ID of the project

        Returns:
            bool: True if successful

        Raises:
            ValidationError: If project_id is empty
            APIError: If the API request fails
        """
        if not project_id:
            raise ValidationError("project_id is required")

        self._make_request(
            method="POST",
            endpoint=f"{ENDPOINT_MENTIONS}/remove_all",
            json={"project_id": project_id},
        )
        return True

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date string format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
