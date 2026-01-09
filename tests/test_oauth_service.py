"""
Unit tests for common/services/oauth.py
"""
import pytest
from unittest.mock import MagicMock, patch
import requests


class TestOAuthClient:
    """Tests for OAuthClient."""

    def test_init(self, mock_config):
        """Test OAuthClient initialization."""
        from common.services.oauth import OAuthClient

        client = OAuthClient(mock_config)

        assert client.config == mock_config

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post, mock_config):
        """Test successful Google OAuth token exchange."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-client-secret"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "google-access-token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_google_token(
            code="auth-code",
            redirect_uri="http://localhost:3000/callback",
            code_verifier="verifier-123"
        )

        assert result["access_token"] == "google-access-token"
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600

        # Verify the request was made with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://oauth2.googleapis.com/token'
        assert call_args[1]['data']['client_id'] == "test-client-id"
        assert call_args[1]['data']['client_secret'] == "test-client-secret"
        assert call_args[1]['data']['code'] == "auth-code"
        assert call_args[1]['data']['grant_type'] == 'authorization_code'
        assert call_args[1]['data']['redirect_uri'] == "http://localhost:3000/callback"
        assert call_args[1]['data']['code_verifier'] == "verifier-123"

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_failure(self, mock_post, mock_config):
        """Test Google OAuth token exchange failure."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-client-secret"

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_token(
                code="invalid-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="verifier-123"
            )

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_network_error(self, mock_post, mock_config):
        """Test Google OAuth token exchange with network error."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "test-client-id"
        mock_config.GOOGLE_CLIENT_SECRET = "test-client-secret"

        # Mock network error
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_google_token(
                code="auth-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="verifier-123"
            )

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get, mock_config):
        """Test successful Google user info retrieval."""
        from common.services.oauth import OAuthClient

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "123456789",
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "email": "john.doe@example.com",
            "email_verified": True,
            "picture": "https://example.com/photo.jpg"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_google_user_info("google-access-token")

        assert result["sub"] == "123456789"
        assert result["email"] == "john.doe@example.com"
        assert result["name"] == "John Doe"

        # Verify the request was made with correct headers
        mock_get.assert_called_once_with(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': 'Bearer google-access-token'}
        )

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_failure(self, mock_get, mock_config):
        """Test Google user info retrieval failure."""
        from common.services.oauth import OAuthClient

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_user_info("invalid-token")

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post, mock_config):
        """Test successful Microsoft OAuth token exchange."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "ms-client-id"
        mock_config.MICROSOFT_CLIENT_SECRET = "ms-client-secret"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "ms-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "User.Read"
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_microsoft_token(
            code="ms-auth-code",
            redirect_uri="http://localhost:3000/callback",
            code_verifier="verifier-456"
        )

        assert result["access_token"] == "ms-access-token"
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600

        # Verify the request was made with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        assert call_args[1]['data']['client_id'] == "ms-client-id"
        assert call_args[1]['data']['client_secret'] == "ms-client-secret"
        assert call_args[1]['data']['code'] == "ms-auth-code"
        assert call_args[1]['data']['grant_type'] == 'authorization_code'
        assert call_args[1]['data']['redirect_uri'] == "http://localhost:3000/callback"
        assert call_args[1]['data']['code_verifier'] == "verifier-456"
        assert call_args[1]['data']['scope'] == 'User.Read'

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_failure(self, mock_post, mock_config):
        """Test Microsoft OAuth token exchange failure."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "ms-client-id"
        mock_config.MICROSOFT_CLIENT_SECRET = "ms-client-secret"

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_token(
                code="invalid-code",
                redirect_uri="http://localhost:3000/callback",
                code_verifier="verifier-456"
            )

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success(self, mock_get, mock_config):
        """Test successful Microsoft user info retrieval."""
        from common.services.oauth import OAuthClient

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ms-user-id",
            "displayName": "Jane Smith",
            "userPrincipalName": "jane.smith@example.com",
            "mail": "jane.smith@example.com"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_microsoft_user_info("ms-access-token")

        assert result["email"] == "jane.smith@example.com"
        assert result["name"] == "Jane Smith"

        # Verify the request was made with correct headers
        mock_get.assert_called_once_with(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': 'Bearer ms-access-token'}
        )

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_upn(self, mock_get, mock_config):
        """Test Microsoft user info retrieval using userPrincipalName."""
        from common.services.oauth import OAuthClient

        # Mock response with only userPrincipalName
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ms-user-id",
            "displayName": "Jane Smith",
            "userPrincipalName": "jane.smith@example.com"
            # No 'mail' field
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_microsoft_user_info("ms-access-token")

        assert result["email"] == "jane.smith@example.com"
        assert result["name"] == "Jane Smith"

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_mail(self, mock_get, mock_config):
        """Test Microsoft user info retrieval using mail field."""
        from common.services.oauth import OAuthClient

        # Mock response with mail field
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ms-user-id",
            "displayName": "Jane Smith",
            "mail": "jane@example.com",
            "userPrincipalName": "jane.smith@example.onmicrosoft.com"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_microsoft_user_info("ms-access-token")

        # mail should be preferred over userPrincipalName
        assert result["email"] == "jane@example.com"
        assert result["name"] == "Jane Smith"

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_no_name(self, mock_get, mock_config):
        """Test Microsoft user info retrieval with missing display name."""
        from common.services.oauth import OAuthClient

        # Mock response without displayName
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ms-user-id",
            "userPrincipalName": "user@example.com"
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        result = client.get_microsoft_user_info("ms-access-token")

        assert result["email"] == "user@example.com"
        assert result["name"] == ""  # Default empty string

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_failure(self, mock_get, mock_config):
        """Test Microsoft user info retrieval failure."""
        from common.services.oauth import OAuthClient

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_user_info("invalid-token")
