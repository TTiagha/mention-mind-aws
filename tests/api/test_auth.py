"""
Tests for authentication functionality
"""

import pytest
import requests_mock
from typing import Dict

from src.api.auth import Auth
from src.api.exceptions import AuthError


@pytest.fixture
def auth() -> Auth:
    return Auth("test_client_id", "test_client_secret")


def test_init(auth: Auth) -> None:
    """Test initialization of Auth class"""
    assert auth.client_id == "test_client_id"
    assert auth.client_secret == "test_client_secret"
    assert auth.access_token is None
    assert auth.token_expiry is None


def test_get_auth_header_no_token(auth: Auth) -> None:
    """Test getting auth header with no token"""
    with pytest.raises(AuthError) as exc_info:
        auth.get_auth_header()
    assert "No access token available" in str(exc_info.value)


def test_get_auth_header_with_token(auth: Auth) -> None:
    """Test getting auth header with token"""
    auth.access_token = "test_token"
    headers: Dict[str, str] = auth.get_auth_header()
    assert headers["Authorization"] == "Bearer test_token"


def test_get_token_success(auth: Auth) -> None:
    """Test successful token retrieval"""
    with requests_mock.Mocker() as m:
        m.post(
            "https://api.mentionmind.com/oauth/token",
            json={"access_token": "test_token", "expires_in": 3600},
        )
        auth.get_token()
        assert auth.access_token == "test_token"
        assert auth.token_expiry is not None


def test_get_token_failure(auth: Auth) -> None:
    """Test failed token retrieval"""
    with requests_mock.Mocker() as m:
        m.post("https://api.mentionmind.com/oauth/token", status_code=401)
        with pytest.raises(AuthError) as exc_info:
            auth.get_token()
        assert "Failed to get access token" in str(exc_info.value)


def test_get_token_invalid_response(auth: Auth) -> None:
    """Test invalid response from token endpoint"""
    with requests_mock.Mocker() as m:
        m.post("https://api.mentionmind.com/oauth/token", json={})
        with pytest.raises(AuthError) as exc_info:
            auth.get_token()
        assert "Invalid token response" in str(exc_info.value)


def test_get_token_server_error(auth: Auth) -> None:
    """Test server error during token retrieval"""
    with requests_mock.Mocker() as m:
        m.post("https://api.mentionmind.com/oauth/token", status_code=500)
        with pytest.raises(AuthError) as exc_info:
            auth.get_token()
        assert "Failed to get access token" in str(exc_info.value)
