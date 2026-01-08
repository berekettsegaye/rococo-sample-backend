"""
Unit tests for common/models/login_method.py
"""
import pytest
from werkzeug.security import check_password_hash
from common.models.login_method import LoginMethod
from rococo.models.versioned_model import ModelValidationError


class TestLoginMethodModel:
    """Tests for LoginMethod model."""

    def test_login_method_initialization_with_password(self):
        """Test LoginMethod initialization with email/password type hashes password."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='email-password',
            raw_password='Test123!@#'
        )

        assert login_method.person_id == 'person-123'
        assert login_method.email_id == 'email-123'
        assert login_method.method_type == 'email-password'
        assert login_method.password is not None
        assert check_password_hash(login_method.password, 'Test123!@#')

    def test_login_method_initialization_with_oauth(self):
        """Test LoginMethod initialization with OAuth type."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='oauth-google',
            method_data={'oauth_id': 'google-123'}
        )

        assert login_method.person_id == 'person-123'
        assert login_method.email_id == 'email-123'
        assert login_method.method_type == 'oauth-google'
        assert login_method.method_data == {'oauth_id': 'google-123'}

    def test_login_method_password_hashing(self):
        """Test that raw_password is properly hashed."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='email-password',
            raw_password='ValidPass123!'
        )

        assert login_method.password is not None
        assert login_method.password != 'ValidPass123!'
        assert check_password_hash(login_method.password, 'ValidPass123!')

    def test_login_method_is_oauth_method_property_true(self):
        """Test is_oauth_method property returns True for OAuth types."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='oauth-microsoft',
            method_data={}
        )

        assert login_method.is_oauth_method is True

    def test_login_method_is_oauth_method_property_false(self):
        """Test is_oauth_method property returns False for non-OAuth types."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='email-password',
            raw_password='Test123!@#'
        )

        assert login_method.is_oauth_method is False

    def test_login_method_oauth_provider_name_property(self):
        """Test oauth_provider_name property extracts provider name correctly."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='oauth-google',
            method_data={}
        )

        assert login_method.oauth_provider_name == 'google'

    def test_login_method_oauth_provider_name_none_for_non_oauth(self):
        """Test oauth_provider_name property returns None for non-OAuth types."""
        login_method = LoginMethod(
            person_id='person-123',
            email_id='email-123',
            method_type='email-password',
            raw_password='Test123!@#'
        )

        assert login_method.oauth_provider_name is None

    def test_login_method_validate_password_too_short(self):
        """Test password validation fails for passwords shorter than 8 characters."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='Test1!'
            )

        assert "at least 8 character long" in str(exc_info.value)

    def test_login_method_validate_password_too_long(self):
        """Test password validation fails for passwords longer than 100 characters."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='A' * 101 + 'a1!'
            )

        assert "at max 100 character long" in str(exc_info.value)

    def test_login_method_validate_password_no_uppercase(self):
        """Test password validation fails without uppercase letter."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='test123!@#'
            )

        assert "uppercase letter" in str(exc_info.value)

    def test_login_method_validate_password_no_lowercase(self):
        """Test password validation fails without lowercase letter."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='TEST123!@#'
            )

        assert "lowercase letter" in str(exc_info.value)

    def test_login_method_validate_password_no_digit(self):
        """Test password validation fails without digit."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='TestPass!@#'
            )

        assert "contain a digit" in str(exc_info.value)

    def test_login_method_validate_password_no_special_char(self):
        """Test password validation fails without special character."""
        with pytest.raises(ModelValidationError) as exc_info:
            LoginMethod(
                person_id='person-123',
                email_id='email-123',
                method_type='email-password',
                raw_password='TestPass123'
            )

        assert "special character" in str(exc_info.value)
