"""
Unit tests for the Email model.
"""
import pytest
from common.models.email import Email
from rococo.models.versioned_model import ModelValidationError


class TestEmailValidation:
    """Test Email model validation logic."""

    def test_validate_email_with_valid_email(self):
        """Test that valid email addresses pass validation."""
        email = Email(email="test@example.com", person_id="person-123")
        email.validate_email()  # Should not raise any exception

    def test_validate_email_with_multiple_valid_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "test+tag@example.com",
            "user123@test-domain.com",
            "a@b.co",
        ]
        for email_str in valid_emails:
            email = Email(email=email_str, person_id="person-123")
            email.validate_email()  # Should not raise any exception

    def test_validate_email_missing_at_symbol(self):
        """Test that email without @ symbol raises validation error."""
        email = Email(email="testexample.com", person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Invalid email address format." in str(exc_info.value)

    def test_validate_email_missing_domain(self):
        """Test that email without domain raises validation error."""
        email = Email(email="test@", person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Invalid email address format." in str(exc_info.value)

    def test_validate_email_missing_local_part(self):
        """Test that email without local part raises validation error."""
        email = Email(email="@example.com", person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Invalid email address format." in str(exc_info.value)

    def test_validate_email_exceeds_max_length(self):
        """Test that email exceeding 254 characters raises validation error."""
        # Create an email that's longer than 254 characters
        long_email = "a" * 250 + "@example.com"
        email = Email(email=long_email, person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Email address exceeds maximum length of 254 characters." in str(exc_info.value)

    def test_validate_email_with_non_string(self):
        """Test that non-string email raises validation error."""
        email = Email(email=12345, person_id="person-123")  # type: ignore
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Email address must be a string." in str(exc_info.value)

    def test_validate_email_with_none(self):
        """Test that None email raises validation error."""
        email = Email(email=None, person_id="person-123")  # type: ignore
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Email address must be a string." in str(exc_info.value)

    def test_validate_email_with_invalid_special_chars(self):
        """Test that email with invalid special characters raises validation error."""
        email = Email(email="test@exam ple.com", person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Invalid email address format." in str(exc_info.value)

    def test_validate_email_without_tld(self):
        """Test that email without top-level domain raises validation error."""
        email = Email(email="test@example", person_id="person-123")
        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()
        assert "Invalid email address format." in str(exc_info.value)

    def test_email_model_instantiation(self):
        """Test basic Email model instantiation."""
        email = Email(
            entity_id="email-123",
            email="test@example.com",
            person_id="person-123",
            is_verified=True
        )
        assert email.entity_id == "email-123"
        assert email.email == "test@example.com"
        assert email.person_id == "person-123"
        assert email.is_verified is True
