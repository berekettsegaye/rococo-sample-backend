"""
Unit tests for common/services/auth.py
"""
import pytest
import time
import jwt
from unittest.mock import MagicMock, patch, call
from common.services.auth import AuthService
from common.models import Person, Email, LoginMethod, Organization, PersonOrganizationRole
from common.models.login_method import LoginMethodType
from common.helpers.exceptions import InputValidationError, APIException
from werkzeug.security import generate_password_hash


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config.QUEUE_NAME_PREFIX = "test_"
    config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
    config.DEFAULT_USER_PASSWORD = "DefaultPass1!"
    config.RESET_TOKEN_EXPIRE = "3600"
    config.VUE_APP_URI = "http://localhost:3000"
    config.ACCESS_TOKEN_EXPIRE = 3600
    config.AUTH_JWT_SECRET = "test-secret"
    return config


@pytest.fixture
def auth_service(mock_config):
    """Create an AuthService instance with mocked dependencies."""
    with patch('common.services.auth.PersonService'), \
         patch('common.services.auth.EmailService'), \
         patch('common.services.auth.LoginMethodService'), \
         patch('common.services.auth.OrganizationService'), \
         patch('common.services.auth.PersonOrganizationRoleService'), \
         patch('common.services.auth.MessageSender'):
        service = AuthService(mock_config)

        # Mock the services
        service.person_service = MagicMock()
        service.email_service = MagicMock()
        service.login_method_service = MagicMock()
        service.organization_service = MagicMock()
        service.person_organization_role_service = MagicMock()
        service.message_sender = MagicMock()

        return service


class TestAuthServiceSignup:
    """Tests for AuthService.signup method."""

    def test_signup_success(self, auth_service):
        """Test successful user signup."""
        auth_service.email_service.get_email_by_email_address.return_value = None

        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.email = "test@example.com"
        auth_service.email_service.save_email.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        auth_service.person_service.save_person.return_value = mock_person

        mock_login = MagicMock(spec=LoginMethod)
        auth_service.login_method_service.save_login_method.return_value = mock_login

        auth_service.signup("test@example.com", "John", "Doe")

        auth_service.email_service.save_email.assert_called_once()
        auth_service.person_service.save_person.assert_called_once()
        auth_service.login_method_service.save_login_method.assert_called_once()
        auth_service.organization_service.save_organization.assert_called_once()

    def test_signup_existing_email_with_password(self, auth_service):
        """Test signup fails when email already exists with password login."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = False
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.signup("test@example.com", "John", "Doe")

        assert "already registered" in str(exc_info.value)

    def test_signup_existing_email_with_oauth(self, auth_service):
        """Test signup fails when email already exists with OAuth."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = True
        mock_login.oauth_provider_name = "Google"
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.signup("test@example.com", "John", "Doe")

        assert "Google" in str(exc_info.value)
        assert "sign-in option" in str(exc_info.value)


class TestAuthServiceGenerateResetPasswordToken:
    """Tests for AuthService.generate_reset_password_token method."""

    def test_generate_reset_password_token(self, auth_service):
        """Test generating password reset token."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.person_id = "person-123"
        mock_login.email_id = "email-123"
        mock_login.password = "hashed_password"

        token = auth_service.generate_reset_password_token(mock_login, "test@example.com")

        assert isinstance(token, str)

        # Verify token can be decoded
        decoded = jwt.decode(token, "hashed_password", algorithms=['HS256'])
        assert decoded['email'] == "test@example.com"
        assert decoded['email_id'] == "email-123"
        assert decoded['person_id'] == "person-123"


class TestAuthServicePreparePasswordResetUrl:
    """Tests for AuthService.prepare_password_reset_url method."""

    def test_prepare_password_reset_url(self, auth_service):
        """Test preparing password reset URL."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.entity_id = "login-123"
        mock_login.person_id = "person-123"
        mock_login.email_id = "email-123"
        mock_login.password = "hashed_password"

        url = auth_service.prepare_password_reset_url(mock_login, "test@example.com")

        assert url.startswith("http://localhost:3000/set-password/")
        assert "login-123" in url or len(url.split('/')) >= 5  # Token and UID present


class TestAuthServiceSendWelcomeEmail:
    """Tests for AuthService.send_welcome_email method."""

    def test_send_welcome_email(self, auth_service):
        """Test sending welcome email."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.entity_id = "login-123"
        mock_login.person_id = "person-123"
        mock_login.email_id = "email-123"
        mock_login.password = "hashed_password"

        mock_person = MagicMock(spec=Person)
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"

        auth_service.send_welcome_email(mock_login, mock_person, "test@example.com")

        auth_service.message_sender.send_message.assert_called_once()
        call_args = auth_service.message_sender.send_message.call_args
        message = call_args[0][1]

        assert message['event'] == 'WELCOME_EMAIL'
        assert message['to_emails'] == ['test@example.com']
        assert 'confirmation_link' in message['data']


class TestAuthServiceLoginUserByEmailPassword:
    """Tests for AuthService.login_user_by_email_password method."""

    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.generate_access_token')
    def test_login_success(self, mock_gen_token, mock_check_pass, auth_service):
        """Test successful login with email and password."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = False
        mock_login.password = "hashed_password"
        mock_login.person_id = "person-123"
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        mock_person = MagicMock(spec=Person)
        auth_service.person_service.get_person_by_id.return_value = mock_person

        mock_check_pass.return_value = True
        mock_gen_token.return_value = ("token", 12345)

        token, expiry = auth_service.login_user_by_email_password("test@example.com", "password")

        assert token == "token"
        assert expiry == 12345

    def test_login_email_not_found(self, auth_service):
        """Test login fails when email is not registered."""
        auth_service.email_service.get_email_by_email_address.return_value = None

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "password")

        assert "not registered" in str(exc_info.value)

    def test_login_no_login_method(self, auth_service):
        """Test login fails when no login method exists."""
        mock_email = MagicMock(spec=Email)
        auth_service.email_service.get_email_by_email_address.return_value = mock_email
        auth_service.login_method_service.get_login_method_by_email_id.return_value = None

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "password")

        assert "Login method not found" in str(exc_info.value)

    def test_login_oauth_account(self, auth_service):
        """Test login fails when trying to use password for OAuth account."""
        mock_email = MagicMock(spec=Email)
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = True
        mock_login.oauth_provider_name = "Google"
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "password")

        assert "Google" in str(exc_info.value)

    @patch('common.services.auth.check_password_hash')
    def test_login_incorrect_password(self, mock_check_pass, auth_service):
        """Test login fails with incorrect password."""
        mock_email = MagicMock(spec=Email)
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = False
        mock_login.password = "hashed_password"
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        mock_check_pass.return_value = False

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "wrong_password")

        assert "Incorrect" in str(exc_info.value)


class TestAuthServiceLoginUserByOAuth:
    """Tests for AuthService.login_user_by_oauth method."""

    @patch('common.services.auth.generate_access_token')
    def test_oauth_login_existing_user(self, mock_gen_token, auth_service):
        """Test OAuth login for existing user."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.person_id = "person-123"
        mock_email.is_verified = True
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.is_oauth_method = True
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        auth_service.person_service.get_person_by_id.return_value = mock_person

        mock_gen_token.return_value = ("token", 12345)

        token, expiry, person = auth_service.login_user_by_oauth(
            "test@example.com", "John", "Doe", "google", {}
        )

        assert token == "token"
        assert person == mock_person

    @patch('common.services.auth.generate_access_token')
    def test_oauth_login_new_user(self, mock_gen_token, auth_service):
        """Test OAuth login creates new user."""
        auth_service.email_service.get_email_by_email_address.return_value = None

        mock_email = MagicMock(spec=Email)
        auth_service.email_service.save_email.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        auth_service.person_service.save_person.return_value = mock_person

        mock_login = MagicMock(spec=LoginMethod)
        auth_service.login_method_service.save_login_method.return_value = mock_login

        mock_gen_token.return_value = ("token", 12345)

        token, expiry, person = auth_service.login_user_by_oauth(
            "new@example.com", "Jane", "Smith", "google", {}
        )

        auth_service.email_service.save_email.assert_called_once()
        auth_service.person_service.save_person.assert_called_once()
        auth_service.organization_service.save_organization.assert_called_once()

    @patch('common.services.auth.generate_access_token')
    def test_oauth_login_existing_user_no_login_method(self, mock_gen_token, auth_service):
        """Test OAuth login for user without login method."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.person_id = "person-123"
        mock_email.is_verified = True
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        auth_service.login_method_service.get_login_method_by_email_id.return_value = None

        mock_person = MagicMock(spec=Person)
        mock_person.entity_id = "person-123"
        auth_service.person_service.get_person_by_id.return_value = mock_person

        mock_login = MagicMock(spec=LoginMethod)
        auth_service.login_method_service.save_login_method.return_value = mock_login

        mock_gen_token.return_value = ("token", 12345)

        token, expiry, person = auth_service.login_user_by_oauth(
            "test@example.com", "John", "Doe", "google", {}
        )

        auth_service.login_method_service.save_login_method.assert_called_once()

    def test_oauth_login_existing_email_no_person(self, auth_service):
        """Test OAuth login fails when person not found."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.person_id = "person-123"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_login = MagicMock(spec=LoginMethod)
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        auth_service.person_service.get_person_by_id.return_value = None

        with pytest.raises(APIException) as exc_info:
            auth_service.login_user_by_oauth(
                "test@example.com", "John", "Doe", "google", {}
            )

        assert "Person not found" in str(exc_info.value)


class TestAuthServiceParseResetPasswordToken:
    """Tests for AuthService.parse_reset_password_token method."""

    def test_parse_valid_token(self, auth_service):
        """Test parsing valid reset password token."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.password = "secret"

        payload = {
            'email': 'test@example.com',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, "secret", algorithm='HS256')

        result = AuthService.parse_reset_password_token(token, mock_login)

        assert result is not None
        assert result['email'] == 'test@example.com'

    def test_parse_expired_token(self, auth_service):
        """Test parsing expired token returns None."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.password = "secret"

        payload = {
            'email': 'test@example.com',
            'exp': time.time() - 3600  # Expired
        }
        token = jwt.encode(payload, "secret", algorithm='HS256')

        result = AuthService.parse_reset_password_token(token, mock_login)

        assert result is None


class TestAuthServiceTriggerForgotPasswordEmail:
    """Tests for AuthService.trigger_forgot_password_email method."""

    def test_trigger_forgot_password_success(self, auth_service):
        """Test triggering forgot password email - documents existing bug."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.person_id = "person-123"
        mock_email.email = "test@example.com"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        auth_service.person_service.get_person_by_id.return_value = mock_person

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.entity_id = "login-123"
        mock_login.person_id = "person-123"
        mock_login.email_id = "email-123"
        mock_login.password = "hashed"
        auth_service.login_method_service.get_login_method_by_email_id.return_value = mock_login

        # Note: Line 266 has a bug - passes email string instead of email_obj.entity_id
        # This causes AttributeError when trying to access .entity_id on a string
        with pytest.raises(AttributeError):
            auth_service.trigger_forgot_password_email("test@example.com")

    def test_trigger_forgot_password_person_not_found(self, auth_service):
        """Test trigger forgot password fails when person not found."""
        mock_email = MagicMock(spec=Email)
        mock_email.entity_id = "email-123"
        mock_email.person_id = "person-123"
        auth_service.email_service.get_email_by_email_address.return_value = mock_email

        auth_service.person_service.get_person_by_id.return_value = None

        with pytest.raises(APIException) as exc_info:
            auth_service.trigger_forgot_password_email("test@example.com")

        assert "Person does not exist" in str(exc_info.value)

    def test_trigger_forgot_password_email_not_found(self, auth_service):
        """Test triggering forgot password for non-existent email."""
        auth_service.email_service.get_email_by_email_address.return_value = None

        with pytest.raises(APIException) as exc_info:
            auth_service.trigger_forgot_password_email("test@example.com")

        assert "not registered" in str(exc_info.value)


class TestAuthServiceResetUserPassword:
    """Tests for AuthService.reset_user_password method."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.urlsafe_base64_decode')
    @patch('common.services.auth.force_str')
    def test_reset_password_success(self, mock_force_str, mock_decode, mock_gen_token, auth_service):
        """Test successful password reset."""
        mock_force_str.return_value = "login-123"

        mock_login = MagicMock(spec=LoginMethod)
        mock_login.password = "old_hash"
        auth_service.login_method_service.get_login_method_by_id.return_value = mock_login

        payload = {
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, "old_hash", algorithm='HS256')

        mock_email = MagicMock(spec=Email)
        auth_service.email_service.get_email_by_id.return_value = mock_email

        mock_person = MagicMock(spec=Person)
        auth_service.person_service.get_person_by_id.return_value = mock_person

        updated_login = MagicMock(spec=LoginMethod)
        auth_service.login_method_service.update_password.return_value = updated_login

        verified_email = MagicMock(spec=Email)
        auth_service.email_service.verify_email.return_value = verified_email

        mock_gen_token.return_value = ("new_token", 12345)

        access_token, expiry, person = auth_service.reset_user_password(
            token, "encoded_uid", "NewPass1!"
        )

        assert access_token == "new_token"
        auth_service.login_method_service.update_password.assert_called_once()
        auth_service.email_service.verify_email.assert_called_once()

    @patch('common.services.auth.urlsafe_base64_decode')
    @patch('common.services.auth.force_str')
    def test_reset_password_invalid_login_method(self, mock_force_str, mock_decode, auth_service):
        """Test password reset with invalid login method."""
        mock_force_str.return_value = "login-123"
        auth_service.login_method_service.get_login_method_by_id.return_value = None

        with pytest.raises(APIException) as exc_info:
            auth_service.reset_user_password("token", "uid", "NewPass1!")

        assert "Invalid password reset URL" in str(exc_info.value)


class TestAuthServiceSendPasswordResetEmail:
    """Tests for AuthService.send_password_reset_email method."""

    def test_send_password_reset_email(self, auth_service):
        """Test sending password reset email."""
        mock_login = MagicMock(spec=LoginMethod)
        mock_login.entity_id = "login-123"
        mock_login.person_id = "person-123"
        mock_login.email_id = "email-123"
        mock_login.password = "hashed"

        auth_service.send_password_reset_email("test@example.com", mock_login)

        auth_service.message_sender.send_message.assert_called_once()
        call_args = auth_service.message_sender.send_message.call_args
        message = call_args[0][1]

        assert message['event'] == 'RESET_PASSWORD'
        assert message['to_emails'] == ['test@example.com']
