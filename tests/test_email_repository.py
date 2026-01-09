"""
Unit tests for the EmailRepository.
"""
from unittest.mock import MagicMock
from common.repositories.email import EmailRepository
from common.models.email import Email


class TestEmailRepository:
    """Test EmailRepository."""

    def test_email_repository_model_is_set(self):
        """Test that EmailRepository has MODEL set to Email."""
        assert EmailRepository.MODEL == Email

    def test_email_repository_instantiation(self):
        """Test EmailRepository instantiation."""
        mock_db_adapter = MagicMock()
        mock_message_adapter = MagicMock()

        repo = EmailRepository(
            db_adapter=mock_db_adapter,
            message_adapter=mock_message_adapter,
            queue_name="email-queue",
            user_id="user-123"
        )

        assert repo.MODEL == Email
        assert repo.user_id == "user-123"

    def test_email_repository_inheritance(self):
        """Test that EmailRepository inherits from BaseRepository."""
        from common.repositories.base import BaseRepository
        assert issubclass(EmailRepository, BaseRepository)
