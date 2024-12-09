"""
Authentication for the MentionMind API
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

from .exceptions import AuthError


class Auth:
    """Handle authentication with the MentionMind API"""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """
        Initialize authentication handler

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def get_auth_header(self) -> Dict[str, str]:
        """
        Get authentication header for API requests

        Returns:
            Dict containing Authorization header

        Raises:
            AuthError: If no access token is available
        """
        if not self.access_token:
            raise AuthError("No access token available")
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_token(self) -> None:
        """
        Get a new access token from the API

        Raises:
            AuthError: If token request fails
        """
        try:
            response = requests.post(
                "https://api.mentionmind.com/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

            if response.status_code != 200:
                msg = f"Failed to get access token: {response.status_code}"
                raise AuthError(f"{msg} {response.text}")

            data = response.json()
            if "access_token" not in data or "expires_in" not in data:
                raise AuthError("Invalid token response")

            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        except requests.exceptions.RequestException as e:
            raise AuthError(f"Failed to get access token: {str(e)}")

    def is_token_expired(self) -> bool:
        """
        Check if the access token is expired

        Returns:
            bool: True if token is expired, False otherwise
        """
        if not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry

    def refresh_token(self) -> None:
        """
        Refresh the access token

        Raises:
            AuthError: If token refresh fails
        """
        if not self.is_token_expired():
            return
        self.get_token()
