"""
Unit tests for the PersonOrganizationRoleRepository.
"""
from unittest.mock import MagicMock
from common.repositories.person_organization_role import PersonOrganizationRoleRepository
from common.models.person_organization_role import PersonOrganizationRole


class TestPersonOrganizationRoleRepository:
    """Test PersonOrganizationRoleRepository."""

    def test_person_org_role_repository_model_is_set(self):
        """Test that PersonOrganizationRoleRepository has MODEL set correctly."""
        assert PersonOrganizationRoleRepository.MODEL == PersonOrganizationRole

    def test_person_org_role_repository_instantiation(self):
        """Test PersonOrganizationRoleRepository instantiation."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = PersonOrganizationRoleRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="role-queue",
            user_id="user-123"
        )

        assert repo.MODEL == PersonOrganizationRole
        assert repo.user_id == "user-123"

    def test_person_org_role_repository_inheritance(self):
        """Test that PersonOrganizationRoleRepository inherits from BaseRepository."""
        from common.repositories.base import BaseRepository
        assert issubclass(PersonOrganizationRoleRepository, BaseRepository)
