"""
Unit tests for common/services/person.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestPersonServiceInit:
    """Tests for PersonService initialization."""

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_init(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.person import PersonService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_email_service = MagicMock()
        mock_email_service_class.return_value = mock_email_service

        service = PersonService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_email_service_class.assert_called_once_with(mock_config)


class TestPersonServiceSavePerson:
    """Tests for save_person functionality."""

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_save_person_success(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test saving a person successfully."""
        from common.services.person import PersonService

        mock_repo = MagicMock()
        mock_saved_person = MagicMock()
        mock_saved_person.entity_id = "person-123"
        mock_saved_person.first_name = "John"
        mock_saved_person.last_name = "Doe"
        mock_repo.save.return_value = mock_saved_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        mock_email_service_class.return_value = MagicMock()

        service = PersonService(mock_config)

        input_person = MagicMock()
        input_person.first_name = "John"
        input_person.last_name = "Doe"

        result = service.save_person(input_person)

        assert result == mock_saved_person
        mock_repo.save.assert_called_once_with(input_person)

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_save_person_with_all_fields(self, mock_email_service_class, mock_factory_class, mock_config):
        """Test saving a person with all fields populated."""
        from common.services.person import PersonService

        mock_repo = MagicMock()
        mock_saved_person = MagicMock()
        mock_repo.save.return_value = mock_saved_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        mock_email_service_class.return_value = MagicMock()

        service = PersonService(mock_config)

        input_person = MagicMock()
        result = service.save_person(input_person)

        assert result == mock_saved_person
        mock_repo.save.assert_called_once()


class TestPersonServiceGetPersonByEmailAddress:
    """Tests for get_person_by_email_address functionality."""

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_email_address_success(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting person by email address successfully."""
        from common.services.person import PersonService

        mock_email = MagicMock()
        mock_email.person_id = "person-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email
        mock_email_service_class.return_value = mock_email_service

        mock_person = MagicMock()
        mock_person.entity_id = "person-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)
        result = service.get_person_by_email_address("test@example.com")

        assert result == mock_person
        mock_email_service.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_email_address_email_not_found(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting person when email doesn't exist."""
        from common.services.person import PersonService

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = None
        mock_email_service_class.return_value = mock_email_service

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)
        result = service.get_person_by_email_address("nonexistent@example.com")

        assert result is None
        mock_email_service.get_email_by_email_address.assert_called_once_with("nonexistent@example.com")

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_email_address_person_not_found(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting person when email exists but person doesn't."""
        from common.services.person import PersonService

        mock_email = MagicMock()
        mock_email.person_id = "person-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email
        mock_email_service_class.return_value = mock_email_service

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)
        result = service.get_person_by_email_address("test@example.com")

        assert result is None


class TestPersonServiceGetPersonById:
    """Tests for get_person_by_id functionality."""

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_id_success(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting person by ID successfully."""
        from common.services.person import PersonService

        mock_person = MagicMock()
        mock_person.entity_id = "person-123"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_person

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        mock_email_service_class.return_value = MagicMock()

        service = PersonService(mock_config)
        result = service.get_person_by_id("person-123")

        assert result == mock_person
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_id_not_found(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting person by ID when not found."""
        from common.services.person import PersonService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        mock_email_service_class.return_value = MagicMock()

        service = PersonService(mock_config)
        result = service.get_person_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    @patch('common.services.person.RepositoryFactory')
    @patch('common.services.person.EmailService')
    def test_get_person_by_id_with_different_ids(
        self, mock_email_service_class, mock_factory_class, mock_config
    ):
        """Test getting persons with different IDs."""
        from common.services.person import PersonService

        mock_person1 = MagicMock()
        mock_person1.entity_id = "person-123"

        mock_person2 = MagicMock()
        mock_person2.entity_id = "person-456"

        mock_repo = MagicMock()
        mock_repo.get_one.side_effect = [mock_person1, mock_person2]

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        mock_email_service_class.return_value = MagicMock()

        service = PersonService(mock_config)

        result1 = service.get_person_by_id("person-123")
        result2 = service.get_person_by_id("person-456")

        assert result1 == mock_person1
        assert result2 == mock_person2
        assert mock_repo.get_one.call_count == 2
