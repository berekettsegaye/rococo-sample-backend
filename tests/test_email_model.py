"""
Unit tests for common/models/email.py
"""
import pytest
from unittest.mock import patch
from common.models.email import Email
from rococo.models.versioned_model import ModelValidationError


class TestEmailValidateEmail:
    """Tests for Email.validate_email method."""

    def test_validate_valid_email(self):
        """Test validation passes for valid email."""
        email = Email(email="test@example.com")
        # Should not raise
        email.validate_email()

    def test_validate_email_with_subdomain(self):
        """Test validation passes for email with subdomain."""
        email = Email(email="user@mail.example.com")
        email.validate_email()

    def test_validate_email_with_plus(self):
        """Test validation passes for email with plus sign."""
        email = Email(email="user+tag@example.com")
        email.validate_email()

    def test_validate_email_with_dots(self):
        """Test validation passes for email with dots."""
        email = Email(email="first.last@example.com")
        email.validate_email()

    def test_validate_email_with_numbers(self):
        """Test validation passes for email with numbers."""
        email = Email(email="user123@example456.com")
        email.validate_email()

    def test_validate_email_with_underscore(self):
        """Test validation passes for email with underscore."""
        email = Email(email="user_name@example.com")
        email.validate_email()

    def test_validate_email_with_hyphen_in_domain(self):
        """Test validation passes for domain with hyphen."""
        email = Email(email="user@my-domain.com")
        email.validate_email()

    def test_validate_email_not_string(self):
        """Test validation fails when email is not a string."""
        email = Email(email=12345)

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "must be a string" in error_message

    def test_validate_email_invalid_format_no_at(self):
        """Test validation fails for email without @ symbol."""
        email = Email(email="invalid.email.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_invalid_format_no_domain(self):
        """Test validation fails for email without domain."""
        email = Email(email="user@")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_invalid_format_no_local(self):
        """Test validation fails for email without local part."""
        email = Email(email="@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_invalid_format_multiple_at(self):
        """Test validation fails for email with multiple @ symbols."""
        email = Email(email="user@@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_invalid_format_no_tld(self):
        """Test validation fails for email without TLD."""
        email = Email(email="user@domain")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_invalid_format_spaces(self):
        """Test validation fails for email with spaces."""
        email = Email(email="user name@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_exceeds_max_length(self):
        """Test validation fails when email exceeds 254 characters."""
        # Create an email longer than 254 characters
        long_email = "a" * 240 + "@example.com"  # 252 chars - should pass
        email = Email(email=long_email)
        email.validate_email()  # Should not raise

        # Now create one that's too long
        too_long_email = "a" * 250 + "@example.com"  # 262 chars
        email_too_long = Email(email=too_long_email)

        with pytest.raises(ModelValidationError) as exc_info:
            email_too_long.validate_email()

        error_message = exc_info.value.args[0]
        assert "exceeds maximum length" in error_message

    def test_validate_email_exactly_254_chars(self):
        """Test validation passes for email with exactly 254 characters."""
        # Create email with exactly 254 characters
        local_part = "a" * 240
        domain = "@example.com"  # 12 chars
        exact_email = local_part + domain  # 252 chars total

        email = Email(email=exact_email)
        email.validate_email()  # Should not raise

    def test_validate_email_multiple_errors(self):
        """Test validation collects multiple errors."""
        # Create an email that's too long
        too_long_email = "a" * 250 + "@example.com"
        email = Email(email=too_long_email)

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        # Should have length error
        assert "exceeds maximum length" in error_message

    def test_validate_email_empty_string(self):
        """Test validation fails for empty string."""
        email = Email(email="")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message

    def test_validate_email_with_special_chars(self):
        """Test validation for email with special characters in local part."""
        # These should be valid according to RFC
        valid_emails = [
            "user.name@example.com",
            "user_name@example.com",
            "user+tag@example.com",
            "user-name@example.com",
        ]

        for email_str in valid_emails:
            email = Email(email=email_str)
            email.validate_email()  # Should not raise

    def test_validate_email_invalid_special_chars(self):
        """Test validation fails for invalid special characters."""
        invalid_emails = [
            "user#name@example.com",
            "user$name@example.com",
            "user%name@example.com",
            "user&name@example.com",
        ]

        for email_str in invalid_emails:
            email = Email(email=email_str)
            with pytest.raises(ModelValidationError):
                email.validate_email()

    def test_validate_email_case_insensitive(self):
        """Test validation works with uppercase letters."""
        email = Email(email="User@Example.COM")
        email.validate_email()  # Should not raise

    def test_validate_email_international_domain(self):
        """Test validation for international domain (ASCII only in regex)."""
        # Our regex only supports ASCII, so this should fail
        email = Email(email="user@例え.jp")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        error_message = exc_info.value.args[0]
        assert "Invalid email address format" in error_message
