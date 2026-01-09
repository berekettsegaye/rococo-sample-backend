"""
Unit tests for the PersonService.
"""
from unittest.mock import MagicMock, patch
from common.services.person import PersonService
from common.models.person import Person
from common.models.email import Email


class TestPersonService:
    """Test PersonService methods."""

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_person_service_init(self, mock_factory_class, mock_email_service_class):
        """Test PersonService initialization."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_email_service_class.assert_called_once_with(mock_config)
        mock_factory.get_repository.assert_called_once()

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_save_person(self, mock_factory_class, mock_email_service_class):
        """Test save_person method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        saved_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        mock_repo.save.return_value = saved_person

        service = PersonService(mock_config)
        person = Person(first_name="John", last_name="Doe")
        result = service.save_person(person)

        assert result.entity_id == "person-123"
        mock_repo.save.assert_called_once_with(person)

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_email_address_existing(self, mock_factory_class, mock_email_service_class):
        """Test get_person_by_email_address with existing person."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_email_service = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo
        mock_email_service_class.return_value = mock_email_service

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        person_obj = Person(entity_id="person-123", first_name="John", last_name="Doe")

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        mock_repo.get_one.return_value = person_obj

        result = service.get_person_by_email_address("test@example.com")

        assert result.entity_id == "person-123"
        service.email_service.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_email_address_email_not_found(self, mock_factory_class, mock_email_service_class):
        """Test get_person_by_email_address when email doesn't exist."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_email_service = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo
        mock_email_service_class.return_value = mock_email_service

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)

        result = service.get_person_by_email_address("nonexistent@example.com")

        assert result is None
        service.email_service.get_email_by_email_address.assert_called_once_with("nonexistent@example.com")
        mock_repo.get_one.assert_not_called()

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_email_address_person_not_found(self, mock_factory_class, mock_email_service_class):
        """Test get_person_by_email_address when email exists but person doesn't."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_email_service = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo
        mock_email_service_class.return_value = mock_email_service

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")

        service = PersonService(mock_config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        mock_repo.get_one.return_value = None

        result = service.get_person_by_email_address("test@example.com")

        assert result is None
        service.email_service.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_id_existing(self, mock_factory_class, mock_email_service_class):
        """Test get_person_by_id with existing person."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        mock_repo.get_one.return_value = found_person

        service = PersonService(mock_config)
        result = service.get_person_by_id("person-123")

        assert result.entity_id == "person-123"
        mock_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_get_person_by_id_not_found(self, mock_factory_class, mock_email_service_class):
        """Test get_person_by_id with non-existing id."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = PersonService(mock_config)
        result = service.get_person_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})
