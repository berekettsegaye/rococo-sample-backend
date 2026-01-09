"""
Unit tests for the BaseRepository.
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.base import BaseRepository


class TestBaseRepository:
    """Test BaseRepository initialization and validation."""

    def test_base_repository_subclass_without_model_raises_error(self):
        """Test that subclass without MODEL attribute raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            class InvalidRepository(BaseRepository):
                pass  # Missing MODEL attribute

        assert "must define the MODEL attribute" in str(exc_info.value)

    def test_base_repository_subclass_with_model_succeeds(self):
        """Test that subclass with MODEL attribute is created successfully."""
        from common.models.person import Person

        class ValidRepository(BaseRepository):
            MODEL = Person

        # Should not raise any exception
        assert ValidRepository.MODEL == Person

    def test_base_repository_init(self):
        """Test BaseRepository initialization."""
        from common.models.person import Person

        class TestRepo(BaseRepository):
            MODEL = Person

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepo(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test-queue",
            user_id="user-123"
        )

        assert repo.MODEL == Person
        assert repo.user_id == "user-123"

    def test_base_repository_init_without_user_id(self):
        """Test BaseRepository initialization without user_id."""
        from common.models.email import Email

        class TestEmailRepo(BaseRepository):
            MODEL = Email

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestEmailRepo(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test-queue"
        )

        assert repo.MODEL == Email
