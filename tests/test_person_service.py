"""
Unit tests for common/services/person.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestPersonService:
    """Tests for PersonService."""

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_init(self, mock_email_service, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.person import PersonService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_email_service.assert_called_once_with(mock_config)

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_save_person(self, mock_email_service, mock_factory_class, mock_config):
        """Test saving a person."""
        from common.services.person import PersonService
        from common.models.person import Person

        mock_repo = MagicMock()
        mock_saved_person = MagicMock(entity_id="person-123", first_name="John", last_name="Doe")
        mock_repo.save.return_value = mock_saved_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        person = Person(first_name="John", last_name="Doe")
        result = service.save_person(person)

        assert result == mock_saved_person
        mock_repo.save.assert_called_once_with(person)

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_get_person_by_email_address_success(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test getting a person by email address successfully."""
        from common.services.person import PersonService

        # Mock email service
        mock_email_service_instance = MagicMock()
        mock_email = MagicMock(entity_id="email-123", person_id="person-456")
        mock_email_service_instance.get_email_by_email_address.return_value = mock_email
        mock_email_service_class.return_value = mock_email_service_instance

        # Mock person repository
        mock_repo = MagicMock()
        mock_person = MagicMock(entity_id="person-456", first_name="Jane", last_name="Smith")
        mock_repo.get_one.return_value = mock_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        result = service.get_person_by_email_address("jane@example.com")

        assert result == mock_person
        mock_email_service_instance.get_email_by_email_address.assert_called_once_with("jane@example.com")
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-456"})

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_get_person_by_email_address_no_email(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test getting a person by email address when email doesn't exist."""
        from common.services.person import PersonService

        # Mock email service to return None
        mock_email_service_instance = MagicMock()
        mock_email_service_instance.get_email_by_email_address.return_value = None
        mock_email_service_class.return_value = mock_email_service_instance

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        result = service.get_person_by_email_address("nonexistent@example.com")

        assert result is None
        mock_email_service_instance.get_email_by_email_address.assert_called_once_with("nonexistent@example.com")

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_get_person_by_email_address_no_person(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test getting a person by email address when person doesn't exist."""
        from common.services.person import PersonService

        # Mock email service
        mock_email_service_instance = MagicMock()
        mock_email = MagicMock(entity_id="email-123", person_id="person-456")
        mock_email_service_instance.get_email_by_email_address.return_value = mock_email
        mock_email_service_class.return_value = mock_email_service_instance

        # Mock person repository to return None
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        result = service.get_person_by_email_address("orphan@example.com")

        assert result is None

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_get_person_by_id_success(self, mock_email_service, mock_factory_class, mock_config):
        """Test getting a person by ID successfully."""
        from common.services.person import PersonService

        mock_repo = MagicMock()
        mock_person = MagicMock(entity_id="person-789", first_name="Bob", last_name="Johnson")
        mock_repo.get_one.return_value = mock_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        result = service.get_person_by_id("person-789")

        assert result == mock_person
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-789"})

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.EmailService')
    def test_get_person_by_id_not_found(self, mock_email_service, mock_factory_class, mock_config):
        """Test getting a person by ID when person doesn't exist."""
        from common.services.person import PersonService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        result = service.get_person_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})
