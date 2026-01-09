"""
Unit tests for common/services/login_method.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.login_method import LoginMethodService
from common.models.login_method import LoginMethod


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    return config


@pytest.fixture
def login_method_service(mock_config):
    """Create a LoginMethodService instance with mocked dependencies."""
    with patch('common.services.login_method.RepositoryFactory'):
        service = LoginMethodService(mock_config)
        service.login_method_repo = MagicMock()
        return service


class TestLoginMethodServiceSaveLoginMethod:
    """Tests for LoginMethodService.save_login_method method."""

    def test_save_login_method_success(self, login_method_service):
        """Test saving a login method successfully."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"
        mock_login_method.person_id = "person-123"

        login_method_service.login_method_repo.save.return_value = mock_login_method

        result = login_method_service.save_login_method(mock_login_method)

        assert result == mock_login_method
        login_method_service.login_method_repo.save.assert_called_once_with(mock_login_method)

    def test_save_login_method_with_email_password(self, login_method_service):
        """Test saving email/password login method."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"
        mock_login_method.method_type = "email-password"
        mock_login_method.password = "hashed_password"

        login_method_service.login_method_repo.save.return_value = mock_login_method

        result = login_method_service.save_login_method(mock_login_method)

        assert result == mock_login_method

    def test_save_login_method_with_oauth(self, login_method_service):
        """Test saving OAuth login method."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"
        mock_login_method.method_type = "oauth-google"

        login_method_service.login_method_repo.save.return_value = mock_login_method

        result = login_method_service.save_login_method(mock_login_method)

        assert result == mock_login_method


class TestLoginMethodServiceGetLoginMethodByEmailId:
    """Tests for LoginMethodService.get_login_method_by_email_id method."""

    def test_get_login_method_by_email_id_success(self, login_method_service):
        """Test getting login method by email ID successfully."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"
        mock_login_method.email_id = "email-123"

        login_method_service.login_method_repo.get_one.return_value = mock_login_method

        result = login_method_service.get_login_method_by_email_id("email-123")

        assert result == mock_login_method
        login_method_service.login_method_repo.get_one.assert_called_once_with({"email_id": "email-123"})

    def test_get_login_method_by_email_id_not_found(self, login_method_service):
        """Test getting login method when not found."""
        login_method_service.login_method_repo.get_one.return_value = None

        result = login_method_service.get_login_method_by_email_id("nonexistent-email-id")

        assert result is None
        login_method_service.login_method_repo.get_one.assert_called_once_with({"email_id": "nonexistent-email-id"})

    def test_get_login_method_by_email_id_with_different_ids(self, login_method_service):
        """Test getting different login methods by email IDs."""
        mock_login_1 = MagicMock(spec=LoginMethod)
        mock_login_1.email_id = "email-1"

        mock_login_2 = MagicMock(spec=LoginMethod)
        mock_login_2.email_id = "email-2"

        def get_one_side_effect(query):
            if query["email_id"] == "email-1":
                return mock_login_1
            elif query["email_id"] == "email-2":
                return mock_login_2
            return None

        login_method_service.login_method_repo.get_one.side_effect = get_one_side_effect

        result_1 = login_method_service.get_login_method_by_email_id("email-1")
        result_2 = login_method_service.get_login_method_by_email_id("email-2")

        assert result_1 == mock_login_1
        assert result_2 == mock_login_2


class TestLoginMethodServiceGetLoginMethodById:
    """Tests for LoginMethodService.get_login_method_by_id method."""

    def test_get_login_method_by_id_success(self, login_method_service):
        """Test getting login method by ID successfully."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"

        login_method_service.login_method_repo.get_one.return_value = mock_login_method

        result = login_method_service.get_login_method_by_id("login-123")

        assert result == mock_login_method
        login_method_service.login_method_repo.get_one.assert_called_once_with({"entity_id": "login-123"})

    def test_get_login_method_by_id_not_found(self, login_method_service):
        """Test getting login method by ID when not found."""
        login_method_service.login_method_repo.get_one.return_value = None

        result = login_method_service.get_login_method_by_id("nonexistent-id")

        assert result is None
        login_method_service.login_method_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    def test_get_login_method_by_id_with_different_ids(self, login_method_service):
        """Test getting different login methods by their entity IDs."""
        mock_login_1 = MagicMock(spec=LoginMethod)
        mock_login_1.entity_id = "login-1"

        mock_login_2 = MagicMock(spec=LoginMethod)
        mock_login_2.entity_id = "login-2"

        def get_one_side_effect(query):
            if query["entity_id"] == "login-1":
                return mock_login_1
            elif query["entity_id"] == "login-2":
                return mock_login_2
            return None

        login_method_service.login_method_repo.get_one.side_effect = get_one_side_effect

        result_1 = login_method_service.get_login_method_by_id("login-1")
        result_2 = login_method_service.get_login_method_by_id("login-2")

        assert result_1 == mock_login_1
        assert result_2 == mock_login_2


class TestLoginMethodServiceUpdatePassword:
    """Tests for LoginMethodService.update_password method."""

    def test_update_password_success(self, login_method_service):
        """Test updating password successfully."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.entity_id = "login-123"
        mock_login_method.password = "old_hashed_password"

        updated_login_method = MagicMock(spec=LoginMethod)
        updated_login_method.entity_id = "login-123"
        updated_login_method.password = "new_hashed_password"

        login_method_service.login_method_repo.save.return_value = updated_login_method

        result = login_method_service.update_password(mock_login_method, "new_hashed_password")

        assert result == updated_login_method
        assert mock_login_method.password == "new_hashed_password"
        login_method_service.login_method_repo.save.assert_called_once_with(mock_login_method)

    def test_update_password_sets_new_password(self, login_method_service):
        """Test that update_password sets the new password on the login method."""
        mock_login_method = MagicMock(spec=LoginMethod)
        mock_login_method.password = "old_password"

        login_method_service.login_method_repo.save.return_value = mock_login_method

        login_method_service.update_password(mock_login_method, "new_password")

        assert mock_login_method.password == "new_password"

    def test_update_password_calls_save(self, login_method_service):
        """Test that update_password calls repository save."""
        mock_login_method = MagicMock(spec=LoginMethod)

        login_method_service.login_method_repo.save.return_value = mock_login_method

        login_method_service.update_password(mock_login_method, "new_password")

        login_method_service.login_method_repo.save.assert_called_once_with(mock_login_method)

    def test_update_password_returns_saved_login_method(self, login_method_service):
        """Test that update_password returns the saved login method."""
        mock_login_method = MagicMock(spec=LoginMethod)
        saved_login_method = MagicMock(spec=LoginMethod)
        saved_login_method.entity_id = "saved-123"

        login_method_service.login_method_repo.save.return_value = saved_login_method

        result = login_method_service.update_password(mock_login_method, "new_password")

        assert result == saved_login_method
        assert result.entity_id == "saved-123"

    def test_update_password_with_empty_password(self, login_method_service):
        """Test updating password with empty string."""
        mock_login_method = MagicMock(spec=LoginMethod)

        login_method_service.login_method_repo.save.return_value = mock_login_method

        result = login_method_service.update_password(mock_login_method, "")

        assert mock_login_method.password == ""
        assert result == mock_login_method


class TestLoginMethodServiceInitialization:
    """Tests for LoginMethodService initialization."""

    @patch('common.services.login_method.RepositoryFactory')
    def test_initialization_creates_dependencies(self, mock_factory_class, mock_config):
        """Test that LoginMethodService initializes its dependencies."""
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_repo = MagicMock()
        mock_factory.get_repository.return_value = mock_repo

        service = LoginMethodService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.login_method.RepositoryFactory')
    def test_initialization_gets_login_method_repository(self, mock_factory_class, mock_config):
        """Test that LoginMethodService gets the login method repository."""
        from common.repositories.factory import RepoType

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = LoginMethodService(mock_config)

        mock_factory.get_repository.assert_called_once_with(RepoType.LOGIN_METHOD)
