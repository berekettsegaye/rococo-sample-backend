"""
Unit tests for common/services/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.services.organization import OrganizationService
from common.models import Organization


class TestOrganizationService:
    """Tests for OrganizationService."""

    @patch('common.services.organization.RepositoryFactory')
    def test_save_organization(self, mock_repo_factory, mock_config):
        """Test saving an organization."""
        organization = Organization(name='Test Org')
        mock_repo = MagicMock()
        mock_repo.save.return_value = organization
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)
        result = service.save_organization(organization)

        assert result == organization
        mock_repo.save.assert_called_once_with(organization)

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_success(self, mock_repo_factory, mock_config):
        """Test getting organization by ID successfully."""
        organization = Organization(entity_id='org-id', name='Test Org')
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = organization
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id('org-id')

        assert result == organization
        mock_repo.get_one.assert_called_once_with({"entity_id": "org-id"})

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organization_by_id_not_found(self, mock_repo_factory, mock_config):
        """Test getting organization by ID when not found."""
        mock_repo = MagicMock()
        mock_repo.get_one.return_value = None
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)
        result = service.get_organization_by_id('nonexistent-id')

        assert result is None

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person(self, mock_repo_factory, mock_config):
        """Test getting organizations with roles by person ID."""
        organizations_data = [
            {'entity_id': 'org-1', 'name': 'Org 1', 'role': 'admin'},
            {'entity_id': 'org-2', 'name': 'Org 2', 'role': 'member'}
        ]
        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = organizations_data
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person('person-id')

        assert result == organizations_data
        assert len(result) == 2
        mock_repo.get_organizations_by_person_id.assert_called_once_with('person-id')

    @patch('common.services.organization.RepositoryFactory')
    def test_get_organizations_with_roles_by_person_empty(self, mock_repo_factory, mock_config):
        """Test getting organizations with roles when person has none."""
        mock_repo = MagicMock()
        mock_repo.get_organizations_by_person_id.return_value = []
        mock_repo_factory.return_value.get_repository.return_value = mock_repo

        service = OrganizationService(mock_config)
        result = service.get_organizations_with_roles_by_person('person-id')

        assert result == []
