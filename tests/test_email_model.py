"""
Unit tests for common/models/email.py
"""
import pytest
from common.models.email import Email
from rococo.models.versioned_model import ModelValidationError


class TestEmailModel:
    """Tests for Email model."""

    def test_email_initialization_with_all_fields(self):
        """Test Email initialization with all fields set correctly."""
        email = Email(
            entity_id='email-123',
            person_id='person-123',
            email='test@example.com',
            is_verified=True
        )

        assert email.entity_id == 'email-123'
        assert email.person_id == 'person-123'
        assert email.email == 'test@example.com'
        assert email.is_verified is True

    def test_email_initialization_with_minimal_fields(self):
        """Test Email initialization with minimal fields and defaults."""
        email = Email(
            person_id='person-123',
            email='test@example.com'
        )

        assert email.person_id == 'person-123'
        assert email.email == 'test@example.com'
        assert email.entity_id is not None
        assert email.is_verified is False

    def test_email_is_verified_default_false(self):
        """Test that is_verified defaults to False."""
        email = Email(
            person_id='person-123',
            email='test@example.com'
        )

        assert email.is_verified is False

    def test_validate_email_with_valid_email(self):
        """Test validate_email with a valid email address."""
        email = Email(
            person_id='person-123',
            email='valid.email@example.com'
        )

        email.validate_email()

    def test_validate_email_with_invalid_format(self):
        """Test validate_email raises error for invalid email format."""
        email = Email(
            person_id='person-123',
            email='invalid-email'
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    def test_validate_email_with_non_string(self):
        """Test validate_email raises error when email is not a string."""
        email = Email(
            person_id='person-123',
            email=12345
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Email address must be a string" in str(exc_info.value)

    def test_validate_email_with_too_long_address(self):
        """Test validate_email raises error when email exceeds 254 characters."""
        long_email = 'a' * 250 + '@example.com'
        email = Email(
            person_id='person-123',
            email=long_email
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "exceeds maximum length" in str(exc_info.value)

    def test_validate_email_with_plus_sign(self):
        """Test validate_email accepts email with plus sign."""
        email = Email(
            person_id='person-123',
            email='user+tag@example.com'
        )

        email.validate_email()

    def test_validate_email_with_dots_and_dashes(self):
        """Test validate_email accepts email with dots and dashes."""
        email = Email(
            person_id='person-123',
            email='first.last-name@my-domain.co.uk'
        )

        email.validate_email()

    def test_validate_email_with_underscore(self):
        """Test validate_email accepts email with underscore."""
        email = Email(
            person_id='person-123',
            email='user_name@example.com'
        )

        email.validate_email()

    def test_validate_email_missing_at_symbol(self):
        """Test validate_email rejects email without @ symbol."""
        email = Email(
            person_id='person-123',
            email='invalidemail.com'
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    def test_validate_email_missing_domain(self):
        """Test validate_email rejects email without domain."""
        email = Email(
            person_id='person-123',
            email='user@'
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    def test_validate_email_with_spaces(self):
        """Test validate_email rejects email with spaces."""
        email = Email(
            person_id='person-123',
            email='user name@example.com'
        )

        with pytest.raises(ModelValidationError) as exc_info:
            email.validate_email()

        assert "Invalid email address format" in str(exc_info.value)

    def test_validate_email_exactly_254_characters(self):
        """Test validate_email accepts email with exactly 254 characters."""
        local_part = 'a' * 64
        domain_part = 'b' * 188 + '.com'
        email_address = local_part + '@' + domain_part

        email = Email(
            person_id='person-123',
            email=email_address
        )

        email.validate_email()
