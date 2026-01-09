"""
Unit tests for the OAuthClient service.
"""
import pytest
from unittest.mock import MagicMock, patch
import requests


class TestOAuthClient:
    """Test OAuthClient methods."""

    def test_oauth_client_init(self):
        """Test OAuthClient initialization."""
        from common.services.oauth import OAuthClient

        mock_config = MagicMock()
        client = OAuthClient(mock_config)
        assert client.config == mock_config

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post):
        """Test get_google_token with successful response."""
        mock_config = MagicMock()
        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-secret"  # NOSONAR

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_token(
            code="test-code",
            redirect_uri="http://localhost:3000/callback",
            code_verifier="test-verifier"
        )

        assert result["access_token"] == "test-access-token"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://oauth2.googleapis.com/token'
        assert call_args[1]['data']['code'] == "test-code"

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_invalid_code(self, mock_post):
        """Test get_google_token with invalid code (400/401 error)."""
        mock_config = MagicMock()
        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-secret"  # NOSONAR

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid authorization code"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_token(
                code="invalid-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="test-verifier"
            )

        mock_post.assert_called_once()

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_network_error(self, mock_post):
        """Test get_google_token with network error (RequestException)."""
        mock_config = MagicMock()
        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-secret"  # NOSONAR

        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        client = OAuthClient(mock_config)
        with pytest.raises(requests.exceptions.RequestException):
            client.get_google_token(
                code="test-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="test-verifier"
            )

        mock_post.assert_called_once()

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get):
        """Test get_google_user_info with valid token."""
        mock_config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "sub": "123456789"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_user_info("test-access-token")

        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == 'https://openidconnect.googleapis.com/v1/userinfo'
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_invalid_token(self, mock_get):
        """Test get_google_user_info with invalid token."""
        mock_config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_user_info("invalid-token")

        mock_get.assert_called_once()

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post):
        """Test get_microsoft_token with valid code."""
        mock_config = MagicMock()
        mock_config.MICROSOFT_CLIENT_ID = "test-ms-client-id"
        mock_config.MICROSOFT_CLIENT_SECRET = "test-ms-secret"  # NOSONAR

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-ms-access-token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_token(
            code="test-code",
            redirect_uri="http://localhost:3000/callback",
            code_verifier="test-verifier"
        )

        assert result["access_token"] == "test-ms-access-token"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        assert call_args[1]['data']['code'] == "test-code"

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_invalid_code(self, mock_post):
        """Test get_microsoft_token with invalid code."""
        mock_config = MagicMock()
        mock_config.MICROSOFT_CLIENT_ID = "test-ms-client-id"
        mock_config.MICROSOFT_CLIENT_SECRET = "test-ms-secret"  # NOSONAR

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_token(
                code="invalid-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="test-verifier"
            )

        mock_post.assert_called_once()

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success(self, mock_get):
        """Test get_microsoft_user_info with valid token."""
        mock_config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "userPrincipalName": "test@example.com",
            "displayName": "Test User",
            "id": "123456"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info("test-access-token")

        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == 'https://graph.microsoft.com/v1.0/me'
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_mail_field(self, mock_get):
        """Test get_microsoft_user_info using mail field instead of userPrincipalName."""
        mock_config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "mail": "testuser@example.com",
            "displayName": "Test User",
            "id": "123456"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info("test-access-token")

        assert result["email"] == "testuser@example.com"
        assert result["name"] == "Test User"
        mock_get.assert_called_once()

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_invalid_token(self, mock_get):
        """Test get_microsoft_user_info with invalid token."""
        mock_config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "invalid_token"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_user_info("invalid-token")

        mock_get.assert_called_once()
