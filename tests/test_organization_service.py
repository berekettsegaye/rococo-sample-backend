"""
Unit tests for common/services/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.organization import OrganizationService
from common.models.organization import Organization


class TestOrganizationService:
    """Tests for OrganizationService."""

    @patch('common.services.organization.RepositoryFactory')
    def test_organization_service_initialization(self, mock_factory):
        """Test OrganizationService initializes correctly."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(config)

        assert service.config == config
        assert service.organization_repo == mock_repo

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization(self, mock_factory):
        """Test save_organization calls repository save."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        org = Organization(name='Test Organization')
        mock_repo.save.return_value = org

        service = OrganizationService(config)
        result = service.save_organization(org)

        mock_repo.save.assert_called_once_with(org)
        assert result == org

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id(self, mock_factory):
        """Test get_organization_by_id queries repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        org = Organization(entity_id='org-123', name='Test Organization')
        mock_repo.get_one.return_value = org

        service = OrganizationService(config)
        result = service.get_organization_by_id('org-123')

        mock_repo.get_one.assert_called_once_with({"entity_id": 'org-123'})
        assert result == org

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person(self, mock_factory):
        """Test get_organizations_with_roles_by_person passes person_id to repository."""
        config = MagicMock()
        mock_repo = MagicMock()
        mock_factory.return_value.get_repository.return_value = mock_repo

        mock_results = [
            {'entity_id': 'org-1', 'name': 'Org 1', 'role': 'admin'},
            {'entity_id': 'org-2', 'name': 'Org 2', 'role': 'member'}
        ]
        mock_repo.get_organizations_by_person_id.return_value = mock_results

        service = OrganizationService(config)
        result = service.get_organizations_with_roles_by_person('person-123')

        mock_repo.get_organizations_by_person_id.assert_called_once_with('person-123')
        assert result == mock_results
