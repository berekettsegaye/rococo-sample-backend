"""
Unit tests for common/services/oauth.py
"""
import pytest
import requests
from unittest.mock import MagicMock, patch
from common.services.oauth import OAuthClient


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config.GOOGLE_CLIENT_ID = "test-google-client-id"
    config.GOOGLE_CLIENT_SECRET = "test-google-secret"
    config.MICROSOFT_CLIENT_ID = "test-microsoft-client-id"
    config.MICROSOFT_CLIENT_SECRET = "test-microsoft-secret"
    return config


@pytest.fixture
def oauth_client(mock_config):
    """Create an OAuthClient instance."""
    return OAuthClient(mock_config)


class TestOAuthClientGetGoogleToken:
    """Tests for OAuthClient.get_google_token method."""

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post, oauth_client):
        """Test successful Google token exchange."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-access-token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        result = oauth_client.get_google_token(
            code="auth-code",
            redirect_uri="http://localhost/callback",
            code_verifier="verifier"
        )

        assert result['access_token'] == 'test-access-token'
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Verify the correct URL
        assert call_args[0][0] == 'https://oauth2.googleapis.com/token'

        # Verify the data payload
        data = call_args[1]['data']
        assert data['client_id'] == 'test-google-client-id'
        assert data['code'] == 'auth-code'
        assert data['grant_type'] == 'authorization_code'
        assert data['redirect_uri'] == 'http://localhost/callback'
        assert data['code_verifier'] == 'verifier'

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_failure(self, mock_post, oauth_client):
        """Test Google token exchange failure."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid code'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            oauth_client.get_google_token(
                code="invalid-code",
                redirect_uri="http://localhost/callback",
                code_verifier="verifier"
            )

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_network_error(self, mock_post, oauth_client):
        """Test Google token exchange with network error."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(requests.exceptions.RequestException):
            oauth_client.get_google_token(
                code="auth-code",
                redirect_uri="http://localhost/callback",
                code_verifier="verifier"
            )

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_non_200_status(self, mock_post, oauth_client):
        """Test Google token exchange with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            oauth_client.get_google_token(
                code="auth-code",
                redirect_uri="http://localhost/callback",
                code_verifier="verifier"
            )


class TestOAuthClientGetGoogleUserInfo:
    """Tests for OAuthClient.get_google_user_info method."""

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get, oauth_client):
        """Test successful Google user info retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/photo.jpg'
        }
        mock_get.return_value = mock_response

        result = oauth_client.get_google_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Verify URL
        assert call_args[0][0] == 'https://openidconnect.googleapis.com/v1/userinfo'

        # Verify headers
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_failure(self, mock_get, oauth_client):
        """Test Google user info retrieval failure."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            oauth_client.get_google_user_info('invalid-token')

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_empty_response(self, mock_get, oauth_client):
        """Test Google user info with empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = oauth_client.get_google_user_info('test-access-token')

        assert result == {}


class TestOAuthClientGetMicrosoftToken:
    """Tests for OAuthClient.get_microsoft_token method."""

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post, oauth_client):
        """Test successful Microsoft token exchange."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test-ms-token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        result = oauth_client.get_microsoft_token(
            code="auth-code",
            redirect_uri="http://localhost/callback",
            code_verifier="verifier"
        )

        assert result['access_token'] == 'test-ms-token'

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Verify URL
        assert call_args[0][0] == 'https://login.microsoftonline.com/common/oauth2/v2.0/token'

        # Verify data
        data = call_args[1]['data']
        assert data['client_id'] == 'test-microsoft-client-id'
        assert data['code'] == 'auth-code'
        assert data['scope'] == 'User.Read'
        assert data['grant_type'] == 'authorization_code'

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_failure(self, mock_post, oauth_client):
        """Test Microsoft token exchange failure."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            oauth_client.get_microsoft_token(
                code="invalid-code",
                redirect_uri="http://localhost/callback",
                code_verifier="verifier"
            )


class TestOAuthClientGetMicrosoftUserInfo:
    """Tests for OAuthClient.get_microsoft_user_info method."""

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success_with_mail(self, mock_get, oauth_client):
        """Test successful Microsoft user info retrieval with mail field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'mail': 'test@example.com',
            'displayName': 'Test User',
            'givenName': 'Test',
            'surname': 'User'
        }
        mock_get.return_value = mock_response

        result = oauth_client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Verify URL
        assert call_args[0][0] == 'https://graph.microsoft.com/v1.0/me'

        # Verify headers
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success_with_upn(self, mock_get, oauth_client):
        """Test Microsoft user info with userPrincipalName fallback."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        result = oauth_client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_no_email(self, mock_get, oauth_client):
        """Test Microsoft user info without email fields."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        result = oauth_client.get_microsoft_user_info('test-access-token')

        assert result['email'] is None
        assert result['name'] == 'Test User'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_failure(self, mock_get, oauth_client):
        """Test Microsoft user info retrieval failure."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            oauth_client.get_microsoft_user_info('invalid-token')

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_empty_display_name(self, mock_get, oauth_client):
        """Test Microsoft user info with missing displayName."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'mail': 'test@example.com'
        }
        mock_get.return_value = mock_response

        result = oauth_client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == ''


class TestOAuthClientConfiguration:
    """Tests for OAuthClient configuration."""

    def test_oauth_client_initialization(self, mock_config):
        """Test OAuthClient initialization stores config."""
        client = OAuthClient(mock_config)

        assert client.config == mock_config
        assert client.config.GOOGLE_CLIENT_ID == 'test-google-client-id'
        assert client.config.MICROSOFT_CLIENT_ID == 'test-microsoft-client-id'
