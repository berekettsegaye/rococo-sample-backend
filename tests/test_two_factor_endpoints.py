"""
Integration tests for two-factor authentication endpoints.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
import pyotp

from common.models.login_method import LoginMethod
from common.helpers.two_factor import generate_totp_secret, generate_backup_codes, hash_backup_code


# Note: These tests are endpoint unit tests that mock the services rather than full integration tests
# The module paths need to match the actual import paths in the auth views module


class TestTwoFactorSetupEndpoint:
    """Tests for POST /auth/2fa/setup endpoint."""

    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.AuthService')
    @patch('app.views.auth.login_required')
    def test_setup_2fa_success(self, mock_login_required, mock_auth_service_class, mock_person_service_class):
        """Test successful 2FA setup initiation."""
        from app.views.auth import TwoFactorSetup
        from flask import Flask, request

        # Mock the login_required decorator to pass through
        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                # Create a mock person object
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        # Setup mocks
        mock_email = MagicMock()
        mock_email.email = "test@example.com"

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = mock_email
        mock_person_service_class.return_value = mock_person_service

        setup_data = {
            'secret': 'JBSWY3DPEHPK3PXP',
            'qr_code_base64': 'base64_qr_code_data',
            'backup_codes': ['CODE1234', 'CODE5678'],
            'uri': 'otpauth://totp/Test'
        }

        mock_auth_service = MagicMock()
        mock_auth_service.setup_two_factor.return_value = setup_data
        mock_auth_service_class.return_value = mock_auth_service

        # Create test resource
        resource = TwoFactorSetup()

        # Mock person for decorator
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        # Call the endpoint
        result = resource.post(person=mock_person)

        # Verify service was called correctly
        mock_auth_service.setup_two_factor.assert_called_once_with("test@example.com")

        # Verify response
        assert result['status'] == 'success'
        assert 'secret' in result
        assert 'qr_code' in result
        assert 'backup_codes' in result

    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.login_required')
    def test_setup_2fa_no_email_found(self, mock_login_required, mock_person_service_class):
        """Test 2FA setup fails when user email not found."""
        from app.views.auth import TwoFactorSetup

        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = None
        mock_person_service_class.return_value = mock_person_service

        resource = TwoFactorSetup()
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        result = resource.post(person=mock_person)

        assert result['status'] == 'failure'
        assert 'Email not found' in result['message']


class TestTwoFactorVerifyAndEnableEndpoint:
    """Tests for POST /auth/2fa/verify-and-enable endpoint."""

    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.AuthService')
    @patch('app.views.auth.login_required')
    @patch('app.views.auth.request')
    def test_verify_and_enable_success(self, mock_request, mock_login_required,
                                       mock_auth_service_class, mock_person_service_class):
        """Test successful 2FA verification and enablement."""
        from app.views.auth import TwoFactorVerifyAndEnable

        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        # Mock request body
        mock_request.get_json.return_value = {'code': '123456'}

        mock_email = MagicMock()
        mock_email.email = "test@example.com"

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = mock_email
        mock_person_service_class.return_value = mock_person_service

        verify_result = {
            'backup_codes': ['CODE1234', 'CODE5678']
        }

        mock_auth_service = MagicMock()
        mock_auth_service.verify_and_enable_two_factor.return_value = verify_result
        mock_auth_service_class.return_value = mock_auth_service

        resource = TwoFactorVerifyAndEnable()
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        # Note: In actual test, parse_request_body would extract 'code'
        with patch('app.views.auth.parse_request_body') as mock_parse:
            mock_parse.return_value = {'code': '123456'}
            with patch('app.views.auth.validate_required_fields'):
                result = resource.post(person=mock_person)

        assert result['status'] == 'success'
        assert 'backup_codes' in result
        mock_auth_service.verify_and_enable_two_factor.assert_called_once()


class TestTwoFactorDisableEndpoint:
    """Tests for POST /auth/2fa/disable endpoint."""

    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.AuthService')
    @patch('app.views.auth.login_required')
    def test_disable_2fa_success(self, mock_login_required, mock_auth_service_class,
                                 mock_person_service_class):
        """Test successful 2FA disablement."""
        from app.views.auth import TwoFactorDisable

        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        mock_email = MagicMock()
        mock_email.email = "test@example.com"

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = mock_email
        mock_person_service_class.return_value = mock_person_service

        mock_auth_service = MagicMock()
        mock_auth_service.disable_two_factor_for_user.return_value = None
        mock_auth_service_class.return_value = mock_auth_service

        resource = TwoFactorDisable()
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        with patch('app.views.auth.parse_request_body') as mock_parse:
            mock_parse.return_value = {'password': 'ValidPass1!'}
            with patch('app.views.auth.validate_required_fields'):
                result = resource.post(person=mock_person)

        assert result['status'] == 'success'
        mock_auth_service.disable_two_factor_for_user.assert_called_once()


class TestTwoFactorStatusEndpoint:
    """Tests for GET /auth/2fa/status endpoint."""

    @patch('app.views.auth.LoginMethodService')
    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.login_required')
    def test_status_2fa_enabled(self, mock_login_required, mock_person_service_class,
                                mock_login_method_service_class):
        """Test 2FA status when enabled."""
        from app.views.auth import TwoFactorStatus

        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        mock_email = MagicMock()
        mock_email.entity_id = "test-email-id"
        mock_email.email = "test@example.com"

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = mock_email
        mock_person_service_class.return_value = mock_person_service

        mock_login_method = MagicMock()
        mock_login_method.has_two_factor_enabled = True

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        resource = TwoFactorStatus()
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        result = resource.get(person=mock_person)

        assert result['status'] == 'success'
        assert result['two_factor_enabled'] is True

    @patch('app.views.auth.LoginMethodService')
    @patch('app.views.auth.PersonService')
    @patch('app.views.auth.login_required')
    def test_status_2fa_disabled(self, mock_login_required, mock_person_service_class,
                                 mock_login_method_service_class):
        """Test 2FA status when disabled."""
        from app.views.auth import TwoFactorStatus

        def mock_decorator(func=None):
            def wrapper(*args, **kwargs):
                mock_person = MagicMock()
                mock_person.entity_id = "test-person-id"
                return func(*args, person=mock_person, **kwargs)
            return wrapper

        mock_login_required.return_value = mock_decorator

        mock_email = MagicMock()
        mock_email.entity_id = "test-email-id"
        mock_email.email = "test@example.com"

        mock_person_service = MagicMock()
        mock_person_service.get_primary_email_by_person_id.return_value = mock_email
        mock_person_service_class.return_value = mock_person_service

        mock_login_method = MagicMock()
        mock_login_method.has_two_factor_enabled = False

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        resource = TwoFactorStatus()
        mock_person = MagicMock()
        mock_person.entity_id = "test-person-id"

        result = resource.get(person=mock_person)

        assert result['status'] == 'success'
        assert result['two_factor_enabled'] is False


class TestLoginMethodTwoFactorProperties:
    """Tests for LoginMethod 2FA properties and methods."""

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_has_two_factor_enabled_true(self, mock_post_init):
        """Test has_two_factor_enabled returns True when properly configured."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )
        login_method.two_factor_secret = 'JBSWY3DPEHPK3PXP'
        login_method.two_factor_enabled = True

        assert login_method.has_two_factor_enabled is True

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_has_two_factor_enabled_false_when_disabled(self, mock_post_init):
        """Test has_two_factor_enabled returns False when disabled."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )
        login_method.two_factor_secret = 'JBSWY3DPEHPK3PXP'
        login_method.two_factor_enabled = False

        assert login_method.has_two_factor_enabled is False

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_has_two_factor_enabled_false_when_no_secret(self, mock_post_init):
        """Test has_two_factor_enabled returns False when no secret."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )
        login_method.two_factor_secret = None
        login_method.two_factor_enabled = True

        assert login_method.has_two_factor_enabled is False

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_is_backup_code_valid_with_valid_code(self, mock_post_init):
        """Test is_backup_code_valid with a valid unused backup code."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )

        code = 'ABC12345'
        hashed = hash_backup_code(code)

        login_method.two_factor_backup_codes = json.dumps([hashed])
        login_method.two_factor_backup_codes_used = json.dumps([])

        assert login_method.is_backup_code_valid(code) is True

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_is_backup_code_valid_with_used_code(self, mock_post_init):
        """Test is_backup_code_valid returns False for used code."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )

        code = 'ABC12345'
        hashed = hash_backup_code(code)

        login_method.two_factor_backup_codes = json.dumps([hashed])
        login_method.two_factor_backup_codes_used = json.dumps([hashed])

        assert login_method.is_backup_code_valid(code) is False

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_mark_backup_code_used(self, mock_post_init):
        """Test mark_backup_code_used marks code as used."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )

        code = 'ABC12345'
        hashed = hash_backup_code(code)

        login_method.two_factor_backup_codes = json.dumps([hashed])
        login_method.two_factor_backup_codes_used = json.dumps([])

        # Mark as used
        result = login_method.mark_backup_code_used(code)

        assert result is True
        used_codes = json.loads(login_method.two_factor_backup_codes_used)
        assert hashed in used_codes

    @patch('common.models.login_method.BaseLoginMethod.__post_init__')
    def test_mark_backup_code_used_invalid_code(self, mock_post_init):
        """Test mark_backup_code_used returns False for invalid code."""
        login_method = LoginMethod(
            method_type='password',
            raw_password='ValidPass1!'
        )

        code = 'ABC12345'
        hashed = hash_backup_code(code)

        login_method.two_factor_backup_codes = json.dumps([hashed])
        login_method.two_factor_backup_codes_used = json.dumps([])

        # Try to mark invalid code as used
        result = login_method.mark_backup_code_used('INVALID123')

        assert result is False
        used_codes = json.loads(login_method.two_factor_backup_codes_used)
        assert len(used_codes) == 0
