"""
Token management for the MentionMind API
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

from .exceptions import AuthError


class TokenManager:
    """Manage authentication tokens for the MentionMind API"""

    def __init__(self, session: requests.Session, base_url: str) -> None:
        """
        Initialize token manager

        Args:
            session: Requests session to use for API calls
            base_url: Base URL for the API
        """
        self.session = session
        self.base_url = base_url
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        """
        Get authentication headers for API requests

        Args:
            api_key: API key to use for authentication

        Returns:
            Dict containing authentication headers
        """
        if not self.token or (
            self.token_expiry and datetime.now() >= self.token_expiry
        ):
            self._refresh_token(api_key)

        return {"Authorization": f"Bearer {self.token}"}

    def _refresh_token(self, api_key: str) -> None:
        """
        Refresh the authentication token

        Args:
            api_key: API key to use for authentication

        Raises:
            AuthError: If token refresh fails
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                json={"apiKey": api_key},
            )

            if not response.ok:
                raise AuthError(
                    f"Failed to refresh token: {response.text}",
                )

            data = response.json()
            self.token = data["token"]
            self.token_expiry = datetime.now() + timedelta(
                seconds=data.get("expiresIn", 3600)
            )

        except requests.exceptions.RequestException as e:
            raise AuthError(f"Failed to refresh token: {str(e)}")
