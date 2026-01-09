"""
Unit tests for common/services/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.organization import OrganizationService
from common.models.organization import Organization


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    return config


@pytest.fixture
def organization_service(mock_config):
    """Create an OrganizationService instance with mocked dependencies."""
    with patch('common.services.organization.RepositoryFactory'):
        service = OrganizationService(mock_config)
        service.organization_repo = MagicMock()
        return service


class TestOrganizationServiceSaveOrganization:
    """Tests for OrganizationService.save_organization method."""

    def test_save_organization_success(self, organization_service):
        """Test saving an organization successfully."""
        mock_org = MagicMock(spec=Organization)
        mock_org.entity_id = "org-123"
        mock_org.name = "Test Organization"

        organization_service.organization_repo.save.return_value = mock_org

        result = organization_service.save_organization(mock_org)

        assert result == mock_org
        organization_service.organization_repo.save.assert_called_once_with(mock_org)

    def test_save_organization_with_all_fields(self, organization_service):
        """Test saving organization with all fields."""
        mock_org = MagicMock(spec=Organization)
        mock_org.entity_id = "org-123"
        mock_org.name = "Acme Corp"
        mock_org.description = "A test organization"

        organization_service.organization_repo.save.return_value = mock_org

        result = organization_service.save_organization(mock_org)

        assert result == mock_org
        organization_service.organization_repo.save.assert_called_once()

    def test_save_organization_calls_repository(self, organization_service):
        """Test that save_organization delegates to repository."""
        mock_org = MagicMock(spec=Organization)
        organization_service.organization_repo.save.return_value = mock_org

        organization_service.save_organization(mock_org)

        organization_service.organization_repo.save.assert_called_once()


class TestOrganizationServiceGetOrganizationById:
    """Tests for OrganizationService.get_organization_by_id method."""

    def test_get_organization_by_id_success(self, organization_service):
        """Test getting organization by ID successfully."""
        mock_org = MagicMock(spec=Organization)
        mock_org.entity_id = "org-123"
        mock_org.name = "Test Organization"

        organization_service.organization_repo.get_one.return_value = mock_org

        result = organization_service.get_organization_by_id("org-123")

        assert result == mock_org
        organization_service.organization_repo.get_one.assert_called_once_with({"entity_id": "org-123"})

    def test_get_organization_by_id_not_found(self, organization_service):
        """Test getting organization by ID when not found."""
        organization_service.organization_repo.get_one.return_value = None

        result = organization_service.get_organization_by_id("nonexistent-id")

        assert result is None
        organization_service.organization_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    def test_get_organization_by_id_with_different_ids(self, organization_service):
        """Test getting different organizations by their IDs."""
        mock_org_1 = MagicMock(spec=Organization)
        mock_org_1.entity_id = "org-1"

        mock_org_2 = MagicMock(spec=Organization)
        mock_org_2.entity_id = "org-2"

        def get_one_side_effect(query):
            if query["entity_id"] == "org-1":
                return mock_org_1
            elif query["entity_id"] == "org-2":
                return mock_org_2
            return None

        organization_service.organization_repo.get_one.side_effect = get_one_side_effect

        result_1 = organization_service.get_organization_by_id("org-1")
        result_2 = organization_service.get_organization_by_id("org-2")

        assert result_1 == mock_org_1
        assert result_2 == mock_org_2


class TestOrganizationServiceGetOrganizationsWithRolesByPerson:
    """Tests for OrganizationService.get_organizations_with_roles_by_person method."""

    def test_get_organizations_with_roles_by_person_success(self, organization_service):
        """Test getting organizations with roles for a person successfully."""
        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"}
        ]

        organization_service.organization_repo.get_organizations_by_person_id.return_value = mock_results

        result = organization_service.get_organizations_with_roles_by_person("person-123")

        assert result == mock_results
        assert len(result) == 2
        assert result[0]["role"] == "admin"
        assert result[1]["role"] == "member"
        organization_service.organization_repo.get_organizations_by_person_id.assert_called_once_with("person-123")

    def test_get_organizations_with_roles_by_person_empty(self, organization_service):
        """Test getting organizations when person has none."""
        organization_service.organization_repo.get_organizations_by_person_id.return_value = []

        result = organization_service.get_organizations_with_roles_by_person("person-123")

        assert result == []
        organization_service.organization_repo.get_organizations_by_person_id.assert_called_once_with("person-123")

    def test_get_organizations_with_roles_by_person_single_org(self, organization_service):
        """Test getting single organization for a person."""
        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "owner"}
        ]

        organization_service.organization_repo.get_organizations_by_person_id.return_value = mock_results

        result = organization_service.get_organizations_with_roles_by_person("person-123")

        assert len(result) == 1
        assert result[0]["role"] == "owner"

    def test_get_organizations_with_roles_by_person_multiple_roles(self, organization_service):
        """Test getting multiple organizations with different roles."""
        mock_results = [
            {"entity_id": "org-1", "name": "Company A", "role": "admin"},
            {"entity_id": "org-2", "name": "Company B", "role": "member"},
            {"entity_id": "org-3", "name": "Company C", "role": "viewer"}
        ]

        organization_service.organization_repo.get_organizations_by_person_id.return_value = mock_results

        result = organization_service.get_organizations_with_roles_by_person("person-456")

        assert len(result) == 3
        assert result[0]["role"] == "admin"
        assert result[1]["role"] == "member"
        assert result[2]["role"] == "viewer"

    def test_get_organizations_with_roles_by_person_nonexistent_person(self, organization_service):
        """Test getting organizations for non-existent person."""
        organization_service.organization_repo.get_organizations_by_person_id.return_value = []

        result = organization_service.get_organizations_with_roles_by_person("nonexistent-person-id")

        assert result == []


class TestOrganizationServiceInitialization:
    """Tests for OrganizationService initialization."""

    @patch('common.services.organization.RepositoryFactory')
    def test_initialization_creates_dependencies(self, mock_factory_class, mock_config):
        """Test that OrganizationService initializes its dependencies."""
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_repo = MagicMock()
        mock_factory.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.organization.RepositoryFactory')
    def test_initialization_gets_organization_repository(self, mock_factory_class, mock_config):
        """Test that OrganizationService gets the organization repository."""
        from common.repositories.factory import RepoType

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        mock_factory.get_repository.assert_called_once_with(RepoType.ORGANIZATION)
