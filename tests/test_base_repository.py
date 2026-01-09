"""
Unit tests for common/repositories/base.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestBaseRepositoryInit:
    """Tests for BaseRepository initialization."""

    def test_base_repository_requires_model(self):
        """Test that BaseRepository subclasses must define MODEL."""
        from common.repositories.base import BaseRepository

        # Attempting to create a subclass without MODEL should raise TypeError
        with pytest.raises(TypeError) as exc_info:
            class InvalidRepository(BaseRepository):
                pass

        assert "must define the MODEL attribute" in str(exc_info.value)

    def test_base_repository_with_model(self):
        """Test that BaseRepository subclass with MODEL is valid."""
        from common.repositories.base import BaseRepository
        from rococo.models import VersionedModel

        # Creating a subclass with MODEL should not raise
        class ValidRepository(BaseRepository):
            MODEL = VersionedModel

        assert ValidRepository.MODEL == VersionedModel

    @patch('common.repositories.base.PostgreSQLRepository.__init__')
    def test_init_passes_model_to_parent(self, mock_parent_init):
        """Test that __init__ passes MODEL to parent class."""
        from common.repositories.base import BaseRepository
        from rococo.models import VersionedModel

        mock_parent_init.return_value = None

        class TestRepository(BaseRepository):
            MODEL = VersionedModel

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()
        queue_name = "test_queue"
        user_id = "user-123"

        repo = TestRepository(mock_db_adapter, mock_message_adapter, queue_name, user_id)

        # Verify parent __init__ was called with correct arguments
        mock_parent_init.assert_called_once_with(
            mock_db_adapter,
            VersionedModel,
            mock_message_adapter,
            queue_name,
            user_id=user_id
        )

    @patch('common.repositories.base.PostgreSQLRepository.__init__')
    def test_init_without_user_id(self, mock_parent_init):
        """Test initialization without user_id parameter."""
        from common.repositories.base import BaseRepository
        from rococo.models import VersionedModel

        mock_parent_init.return_value = None

        class TestRepository(BaseRepository):
            MODEL = VersionedModel

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()
        queue_name = "test_queue"

        repo = TestRepository(mock_db_adapter, mock_message_adapter, queue_name)

        # Verify parent __init__ was called with user_id=None
        mock_parent_init.assert_called_once_with(
            mock_db_adapter,
            VersionedModel,
            mock_message_adapter,
            queue_name,
            user_id=None
        )

    @patch('common.repositories.base.PostgreSQLRepository.__init__')
    def test_init_with_none_message_adapter(self, mock_parent_init):
        """Test initialization with None message_adapter."""
        from common.repositories.base import BaseRepository
        from rococo.models import VersionedModel

        mock_parent_init.return_value = None

        class TestRepository(BaseRepository):
            MODEL = VersionedModel

        mock_db_adapter = MagicMock()
        queue_name = "test_queue"

        repo = TestRepository(mock_db_adapter, None, queue_name)

        # Verify parent __init__ was called with None message_adapter
        mock_parent_init.assert_called_once_with(
            mock_db_adapter,
            VersionedModel,
            None,
            queue_name,
            user_id=None
        )


class TestBaseRepositorySubclassing:
    """Tests for BaseRepository subclassing behavior."""

    def test_multiple_subclasses_with_different_models(self):
        """Test that multiple subclasses can have different MODELs."""
        from common.repositories.base import BaseRepository

        class Model1:
            pass

        class Model2:
            pass

        class Repository1(BaseRepository):
            MODEL = Model1

        class Repository2(BaseRepository):
            MODEL = Model2

        assert Repository1.MODEL == Model1
        assert Repository2.MODEL == Model2

    def test_subclass_inherits_from_postgresql_repository(self):
        """Test that BaseRepository inherits from PostgreSQLRepository."""
        from common.repositories.base import BaseRepository
        from rococo.repositories.postgresql import PostgreSQLRepository

        assert issubclass(BaseRepository, PostgreSQLRepository)

    def test_model_attribute_is_class_level(self):
        """Test that MODEL attribute is at class level."""
        from common.repositories.base import BaseRepository

        class TestModel:
            pass

        class TestRepository(BaseRepository):
            MODEL = TestModel

        # MODEL should be accessible on class, not instance
        assert hasattr(TestRepository, 'MODEL')
        assert TestRepository.MODEL == TestModel


class TestBaseRepositoryEdgeCases:
    """Tests for edge cases in BaseRepository."""

    def test_model_cannot_be_none(self):
        """Test that MODEL cannot be None."""
        from common.repositories.base import BaseRepository

        with pytest.raises(TypeError) as exc_info:
            class InvalidRepository(BaseRepository):
                MODEL = None

        assert "must define the MODEL attribute" in str(exc_info.value)

    def test_subclass_of_subclass_requires_model(self):
        """Test that subclasses of valid repositories also need MODEL."""
        from common.repositories.base import BaseRepository

        class ParentModel:
            pass

        class ParentRepository(BaseRepository):
            MODEL = ParentModel

        # Child class should inherit MODEL from parent
        class ChildRepository(ParentRepository):
            pass

        # Should inherit MODEL from parent
        assert ChildRepository.MODEL == ParentModel

    def test_model_attribute_type_checking(self):
        """Test that MODEL can be any type (not just class)."""
        from common.repositories.base import BaseRepository

        # MODEL can be a class
        class SomeClass:
            pass

        class Repository1(BaseRepository):
            MODEL = SomeClass

        assert Repository1.MODEL == SomeClass

    @patch('common.repositories.base.PostgreSQLRepository.__init__')
    def test_init_preserves_all_parameters(self, mock_parent_init):
        """Test that all init parameters are passed correctly."""
        from common.repositories.base import BaseRepository

        mock_parent_init.return_value = None

        class TestModel:
            pass

        class TestRepository(BaseRepository):
            MODEL = TestModel

        db_adapter = MagicMock()
        message_adapter = MagicMock()
        queue_name = "my_queue"
        user_id = "user-abc-123"

        repo = TestRepository(db_adapter, message_adapter, queue_name, user_id=user_id)

        # Verify all parameters were passed
        call_args = mock_parent_init.call_args
        assert call_args[0][0] == db_adapter
        assert call_args[0][1] == TestModel
        assert call_args[0][2] == message_adapter
        assert call_args[0][3] == queue_name
        assert call_args[1]['user_id'] == user_id
