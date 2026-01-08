"""
Unit tests for common/services/login_method.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.login_method import LoginMethodService
from common.models.login_method import LoginMethod


class TestLoginMethodService:
    """Tests for LoginMethodService."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_login_method_service_initialization(self, mock_factory):
        """Test LoginMethodService initializes correctly."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        service = LoginMethodService(config)

        assert service.config == config
        assert service.login_method_repo == mock_repo

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method(self, mock_factory):
        """Test save_login_method calls repository save."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        login_method = LoginMethod(method_type='oauth-google')
        mock_repo.save.return_value = login_method

        service = LoginMethodService(config)
        result = service.save_login_method(login_method)

        mock_repo.save.assert_called_once_with(login_method)
        assert result == login_method

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id(self, mock_factory):
        """Test get_login_method_by_email_id queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        login_method = LoginMethod(entity_id='lm-123', method_type='password')
        mock_repo.get_one.return_value = login_method

        service = LoginMethodService(config)
        result = service.get_login_method_by_email_id('email-123')

        mock_repo.get_one.assert_called_once_with({"email_id": 'email-123'})
        assert result == login_method

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_not_found(self, mock_factory):
        """Test get_login_method_by_email_id returns None when not found."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo
        mock_repo.get_one.return_value = None

        service = LoginMethodService(config)
        result = service.get_login_method_by_email_id('nonexistent-email-id')

        mock_repo.get_one.assert_called_once_with({"email_id": 'nonexistent-email-id'})
        assert result is None

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id(self, mock_factory):
        """Test get_login_method_by_id queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        login_method = LoginMethod(entity_id='lm-123', method_type='password')
        mock_repo.get_one.return_value = login_method

        service = LoginMethodService(config)
        result = service.get_login_method_by_id('lm-123')

        mock_repo.get_one.assert_called_once_with({"entity_id": 'lm-123'})
        assert result == login_method

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_not_found(self, mock_factory):
        """Test get_login_method_by_id returns None when not found."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo
        mock_repo.get_one.return_value = None

        service = LoginMethodService(config)
        result = service.get_login_method_by_id('nonexistent-id')

        mock_repo.get_one.assert_called_once_with({"entity_id": 'nonexistent-id'})
        assert result is None

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password(self, mock_factory):
        """Test update_password updates password and saves."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        login_method = LoginMethod(entity_id='lm-123', method_type='password')
        updated_login_method = LoginMethod(entity_id='lm-123', method_type='password')
        updated_login_method.password = 'new_hashed_password'

        mock_repo.save.return_value = updated_login_method

        service = LoginMethodService(config)
        result = service.update_password(login_method, 'new_hashed_password')

        assert login_method.password == 'new_hashed_password'
        mock_repo.save.assert_called_once_with(login_method)
        assert result.password == 'new_hashed_password'

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_with_none(self, mock_factory):
        """Test update_password can set password to None."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        login_method = LoginMethod(entity_id='lm-123', method_type='oauth-google')
        updated_login_method = LoginMethod(entity_id='lm-123', method_type='oauth-google')
        updated_login_method.password = None

        mock_repo.save.return_value = updated_login_method

        service = LoginMethodService(config)
        result = service.update_password(login_method, None)

        assert login_method.password is None
        mock_repo.save.assert_called_once_with(login_method)
        assert result.password is None
