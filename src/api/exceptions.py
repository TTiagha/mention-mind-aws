"""
Custom exceptions for the MentionMind API client
"""


from typing import Dict, Optional


class MentionMindError(Exception):
    """Base exception for MentionMind API errors"""

    pass


class RateLimitError(MentionMindError):
    """Raised when rate limit is exceeded"""

    pass


class ValidationError(MentionMindError):
    """Raised when request validation fails"""

    pass


class AuthError(MentionMindError):
    """Raised when authentication fails"""

    pass


class APIError(MentionMindError):
    """Raised when the API returns an error response"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
