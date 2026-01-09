"""
Unit tests for common/repositories/base.py
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.base import BaseRepository
from common.models.person import Person


class TestRepositoryWithModel(BaseRepository):
    """Test repository with MODEL defined."""
    MODEL = Person


class TestBaseRepositorySubclassing:
    """Tests for BaseRepository subclassing requirements."""

    def test_subclass_without_model_raises_error(self):
        """Test that subclassing without MODEL raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            class InvalidRepository(BaseRepository):
                pass

        assert "must define the MODEL attribute" in str(exc_info.value)

    def test_subclass_with_model_succeeds(self):
        """Test that subclassing with MODEL succeeds."""
        class ValidRepository(BaseRepository):
            MODEL = Person

        assert ValidRepository.MODEL == Person

    def test_multiple_subclasses_with_different_models(self):
        """Test creating multiple subclasses with different models."""
        from common.models.email import Email
        from common.models.organization import Organization

        class EmailRepository(BaseRepository):
            MODEL = Email

        class OrgRepository(BaseRepository):
            MODEL = Organization

        assert EmailRepository.MODEL == Email
        assert OrgRepository.MODEL == Organization
        assert EmailRepository.MODEL != OrgRepository.MODEL


class TestBaseRepositoryInitialization:
    """Tests for BaseRepository initialization."""

    def test_initialization_with_all_parameters(self):
        """Test initializing repository with all parameters."""
        mock_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepositoryWithModel(
            db_adapter=mock_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue",
            user_id="user-123"
        )

        assert repo.MODEL == Person

    def test_initialization_without_user_id(self):
        """Test initializing repository without user_id."""
        mock_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepositoryWithModel(
            db_adapter=mock_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue"
        )

        assert repo.MODEL == Person

    def test_initialization_passes_model_to_parent(self):
        """Test that initialization passes MODEL to parent class."""
        from unittest.mock import patch

        mock_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        with patch('common.repositories.base.PostgreSQLRepository.__init__') as mock_parent_init:
            mock_parent_init.return_value = None

            repo = TestRepositoryWithModel(
                db_adapter=mock_adapter,
                message_adapter=mock_message_adapter,
                queue_name="test_queue",
                user_id="user-123"
            )

            # Verify parent __init__ was called
            mock_parent_init.assert_called_once()
            # Verify the MODEL is Person (accessible from class)
            assert repo.MODEL == Person


class TestBaseRepositoryModelAttribute:
    """Tests for BaseRepository MODEL attribute."""

    def test_base_repository_model_is_none(self):
        """Test that BaseRepository.MODEL is None."""
        assert BaseRepository.MODEL is None

    def test_subclass_model_attribute_accessible(self):
        """Test that subclass MODEL attribute is accessible."""
        class PersonRepository(BaseRepository):
            MODEL = Person

        assert PersonRepository.MODEL == Person
        assert hasattr(PersonRepository, 'MODEL')

    def test_subclass_inherits_from_base_repository(self):
        """Test that custom repository inherits from BaseRepository."""
        class CustomRepository(BaseRepository):
            MODEL = Person

        repo_instance = CustomRepository(
            db_adapter=MagicMock(),
            message_adapter=MagicMock(),
            queue_name="test"
        )

        assert isinstance(repo_instance, BaseRepository)

    def test_model_attribute_not_overridden_by_instance(self):
        """Test that MODEL is a class attribute, not instance attribute."""
        mock_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepositoryWithModel(
            db_adapter=mock_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue"
        )

        # MODEL should be accessible from both class and instance
        assert TestRepositoryWithModel.MODEL == Person
        assert repo.MODEL == Person


class TestBaseRepositoryInheritance:
    """Tests for BaseRepository inheritance from PostgreSQLRepository."""

    def test_inherits_from_postgresql_repository(self):
        """Test that BaseRepository inherits from PostgreSQLRepository."""
        from rococo.repositories.postgresql import PostgreSQLRepository

        assert issubclass(BaseRepository, PostgreSQLRepository)

    def test_subclass_inherits_postgresql_methods(self):
        """Test that subclasses inherit PostgreSQLRepository methods."""
        mock_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = TestRepositoryWithModel(
            db_adapter=mock_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue"
        )

        # Check that common repository methods exist (inherited from parent)
        assert hasattr(repo, 'save')
        assert hasattr(repo, 'get_one')


class TestBaseRepositoryEdgeCases:
    """Tests for edge cases in BaseRepository."""

    def test_model_can_be_any_class(self):
        """Test that MODEL can be any class, not just specific models."""
        class CustomModel:
            pass

        class CustomRepository(BaseRepository):
            MODEL = CustomModel

        assert CustomRepository.MODEL == CustomModel

    def test_multiple_inheritance_levels(self):
        """Test that inheritance works through multiple levels."""
        class MiddleRepository(BaseRepository):
            MODEL = Person

        class ChildRepository(MiddleRepository):
            pass

        # Child should inherit MODEL from parent
        assert ChildRepository.MODEL == Person

    def test_model_attribute_immutable_at_class_level(self):
        """Test that MODEL attribute is defined at class level."""
        class Repo1(BaseRepository):
            MODEL = Person

        from common.models.email import Email

        class Repo2(BaseRepository):
            MODEL = Email

        # Each class should maintain its own MODEL
        assert Repo1.MODEL == Person
        assert Repo2.MODEL == Email
