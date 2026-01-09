"""
Unit tests for common/services/person.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.person import PersonService
from common.models.person import Person


class TestPersonService:
    """Tests for PersonService."""

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_save_person(self, mock_repo_factory, mock_config):
        """Test saving a person."""
        person = Person(first_name='John', last_name='Doe')
        mock_repo = MagicMock()
        mock_repo.save.return_value = person
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        result = service.save_person(person)

        assert result == person
        mock_repo.save.assert_called_once_with(person)

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_get_person_by_id_success(self, mock_repo_factory, mock_config):
        """Test getting person by ID successfully."""
        person = Person(entity_id='person-id', first_name='John', last_name='Doe')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = person
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        result = service.get_person_by_id('person-id')

        assert result == person
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-id"})

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_get_person_by_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting person by ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        result = service.get_person_by_id('nonexistent-id')

        assert result is None

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_get_person_by_email_address_success(self, mock_repo_factory, mock_config):
        """Test getting person by email address successfully."""
        email_obj = MagicMock(person_id='person-id')
        person = Person(entity_id='person-id', first_name='John', last_name='Doe')

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = person
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)

        result = service.get_person_by_email_address('test@example.com')

        assert result == person
        service.email_service.get_email_by_email_address.assert_called_once_with('test@example.com')
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-id"})

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_get_person_by_email_address_email_not_found(self, mock_repo_factory, mock_config):
        """Test getting person by email address when email doesn't exist."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)

        result = service.get_person_by_email_address('nonexistent@example.com')

        assert result is None
        service.email_service.get_email_by_email_address.assert_called_once_with('nonexistent@example.com')

    @patch('common.services.person.RepositoryFactory')
    # EmailService is imported inside __init__, no need to patch at module level
    def test_get_person_by_email_address_person_not_found(self, mock_repo_factory, mock_config):
        """Test getting person by email address when person doesn't exist."""
        email_obj = MagicMock(person_id='person-id')

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)

        result = service.get_person_by_email_address('test@example.com')

        assert result is None
