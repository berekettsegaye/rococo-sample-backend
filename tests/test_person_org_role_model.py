"""
Unit tests for common/models/person_organization_role.py
"""
import pytest
from common.models.person_organization_role import PersonOrganizationRole


class TestPersonOrganizationRoleModel:
    """Tests for PersonOrganizationRole model."""

    def test_person_organization_role_initialization(self):
        """Test PersonOrganizationRole initialization with all fields."""
        role = PersonOrganizationRole(
            entity_id='role-123',
            person_id='person-123',
            organization_id='org-123',
            role='admin'
        )

        assert role.entity_id == 'role-123'
        assert role.person_id == 'person-123'
        assert role.organization_id == 'org-123'
        assert role.role == 'admin'

    def test_person_organization_role_with_minimal_fields(self):
        """Test PersonOrganizationRole initialization with minimal required fields."""
        role = PersonOrganizationRole(
            person_id='person-456',
            organization_id='org-456',
            role='member'
        )

        assert role.person_id == 'person-456'
        assert role.organization_id == 'org-456'
        assert role.role == 'member'
        assert role.entity_id is not None

    def test_person_organization_role_entity_id_generation(self):
        """Test that different roles get unique entity_ids."""
        role1 = PersonOrganizationRole(
            person_id='person-1',
            organization_id='org-1',
            role='admin'
        )
        role2 = PersonOrganizationRole(
            person_id='person-2',
            organization_id='org-2',
            role='member'
        )

        assert role1.entity_id is not None
        assert role2.entity_id is not None
        assert role1.entity_id != role2.entity_id
