"""
Unit tests for the OrganizationRepository.
"""
from unittest.mock import MagicMock
from common.repositories.organization import OrganizationRepository
from common.models.organization import Organization


class TestOrganizationRepository:
    """Test OrganizationRepository."""

    def test_organization_repository_model_is_set(self):
        """Test that OrganizationRepository has MODEL set to Organization."""
        assert OrganizationRepository.MODEL == Organization

    def test_organization_repository_instantiation(self):
        """Test OrganizationRepository instantiation."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="org-queue",
            user_id="user-123"
        )

        assert repo.MODEL == Organization
        assert repo.user_id == "user-123"

    def test_get_organizations_by_person_id_with_results(self):
        """Test get_organizations_by_person_id returns organizations."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        # Mock the context manager and execute_query
        mock_db_adapter.__enter__ = MagicMock(return_value=mock_db_adapter)
        mock_db_adapter.__exit__ = MagicMock(return_value=False)
        mock_db_adapter.execute_query = MagicMock(return_value=[
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"}
        ])

        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="org-queue"
        )

        results = repo.get_organizations_by_person_id("person-123")

        assert len(results) == 2
        assert results[0]["entity_id"] == "org-1"
        assert results[1]["role"] == "member"
        mock_db_adapter.execute_query.assert_called_once()

    def test_get_organizations_by_person_id_with_empty_results(self):
        """Test get_organizations_by_person_id returns empty list."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        mock_db_adapter.__enter__ = MagicMock(return_value=mock_db_adapter)
        mock_db_adapter.__exit__ = MagicMock(return_value=False)
        mock_db_adapter.execute_query = MagicMock(return_value=[])

        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="org-queue"
        )

        results = repo.get_organizations_by_person_id("person-456")

        assert len(results) == 0
        mock_db_adapter.execute_query.assert_called_once()

    def test_organization_repository_inheritance(self):
        """Test that OrganizationRepository inherits from BaseRepository."""
        from common.repositories.base import BaseRepository
        assert issubclass(OrganizationRepository, BaseRepository)
