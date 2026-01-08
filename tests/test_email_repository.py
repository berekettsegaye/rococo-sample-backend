"""
Unit tests for common/repositories/email.py
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.email import EmailRepository
from common.models.email import Email


class TestEmailRepository:
    """Tests for EmailRepository."""

    def test_email_repository_inherits_from_base(self):
        """Test EmailRepository properly initializes with MODEL."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = EmailRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='email_queue'
        )

        assert repo.MODEL == Email
        assert repo is not None

    def test_email_repository_model_is_email(self):
        """Test that EmailRepository has Email as MODEL."""
        assert EmailRepository.MODEL == Email
