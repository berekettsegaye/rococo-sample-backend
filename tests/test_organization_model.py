"""
Unit tests for the Organization model.
"""
from common.models.organization import Organization


class TestOrganizationModel:
    """Test Organization model."""

    def test_organization_instantiation(self):
        """Test basic Organization instantiation."""
        org = Organization(
            entity_id="org-123",
            name="Test Organization"
        )
        assert org.entity_id == "org-123"
        assert org.name == "Test Organization"

    def test_organization_with_minimal_fields(self):
        """Test Organization with only required fields."""
        org = Organization(name="Minimal Org")
        assert org.name == "Minimal Org"

    def test_organization_inheritance(self):
        """Test that Organization properly inherits from BaseOrganization."""
        from rococo.models import Organization as BaseOrganization
        org = Organization(name="Test")
        assert isinstance(org, BaseOrganization)
