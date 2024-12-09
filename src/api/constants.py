"""
Constants for the MentionMind API client
"""

# API Configuration
DEFAULT_BASE_URL = "https://app.mentionmind.com/api"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3

# Rate Limiting
DEFAULT_RATE_LIMIT_CALLS = 100
DEFAULT_RATE_LIMIT_PERIOD = 60.0  # seconds

# Endpoints
ENDPOINT_LOGIN = "/login.php"
ENDPOINT_MENTIONS = "/mention.php"

# Functions
FUNCTION_GET_MENTIONS = "getMentions"
FUNCTION_GET_RECOMMENDATIONS = "getRecommendations"
FUNCTION_GET_TOTAL_MENTIONS = "getTotalMentions"
FUNCTION_REMOVE_MENTION = "removeMention"
FUNCTION_REMOVE_ALL_MENTIONS = "removeAllMentions"

# HTTP Headers
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_USER_AGENT = "User-Agent"
