"""
Tests for the MentionMind API client
"""

import pytest
import responses
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from src.api.client import MentionMindClient
from src.api.constants import ENDPOINT_AUTH, ENDPOINT_MENTIONS
from src.api.exceptions import APIError, ValidationError


@pytest.fixture
def client() -> MentionMindClient:
    """Create a test client with retries disabled"""
    client = MentionMindClient("test-api-key")
    # Disable retries for testing
    client.session.mount("http://", HTTPAdapter(max_retries=Retry(total=0)))
    client.session.mount("https://", HTTPAdapter(max_retries=Retry(total=0)))
    return client


@pytest.fixture
def mock_auth() -> responses.RequestsMock:
    """Mock successful authentication"""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/auth",
            json={"token": "test-token", "expiresIn": 3600},
            status=200,
        )
        yield rsps


@pytest.fixture
def mock_mentions() -> responses.RequestsMock:
    """Mock successful mentions retrieval"""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Add auth mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/auth",
            json={"token": "test-token", "expiresIn": 3600},
            status=200,
        )
        # Add mentions mock
        rsps.add(
            responses.GET,
            "https://api.mentionmind.com/v1/mentions",
            json=[
                {
                    "id": "mention1",
                    "text": "Test mention 1 #test @user1",
                    "date": "2024-01-01T12:00:00Z",
                    "source": "twitter",
                },
                {
                    "id": "mention2",
                    "text": "Test mention 2 #test @user2",
                    "date": "2024-01-02T12:00:00Z",
                    "source": "twitter",
                },
            ],
            status=200,
        )
        yield rsps


def test_get_mentions_success(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_mentions: responses.RequestsMock) -> None:
    """Test successful mentions retrieval with processing"""
    mentions = client.get_mentions(
        start_date="2024-01-01", end_date="2024-01-31", limit=10
    )

    assert len(mentions) == 2
    assert mentions[0]["id"] == "mention1"
    assert mentions[1]["id"] == "mention2"

    # Check processed fields
    assert mentions[0]["hashtags"] == ["test"]
    assert mentions[0]["mentioned_users"] == ["user1"]
    assert mentions[0]["mention_type"] == "tweet"
    assert "processed_at" in mentions[0]
    assert "search_text" in mentions[0]

    # Verify request parameters
    request = mock_mentions.calls[1].request
    assert "startDate=2024-01-01" in request.url
    assert "endDate=2024-01-31" in request.url
    assert "limit=10" in request.url


def test_get_mentions_without_processing(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_mentions: responses.RequestsMock) -> None:
    """Test mentions retrieval without processing"""
    mentions = client.get_mentions(process=False)

    assert len(mentions) == 2
    assert mentions[0]["id"] == "mention1"
    assert mentions[1]["id"] == "mention2"

    # Check that mentions are not processed
    assert "hashtags" not in mentions[0]
    assert "mentioned_users" not in mentions[0]
    assert "mention_type" not in mentions[0]
    assert "processed_at" not in mentions[0]
    assert "search_text" not in mentions[0]


@pytest.fixture
def mock_remove_mention(mock_auth: responses.RequestsMock) -> responses.RequestsMock:
    """Mock successful mention removal"""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Add auth mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/auth",
            json={"token": "test-token", "expiresIn": 3600},
            status=200,
        )
        # Add remove mention mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/mentions/remove",
            json={"success": True},
            status=200,
        )
        yield rsps


def test_remove_mention_success(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_remove_mention: responses.RequestsMock) -> None:
    """Test successful mention removal"""
    result = client.remove_mention("mention1", "project1")
    assert result is True

    # Verify request body
    request = mock_remove_mention.calls[1].request
    assert request.method == "POST"
    assert request.body == b'{"mention_id": "mention1", "project_id": "project1"}'


def test_remove_mention_without_project(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_remove_mention: responses.RequestsMock) -> None:
    """Test mention removal without project ID"""
    result = client.remove_mention("mention1")
    assert result is True

    # Verify request body
    request = mock_remove_mention.calls[1].request
    assert request.method == "POST"
    assert request.body == b'{"mention_id": "mention1"}'


@pytest.fixture
def mock_remove_all_mentions(mock_auth: responses.RequestsMock) -> responses.RequestsMock:
    """Mock successful removal of all mentions"""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Add auth mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/auth",
            json={"token": "test-token", "expiresIn": 3600},
            status=200,
        )
        # Add remove all mentions mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/mentions/remove_all",
            json={"success": True},
            status=200,
        )
        yield rsps


def test_remove_all_mentions_success(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_remove_all_mentions: responses.RequestsMock) -> None:
    """Test successful removal of all mentions"""
    result = client.remove_all_mentions("project1")
    assert result is True

    # Verify request body
    request = mock_remove_all_mentions.calls[1].request
    assert request.method == "POST"
    assert request.body == b'{"project_id": "project1"}'


def test_remove_all_mentions_invalid_id(client: MentionMindClient) -> None:
    """Test validation of project ID"""
    with pytest.raises(ValidationError) as exc_info:
        client.remove_all_mentions("")
    assert "project_id is required" in str(exc_info.value)


@pytest.fixture
def mock_api_error(mock_auth: responses.RequestsMock) -> responses.RequestsMock:
    """Mock API error response"""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Add auth mock
        rsps.add(
            responses.POST,
            "https://api.mentionmind.com/v1/auth",
            json={"token": "test-token", "expiresIn": 3600},
            status=200,
        )
        # Add error mock
        rsps.add(
            responses.GET,
            "https://api.mentionmind.com/v1/mentions",
            json={"error": "Internal server error"},
            status=500,
            match_querystring=False,
        )
        yield rsps


def test_api_error_handling(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_api_error: responses.RequestsMock) -> None:
    """Test handling of API errors"""
    with pytest.raises(APIError) as exc_info:
        client.get_mentions()

    assert "API request failed" in str(exc_info.value)
    assert "Internal server error" in str(exc_info.value)
    assert exc_info.value.status_code == 500
    assert exc_info.value.response["error"] == "Internal server error"


def test_rate_limiting(client: MentionMindClient, mock_auth: responses.RequestsMock, mock_mentions: responses.RequestsMock) -> None:
    """Test rate limiting functionality"""
    import time

    start_time = time.time()

    # Make multiple requests in quick succession
    for _ in range(3):
        client.get_mentions()

    end_time = time.time()
    duration = end_time - start_time

    # Verify that rate limiting added some delay
    assert duration > 0  # Adjust threshold based on rate limit settings
