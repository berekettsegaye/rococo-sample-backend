"""
Unit tests for common/repositories/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.repositories.organization import OrganizationRepository


@pytest.fixture
def mock_adapter():
    """Create a mock database adapter."""
    adapter = MagicMock()
    return adapter


@pytest.fixture
def organization_repo(mock_adapter):
    """Create an OrganizationRepository instance with mocked dependencies."""
    mock_message_adapter = MagicMock()
    repo = OrganizationRepository(
        db_adapter=mock_adapter,
        message_adapter=mock_message_adapter,
        queue_name="test_queue",
        user_id="test-user-id"
    )
    return repo


class TestOrganizationRepositoryGetOrganizationsByPersonId:
    """Tests for OrganizationRepository.get_organizations_by_person_id method."""

    def test_get_organizations_by_person_id_success(self, organization_repo, mock_adapter):
        """Test getting organizations by person ID successfully."""
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

        mock_adapter.execute_query.return_value = mock_results

        result = organization_repo.get_organizations_by_person_id("person-123")

        assert result == mock_results
        assert len(result) == 2
        assert result[0]["role"] == "admin"
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

    def test_get_organizations_by_person_id_empty_results(self, organization_repo, mock_adapter):
        """Test getting organizations when person has no organizations."""
        mock_adapter.execute_query.return_value = []

        result = organization_repo.get_organizations_by_person_id("person-with-no-orgs")

        assert result == []
        mock_adapter.execute_query.assert_called_once()

    def test_get_organizations_by_person_id_single_org(self, organization_repo, mock_adapter):
        """Test getting single organization for a person."""
        mock_results = [
            {
                "entity_id": "org-1",
                "name": "Solo Organization",
                "role": "owner"
            }
        ]

        mock_adapter.execute_query.return_value = mock_results

        result = organization_repo.get_organizations_by_person_id("person-solo")

        assert len(result) == 1
        assert result[0]["name"] == "Solo Organization"
        assert result[0]["role"] == "owner"

    def test_get_organizations_by_person_id_multiple_orgs(self, organization_repo, mock_adapter):
        """Test getting multiple organizations with various roles."""
        mock_results = [
            {"entity_id": "org-1", "name": "Company A", "role": "admin"},
            {"entity_id": "org-2", "name": "Company B", "role": "member"},
            {"entity_id": "org-3", "name": "Company C", "role": "viewer"},
            {"entity_id": "org-4", "name": "Company D", "role": "contributor"}
        ]

        mock_adapter.execute_query.return_value = mock_results

        result = organization_repo.get_organizations_by_person_id("person-multi")

        assert len(result) == 4
        assert all("role" in org for org in result)

    def test_get_organizations_by_person_id_uses_adapter_context(self, organization_repo, mock_adapter):
        """Test that the method uses adapter context manager."""
        mock_adapter.execute_query.return_value = []

        organization_repo.get_organizations_by_person_id("person-123")

        # Verify adapter was used as context manager
        mock_adapter.__enter__.assert_called()
        mock_adapter.__exit__.assert_called()

    def test_get_organizations_by_person_id_with_special_chars(self, organization_repo, mock_adapter):
        """Test getting organizations with person ID containing special characters."""
        mock_results = [{"entity_id": "org-1", "name": "Test Org", "role": "admin"}]
        mock_adapter.execute_query.return_value = mock_results

        result = organization_repo.get_organizations_by_person_id("person-with-special-123@#")

        # Should use parameterized query, so special chars are safe
        assert result == mock_results
        call_args = mock_adapter.execute_query.call_args
        params = call_args[0][1]
        assert params == ("person-with-special-123@#",)

    def test_get_organizations_by_person_id_query_structure(self, organization_repo, mock_adapter):
        """Test the SQL query structure is correct."""
        mock_adapter.execute_query.return_value = []

        organization_repo.get_organizations_by_person_id("person-123")

        call_args = mock_adapter.execute_query.call_args
        query = call_args[0][0]

        # Verify query structure
        assert "SELECT o.*, por.role" in query
        assert "FROM organization AS o" in query
        assert "JOIN person_organization_role AS por" in query
        assert "ON o.entity_id = por.organization_id" in query
        assert "WHERE por.person_id = %s" in query

    def test_get_organizations_by_person_id_returns_all_org_fields(self, organization_repo, mock_adapter):
        """Test that all organization fields are returned."""
        mock_results = [
            {
                "entity_id": "org-1",
                "name": "Full Org",
                "description": "A complete organization",
                "created_at": "2023-01-01",
                "updated_at": "2023-01-02",
                "role": "admin"
            }
        ]

        mock_adapter.execute_query.return_value = mock_results

        result = organization_repo.get_organizations_by_person_id("person-123")

        assert len(result) == 1
        org = result[0]
        assert org["entity_id"] == "org-1"
        assert org["name"] == "Full Org"
        assert org["description"] == "A complete organization"
        assert org["role"] == "admin"


class TestOrganizationRepositoryModel:
    """Tests for OrganizationRepository MODEL attribute."""

    def test_repository_has_model_attribute(self):
        """Test that repository has MODEL attribute set."""
        from common.models.organization import Organization

        assert OrganizationRepository.MODEL == Organization

    def test_repository_model_is_organization(self):
        """Test that MODEL is the Organization class."""
        from common.models.organization import Organization

        assert OrganizationRepository.MODEL is Organization
