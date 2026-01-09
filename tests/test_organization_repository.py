"""
Unit tests for common/repositories/organization.py
"""
import pytest
from unittest.mock import MagicMock, patch
from common.repositories.organization import OrganizationRepository


class TestOrganizationRepository:
    """Tests for OrganizationRepository."""

    def test_model_is_set(self):
        """Test that MODEL is correctly set to Organization."""
        from common.models.organization import Organization
        assert OrganizationRepository.MODEL == Organization

    @patch('rococo.data.postgresql.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_get_organizations_by_person_id_success(self, mock_message_adapter, mock_db_adapter):
        """Test getting organizations by person ID successfully."""
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.__enter__ = MagicMock(return_value=mock_adapter_instance)
        mock_adapter_instance.__exit__ = MagicMock(return_value=None)
        mock_adapter_instance.execute_query.return_value = [
            {'entity_id': 'org-1', 'name': 'Org 1', 'role': 'admin'},
            {'entity_id': 'org-2', 'name': 'Org 2', 'role': 'member'}
        ]

        repo = OrganizationRepository(mock_db_adapter, mock_message_adapter, 'test-queue')
        repo.adapter = mock_adapter_instance

        result = repo.get_organizations_by_person_id('person-id')

        assert len(result) == 2
        assert result[0]['entity_id'] == 'org-1'
        assert result[0]['role'] == 'admin'
        mock_adapter_instance.execute_query.assert_called_once()

        # Verify the query contains expected SQL elements
        call_args = mock_adapter_instance.execute_query.call_args
        query = call_args[0][0]
        assert 'SELECT' in query
        assert 'organization' in query
        assert 'person_organization_role' in query

    @patch('rococo.data.postgresql.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_get_organizations_by_person_id_empty(self, mock_message_adapter, mock_db_adapter):
        """Test getting organizations by person ID when person has no organizations."""
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.__enter__ = MagicMock(return_value=mock_adapter_instance)
        mock_adapter_instance.__exit__ = MagicMock(return_value=None)
        mock_adapter_instance.execute_query.return_value = []

        repo = OrganizationRepository(mock_db_adapter, mock_message_adapter, 'test-queue')
        repo.adapter = mock_adapter_instance

        result = repo.get_organizations_by_person_id('person-id')

        assert result == []

    @patch('rococo.data.postgresql.PostgreSQLAdapter')
    @patch('rococo.messaging.base.MessageAdapter')
    def test_get_organizations_by_person_id_with_params(self, mock_message_adapter, mock_db_adapter):
        """Test that correct parameters are passed to execute_query."""
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.__enter__ = MagicMock(return_value=mock_adapter_instance)
        mock_adapter_instance.__exit__ = MagicMock(return_value=None)
        mock_adapter_instance.execute_query.return_value = []

        repo = OrganizationRepository(mock_db_adapter, mock_message_adapter, 'test-queue')
        repo.adapter = mock_adapter_instance

        repo.get_organizations_by_person_id('test-person-id')

        call_args = mock_adapter_instance.execute_query.call_args
        params = call_args[0][1]
        assert params == ('test-person-id',)
