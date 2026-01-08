"""
Unit tests for common/repositories/person_organization_role.py
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.person_organization_role import PersonOrganizationRoleRepository
from common.models.person_organization_role import PersonOrganizationRole


class TestPersonOrganizationRoleRepository:
    """Tests for PersonOrganizationRoleRepository."""

    def test_person_org_role_repository_inherits_from_base(self):
        """Test PersonOrganizationRoleRepository properly initializes with MODEL."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = PersonOrganizationRoleRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='person_org_role_queue'
        )

        assert repo.MODEL == PersonOrganizationRole
        assert repo is not None

    def test_person_org_role_repository_model_is_person_org_role(self):
        """Test that PersonOrganizationRoleRepository has PersonOrganizationRole as MODEL."""
        assert PersonOrganizationRoleRepository.MODEL == PersonOrganizationRole
