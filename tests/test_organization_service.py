"""
Unit tests for common/services/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch


class TestOrganizationService:
    """Tests for OrganizationService."""

    @patch('common.services.organization.RepositoryFactory')
    def test_init(self, mock_factory_class, mock_config):
        """Test service initialization."""
        from common.services.organization import OrganizationService

        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization(self, mock_factory_class, mock_config):
        """Test saving an organization."""
        from common.services.organization import OrganizationService
        from common.models import Organization

        mock_repo = MagicMock()
        mock_saved_org = MagicMock(
            entity_id="org-123",
            name="Test Organization"
        )
        mock_repo.save.return_value = mock_saved_org

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        organization = Organization(name="Test Organization")
        result = service.save_organization(organization)

        assert result == mock_saved_org
        mock_repo.save.assert_called_once_with(organization)

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_success(self, mock_factory_class, mock_config):
        """Test getting an organization by ID successfully."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_org = MagicMock(
            entity_id="org-456",
            name="Another Organization"
        )
        mock_repo.get_one.return_value = mock_org

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        result = service.get_organization_by_id("org-456")

        assert result == mock_org
        mock_repo.get_one.assert_called_once_with({"entity_id": "org-456"})

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_not_found(self, mock_factory_class, mock_config):
        """Test getting an organization by ID when it doesn't exist."""
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

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person(self, mock_factory_class, mock_config):
        """Test getting organizations with roles by person ID."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_results = [
            {"organization_id": "org-1", "name": "Org 1", "role": "admin"},
            {"organization_id": "org-2", "name": "Org 2", "role": "member"}
        ]
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        result = service.get_organizations_with_roles_by_person("person-789")

        assert result == mock_results
        assert len(result) == 2
        assert result[0]["organization_id"] == "org-1"
        assert result[1]["role"] == "member"
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-789")

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_empty(self, mock_factory_class, mock_config):
        """Test getting organizations when person has no organizations."""
        from common.services.organization import OrganizationService

        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = []

        mock_factory = MagicMock()
        mock_factory.get_repository.return_value = mock_repo
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        result = service.get_organizations_with_roles_by_person("person-no-orgs")

        assert result == []
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-no-orgs")
