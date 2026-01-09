"""
Unit tests for the EmailService.
"""
from unittest.mock import MagicMock, patch
from common.services.email import EmailService
from common.models.email import Email


class TestEmailService:
    """Test EmailService methods."""

    @patch('common.services.email.RepositoryFactory')
    def test_email_service_init(self, mock_factory_class):
        """Test EmailService initialization."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = EmailService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_factory.get_repository.assert_called_once()

    @patch('common.services.email.RepositoryFactory')
    def test_save_email(self, mock_factory_class):
        """Test save_email method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        saved_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        mock_repo.save.return_value = saved_email

        service = EmailService(mock_config)
        email = Email(email="test@example.com", person_id="person-123")
        result = service.save_email(email)

        assert result.entity_id == "email-123"
        mock_repo.save.assert_called_once_with(email)

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_existing(self, mock_factory_class):
        """Test get_email_by_email_address with existing email."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        mock_repo.get_one.return_value = found_email

        service = EmailService(mock_config)
        result = service.get_email_by_email_address("test@example.com")

        assert result.entity_id == "email-123"
        mock_repo.get_one.assert_called_once_with({'email': "test@example.com"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_not_found(self, mock_factory_class):
        """Test get_email_by_email_address with non-existing email."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = EmailService(mock_config)
        result = service.get_email_by_email_address("nonexistent@example.com")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'email': "nonexistent@example.com"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_existing(self, mock_factory_class):
        """Test get_email_by_id with existing email."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        mock_repo.get_one.return_value = found_email

        service = EmailService(mock_config)
        result = service.get_email_by_id("email-123")

        assert result.entity_id == "email-123"
        mock_repo.get_one.assert_called_once_with({'entity_id': "email-123"})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_not_found(self, mock_factory_class):
        """Test get_email_by_id with non-existing id."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = EmailService(mock_config)
        result = service.get_email_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({'entity_id': "nonexistent-id"})

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email(self, mock_factory_class):
        """Test verify_email method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=False)
        verified_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=True)
        mock_repo.save.return_value = verified_email

        service = EmailService(mock_config)
        result = service.verify_email(email)

        assert result.is_verified is True
        assert email.is_verified is True
        mock_repo.save.assert_called_once_with(email)
