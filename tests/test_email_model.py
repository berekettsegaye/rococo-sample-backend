"""
Unit tests for common/models/email.py
"""
import pytest
from rococo.models.versioned_model import ModelValidationError


class TestEmailModel:
    """Tests for Email model validation."""

    def test_validate_email_valid(self):
        """Test validating a valid email address."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@example.com")
        # Should not raise exception
        email.validate_email()

    def test_validate_email_valid_with_plus(self):
        """Test validating email with plus sign."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test+tag@example.com")
        email.validate_email()

    def test_validate_email_valid_with_dots(self):
        """Test validating email with dots."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="first.last@example.com")
        email.validate_email()

    def test_validate_email_valid_with_underscore(self):
        """Test validating email with underscore."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test_user@example.com")
        email.validate_email()

    def test_validate_email_valid_with_dash(self):
        """Test validating email with dash."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test-user@example.com")
        email.validate_email()

    def test_validate_email_valid_with_numbers(self):
        """Test validating email with numbers."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="user123@example456.com")
        email.validate_email()

    def test_validate_email_valid_subdomain(self):
        """Test validating email with subdomain."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@mail.example.com")
        email.validate_email()

    def test_validate_email_not_string(self):
        """Test validation fails when email is not a string."""
        from common.models.email import Email

        email = Email(person_id="person-123", email=None)
        email.email = 12345  # Set to non-string

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "must be a string" in errors

    def test_validate_email_invalid_format_no_at(self):
        """Test validation fails for email without @ symbol."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="testexample.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_invalid_format_no_domain(self):
        """Test validation fails for email without domain."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_invalid_format_no_local(self):
        """Test validation fails for email without local part."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_invalid_format_no_tld(self):
        """Test validation fails for email without TLD."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@example")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_invalid_format_spaces(self):
        """Test validation fails for email with spaces."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test user@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_invalid_format_multiple_at(self):
        """Test validation fails for email with multiple @ symbols."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@@example.com")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_validate_email_exceeds_max_length(self):
        """Test validation fails for email exceeding 254 characters."""
        from common.models.email import Email

        # Create an email address longer than 254 characters
        long_email = "a" * 240 + "@example.com"  # 252 chars - should be fine
        email = Email(person_id="person-123", email=long_email)
        email.validate_email()  # Should pass

        # Now create one that's too long
        too_long_email = "a" * 250 + "@example.com"  # 262 chars
        email_too_long = Email(person_id="person-123", email=too_long_email)

        with pytest.raises(ModelValidationError) as exc_info:
            email_too_long.validate_email()

        errors = exc_info.value.args[0]
        assert "exceeds maximum length" in errors

    def test_validate_email_exact_max_length(self):
        """Test validation passes for email exactly 254 characters."""
        from common.models.email import Email

        # Create an email address exactly 254 characters
        # Format: local@domain.com
        local_part = "a" * 240
        domain_part = "@example.com"  # 12 chars
        exact_length_email = local_part + domain_part  # 252 chars

        email = Email(person_id="person-123", email=exact_length_email)
        email.validate_email()  # Should pass

    def test_validate_email_special_chars_invalid(self):
        """Test validation fails for email with invalid special characters."""
        from common.models.email import Email

        invalid_emails = [
            "test!user@example.com",
            "test#user@example.com",
            "test$user@example.com",
            "test%user@example.com",
        ]

        for invalid_email in invalid_emails:
            email = Email(person_id="person-123", email=invalid_email)
            with pytest.raises(ModelValidationError) as exc_info:
                email.validate_email()
            errors = exc_info.value.args[0]
            assert "Invalid email address format" in errors

    def test_validate_email_empty_string(self):
        """Test validation fails for empty email string."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="")

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        errors = exc_info.value.args[0]
        assert "Invalid email address format" in errors

    def test_email_model_initialization(self):
        """Test Email model can be initialized properly."""
        from common.models.email import Email

        email = Email(
            person_id="person-123",
            email="test@example.com",
            is_verified=True
        )

        assert email.person_id == "person-123"
        assert email.email == "test@example.com"
        assert email.is_verified is True

    def test_email_model_default_values(self):
        """Test Email model default values."""
        from common.models.email import Email

        email = Email(person_id="person-123", email="test@example.com")

        # Check that entity_id is generated
        assert email.entity_id is not None
        assert isinstance(email.entity_id, str)
