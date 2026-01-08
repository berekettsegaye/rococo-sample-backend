"""
Unit tests for common/repositories/person.py
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.person import PersonRepository
from common.models.person import Person


class TestPersonRepository:
    """Tests for PersonRepository."""

    def test_person_repository_inherits_from_base(self):
        """Test PersonRepository properly initializes with MODEL."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = PersonRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='person_queue'
        )

        assert repo.MODEL == Person
        assert repo is not None

    def test_person_repository_model_is_person(self):
        """Test that PersonRepository has Person as MODEL."""
        assert PersonRepository.MODEL == Person
