"""
Unit tests for common/services/oauth.py
"""
import pytest
import requests
from unittest.mock import MagicMock, patch
from common.services.oauth import OAuthClient


class TestOAuthClientGoogle:
    """Tests for Google OAuth functionality."""

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_success(self, mock_post, mock_config):
        """Test successfully getting Google OAuth token."""
        mock_config.GOOGLE_CLIENT_ID = 'test-client-id'
        mock_config.GOOGLE_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-access-token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_token('auth-code', 'http://localhost:3000/callback', 'verifier')

        assert result['access_token'] == 'test-access-token'
        assert result['expires_in'] == 3600
        mock_post.assert_called_once()

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_failure(self, mock_post, mock_config):
        """Test handling Google OAuth token request failure."""
        mock_config.GOOGLE_CLIENT_ID = 'test-client-id'
        mock_config.GOOGLE_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_token('invalid-code', 'http://localhost:3000/callback', 'verifier')

    @patch('common.services.oauth.requests.post')
    def test_get_google_token_network_error(self, mock_post, mock_config):
        """Test handling network error during Google OAuth token request."""
        mock_config.GOOGLE_CLIENT_ID = 'test-client-id'
        mock_config.GOOGLE_CLIENT_SECRET = 'test-client-secret'

        mock_post.side_effect = requests.exceptions.ConnectionError('Network error')

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_google_token('auth-code', 'http://localhost:3000/callback', 'verifier')

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_success(self, mock_get, mock_config):
        """Test successfully getting Google user info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'http://example.com/pic.jpg'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_google_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        mock_get.assert_called_once()

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_failure(self, mock_get, mock_config):
        """Test handling failure when getting Google user info."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_google_user_info('invalid-token')

    @patch('common.services.oauth.requests.get')
    def test_get_google_user_info_with_headers(self, mock_get, mock_config):
        """Test that correct headers are sent when getting Google user info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'email': 'test@example.com'}
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        client.get_google_user_info('test-access-token')

        call_args = mock_get.call_args
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'


class TestOAuthClientMicrosoft:
    """Tests for Microsoft OAuth functionality."""

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_success(self, mock_post, mock_config):
        """Test successfully getting Microsoft OAuth token."""
        mock_config.MICROSOFT_CLIENT_ID = 'test-client-id'
        mock_config.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-access-token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_token('auth-code', 'http://localhost:3000/callback', 'verifier')

        assert result['access_token'] == 'test-access-token'
        assert result['expires_in'] == 3600
        mock_post.assert_called_once()

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_failure(self, mock_post, mock_config):
        """Test handling Microsoft OAuth token request failure."""
        mock_config.MICROSOFT_CLIENT_ID = 'test-client-id'
        mock_config.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_token('invalid-code', 'http://localhost:3000/callback', 'verifier')

    @patch('common.services.oauth.requests.post')
    def test_get_microsoft_token_with_pkce(self, mock_post, mock_config):
        """Test Microsoft OAuth token request includes PKCE verifier."""
        mock_config.MICROSOFT_CLIENT_ID = 'test-client-id'
        mock_config.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'token'}
        mock_post.return_value = mock_response

        client = OAuthClient(mock_config)
        client.get_microsoft_token('code', 'http://localhost:3000/callback', 'test-verifier')

        call_args = mock_post.call_args
        assert call_args[1]['data']['code_verifier'] == 'test-verifier'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_success(self, mock_get, mock_config):
        """Test successfully getting Microsoft user info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com',
            'displayName': 'Test User',
            'mail': 'test@example.com'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        mock_get.assert_called_once()

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_mail_fallback(self, mock_get, mock_config):
        """Test Microsoft user info uses mail field when userPrincipalName is not present."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'mail': 'test@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'test@example.com'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_prefers_principal_name(self, mock_get, mock_config):
        """Test Microsoft user info prefers userPrincipalName over mail."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'principal@example.com',
            'mail': 'mail@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info('test-access-token')

        assert result['email'] == 'principal@example.com'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_failure(self, mock_get, mock_config):
        """Test handling failure when getting Microsoft user info."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)

        with pytest.raises(requests.exceptions.HTTPError):
            client.get_microsoft_user_info('invalid-token')

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_headers(self, mock_get, mock_config):
        """Test that correct headers are sent when getting Microsoft user info."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com',
            'displayName': 'Test User'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        client.get_microsoft_user_info('test-access-token')

        call_args = mock_get.call_args
        assert call_args[1]['headers']['Authorization'] == 'Bearer test-access-token'

    @patch('common.services.oauth.requests.get')
    def test_get_microsoft_user_info_with_empty_display_name(self, mock_get, mock_config):
        """Test Microsoft user info handles missing displayName."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'userPrincipalName': 'test@example.com'
        }
        mock_get.return_value = mock_response

        client = OAuthClient(mock_config)
        result = client.get_microsoft_user_info('test-access-token')

        assert result['name'] == ''
