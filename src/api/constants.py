"""
Constants for the MentionMind API client
"""

# API Configuration
DEFAULT_BASE_URL = "https://api.mentionmind.com/v1"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3

# Rate Limiting
DEFAULT_RATE_LIMIT_CALLS = 100
DEFAULT_RATE_LIMIT_PERIOD = 60.0  # seconds

# Authentication
TOKEN_REFRESH_BUFFER = 300  # seconds (5 minutes before expiry)

# Endpoints
ENDPOINT_AUTH = "/auth"
ENDPOINT_MENTIONS = "/mentions"

# HTTP Headers
CONTENT_TYPE_JSON = "application/json"
HEADER_AUTHORIZATION = "Authorization"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_ACCEPT = "Accept"
