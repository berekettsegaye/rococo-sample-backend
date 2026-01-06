"""
Unit tests for common/models/organization.py
"""
import pytest
from common.models.organization import Organization


class TestOrganizationModel:
    """Tests for Organization model."""

    def test_organization_initialization_with_name(self):
        """Test Organization initialization with name."""
        org = Organization(name='Test Organization')

        assert org.name == 'Test Organization'
        assert org.entity_id is not None

    def test_organization_initialization_with_entity_id(self):
        """Test Organization initialization with entity_id."""
        org = Organization(
            entity_id='org-123',
            name='Test Organization'
        )

        assert org.entity_id == 'org-123'
        assert org.name == 'Test Organization'

    def test_organization_entity_id_generation(self):
        """Test that different organizations get unique entity_ids."""
        org1 = Organization(name='Organization 1')
        org2 = Organization(name='Organization 2')

        assert org1.entity_id is not None
        assert org2.entity_id is not None
        assert org1.entity_id != org2.entity_id
