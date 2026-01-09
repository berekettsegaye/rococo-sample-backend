"""
Unit tests for common/services/login_method.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestLoginMethodService:
    """Tests for LoginMethodService."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.login_method import LoginMethodService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method(self, mock_factory_class, mock_config):
        """Test saving a login method."""
        from common.services.login_method import LoginMethodService
        from common.models import LoginMethod

        mock_repo = MagicMock()
        mock_saved_method = MagicMock(
            entity_id="login-123",
            email_id="email-456",
            person_id="person-789"
        )
        mock_repo.save.return_value = mock_saved_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        login_method = LoginMethod(
            method_type="email-password",
            raw_password="TestPassword123!"
        )
        result = service.save_login_method(login_method)

        assert result == mock_saved_method
        mock_repo.save.assert_called_once_with(login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_success(self, mock_factory_class, mock_config):
        """Test getting a login method by email ID successfully."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_login_method = MagicMock(
            entity_id="login-345",
            email_id="email-678",
            person_id="person-901"
        )
        mock_repo.get_one.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        result = service.get_login_method_by_email_id("email-678")

        assert result == mock_login_method
        mock_repo.get_one.assert_called_once_with({"email_id": "email-678"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_not_found(self, mock_factory_class, mock_config):
        """Test getting a login method by email ID when it doesn't exist."""
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

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_success(self, mock_factory_class, mock_config):
        """Test getting a login method by ID successfully."""
        from common.services.login_method import LoginMethodService

        mock_repo = MagicMock()
        mock_login_method = MagicMock(
            entity_id="login-234",
            email_id="email-567",
            person_id="person-890"
        )
        mock_repo.get_one.return_value = mock_login_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        result = service.get_login_method_by_id("login-234")

        assert result == mock_login_method
        mock_repo.get_one.assert_called_once_with({"entity_id": "login-234"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting a login method by ID when it doesn't exist."""
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

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password(self, mock_factory_class, mock_config):
        """Test updating a login method password."""
        from common.services.login_method import LoginMethodService
        from common.models import LoginMethod

        mock_repo = MagicMock()

        # Create login method
        login_method = LoginMethod(
            method_type="email-password",
            raw_password="OldPassword123!"
        )
        login_method.entity_id = "login-999"

        # Mock the save to return the updated login method
        updated_method = MagicMock(
            entity_id="login-999",
            password="new_hashed_password"
        )
        mock_repo.save.return_value = updated_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        result = service.update_password(login_method, "new_hashed_password")

        assert result == updated_method
        assert login_method.password == "new_hashed_password"
        mock_repo.save.assert_called_once_with(login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password_with_none(self, mock_factory_class, mock_config):
        """Test updating password to None (for OAuth users)."""
        from common.services.login_method import LoginMethodService
        from common.models import LoginMethod

        mock_repo = MagicMock()

        # Create login method
        login_method = LoginMethod(
            method_type="oauth-google",
            raw_password="TempPassword123!"
        )
        login_method.entity_id = "login-oauth"

        # Mock the save
        updated_method = MagicMock(
            entity_id="login-oauth",
            password=None
        )
        mock_repo.save.return_value = updated_method

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        result = service.update_password(login_method, None)

        assert result == updated_method
        assert login_method.password is None
        mock_repo.save.assert_called_once_with(login_method)
