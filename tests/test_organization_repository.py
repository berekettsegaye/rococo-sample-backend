"""
Unit tests for common/repositories/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestOrganizationRepositoryInit:
    """Tests for OrganizationRepository initialization."""

    def test_repository_has_model(self):
        """Test that repository has MODEL attribute set."""
        from common.repositories.organization import OrganizationRepository
        from common.models.organization import Organization

        assert OrganizationRepository.MODEL == Organization


class TestOrganizationRepositoryGetOrganizationsByPersonId:
    """Tests for get_organizations_by_person_id functionality."""

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_success(self, mock_base_init):
        """Test getting organizations by person ID successfully."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        # Mock adapter
        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"}
        ]

        repo.adapter = mock_adapter

        result = repo.get_organizations_by_person_id("person-123")

        assert len(result) == 2
        assert result[0]["entity_id"] == "org-1"
        assert result[0]["role"] == "admin"
        assert result[1]["entity_id"] == "org-2"
        assert result[1]["role"] == "member"

        # Verify query was called with correct parameters
        mock_adapter.execute_query.assert_called_once()
        call_args = mock_adapter.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "SELECT o.*, por.role" in query
        assert "FROM organization AS o" in query
        assert "JOIN person_organization_role AS por" in query
        assert "WHERE por.person_id = %s" in query
        assert params == ("person-123",)

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_empty_result(self, mock_base_init):
        """Test getting organizations when person has none."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = []

        repo.adapter = mock_adapter

        result = repo.get_organizations_by_person_id("person-123")

        assert result == []
        mock_adapter.execute_query.assert_called_once()

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_query_structure(self, mock_base_init):
        """Test that the SQL query has correct structure."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = []

        repo.adapter = mock_adapter

        repo.get_organizations_by_person_id("person-456")

        call_args = mock_adapter.execute_query.call_args
        query = call_args[0][0]

        # Verify query components
        assert "SELECT o.*, por.role" in query
        assert "FROM organization AS o" in query
        assert "JOIN person_organization_role AS por" in query
        assert "ON o.entity_id = por.organization_id" in query
        assert "WHERE por.person_id = %s" in query

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_uses_context_manager(self, mock_base_init):
        """Test that method uses adapter context manager."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.__enter__ = MagicMock(return_value=mock_adapter)
        mock_adapter.__exit__ = MagicMock(return_value=False)
        mock_adapter.execute_query.return_value = []

        repo.adapter = mock_adapter

        repo.get_organizations_by_person_id("person-123")

        # Verify context manager was used
        mock_adapter.__enter__.assert_called_once()
        mock_adapter.__exit__.assert_called_once()

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_multiple_orgs_same_person(self, mock_base_init):
        """Test getting multiple organizations for the same person."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = [
            {"entity_id": "org-1", "name": "Organization One", "role": "admin"},
            {"entity_id": "org-2", "name": "Organization Two", "role": "member"},
            {"entity_id": "org-3", "name": "Organization Three", "role": "viewer"}
        ]

        repo.adapter = mock_adapter

        result = repo.get_organizations_by_person_id("person-123")

        assert len(result) == 3
        assert all("entity_id" in org for org in result)
        assert all("role" in org for org in result)

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_parameterized_query(self, mock_base_init):
        """Test that query uses parameterized values."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = []

        repo.adapter = mock_adapter

        test_person_id = "test-person-abc-123"
        repo.get_organizations_by_person_id(test_person_id)

        call_args = mock_adapter.execute_query.call_args
        params = call_args[0][1]

        # Verify parameterized query
        assert params == (test_person_id,)

    @patch('common.repositories.organization.BaseRepository.__init__')
    def test_get_organizations_by_person_id_with_special_chars(self, mock_base_init):
        """Test getting organizations with special characters in person ID."""
        from common.repositories.organization import OrganizationRepository

        mock_base_init.return_value = None

        repo = OrganizationRepository.__new__(OrganizationRepository)

        mock_adapter = MagicMock()
        mock_adapter.execute_query.return_value = []

        repo.adapter = mock_adapter

        # Should handle special characters safely via parameterization
        repo.get_organizations_by_person_id("person-with-'quotes'")

        call_args = mock_adapter.execute_query.call_args
        params = call_args[0][1]

        assert params == ("person-with-'quotes'",)
