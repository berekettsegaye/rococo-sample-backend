"""
Unit tests for common/models/email.py
"""
import pytest
from unittest.mock import patch
from rococo.models.versioned_model import ModelValidationError


class TestEmailValidation:
    """Tests for Email model validation."""

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_valid(self, mock_post_init):
        """Test validation passes for valid email."""
        from common.models.email import Email

        email = Email(email='test@example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_not_string(self, mock_post_init):
        """Test validation fails when email is not a string."""
        from common.models.email import Email

        email = Email(email=123)
        with pytest.raises(ModelValidationError, match="must be a string"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_invalid_format(self, mock_post_init):
        """Test validation fails for invalid email format."""
        from common.models.email import Email

        email = Email(email='invalid-email')
        with pytest.raises(ModelValidationError, match="Invalid email address format"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_missing_at_symbol(self, mock_post_init):
        """Test validation fails when missing @ symbol."""
        from common.models.email import Email

        email = Email(email='testexample.com')
        with pytest.raises(ModelValidationError, match="Invalid email address format"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_missing_domain(self, mock_post_init):
        """Test validation fails when missing domain."""
        from common.models.email import Email

        email = Email(email='test@')
        with pytest.raises(ModelValidationError, match="Invalid email address format"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_missing_local_part(self, mock_post_init):
        """Test validation fails when missing local part."""
        from common.models.email import Email

        email = Email(email='@example.com')
        with pytest.raises(ModelValidationError, match="Invalid email address format"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_exceeds_max_length(self, mock_post_init):
        """Test validation fails when email exceeds 254 characters."""
        from common.models.email import Email

        long_email = 'a' * 250 + '@example.com'  # More than 254 chars
        email = Email(email=long_email)
        with pytest.raises(ModelValidationError, match="exceeds maximum length"):
            email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_subdomain(self, mock_post_init):
        """Test validation passes for email with subdomain."""
        from common.models.email import Email

        email = Email(email='test@mail.example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_plus_sign(self, mock_post_init):
        """Test validation passes for email with plus sign."""
        from common.models.email import Email

        email = Email(email='test+tag@example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_hyphen(self, mock_post_init):
        """Test validation passes for email with hyphen."""
        from common.models.email import Email

        email = Email(email='test-user@example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_underscore(self, mock_post_init):
        """Test validation passes for email with underscore."""
        from common.models.email import Email

        email = Email(email='test_user@example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_numbers(self, mock_post_init):
        """Test validation passes for email with numbers."""
        from common.models.email import Email

        email = Email(email='test123@example456.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_dots(self, mock_post_init):
        """Test validation passes for email with dots in local part."""
        from common.models.email import Email

        email = Email(email='test.user@example.com')
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_at_max_length(self, mock_post_init):
        """Test validation passes for email at exactly 254 characters."""
        from common.models.email import Email

        # Create an email that's exactly 254 characters
        local = 'a' * 64
        # Domain needs to be valid format, max 254 total including @ and .
        domain = 'b' * 185 + '.com'  # 64 + 1 + 185 + 4 = 254
        email_str = f"{local}@{domain}"
        email = Email(email=email_str)
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_special_chars_invalid(self, mock_post_init):
        """Test validation fails for email with invalid special characters."""
        from common.models.email import Email

        email = Email(email='test#user@example.com')
        with pytest.raises(ModelValidationError, match="Invalid email address format"):
            email.validate_email()
