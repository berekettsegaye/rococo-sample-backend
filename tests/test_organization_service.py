"""
Unit tests for common/services/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestOrganizationServiceInit:
    """Tests for OrganizationService initialization."""

    @patch('common.services.organization.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.organization import OrganizationService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)


class TestOrganizationServiceSaveOrganization:
    """Tests for save_organization functionality."""

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization_success(self, mock_factory_class, mock_config):
        """Test saving an organization successfully."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_saved_org = MagicMock()
        mock_saved_org.entity_id = "org-123"
        mock_saved_org.name = "Test Organization"
        mock_repo.save.return_value = mock_saved_org

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        input_org = MagicMock()
        input_org.name = "Test Organization"

        result = service.save_organization(input_org)

        assert result == mock_saved_org
        mock_repo.save.assert_called_once_with(input_org)

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization_returns_saved_object(self, mock_factory_class, mock_config):
        """Test that save_organization returns the saved object."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_saved = MagicMock()
        mock_repo.save.return_value = mock_saved

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        input_org = MagicMock()
        result = service.save_organization(input_org)

        assert result == mock_saved


class TestOrganizationServiceGetOrganizationById:
    """Tests for get_organization_by_id functionality."""

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_success(self, mock_factory_class, mock_config):
        """Test getting organization by ID successfully."""
        from common.services.organization import OrganizationService

        mock_org = MagicMock()
        mock_org.entity_id = "org-123"
        mock_org.name = "Test Organization"

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = mock_org

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id("org-123")

        assert result == mock_org
        mock_repo.get_one.assert_called_once_with({"entity_id": "org-123"})

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting organization by ID when not found."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})


class TestOrganizationServiceGetOrganizationsWithRolesByPerson:
    """Tests for get_organizations_with_roles_by_person functionality."""

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_success(self, mock_factory_class, mock_config):
        """Test getting organizations with roles for a person."""
        from common.services.organization import OrganizationService

        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"}
        ]

        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-123")

        assert result == mock_results
        assert len(result) == 2
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-123")

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_empty_list(self, mock_factory_class, mock_config):
        """Test getting organizations when person has no organizations."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = []

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-123")

        assert result == []
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-123")

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_single_org(self, mock_factory_class, mock_config):
        """Test getting organizations when person has one organization."""
        from common.services.organization import OrganizationService

        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"}
        ]

        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-123")

        assert result == mock_results
        assert len(result) == 1

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_different_roles(self, mock_factory_class, mock_config):
        """Test getting organizations with different roles."""
        from common.services.organization import OrganizationService

        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"},
            {"entity_id": "org-3", "name": "Org 3", "role": "viewer"}
        ]

        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-123")

        assert result == mock_results
        assert len(result) == 3
        assert result[0]["role"] == "admin"
        assert result[1]["role"] == "member"
        assert result[2]["role"] == "viewer"
