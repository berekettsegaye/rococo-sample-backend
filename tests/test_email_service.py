"""
Unit tests for common/services/email.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.email import EmailService
from common.models.email import Email


class TestEmailService:
    """Tests for EmailService."""

    @patch('common.services.email.RepositoryFactory')
    def test_email_service_initialization(self, mock_factory):
        """Test EmailService initializes correctly."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(config)

        assert service.config == config
        assert service.email_repo == mock_repo

    @patch('common.services.email.RepositoryFactory')
    def test_save_email(self, mock_factory):
        """Test save_email calls repository save."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        email = Email(person_id='person-123', email='test@example.com')
        mock_repo.save.return_value = email

        service = EmailService(config)
        result = service.save_email(email)

        mock_repo.save.assert_called_once_with(email)
        assert result == email

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address(self, mock_factory):
        """Test get_email_by_email_address queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        email = Email(person_id='person-123', email='test@example.com')
        mock_repo.get_one.return_value = email

        service = EmailService(config)
        result = service.get_email_by_email_address('test@example.com')

        mock_repo.get_one.assert_called_once_with({'email': 'test@example.com'})
        assert result == email

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id(self, mock_factory):
        """Test get_email_by_id queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        email = Email(entity_id='email-123', person_id='person-123', email='test@example.com')
        mock_repo.get_one.return_value = email

        service = EmailService(config)
        result = service.get_email_by_id('email-123')

        mock_repo.get_one.assert_called_once_with({'entity_id': 'email-123'})
        assert result == email

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email(self, mock_factory):
        """Test verify_email sets is_verified to True and saves."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        email = Email(person_id='person-123', email='test@example.com', is_verified=False)
        verified_email = Email(person_id='person-123', email='test@example.com', is_verified=True)
        mock_repo.save.return_value = verified_email

        service = EmailService(config)
        result = service.verify_email(email)

        assert email.is_verified is True
        mock_repo.save.assert_called_once()
        assert result.is_verified is True
