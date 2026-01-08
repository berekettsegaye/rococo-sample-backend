"""
Unit tests for common/services/oauth.py
"""
import pytest
from unittest.mock import MagicMock, patch
import requests
from common.services.oauth import OAuthClient


class TestOAuthClient:
    """Tests for OAuthClient."""

    def test_oauth_client_initialization(self):
        """Test OAuthClient initializes correctly."""
        config = MagicMock()
        client = OAuthClient(config)

        assert client.config == config

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post):
        """Test get_google_token with successful response."""
        config = MagicMock()
        config.GOOGLE_CLIENT_ID = 'test-client-id'
        config.GOOGLE_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test-token', 'token_type': 'Bearer'}
        mock_post.return_value = mock_response

        client = OAuthClient(config)
        result = client.get_google_token('auth-code', 'http://localhost/callback', 'verifier')

        mock_post.assert_called_once()
        assert result['access_token'] == 'test-token'

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_error(self, mock_post):
        """Test get_google_token with error response."""
        config = MagicMock()
        config.GOOGLE_CLIENT_ID = 'test-client-id'
        config.GOOGLE_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid request'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('400 Client Error')
        mock_post.return_value = mock_response

        client = OAuthClient(config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_token('invalid-code', 'http://localhost/callback', 'verifier')

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get):
        """Test get_google_user_info with successful response."""
        config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'sub': 'google-123'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(config)
        result = client.get_google_user_info('test-access-token')

        mock_get.assert_called_once()
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_error(self, mock_get):
        """Test get_google_user_info with error response."""
        config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('401 Unauthorized')
        mock_get.return_value = mock_response

        client = OAuthClient(config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_user_info('invalid-token')

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post):
        """Test get_microsoft_token with successful response."""
        config = MagicMock()
        config.MICROSOFT_CLIENT_ID = 'test-client-id'
        config.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test-token', 'token_type': 'Bearer'}
        mock_post.return_value = mock_response

        client = OAuthClient(config)
        result = client.get_microsoft_token('auth-code', 'http://localhost/callback', 'verifier')

        mock_post.assert_called_once()
        assert result['access_token'] == 'test-token'

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_error(self, mock_post):
        """Test get_microsoft_token with error response."""
        config = MagicMock()
        config.MICROSOFT_CLIENT_ID = 'test-client-id'
        config.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('400 Client Error')
        mock_post.return_value = mock_response

        client = OAuthClient(config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_token('invalid-code', 'http://localhost/callback', 'verifier')

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success(self, mock_get):
        """Test get_microsoft_user_info with successful response and transformation."""
        config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com',
            'displayName': 'Test User',
            'id': 'microsoft-123'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(config)
        result = client.get_microsoft_user_info('test-access-token')

        mock_get.assert_called_once()
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_mail_field(self, mock_get):
        """Test get_microsoft_user_info uses mail field if userPrincipalName is missing."""
        config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'mail': 'test@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(config)
        result = client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_error(self, mock_get):
        """Test get_microsoft_user_info with error response."""
        config = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('401 Unauthorized')
        mock_get.return_value = mock_response

        client = OAuthClient(config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_user_info('invalid-token')
