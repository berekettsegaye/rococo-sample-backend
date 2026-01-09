"""
Unit tests for common/services/email.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestEmailServiceInit:
    """Tests for EmailService initialization."""

    @patch('common.services.email.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.email import EmailService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)


class TestEmailServiceSaveEmail:
    """Tests for save_email functionality."""

    @patch('common.services.email.RepositoryFactory')
    def test_save_email_success(self, mock_factory_class, mock_config):
        """Test saving an email successfully."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_saved_email = MagicMock()
        mock_saved_email.entity_id = "email-123"
        mock_saved_email.email = "test@example.com"
        mock_repo.save.return_value = mock_saved_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        input_email = MagicMock()
        input_email.email = "test@example.com"

        result = service.save_email(input_email)

        assert result == mock_saved_email
        mock_repo.save.assert_called_once_with(input_email)

    @patch('common.services.email.RepositoryFactory')
    def test_save_email_returns_saved_object(self, mock_factory_class, mock_config):
        """Test that save_email returns the saved email object."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_saved_email = MagicMock()
        mock_repo.save.return_value = mock_saved_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        input_email = MagicMock()
        result = service.save_email(input_email)

        assert result == mock_saved_email


class TestEmailServiceGetEmailByEmailAddress:
    """Tests for get_email_by_email_address functionality."""

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_success(self, mock_factory_class, mock_config):
        """Test getting email by address successfully."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_email.email = "test@example.com"
        mock_email.entity_id = "email-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.get_email_by_email_address("test@example.com")

        assert result == mock_email
        mock_repo.get_one.assert_called_once_with({'email': "test@example.com"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_not_found(self, mock_factory_class, mock_config):
        """Test getting email by address when not found."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.get_email_by_email_address("nonexistent@example.com")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'email': "nonexistent@example.com"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_case_sensitive(self, mock_factory_class, mock_config):
        """Test getting email by address is case-sensitive."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        service.get_email_by_email_address("Test@Example.com")

        mock_repo.get_one.assert_called_once_with({'email': "Test@Example.com"})


class TestEmailServiceGetEmailById:
    """Tests for get_email_by_id functionality."""

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_success(self, mock_factory_class, mock_config):
        """Test getting email by ID successfully."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_email.entity_id = "email-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.get_email_by_id("email-123")

        assert result == mock_email
        mock_repo.get_one.assert_called_once_with({'entity_id': "email-123"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting email by ID when not found."""
        from common.services.email import EmailService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.get_email_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'entity_id': "nonexistent-id"})


class TestEmailServiceVerifyEmail:
    """Tests for verify_email functionality."""

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email_success(self, mock_factory_class, mock_config):
        """Test verifying an email successfully."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_email.is_verified = False

        mock_verified_email = MagicMock()
        mock_verified_email.is_verified = True

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_verified_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.verify_email(mock_email)

        assert result == mock_verified_email
        assert mock_email.is_verified is True
        mock_repo.save.assert_called_once_with(mock_email)

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email_already_verified(self, mock_factory_class, mock_config):
        """Test verifying an already verified email."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_email.is_verified = False

        mock_saved_email = MagicMock()
        mock_saved_email.is_verified = True

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_saved_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        result = service.verify_email(mock_email)

        assert result.is_verified is True
        mock_repo.save.assert_called_once()

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email_sets_flag(self, mock_factory_class, mock_config):
        """Test that verify_email sets is_verified to True."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_email.is_verified = False

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)
        service.verify_email(mock_email)

        assert mock_email.is_verified is True

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email_calls_save(self, mock_factory_class, mock_config):
        """Test that verify_email calls save_email."""
        from common.services.email import EmailService

        mock_email = MagicMock()
        mock_saved_email = MagicMock()

        mock_repo = MagicMock()
        mock_repo.save.return_value = mock_saved_email

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        with patch.object(service, 'save_email', wraps=service.save_email) as mock_save:
            result = service.verify_email(mock_email)

            mock_save.assert_called_once_with(mock_email)
            assert result == mock_saved_email
