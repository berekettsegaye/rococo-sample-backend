"""
Unit tests for common/repositories/base.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.repositories.base import BaseRepository
from common.models.person import Person


class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_base_repository_requires_model_attribute(self):
        """Test that subclasses must define MODEL attribute."""
        with pytest.raises(TypeError) as exc_info:
            class InvalidRepository(BaseRepository):
                pass

        assert "must define the MODEL attribute" in str(exc_info.value)

    def test_base_repository_initialization(self):
        """Test BaseRepository initialization with all parameters."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        class TestRepository(BaseRepository):
            MODEL = Person

        repo = TestRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='test_queue',
            user_id='user-123'
        )

        assert repo is not None

    def test_base_repository_save_operation(self):
        """Test save operation calls adapter correctly."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        class TestRepository(BaseRepository):
            MODEL = Person

        repo = TestRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='test_queue'
        )

        person = Person(first_name='John', last_name='Doe')

        with patch.object(repo, 'save', return_value=person) as mock_save:
            result = repo.save(person)
            mock_save.assert_called_once_with(person)
            assert result == person

    def test_base_repository_get_one_operation(self):
        """Test get_one operation queries adapter correctly."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        class TestRepository(BaseRepository):
            MODEL = Person

        repo = TestRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='test_queue'
        )

        with patch.object(repo, 'get_one', return_value=Person(first_name='John', last_name='Doe')) as mock_get:
            result = repo.get_one(entity_id='person-123')
            mock_get.assert_called_once_with(entity_id='person-123')
            assert result.first_name == 'John'

    def test_base_repository_get_many_operation(self):
        """Test get_many operation returns list."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        class TestRepository(BaseRepository):
            MODEL = Person

        repo = TestRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='test_queue'
        )

        persons = [
            Person(first_name='John', last_name='Doe'),
            Person(first_name='Jane', last_name='Smith')
        ]

        with patch.object(repo, 'get_many', return_value=persons) as mock_get_many:
            result = repo.get_many()
            mock_get_many.assert_called_once()
            assert len(result) == 2

    def test_base_repository_delete_operation(self):
        """Test delete operation calls adapter correctly."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        class TestRepository(BaseRepository):
            MODEL = Person

        repo = TestRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='test_queue'
        )

        with patch.object(repo, 'delete', return_value=True) as mock_delete:
            result = repo.delete(entity_id='person-123')
            mock_delete.assert_called_once_with(entity_id='person-123')
            assert result is True
