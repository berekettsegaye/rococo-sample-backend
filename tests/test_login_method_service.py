"""
Unit tests for common/services/login_method.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.login_method import LoginMethodService
from common.models import LoginMethod


class TestLoginMethodService:
    """Tests for LoginMethodService."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method(self, mock_repo_factory, mock_config):
        """Test saving a login method."""
        login_method = LoginMethod(method_type='password')
        mock_repo = MagicMock()
        mock_repo.save.return_value = login_method
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.save_login_method(login_method)

        assert result == login_method
        mock_repo.save.assert_called_once_with(login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_success(self, mock_repo_factory, mock_config):
        """Test getting login method by email ID successfully."""
        login_method = LoginMethod(entity_id='login-id', email_id='email-id')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = login_method
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id('email-id')

        assert result == login_method
        mock_repo.get_one.assert_called_once_with({"email_id": "email-id"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting login method by email ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id('nonexistent-email-id')

        assert result is None

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_success(self, mock_repo_factory, mock_config):
        """Test getting login method by ID successfully."""
        login_method = LoginMethod(entity_id='login-id')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = login_method
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id('login-id')

        assert result == login_method
        mock_repo.get_one.assert_called_once_with({"entity_id": "login-id"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting login method by ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id('nonexistent-id')

        assert result is None

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password(self, mock_repo_factory, mock_config):
        """Test updating login method password."""
        login_method = LoginMethod(entity_id='login-id', password='old-hash')
        updated_login_method = LoginMethod(entity_id='login-id', password='new-hash')

        mock_repo = MagicMock()
        mock_repo.save.return_value = updated_login_method
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)
        result = service.update_password(login_method, 'new-hash')

        assert result.password == 'new-hash'
        mock_repo.save.assert_called_once()
