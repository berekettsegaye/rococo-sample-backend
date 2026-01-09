"""
Unit tests for common/services/person.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.person import PersonService
from common.models.person import Person
from common.models.email import Email


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    return config


@pytest.fixture
def person_service(mock_config):
    """Create a PersonService instance with mocked dependencies."""
    with patch('common.services.person.EmailService'), \
         patch('common.services.person.RepositoryFactory'):
        service = PersonService(mock_config)

        # Mock the repositories
        service.person_repo = MagicMock()
        service.email_service = MagicMock()

        return service


class TestPersonServiceSavePerson:
    """Tests for PersonService.save_person method."""

    def test_save_person_success(self, person_service):
        """Test saving a person successfully."""
        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"

        person_service.person_repo.save.return_value = mock_person

        result = person_service.save_person(mock_person)

        assert result == mock_person
        person_service.person_repo.save.assert_called_once_with(mock_person)

    def test_save_person_calls_repository(self, person_service):
        """Test that save_person delegates to repository."""
        mock_person = MagicMock(spec=Person)
        person_service.person_repo.save.return_value = mock_person

        person_service.save_person(mock_person)

        person_service.person_repo.save.assert_called_once()


class TestPersonServiceGetPersonByEmailAddress:
    """Tests for PersonService.get_person_by_email_address method."""

    def test_get_person_by_email_address_success(self, person_service):
        """Test getting person by email address successfully."""
        mock_email = MagicMock(spec=Email)
        mock_email.person_id = "person-123"
        person_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        person_service.person_repo.get_one.return_value = mock_person

        result = person_service.get_person_by_email_address("test@example.com")

        assert result == mock_person
        person_service.email_service.get_email_by_email_address.assert_called_once_with("test@example.com")
        person_service.person_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    def test_get_person_by_email_address_email_not_found(self, person_service):
        """Test getting person when email doesn't exist."""
        person_service.email_service.get_email_by_email_address.return_value = None

        result = person_service.get_person_by_email_address("nonexistent@example.com")

        assert result is None
        person_service.person_repo.get_one.assert_not_called()

    def test_get_person_by_email_address_person_not_found(self, person_service):
        """Test getting person when person doesn't exist."""
        mock_email = MagicMock(spec=Email)
        mock_email.person_id = "person-123"
        person_service.email_service.get_email_by_email_address.return_value = mock_email

        person_service.person_repo.get_one.return_value = None

        result = person_service.get_person_by_email_address("test@example.com")

        assert result is None

    def test_get_person_by_email_address_with_valid_email_format(self, person_service):
        """Test getting person with properly formatted email."""
        mock_email = MagicMock(spec=Email)
        mock_email.person_id = "person-456"
        person_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        person_service.person_repo.get_one.return_value = mock_person

        result = person_service.get_person_by_email_address("user+tag@example.com")

        assert result == mock_person
        person_service.email_service.get_email_by_email_address.assert_called_once_with("user+tag@example.com")


class TestPersonServiceGetPersonById:
    """Tests for PersonService.get_person_by_id method."""

    def test_get_person_by_id_success(self, person_service):
        """Test getting person by ID successfully."""
        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        mock_person.first_name = "Jane"
        mock_person.last_name = "Smith"

        person_service.person_repo.get_one.return_value = mock_person

        result = person_service.get_person_by_id("person-123")

        assert result == mock_person
        person_service.person_repo.get_one.assert_called_once_with({"entity_id": "person-123"})

    def test_get_person_by_id_not_found(self, person_service):
        """Test getting person by ID when not found."""
        person_service.person_repo.get_one.return_value = None

        result = person_service.get_person_by_id("nonexistent-id")

        assert result is None
        person_service.person_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    def test_get_person_by_id_with_different_ids(self, person_service):
        """Test getting different persons by their IDs."""
        mock_person_1 = MagicMock(spec=Person)
        mock_person_1.entity_id = "person-1"

        mock_person_2 = MagicMock(spec=Person)
        mock_person_2.entity_id = "person-2"

        def get_one_side_effect(query):
            if query["entity_id"] == "person-1":
                return mock_person_1
            elif query["entity_id"] == "person-2":
                return mock_person_2
            return None

        person_service.person_repo.get_one.side_effect = get_one_side_effect

        result_1 = person_service.get_person_by_id("person-1")
        result_2 = person_service.get_person_by_id("person-2")

        assert result_1 == mock_person_1
        assert result_2 == mock_person_2


class TestPersonServiceInitialization:
    """Tests for PersonService initialization."""

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_initialization_creates_dependencies(self, mock_factory_class, mock_email_class, mock_config):
        """Test that PersonService initializes its dependencies."""
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_repo = MagicMock()
        mock_factory.get_repository.return_value = mock_repo

        service = PersonService(mock_config)

        assert service.config == mock_config
        mock_email_class.assert_called_once_with(mock_config)
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.person.EmailService')
    @patch('common.services.person.RepositoryFactory')
    def test_initialization_gets_person_repository(self, mock_factory_class, mock_email_class, mock_config):
        """Test that PersonService gets the person repository."""
        from common.repositories.factory import RepoType

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = PersonService(mock_config)

        mock_factory.get_repository.assert_called_once_with(RepoType.PERSON)
