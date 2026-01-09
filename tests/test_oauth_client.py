"""
Unit tests for common/services/oauth.py
"""
import pytest
from unittest.mock import MagicMock, patch
import requests


class TestOAuthClientInit:
    """Tests for OAuthClient initialization."""

    def test_init(self, mock_config):
        """Test client initialization."""
        from common.services.oauth import OAuthClient

        client = OAuthClient(mock_config)

        assert client.config == mock_config


class TestOAuthClientGoogle:
    """Tests for Google OAuth functionality."""

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post, mock_config):
        """Test successful Google token retrieval."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "google_client_id"
        mock_config.GOOGLE_CLIENT_SECRET = "google_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_token(
            code="auth_code",
            redirect_uri="https://example.com/callback",
            code_verifier="code_verifier_123"
        )

        assert result['access_token'] == 'test_access_token'
        assert result['token_type'] == 'Bearer'
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://oauth2.googleapis.com/token'
        assert call_args[1]['data']['client_id'] == 'google_client_id'
        assert call_args[1]['data']['code'] == 'auth_code'

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_error_response(self, mock_post, mock_config):
        """Test Google token retrieval with error response."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "google_client_id"
        mock_config.GOOGLE_CLIENT_SECRET = "google_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid grant"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_token(
                code="invalid_code",
                redirect_uri="https://example.com/callback",
                code_verifier="code_verifier_123"
            )

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_request_exception(self, mock_post, mock_config):
        """Test Google token retrieval with request exception."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "google_client_id"
        mock_config.GOOGLE_CLIENT_SECRET = "google_client_secret"

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.RequestException):
            client.get_google_token(
                code="auth_code",
                redirect_uri="https://example.com/callback",
                code_verifier="code_verifier_123"
            )

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get, mock_config):
        """Test successful Google user info retrieval."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/photo.jpg'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_user_info(access_token="test_token")

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        mock_get.assert_called_once_with(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_error(self, mock_get, mock_config):
        """Test Google user info retrieval with error."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_user_info(access_token="invalid_token")


class TestOAuthClientMicrosoft:
    """Tests for Microsoft OAuth functionality."""

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post, mock_config):
        """Test successful Microsoft token retrieval."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "microsoft_client_id"
        mock_config.MICROSOFT_CLIENT_SECRET = "microsoft_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_token(
            code="auth_code",
            redirect_uri="https://example.com/callback",
            code_verifier="code_verifier_123"
        )

        assert result['access_token'] == 'test_access_token'
        assert result['token_type'] == 'Bearer'
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        assert call_args[1]['data']['client_id'] == 'microsoft_client_id'
        assert call_args[1]['data']['code'] == 'auth_code'
        assert call_args[1]['data']['scope'] == 'User.Read'

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_error_response(self, mock_post, mock_config):
        """Test Microsoft token retrieval with error response."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "microsoft_client_id"
        mock_config.MICROSOFT_CLIENT_SECRET = "microsoft_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'invalid_grant'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_token(
                code="invalid_code",
                redirect_uri="https://example.com/callback",
                code_verifier="code_verifier_123"
            )

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_with_pkce(self, mock_post, mock_config):
        """Test Microsoft token retrieval includes PKCE code_verifier."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "microsoft_client_id"
        mock_config.MICROSOFT_CLIENT_SECRET = "microsoft_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        client.get_microsoft_token(
            code="auth_code",
            redirect_uri="https://example.com/callback",
            code_verifier="pkce_code_verifier"
        )

        call_args = mock_post.call_args
        assert call_args[1]['data']['code_verifier'] == 'pkce_code_verifier'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success(self, mock_get, mock_config):
        """Test successful Microsoft user info retrieval."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com',
            'displayName': 'Test User',
            'givenName': 'Test',
            'surname': 'User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info(access_token="test_token")

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        mock_get.assert_called_once_with(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': 'Bearer test_token'}
        )

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_mail_field(self, mock_get, mock_config):
        """Test Microsoft user info retrieval using 'mail' field."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'mail': 'test@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info(access_token="test_token")

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_no_display_name(self, mock_get, mock_config):
        """Test Microsoft user info retrieval without displayName."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info(access_token="test_token")

        assert result['email'] == 'test@example.com'
        assert result['name'] == ''

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_error(self, mock_get, mock_config):
        """Test Microsoft user info retrieval with error."""
        from common.services.oauth import OAuthClient

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_user_info(access_token="invalid_token")

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_network_error(self, mock_get, mock_config):
        """Test Microsoft user info retrieval with network error."""
        from common.services.oauth import OAuthClient

        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_microsoft_user_info(access_token="test_token")


class TestOAuthClientEdgeCases:
    """Tests for OAuth edge cases."""

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_with_special_characters(self, mock_post, mock_config):
        """Test Google token with special characters in parameters."""
        from common.services.oauth import OAuthClient

        mock_config.GOOGLE_CLIENT_ID = "google_client_id"
        mock_config.GOOGLE_CLIENT_SECRET = "google_client_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'token'}
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        client.get_google_token(
            code="code/with+special=chars",
            redirect_uri="https://example.com/callback?param=value",
            code_verifier="verifier-123_abc"
        )

        # Should not raise and should handle special characters
        assert mock_post.called

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_timeout(self, mock_post, mock_config):
        """Test Microsoft token retrieval with timeout."""
        from common.services.oauth import OAuthClient

        mock_config.MICROSOFT_CLIENT_ID = "microsoft_client_id"
        mock_config.MICROSOFT_CLIENT_SECRET = "microsoft_client_secret"

        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.Timeout):
            client.get_microsoft_token(
                code="auth_code",
                redirect_uri="https://example.com/callback",
                code_verifier="code_verifier"
            )
