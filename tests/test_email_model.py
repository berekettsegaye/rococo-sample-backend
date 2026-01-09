"""
Unit tests for common/models/email.py
"""
import pytest
from unittest.mock import patch


class TestEmailValidation:
    """Tests for email validation functionality."""

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_valid(self, mock_post_init):
        """Test validation passes for valid email."""
        from common.models.email import Email

        email = Email(email="test@example.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_not_string(self, mock_post_init):
        """Test validation fails when email is not a string."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email=123)  # Not a string

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Email address must be a string" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_invalid_format_no_at(self, mock_post_init):
        """Test validation fails for email without @ symbol."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="invalid.email.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_invalid_format_no_domain(self, mock_post_init):
        """Test validation fails for email without domain."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="test@")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_invalid_format_no_local_part(self, mock_post_init):
        """Test validation fails for email without local part."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_too_long(self, mock_post_init):
        """Test validation fails for email exceeding 254 characters."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        # Create email longer than 254 characters
        long_email = "a" * 240 + "@example.com"  # Total > 254 chars
        email = Email(email=long_email)

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "exceeds maximum length of 254 characters" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_subdomain(self, mock_post_init):
        """Test validation passes for email with subdomain."""
        from common.models.email import Email

        email = Email(email="test@mail.example.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_plus_addressing(self, mock_post_init):
        """Test validation passes for email with plus addressing."""
        from common.models.email import Email

        email = Email(email="test+tag@example.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_dots(self, mock_post_init):
        """Test validation passes for email with dots in local part."""
        from common.models.email import Email

        email = Email(email="first.last@example.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_numbers(self, mock_post_init):
        """Test validation passes for email with numbers."""
        from common.models.email import Email

        email = Email(email="user123@example456.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_hyphens(self, mock_post_init):
        """Test validation passes for email with hyphens in domain."""
        from common.models.email import Email

        email = Email(email="test@my-domain.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_underscores(self, mock_post_init):
        """Test validation passes for email with underscores."""
        from common.models.email import Email

        email = Email(email="test_user@example.com")
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_invalid_special_chars(self, mock_post_init):
        """Test validation fails for email with invalid special characters."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="test#user@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_multiple_at_symbols(self, mock_post_init):
        """Test validation fails for email with multiple @ symbols."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="test@@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_spaces(self, mock_post_init):
        """Test validation fails for email with spaces."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="test user@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_exactly_254_chars(self, mock_post_init):
        """Test validation passes for email with exactly 254 characters."""
        from common.models.email import Email

        # Create email with exactly 254 characters (254 - 12 for @example.com = 242)
        local_part = "a" * 242
        email_address = f"{local_part}@example.com"
        assert len(email_address) == 254

        email = Email(email=email_address)
        # Should not raise
        email.validate_email()

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_empty_string(self, mock_post_init):
        """Test validation fails for empty email string."""
        from common.models.email import Email
        from rococo.models.versioned_model import ModelValidationError

        email = Email(email="")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    @patch('common.models.email.BaseEmail.__post_init__')
    def test_validate_email_with_uppercase(self, mock_post_init):
        """Test validation passes for email with uppercase letters."""
        from common.models.email import Email

        email = Email(email="Test@Example.COM")
        # Should not raise
        email.validate_email()
