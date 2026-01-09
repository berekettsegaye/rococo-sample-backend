"""
Unit tests for common/services/email.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.email import EmailService
from common.models.email import Email


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    return config


@pytest.fixture
def email_service(mock_config):
    """Create an EmailService instance with mocked dependencies."""
    with patch('common.services.email.RepositoryFactory'):
        service = EmailService(mock_config)
        service.email_repo = MagicMock()
        return service


class TestEmailServiceSaveEmail:
    """Tests for EmailService.save_email method."""

    def test_save_email_success(self, email_service):
        """Test saving an email successfully."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.email = "test@example.com"

        email_service.email_repo.save.return_value = mock_email

        result = email_service.save_email(mock_email)

        assert result == mock_email
        email_service.email_repo.save.assert_called_once_with(mock_email)

    def test_save_email_with_person_id(self, email_service):
        """Test saving email with person_id."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.email = "test@example.com"
        mock_email.person_id = "person-123"

        email_service.email_repo.save.return_value = mock_email

        result = email_service.save_email(mock_email)

        assert result == mock_email
        email_service.email_repo.save.assert_called_once()

    def test_save_email_verified(self, email_service):
        """Test saving a verified email."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.email = "test@example.com"
        mock_email.is_verified = True

        email_service.email_repo.save.return_value = mock_email

        result = email_service.save_email(mock_email)

        assert result == mock_email


class TestEmailServiceGetEmailByEmailAddress:
    """Tests for EmailService.get_email_by_email_address method."""

    def test_get_email_by_email_address_success(self, email_service):
        """Test getting email by email address successfully."""
        mock_email = MagicMock(spec=Email)
        mock_email.email = "test@example.com"
        mock_email.entity_id = "email-123"

        email_service.email_repo.get_one.return_value = mock_email

        result = email_service.get_email_by_email_address("test@example.com")

        assert result == mock_email
        email_service.email_repo.get_one.assert_called_once_with({'email': 'test@example.com'})

    def test_get_email_by_email_address_not_found(self, email_service):
        """Test getting email when not found."""
        email_service.email_repo.get_one.return_value = None

        result = email_service.get_email_by_email_address("nonexistent@example.com")

        assert result is None
        email_service.email_repo.get_one.assert_called_once_with({'email': 'nonexistent@example.com'})

    def test_get_email_by_email_address_case_sensitive(self, email_service):
        """Test getting email is case-sensitive."""
        mock_email = MagicMock(spec=Email)
        mock_email.email = "Test@Example.com"

        email_service.email_repo.get_one.return_value = mock_email

        result = email_service.get_email_by_email_address("Test@Example.com")

        assert result == mock_email
        email_service.email_repo.get_one.assert_called_once_with({'email': 'Test@Example.com'})

    def test_get_email_by_email_address_with_special_chars(self, email_service):
        """Test getting email with special characters."""
        mock_email = MagicMock(spec=Email)
        mock_email.email = "user+tag@example.com"

        email_service.email_repo.get_one.return_value = mock_email

        result = email_service.get_email_by_email_address("user+tag@example.com")

        assert result == mock_email


class TestEmailServiceGetEmailById:
    """Tests for EmailService.get_email_by_id method."""

    def test_get_email_by_id_success(self, email_service):
        """Test getting email by ID successfully."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.email = "test@example.com"

        email_service.email_repo.get_one.return_value = mock_email

        result = email_service.get_email_by_id("email-123")

        assert result == mock_email
        email_service.email_repo.get_one.assert_called_once_with({'entity_id': 'email-123'})

    def test_get_email_by_id_not_found(self, email_service):
        """Test getting email by ID when not found."""
        email_service.email_repo.get_one.return_value = None

        result = email_service.get_email_by_id("nonexistent-id")

        assert result is None
        email_service.email_repo.get_one.assert_called_once_with({'entity_id': 'nonexistent-id'})

    def test_get_email_by_id_with_different_ids(self, email_service):
        """Test getting different emails by their IDs."""
        mock_email_1 = MagicMock(spec=Email)
        mock_email_1.entity_id = "email-1"

        mock_email_2 = MagicMock(spec=Email)
        mock_email_2.entity_id = "email-2"

        def get_one_side_effect(query):
            if query['entity_id'] == "email-1":
                return mock_email_1
            elif query['entity_id'] == "email-2":
                return mock_email_2
            return None

        email_service.email_repo.get_one.side_effect = get_one_side_effect

        result_1 = email_service.get_email_by_id("email-1")
        result_2 = email_service.get_email_by_id("email-2")

        assert result_1 == mock_email_1
        assert result_2 == mock_email_2


class TestEmailServiceVerifyEmail:
    """Tests for EmailService.verify_email method."""

    def test_verify_email_success(self, email_service):
        """Test verifying an email successfully."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.is_verified = False

        verified_email = MagicMock(spec=Email)
        verified_email.entity_id = "email-123"
        verified_email.is_verified = True

        email_service.email_repo.save.return_value = verified_email

        result = email_service.verify_email(mock_email)

        assert result == verified_email
        assert mock_email.is_verified is True
        email_service.email_repo.save.assert_called_once_with(mock_email)

    def test_verify_email_already_verified(self, email_service):
        """Test verifying an already verified email."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.is_verified = True

        email_service.email_repo.save.return_value = mock_email

        result = email_service.verify_email(mock_email)

        assert result == mock_email
        assert mock_email.is_verified is True
        email_service.email_repo.save.assert_called_once()

    def test_verify_email_sets_verified_flag(self, email_service):
        """Test that verify_email sets is_verified to True."""
        mock_email = MagicMock(spec=Email)
        mock_email.is_verified = False

        email_service.email_repo.save.return_value = mock_email

        email_service.verify_email(mock_email)

        assert mock_email.is_verified is True

    def test_verify_email_returns_saved_email(self, email_service):
        """Test that verify_email returns the saved email."""
        mock_email = MagicMock(spec=Email)
        saved_email = MagicMock(spec=Email)
        saved_email.entity_id = "saved-123"

        email_service.email_repo.save.return_value = saved_email

        result = email_service.verify_email(mock_email)

        assert result == saved_email
        assert result.entity_id == "saved-123"


class TestEmailServiceInitialization:
    """Tests for EmailService initialization."""

    @patch('common.services.email.RepositoryFactory')
    def test_initialization_creates_dependencies(self, mock_factory_class, mock_config):
        """Test that EmailService initializes its dependencies."""
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_repo = MagicMock()
        mock_factory.get_repository.return_value = mock_repo

        service = EmailService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.email.RepositoryFactory')
    def test_initialization_gets_email_repository(self, mock_factory_class, mock_config):
        """Test that EmailService gets the email repository."""
        from common.repositories.factory import RepoType

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        mock_factory.get_repository.assert_called_once_with(RepoType.EMAIL)
