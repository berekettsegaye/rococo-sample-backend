"""
Unit tests for common/repositories/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.repositories.organization import OrganizationRepository
from common.models.organization import Organization


class TestOrganizationRepository:
    """Tests for OrganizationRepository."""

    def test_organization_repository_inherits_from_base(self):
        """Test OrganizationRepository properly initializes with MODEL."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = OrganizationRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='org_queue'
        )

        assert repo.MODEL == Organization
        assert repo is not None

    def test_organization_repository_model_is_organization(self):
        """Test that OrganizationRepository has Organization as MODEL."""
        assert OrganizationRepository.MODEL == Organization

    def test_get_organizations_by_person_id(self):
        """Test get_organizations_by_person_id queries database correctly."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = OrganizationRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='org_queue'
        )

        mock_results = [
            {'entity_id': 'org-1', 'name': 'Org 1', 'role': 'admin'},
            {'entity_id': 'org-2', 'name': 'Org 2', 'role': 'member'}
        ]

        db_adapter.execute_query = MagicMock(return_value=mock_results)
        db_adapter.__enter__ = MagicMock(return_value=db_adapter)
        db_adapter.__exit__ = MagicMock(return_value=False)

        results = repo.get_organizations_by_person_id('person-123')

        assert results == mock_results
        db_adapter.execute_query.assert_called_once()
        call_args = db_adapter.execute_query.call_args
        assert 'person-123' in call_args[0][1]
