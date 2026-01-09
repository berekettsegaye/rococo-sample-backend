"""
Unit tests for the PersonOrganizationRole model.
"""
from common.models.person_organization_role import PersonOrganizationRole


class TestPersonOrganizationRoleModel:
    """Test PersonOrganizationRole model."""

    def test_person_org_role_instantiation(self):
        """Test basic PersonOrganizationRole instantiation."""
        role = PersonOrganizationRole(
            entity_id="role-123",
            person_id="person-123",
            organization_id="org-123",
            role="admin"
        )
        assert role.entity_id == "role-123"
        assert role.person_id == "person-123"
        assert role.organization_id == "org-123"
        assert role.role == "admin"

    def test_person_org_role_with_minimal_fields(self):
        """Test PersonOrganizationRole with only required fields."""
        role = PersonOrganizationRole(
            person_id="person-456",
            organization_id="org-456",
            role="member"
        )
        assert role.person_id == "person-456"
        assert role.organization_id == "org-456"
        assert role.role == "member"

    def test_person_org_role_inheritance(self):
        """Test that PersonOrganizationRole properly inherits from base."""
        from rococo.models import PersonOrganizationRole as BasePersonOrganizationRole
        role = PersonOrganizationRole(
            person_id="person-123",
            organization_id="org-123",
            role="member"
        )
        assert isinstance(role, BasePersonOrganizationRole)
