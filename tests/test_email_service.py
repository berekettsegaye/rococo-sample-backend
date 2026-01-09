"""
Unit tests for common/services/email.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestEmailService:
    """Tests for EmailService."""

    @patch('common.services.email.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.email import EmailService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.email.RepositoryFactory')
    def test_save_email(self, mock_factory_class, mock_config):
        """Test saving an email."""
        from common.services.email import EmailService
        from common.models import Email

        mock_repo = MagicMock()
        mock_saved_email = MagicMock(
            entity_id="email-123",
            email="test@example.com",
            person_id="person-456"
        )
        mock_repo.save.return_value = mock_saved_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        email = Email(person_id="person-456", email="test@example.com")
        result = service.save_email(email)

        assert result == mock_saved_email
        mock_repo.save.assert_called_once_with(email)

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_success(self, mock_factory_class, mock_config):
        """Test getting an email by email address successfully."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_email = MagicMock(
            entity_id="email-789",
            email="user@example.com",
            person_id="person-012"
        )
        mock_repo.get_one.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.get_email_by_email_address("user@example.com")

        assert result == mock_email
        mock_repo.get_one.assert_called_once_with({'email': 'user@example.com'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_not_found(self, mock_factory_class, mock_config):
        """Test getting an email by email address when it doesn't exist."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.get_email_by_email_address("nonexistent@example.com")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'email': 'nonexistent@example.com'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_success(self, mock_factory_class, mock_config):
        """Test getting an email by ID successfully."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_email = MagicMock(
            entity_id="email-345",
            email="another@example.com",
            person_id="person-678"
        )
        mock_repo.get_one.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.get_email_by_id("email-345")

        assert result == mock_email
        mock_repo.get_one.assert_called_once_with({'entity_id': 'email-345'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting an email by ID when it doesn't exist."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.get_email_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'entity_id': 'nonexistent-id'})

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email(self, mock_factory_class, mock_config):
        """Test verifying an email."""
        from common.services.email import EmailService
        from common.models import Email

        mock_repo = MagicMock()

        # Create email object
        email = Email(person_id="person-123", email="verify@example.com")
        email.is_verified = False

        # Mock the save to return the verified email
        verified_email = Email(person_id="person-123", email="verify@example.com")
        verified_email.is_verified = True
        mock_repo.save.return_value = verified_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.verify_email(email)

        assert result.is_verified is True
        mock_repo.save.assert_called_once()
        # Verify that the email's is_verified was set to True before saving
        assert email.is_verified is True

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email_already_verified(self, mock_factory_class, mock_config):
        """Test verifying an already verified email."""
        from common.services.email import EmailService
        from common.models import Email

        mock_repo = MagicMock()

        # Create already verified email
        email = Email(person_id="person-123", email="already@example.com")
        email.is_verified = True

        mock_repo.save.return_value = email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        result = service.verify_email(email)

        assert result.is_verified is True
        mock_repo.save.assert_called_once()
