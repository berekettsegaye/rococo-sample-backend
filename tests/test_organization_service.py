"""
Unit tests for the OrganizationService.
"""
from unittest.mock import MagicMock, patch
from common.services.organization import OrganizationService
from common.models.organization import Organization


class TestOrganizationService:
    """Test OrganizationService methods."""

    @patch('common.services.organization.RepositoryFactory')
    def test_organization_service_init(self, mock_factory_class):
        """Test OrganizationService initialization."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        service = OrganizationService(mock_config)

        assert service.config == mock_config
        mock_factory_class.assert_called_once_with(mock_config)
        mock_factory.get_repository.assert_called_once()

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization(self, mock_factory_class):
        """Test save_organization method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        saved_org = Organization(entity_id="org-123", name="Test Organization")
        mock_repo.save.return_value = saved_org

        service = OrganizationService(mock_config)
        org = Organization(name="Test Organization")
        result = service.save_organization(org)

        assert result.entity_id == "org-123"
        mock_repo.save.assert_called_once_with(org)

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_existing(self, mock_factory_class):
        """Test get_organization_by_id with existing organization."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        found_org = Organization(entity_id="org-123", name="Test Organization")
        mock_repo.get_one.return_value = found_org

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id("org-123")

        assert result.entity_id == "org-123"
        mock_repo.get_one.assert_called_once_with({"entity_id": "org-123"})

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_not_found(self, mock_factory_class):
        """Test get_organization_by_id with non-existing id."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_one.return_value = None

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id("nonexistent-id")

        assert result is None
        mock_repo.get_one.assert_called_once_with({"entity_id": "nonexistent-id"})

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person(self, mock_factory_class):
        """Test get_organizations_with_roles_by_person method."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_results = [
            {"entity_id": "org-1", "name": "Org 1", "role": "admin"},
            {"entity_id": "org-2", "name": "Org 2", "role": "member"}
        ]
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-123")

        assert len(result) == 2
        assert result[0]["entity_id"] == "org-1"
        assert result[1]["role"] == "member"
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-123")

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_empty(self, mock_factory_class):
        """Test get_organizations_with_roles_by_person with no results."""
        mock_config = MagicMock()
        mock_factory = MagicMock()
        mock_repo = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.get_repository.return_value = mock_repo

        mock_repo.get_organizations_by_person_id.return_value = []

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person("person-456")

        assert len(result) == 0
        mock_repo.get_organizations_by_person_id.assert_called_once_with("person-456")
