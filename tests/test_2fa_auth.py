"""
Integration tests for 2FA authentication flow
"""
import pytest
from unittest.mock import MagicMock
from common.models import Person, Email, LoginMethod
from common.helpers.totp import generate_totp_secret, get_current_totp_code
from werkzeug.security import generate_password_hash


class TestEnable2FA:
    """Tests for POST /auth/2fa/enable endpoint."""

    def test_enable_2fa_success(self):
        """Test successful 2FA enablement returns secret and QR code."""
        from common.services.totp import TotpService

        # Setup mocks
        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")
        mock_email = Email(entity_id="email-123", person_id="person-123", email="test@example.com")

        # Create service and mock dependencies
        totp_service = TotpService(mock_config)
        totp_service.email_service = MagicMock()
        totp_service.email_service.get_email_by_person_id = MagicMock(return_value=mock_email)

        secret, qr_code, uri = totp_service.enable_2fa(mock_person)

        # Assertions
        assert secret is not None
        assert len(secret) >= 32
        assert qr_code is not None
        assert len(qr_code) > 0
        assert uri.startswith("otpauth://totp/")
        assert "test%40example.com" in uri or "test@example.com" in uri
        totp_service.email_service.get_email_by_person_id.assert_called_once_with("person-123")

    def test_enable_2fa_no_email(self):
        """Test 2FA enablement fails when user has no email."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import APIException

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")

        totp_service = TotpService(mock_config)
        totp_service.email_service = MagicMock()
        totp_service.email_service.get_email_by_person_id = MagicMock(return_value=None)

        with pytest.raises(APIException, match="No email found"):
            totp_service.enable_2fa(mock_person)

    def test_enable_2fa_no_person(self):
        """Test 2FA enablement fails when person is None."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import APIException

        mock_config = MagicMock()
        totp_service = TotpService(mock_config)

        with pytest.raises(APIException, match="Person not found"):
            totp_service.enable_2fa(None)


class TestConfirm2FA:
    """Tests for POST /auth/2fa/confirm endpoint."""

    def test_confirm_2fa_success(self):
        """Test successful 2FA confirmation with valid code."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")
        secret = generate_totp_secret()
        code = get_current_totp_code(secret)

        totp_service = TotpService(mock_config)
        totp_service.person_service = MagicMock()
        totp_service.person_service.save_person = MagicMock(return_value=mock_person)

        result = totp_service.confirm_enable_2fa(mock_person, secret, code)

        assert result.is_2fa_enabled is True
        assert result.totp_secret == secret
        totp_service.person_service.save_person.assert_called_once()

    def test_confirm_2fa_invalid_code(self):
        """Test 2FA confirmation fails with invalid code."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import InputValidationError

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")
        secret = generate_totp_secret()
        invalid_code = "000000"

        totp_service = TotpService(mock_config)

        with pytest.raises(InputValidationError, match="Invalid verification code"):
            totp_service.confirm_enable_2fa(mock_person, secret, invalid_code)

    def test_confirm_2fa_missing_secret(self):
        """Test 2FA confirmation fails when secret is missing."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import InputValidationError

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")

        totp_service = TotpService(mock_config)

        with pytest.raises(InputValidationError, match="Secret and verification code are required"):
            totp_service.confirm_enable_2fa(mock_person, "", "123456")

    def test_confirm_2fa_missing_code(self):
        """Test 2FA confirmation fails when code is missing."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import InputValidationError

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")
        secret = generate_totp_secret()

        totp_service = TotpService(mock_config)

        with pytest.raises(InputValidationError, match="Secret and verification code are required"):
            totp_service.confirm_enable_2fa(mock_person, secret, "")


class TestDisable2FA:
    """Tests for POST /auth/2fa/disable endpoint."""

    def test_disable_2fa_success(self):
        """Test successful 2FA disablement with valid password."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=True,
            totp_secret="TESTSECRET123"
        )
        mock_email = Email(entity_id="email-123", person_id="person-123", email="test@example.com")
        mock_login_method = LoginMethod(
            entity_id="login-123",
            method_type="email-password",
            raw_password="TestPass123!"
        )
        mock_login_method.password = generate_password_hash("TestPass123!")

        totp_service = TotpService(mock_config)
        totp_service.email_service = MagicMock()
        totp_service.email_service.get_email_by_person_id = MagicMock(return_value=mock_email)
        totp_service.login_method_service = MagicMock()
        totp_service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=mock_login_method)
        totp_service.person_service = MagicMock()
        totp_service.person_service.save_person = MagicMock(return_value=mock_person)

        result = totp_service.disable_2fa(mock_person, "TestPass123!")

        assert result.is_2fa_enabled is False
        assert result.totp_secret is None
        totp_service.person_service.save_person.assert_called_once()

    def test_disable_2fa_not_enabled(self):
        """Test disabling 2FA when it's not enabled."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import InputValidationError

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=False
        )

        totp_service = TotpService(mock_config)

        with pytest.raises(InputValidationError, match="2FA is not enabled"):
            totp_service.disable_2fa(mock_person, "password")

    def test_disable_2fa_invalid_password(self):
        """Test 2FA disablement fails with invalid password."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import InputValidationError

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=True,
            totp_secret="TESTSECRET123"
        )
        mock_email = Email(entity_id="email-123", person_id="person-123", email="test@example.com")
        mock_login_method = LoginMethod(
            entity_id="login-123",
            method_type="email-password",
            raw_password="TestPass123!"
        )
        mock_login_method.password = generate_password_hash("TestPass123!")

        totp_service = TotpService(mock_config)
        totp_service.email_service = MagicMock()
        totp_service.email_service.get_email_by_person_id = MagicMock(return_value=mock_email)
        totp_service.login_method_service = MagicMock()
        totp_service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=mock_login_method)

        with pytest.raises(InputValidationError, match="Invalid password"):
            totp_service.disable_2fa(mock_person, "WrongPassword")


class TestVerify2FACode:
    """Tests for verify_2fa_code method."""

    def test_verify_2fa_code_success(self):
        """Test successful TOTP code verification."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        secret = generate_totp_secret()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=True,
            totp_secret=secret
        )

        totp_service = TotpService(mock_config)
        code = get_current_totp_code(secret)
        result = totp_service.verify_2fa_code(mock_person, code)

        assert result is True

    def test_verify_2fa_code_invalid(self):
        """Test TOTP code verification with invalid code."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        secret = generate_totp_secret()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=True,
            totp_secret=secret
        )

        totp_service = TotpService(mock_config)
        result = totp_service.verify_2fa_code(mock_person, "000000")

        assert result is False

    def test_verify_2fa_code_not_enabled(self):
        """Test verification fails when 2FA is not enabled."""
        from common.services.totp import TotpService
        from common.helpers.exceptions import APIException

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=False
        )

        totp_service = TotpService(mock_config)

        with pytest.raises(APIException, match="2FA is not enabled"):
            totp_service.verify_2fa_code(mock_person, "123456")


class TestGet2FAStatus:
    """Tests for GET /auth/2fa/status endpoint."""

    def test_get_2fa_status_enabled(self):
        """Test getting status when 2FA is enabled."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=True,
            totp_secret="TESTSECRET123"
        )

        totp_service = TotpService(mock_config)
        status = totp_service.get_2fa_status(mock_person)

        assert status["is_2fa_enabled"] is True
        assert status["has_totp_secret"] is True

    def test_get_2fa_status_disabled(self):
        """Test getting status when 2FA is disabled."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        mock_person = Person(
            entity_id="person-123",
            first_name="Test",
            last_name="User",
            is_2fa_enabled=False,
            totp_secret=None
        )

        totp_service = TotpService(mock_config)
        status = totp_service.get_2fa_status(mock_person)

        assert status["is_2fa_enabled"] is False
        assert status["has_totp_secret"] is False

    def test_get_2fa_status_no_person(self):
        """Test getting status when person is None."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        totp_service = TotpService(mock_config)
        status = totp_service.get_2fa_status(None)

        assert status["is_2fa_enabled"] is False
        assert status["has_totp_secret"] is False


class TestComplete2FAFlow:
    """Integration tests for complete 2FA workflows."""

    def test_complete_enable_and_disable_flow(self):
        """Test complete flow: enable -> confirm -> disable 2FA."""
        from common.services.totp import TotpService

        mock_config = MagicMock()
        mock_person = Person(entity_id="person-123", first_name="Test", last_name="User")
        mock_email = Email(entity_id="email-123", person_id="person-123", email="test@example.com")
        mock_login_method = LoginMethod(
            entity_id="login-123",
            method_type="email-password",
            raw_password="TestPass123!"
        )
        mock_login_method.password = generate_password_hash("TestPass123!")

        totp_service = TotpService(mock_config)

        # Mock all service dependencies
        totp_service.email_service = MagicMock()
        totp_service.email_service.get_email_by_person_id = MagicMock(return_value=mock_email)
        totp_service.person_service = MagicMock()
        totp_service.person_service.save_person = MagicMock(return_value=mock_person)
        totp_service.login_method_service = MagicMock()
        totp_service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=mock_login_method)

        # Step 1: Enable 2FA
        secret, qr_code, uri = totp_service.enable_2fa(mock_person)
        assert secret is not None
        assert qr_code is not None

        # Step 2: Confirm with valid code
        code = get_current_totp_code(secret)
        confirmed_person = totp_service.confirm_enable_2fa(mock_person, secret, code)
        assert confirmed_person.is_2fa_enabled is True
        assert confirmed_person.totp_secret == secret

        # Step 3: Verify status
        status = totp_service.get_2fa_status(confirmed_person)
        assert status["is_2fa_enabled"] is True
        assert status["has_totp_secret"] is True

        # Step 4: Verify a code
        new_code = get_current_totp_code(secret)
        verify_result = totp_service.verify_2fa_code(confirmed_person, new_code)
        assert verify_result is True

        # Step 5: Disable 2FA
        disabled_person = totp_service.disable_2fa(confirmed_person, "TestPass123!")
        assert disabled_person.is_2fa_enabled is False
        assert disabled_person.totp_secret is None

        # Step 6: Verify status after disable
        status = totp_service.get_2fa_status(disabled_person)
        assert status["is_2fa_enabled"] is False
        assert status["has_totp_secret"] is False
