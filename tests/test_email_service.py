"""
Unit tests for common/services/email.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.email import EmailService
from common.models import Email


class TestEmailService:
    """Tests for EmailService."""

    @patch('common.services.email.RepositoryFactory')
    def test_save_email(self, mock_repo_factory, mock_config):
        """Test saving an email."""
        email = Email(email='test@example.com', person_id='person-id')
        mock_repo = MagicMock()
        mock_repo.save.return_value = email
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.save_email(email)

        assert result == email
        mock_repo.save.assert_called_once_with(email)

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_success(self, mock_repo_factory, mock_config):
        """Test getting email by email address successfully."""
        email = Email(entity_id='email-id', email='test@example.com')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = email
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_email_address('test@example.com')

        assert result == email
        mock_repo.get_one.assert_called_once_with({'email': 'test@example.com'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_email_address_not_found(self, mock_repo_factory, mock_config):
        """Test getting email by email address when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_email_address('nonexistent@example.com')

        assert result is None

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_success(self, mock_repo_factory, mock_config):
        """Test getting email by ID successfully."""
        email = Email(entity_id='email-id', email='test@example.com')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = email
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_id('email-id')

        assert result == email
        mock_repo.get_one.assert_called_once_with({'entity_id': 'email-id'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting email by ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_id('nonexistent-id')

        assert result is None

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_person_id_success(self, mock_repo_factory, mock_config):
        """Test getting email by person ID successfully."""
        email = Email(entity_id='email-id', email='test@example.com', person_id='person-id')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = email
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_person_id('person-id')

        assert result == email
        mock_repo.get_one.assert_called_once_with({'person_id': 'person-id'})

    @patch('common.services.email.RepositoryFactory')
    def test_get_email_by_person_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting email by person ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.get_email_by_person_id('nonexistent-person-id')

        assert result is None

    @patch('common.services.email.RepositoryFactory')
    def test_verify_email(self, mock_repo_factory, mock_config):
        """Test verifying an email."""
        email = Email(entity_id='email-id', email='test@example.com', is_verified=False)
        verified_email = Email(entity_id='email-id', email='test@example.com', is_verified=True)

        mock_repo = MagicMock()
        mock_repo.save.return_value = verified_email
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = EmailService(mock_config)
        result = service.verify_email(email)

        assert result.is_verified is True
        mock_repo.save.assert_called_once()
