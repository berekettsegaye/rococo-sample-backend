"""
Unit tests for common/services/person.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.person import PersonService
from common.models.person import Person
from common.models.email import Email


class TestPersonService:
    """Tests for PersonService."""

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_person_service_initialization(self, mock_factory, mock_email_service):
        """Test PersonService initializes correctly."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(config)

        assert service.config == config
        assert service.person_repo == mock_repo

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_save_person(self, mock_factory, mock_email_service):
        """Test save_person calls repository save."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        person = Person(first_name='John', last_name='Doe')
        mock_repo.save.return_value = person

        service = PersonService(config)
        result = service.save_person(person)

        mock_repo.save.assert_called_once_with(person)
        assert result == person

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_email_address(self, mock_factory, mock_email_service_class):
        """Test get_person_by_email_address uses email service and person repo."""
        config = MagicMock()
        mock_person_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_person_repo

        email = Email(entity_id='email-123', person_id='person-123', email='test@example.com')
        person = Person(entity_id='person-123', first_name='John', last_name='Doe')

        mock_person_repo.get_one.return_value = person

        service = PersonService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=email)

        result = service.get_person_by_email_address('test@example.com')

        service.email_service.get_email_by_email_address.assert_called_once_with('test@example.com')
        mock_person_repo.get_one.assert_called_once_with({"entity_id": 'person-123'})
        assert result == person

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_email_address_with_nonexistent_email(self, mock_factory, mock_email_service_class):
        """Test get_person_by_email_address returns None for non-existent email."""
        config = MagicMock()
        mock_person_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_person_repo

        service = PersonService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)

        result = service.get_person_by_email_address('nonexistent@example.com')

        service.email_service.get_email_by_email_address.assert_called_once_with('nonexistent@example.com')
        mock_person_repo.get_one.assert_not_called()
        assert result is None

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_id(self, mock_factory, mock_email_service):
        """Test get_person_by_id queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        person = Person(entity_id='person-123', first_name='John', last_name='Doe')
        mock_repo.get_one.return_value = person

        service = PersonService(config)
        result = service.get_person_by_id('person-123')

        mock_repo.get_one.assert_called_once_with({"entity_id": 'person-123'})
        assert result == person
