"""
Unit tests for the PersonRepository.
"""
from unittest.mock import MagicMock
from common.repositories.person import PersonRepository
from common.models.person import Person


class TestPersonRepository:
    """Test PersonRepository."""

    def test_person_repository_model_is_set(self):
        """Test that PersonRepository has MODEL set to Person."""
        assert PersonRepository.MODEL == Person

    def test_person_repository_instantiation(self):
        """Test PersonRepository instantiation."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = PersonRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="person-queue",
            user_id="user-123"
        )

        assert repo.MODEL == Person
        assert repo.user_id == "user-123"

    def test_person_repository_inheritance(self):
        """Test that PersonRepository inherits from BaseRepository."""
        from common.repositories.base import BaseRepository
        assert issubclass(PersonRepository, BaseRepository)
