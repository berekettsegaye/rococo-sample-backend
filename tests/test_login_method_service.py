"""
Unit tests for the LoginMethodService.
"""
from unittest.mock import MagicMock, patch
from common.services.login_method import LoginMethodService
from common.models.login_method import LoginMethod


class TestLoginMethodService:
    """Test LoginMethodService methods."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_login_method_service_init(self, mock_factory_class):
        """Test LoginMethodService initialization."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_factory.get_repository.assert_called_once()

    @patch('common.services.login_method.RepositoryFactory')
    def test_save_login_method(self, mock_factory_class):
        """Test save_login_method method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        saved_login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            method_type="local"
        )
        mock_repo.save.return_value = saved_login_method

        service = LoginMethodService(mock_config)
        login_method = LoginMethod(email_id="email-123", person_id="person-123", method_type="local")
        result = service.save_login_method(login_method)

        assert result.entity_id == "login-123"
        mock_repo.save.assert_called_once_with(login_method)

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_existing(self, mock_factory_class):
        """Test get_login_method_by_email_id with existing login method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            method_type="local"
        )
        mock_repo.get_one.return_value = found_login_method

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id("email-123")

        assert result.entity_id == "login-123"
        mock_repo.get_one.assert_called_once_with({"email_id": "email-123"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_email_id_not_found(self, mock_factory_class):
        """Test get_login_method_by_email_id with non-existing email_id."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_email_id("nonexistent-email-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"email_id": "nonexistent-email-id"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_existing(self, mock_factory_class):
        """Test get_login_method_by_id with existing login method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            method_type="local"
        )
        mock_repo.get_one.return_value = found_login_method

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id("login-123")

        assert result.entity_id == "login-123"
        mock_repo.get_one.assert_called_once_with({"entity_id": "login-123"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_get_login_method_by_id_not_found(self, mock_factory_class):
        """Test get_login_method_by_id with non-existing id."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = LoginMethodService(mock_config)
        result = service.get_login_method_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    @patch('common.services.login_method.RepositoryFactory')
    def test_update_password(self, mock_factory_class):
        """Test update_password method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            method_type="local",
            password="old_password"  # NOSONAR
        )
        updated_login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            method_type="local",
            password="new_password"  # NOSONAR
        )
        mock_repo.save.return_value = updated_login_method

        service = LoginMethodService(mock_config)
        result = service.update_password(login_method, "new_password")  # NOSONAR

        assert login_method.password == "new_password"  # NOSONAR
        mock_repo.save.assert_called_once_with(login_method)
