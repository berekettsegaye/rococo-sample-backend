"""
Unit tests for common/repositories/base.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_subclass_without_model_raises_error(self):
        """Test that subclasses without MODEL attribute raise TypeError."""
        from common.repositories.base import BaseRepository

        with pytest.raises(TypeError, match="must define the MODEL attribute"):
            class InvalidRepository(BaseRepository):
                pass  # No MODEL defined

    def test_subclass_with_model_succeeds(self):
        """Test that subclasses with MODEL attribute are valid."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person

        class ValidRepository(BaseRepository):
            MODEL = Person

        assert ValidRepository.MODEL == Person

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_init_with_all_parameters(self, mock_adapter):
        """Test repository initialization with all parameters."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person

        class TestRepository(BaseRepository):
            MODEL = Person

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue",
            user_id="user-123"
        )

        assert repo is not None

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_init_without_user_id(self, mock_adapter):
        """Test repository initialization without user_id."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person

        class TestRepository(BaseRepository):
            MODEL = Person

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue"
        )

        assert repo is not None

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_init_without_message_adapter(self, mock_adapter):
        """Test repository initialization without message adapter."""
        from common.repositories.base import BaseRepository
        from common.models.email import Email

        class TestRepository(BaseRepository):
            MODEL = Email

        mock_db_adapter = MagicMock()

        repo = TestRepository(
            db_adapter=mock_db_adapter,
            message_adapter=None,
            queue_name="test_queue"
        )

        assert repo is not None

    def test_multiple_subclasses(self):
        """Test creating multiple subclasses with different models."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person
        from common.models.email import Email
        from common.models.organization import Organization

        class PersonRepository(BaseRepository):
            MODEL = Person

        class EmailRepository(BaseRepository):
            MODEL = Email

        class OrgRepository(BaseRepository):
            MODEL = Organization

        assert PersonRepository.MODEL == Person
        assert EmailRepository.MODEL == Email
        assert OrgRepository.MODEL == Organization

    def test_model_inheritance(self):
        """Test that MODEL attribute is properly inherited."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person

        class ParentRepository(BaseRepository):
            MODEL = Person

        # Subclassing a repository that already has MODEL should work
        class ChildRepository(ParentRepository):
            pass  # Inherits MODEL from parent

        assert ChildRepository.MODEL == Person

    @patch('common.repositories.base.PostgreSQLRepository.__init__')
    def test_init_calls_super(self, mock_super_init):
        """Test that __init__ calls parent class __init__ with correct parameters."""
        from common.repositories.base import BaseRepository
        from common.models.person import Person

        class TestRepository(BaseRepository):
            MODEL = Person

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        mock_super_init.return_value = None

        repo = TestRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue",
            user_id="user-456"
        )

        # Verify super().__init__ was called with correct arguments
        mock_super_init.assert_called_once_with(
            mock_db_adapter,
            Person,
            mock_message_adapter,
            "test_queue",
            user_id="user-456"
        )
