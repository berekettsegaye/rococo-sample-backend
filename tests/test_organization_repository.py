"""
Unit tests for common/repositories/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestOrganizationRepository:
    """Tests for OrganizationRepository."""

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_repository_has_model(self, mock_adapter):
        """Test that OrganizationRepository has MODEL defined."""
        from common.repositories.organization import OrganizationRepository
        from common.models.organization import Organization

        assert OrganizationRepository.MODEL == Organization

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_get_organizations_by_person_id_success(self, mock_adapter):
        """Test getting organizations by person ID successfully."""
        from common.repositories.organization import OrganizationRepository

        # Mock adapter
        mock_db_adapter = MagicMock()
        mock_results = [
            {
                "entity_id": "org-1",
                "name": "Organization 1",
                "role": "admin"
            },
            {
                "entity_id": "org-2",
                "name": "Organization 2",
                "role": "member"
            }
        ]
        mock_db_adapter.execute_query.return_value = mock_results
        mock_db_adapter.__enter__ = MagicMock(return_value=mock_db_adapter)
        mock_db_adapter.__exit__ = MagicMock(return_value=False)

        # Create repository
        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=None,
            queue_name="test_queue"
        )

        result = repo.get_organizations_by_person_id("person-123")

        assert len(result) == 2
        assert result[0]["entity_id"] == "org-1"
        assert result[0]["role"] == "admin"
        assert result[1]["entity_id"] == "org-2"
        assert result[1]["role"] == "member"

        # Verify query was executed
        mock_db_adapter.execute_query.assert_called_once()
        call_args = mock_db_adapter.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "SELECT o.*, por.role" in query
        assert "FROM organization AS o" in query
        assert "JOIN person_organization_role AS por" in query
        assert "WHERE por.person_id = %s" in query
        assert params == ("person-123",)

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_get_organizations_by_person_id_empty(self, mock_adapter):
        """Test getting organizations when person has no organizations."""
        from common.repositories.organization import OrganizationRepository

        # Mock adapter
        mock_db_adapter = MagicMock()
        mock_db_adapter.execute_query.return_value = []
        mock_db_adapter.__enter__ = MagicMock(return_value=mock_db_adapter)
        mock_db_adapter.__exit__ = MagicMock(return_value=False)

        # Create repository
        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=None,
            queue_name="test_queue"
        )

        result = repo.get_organizations_by_person_id("person-no-orgs")

        assert result == []
        mock_db_adapter.execute_query.assert_called_once()

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_get_organizations_by_person_id_multiple_roles(self, mock_adapter):
        """Test getting organizations where person has multiple roles."""
        from common.repositories.organization import OrganizationRepository

        # Mock adapter
        mock_db_adapter = MagicMock()
        mock_results = [
            {
                "entity_id": "org-1",
                "name": "Organization 1",
                "role": "admin"
            },
            {
                "entity_id": "org-2",
                "name": "Organization 2",
                "role": "member"
            },
            {
                "entity_id": "org-3",
                "name": "Organization 3",
                "role": "viewer"
            }
        ]
        mock_db_adapter.execute_query.return_value = mock_results
        mock_db_adapter.__enter__ = MagicMock(return_value=mock_db_adapter)
        mock_db_adapter.__exit__ = MagicMock(return_value=False)

        # Create repository
        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=None,
            queue_name="test_queue"
        )

        result = repo.get_organizations_by_person_id("person-456")

        assert len(result) == 3
        assert result[0]["role"] == "admin"
        assert result[1]["role"] == "member"
        assert result[2]["role"] == "viewer"

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_init_with_message_adapter(self, mock_adapter):
        """Test repository initialization with message adapter."""
        from common.repositories.organization import OrganizationRepository

        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="test_queue",
            user_id="user-123"
        )

        assert repo is not None

    @patch('common.repositories.base.PostgreSQLAdapter')
    def test_init_without_message_adapter(self, mock_adapter):
        """Test repository initialization without message adapter."""
        from common.repositories.organization import OrganizationRepository

        mock_db_adapter = MagicMock()

        repo = OrganizationRepository(
            db_adapter=mock_db_adapter,
            message_adapter=None,
            queue_name="test_queue"
        )

        assert repo is not None
