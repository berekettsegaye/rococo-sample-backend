"""
Unit tests for common/services/login_method.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestLoginMethodServiceInit:
    """Tests for LoginMethodService initialization."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.login_method import LoginMethodService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)


class TestLoginMethodServiceSaveLoginMethod:
    """Tests for save_login_method functionality."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method_success(self, mock_factory_class, mock_config):
        """Test saving a login method successfully."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_saved_login_method = MagicMock()
        mock_saved_login_method.entity_id = "login-method-123"
        mock_repo.save.return_value = mock_saved_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        input_login_method = MagicMock()
        result = service.save_login_method(input_login_method)

        assert result == mock_saved_login_method
        mock_repo.save.assert_called_once_with(input_login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method_returns_saved_object(self, mock_factory_class, mock_config):
        """Test that save_login_method returns the saved object."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_saved = MagicMock()
        mock_repo.save.return_value = mock_saved

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        input_login_method = MagicMock()
        result = service.save_login_method(input_login_method)

        assert result == mock_saved


class TestLoginMethodServiceGetLoginMethodByEmailId:
    """Tests for get_login_method_by_email_id functionality."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_success(self, mock_factory_class, mock_config):
        """Test getting login method by email ID successfully."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_login_method.email_id = "email-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id("email-123")

        assert result == mock_login_method
        mock_repo.get_one.assert_called_once_with({"email_id": "email-123"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_not_found(self, mock_factory_class, mock_config):
        """Test getting login method when not found."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id("nonexistent-email-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"email_id": "nonexistent-email-id"})


class TestLoginMethodServiceGetLoginMethodById:
    """Tests for get_login_method_by_id functionality."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_success(self, mock_factory_class, mock_config):
        """Test getting login method by ID successfully."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_login_method.entity_id = "login-method-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id("login-method-123")

        assert result == mock_login_method
        mock_repo.get_one.assert_called_once_with({"entity_id": "login-method-123"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting login method by ID when not found."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})


class TestLoginMethodServiceUpdatePassword:
    """Tests for update_password functionality."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_success(self, mock_factory_class, mock_config):
        """Test updating password successfully."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_login_method.password = "old_hashed_password"

        mock_updated_login_method = MagicMock()
        mock_updated_login_method.password = "new_hashed_password"

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_updated_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.update_password(mock_login_method, "new_hashed_password")

        assert result == mock_updated_login_method
        assert mock_login_method.password == "new_hashed_password"
        mock_repo.save.assert_called_once_with(mock_login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_changes_password_field(self, mock_factory_class, mock_config):
        """Test that update_password changes the password field."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_login_method.password = "old_password"

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        service.update_password(mock_login_method, "new_hashed_password")

        assert mock_login_method.password == "new_hashed_password"

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_calls_save(self, mock_factory_class, mock_config):
        """Test that update_password saves the login method."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_saved_login_method = MagicMock()

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_saved_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.update_password(mock_login_method, "new_password_hash")

        mock_repo.save.assert_called_once_with(mock_login_method)
        assert result == mock_saved_login_method

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_returns_saved_object(self, mock_factory_class, mock_config):
        """Test that update_password returns the saved login method."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_saved = MagicMock()

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_saved

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        result = service.update_password(mock_login_method, "password_hash")

        assert result == mock_saved

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_with_none_password(self, mock_factory_class, mock_config):
        """Test updating password to None (for OAuth users)."""
        from common.services.login_method import LoginMethodService

        mock_login_method = MagicMock()
        mock_login_method.password = "old_password"

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)
        service.update_password(mock_login_method, None)

        assert mock_login_method.password is None
        mock_repo.save.assert_called_once()
