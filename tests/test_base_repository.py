"""
Unit tests for common/repositories/base.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.repositories.base import BaseRepository
from rococo.models.versioned_model import VersionedModel


class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_init_subclass_without_model_raises_error(self):
        """Test that subclassing without MODEL attribute raises TypeError."""
        with pytest.raises(TypeError, match="must define the MODEL attribute"):
            class InvalidRepository(BaseRepository):
                pass

    def test_init_subclass_with_model_succeeds(self):
        """Test that subclassing with MODEL attribute succeeds."""
        class DummyModel(VersionedModel):
            pass

        class ValidRepository(BaseRepository):
            MODEL = DummyModel

        assert ValidRepository.MODEL == DummyModel

    @patch('common.repositories.base.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_init_passes_model_to_parent(self, mock_message_adapter, mock_db_adapter):
        """Test that __init__ passes MODEL to parent PostgreSQLRepository."""
        class DummyModel(VersionedModel):
            pass

        class TestRepo(BaseRepository):
            MODEL = DummyModel

        with patch('common.repositories.base.PostgreSQLRepository.__init__') as mock_parent_init:
            mock_parent_init.return_value = None
            repo = TestRepo(mock_db_adapter, mock_message_adapter, 'test-queue')

            # Verify parent __init__ was called with MODEL
            mock_parent_init.assert_called_once()
            call_args = mock_parent_init.call_args
            # args are (self, db_adapter, model, message_adapter, queue_name)
            assert call_args[0][1] == DummyModel

    @patch('common.repositories.base.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_init_with_user_id(self, mock_message_adapter, mock_db_adapter):
        """Test initialization with user_id parameter."""
        class DummyModel(VersionedModel):
            pass

        class TestRepo(BaseRepository):
            MODEL = DummyModel

        with patch('common.repositories.base.PostgreSQLRepository.__init__') as mock_parent_init:
            mock_parent_init.return_value = None
            repo = TestRepo(mock_db_adapter, mock_message_adapter, 'test-queue', user_id='user-123')

            # Verify user_id was passed
            call_args = mock_parent_init.call_args
            assert call_args[1]['user_id'] == 'user-123'

    @patch('common.repositories.base.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_init_without_user_id(self, mock_message_adapter, mock_db_adapter):
        """Test initialization without user_id parameter."""
        class DummyModel(VersionedModel):
            pass

        class TestRepo(BaseRepository):
            MODEL = DummyModel

        with patch('common.repositories.base.PostgreSQLRepository.__init__') as mock_parent_init:
            mock_parent_init.return_value = None
            repo = TestRepo(mock_db_adapter, mock_message_adapter, 'test-queue')

            # Verify user_id defaults to None
            call_args = mock_parent_init.call_args
            assert call_args[1]['user_id'] is None
