"""
Unit tests for common/repositories/login_method.py
"""
import pytest
from unittest.mock import MagicMock
from common.repositories.login_method import LoginMethodRepository
from common.models.login_method import LoginMethod


class TestLoginMethodRepository:
    """Tests for LoginMethodRepository."""

    def test_login_method_repository_inherits_from_base(self):
        """Test LoginMethodRepository properly initializes with MODEL."""
        db_adapter = MagicMock()
        message_adapter = MagicMock()

        repo = LoginMethodRepository(
            db_adapter=db_adapter,
            message_adapter=message_adapter,
            queue_name='login_method_queue'
        )

        assert repo.MODEL == LoginMethod
        assert repo is not None

    def test_login_method_repository_model_is_login_method(self):
        """Test that LoginMethodRepository has LoginMethod as MODEL."""
        assert LoginMethodRepository.MODEL == LoginMethod
