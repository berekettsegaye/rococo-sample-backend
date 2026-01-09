"""
Unit tests for common/services/auth.py
"""
import time
import jwt
import pytest
from unittest.mock import MagicMock, patch, call
from common.services.auth import AuthService
from common.models import Person, Email, LoginMethod, Organization, PersonOrganizationRole
from common.models.login_method import LoginMethodType
from common.helpers.exceptions import InputValidationError, APIException


class TestAuthServiceInitialization:
    """Tests for AuthService initialization."""

    def test_init_creates_all_services(self, mock_config):
        """Test that __init__ creates all required service instances."""
        with patch('common.services.auth.PersonService'), \
             patch('common.services.auth.EmailService'), \
             patch('common.services.auth.LoginMethodService'), \
             patch('common.services.auth.OrganizationService'), \
             patch('common.services.auth.PersonOrganizationRoleService'), \
             patch('common.services.auth.MessageSender'):

            auth_service = AuthService(mock_config)

            assert auth_service.config == mock_config
            assert auth_service.person_service is not None
            assert auth_service.email_service is not None
            assert auth_service.login_method_service is not None
            assert auth_service.organization_service is not None
            assert auth_service.person_organization_role_service is not None
            assert auth_service.message_sender is not None


class TestSignup:
    """Tests for signup method."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_success(self, mock_person_service_class, mock_email_service_class,
                           mock_login_method_service_class, mock_org_service_class,
                           mock_por_service_class, mock_message_sender_class, mock_config):
        """Test successful user signup."""
        # Setup mocks
        mock_email_service = mock_email_service_class.return_value
        mock_email_service.get_email_by_email_address.return_value = None
        mock_email_service.save_email.return_value = MagicMock(email="test@example.com", entity_id="email-123")

        mock_person_service = mock_person_service_class.return_value
        mock_person_service.save_person.return_value = MagicMock(entity_id="person-123", first_name="John", last_name="Doe")

        mock_login_method_service = mock_login_method_service_class.return_value
        mock_login_method_service.save_login_method.return_value = MagicMock(entity_id="login-123")

        auth_service = AuthService(mock_config)

        # Execute
        auth_service.signup("test@example.com", "John", "Doe")

        # Verify
        mock_email_service.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_email_service.save_email.assert_called_once()
        mock_person_service.save_person.assert_called_once()
        mock_login_method_service.save_login_method.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_with_existing_email(self, mock_person_service_class, mock_email_service_class,
                                       mock_login_method_service_class, mock_org_service_class,
                                       mock_por_service_class, mock_message_sender_class, mock_config):
        """Test signup with already registered email."""
        # Setup mocks
        mock_email_service = mock_email_service_class.return_value
        existing_email = MagicMock(entity_id="email-123", email="test@example.com")
        mock_email_service.get_email_by_email_address.return_value = existing_email

        mock_login_method_service = mock_login_method_service_class.return_value
        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = False
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method

        auth_service = AuthService(mock_config)

        # Execute and verify exception
        with pytest.raises(InputValidationError) as exc_info:
            auth_service.signup("test@example.com", "John", "Doe")

        assert "already registered" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_with_oauth_existing_email(self, mock_person_service_class, mock_email_service_class,
                                             mock_login_method_service_class, mock_org_service_class,
                                             mock_por_service_class, mock_message_sender_class, mock_config):
        """Test signup when email is already registered with OAuth."""
        # Setup mocks
        mock_email_service = mock_email_service_class.return_value
        existing_email = MagicMock(entity_id="email-123", email="test@example.com")
        mock_email_service.get_email_by_email_address.return_value = existing_email

        mock_login_method_service = mock_login_method_service_class.return_value
        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = True
        mock_login_method.oauth_provider_name = "google"
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method

        auth_service = AuthService(mock_config)

        # Execute and verify exception
        with pytest.raises(InputValidationError) as exc_info:
            auth_service.signup("test@example.com", "John", "Doe")

        assert "google" in str(exc_info.value).lower()


class TestLoginUserByEmailPassword:
    """Tests for login_user_by_email_password method."""

    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_success(self, mock_person_service_class, mock_email_service_class,
                          mock_login_method_service_class, mock_org_service_class,
                          mock_por_service_class, mock_message_sender_class,
                          mock_generate_token, mock_check_password, mock_config):
        """Test successful login."""
        # Setup mocks
        mock_email_service = mock_email_service_class.return_value
        email_obj = MagicMock(entity_id="email-123", email="test@example.com")
        mock_email_service.get_email_by_email_address.return_value = email_obj

        mock_login_method_service = mock_login_method_service_class.return_value
        login_method = MagicMock()
        login_method.is_oauth_method = False
        login_method.password = "hashed_password"
        login_method.person_id = "person-123"
        mock_login_method_service.get_login_method_by_email_id.return_value = login_method

        mock_person_service = mock_person_service_class.return_value
        person = MagicMock(entity_id="person-123", first_name="John", last_name="Doe")
        mock_person_service.get_person_by_id.return_value = person

        mock_check_password.return_value = True
        mock_generate_token.return_value = ("access_token", 1234567890)

        auth_service = AuthService(mock_config)

        # Execute
        token, expiry = auth_service.login_user_by_email_password("test@example.com", "password")  # NOSONAR - Test data

        # Verify
        assert token == "access_token"
        assert expiry == 1234567890
        mock_check_password.assert_called_once_with("hashed_password", "password")  # NOSONAR - Test data

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_email_not_registered(self, mock_person_service_class, mock_email_service_class,
                                       mock_login_method_service_class, mock_org_service_class,
                                       mock_por_service_class, mock_message_sender_class, mock_config):
        """Test login with unregistered email."""
        mock_email_service = mock_email_service_class.return_value
        mock_email_service.get_email_by_email_address.return_value = None

        auth_service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "password")  # NOSONAR - Test data

        assert "not registered" in str(exc_info.value)

    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_incorrect_password(self, mock_person_service_class, mock_email_service_class,
                                     mock_login_method_service_class, mock_org_service_class,
                                     mock_por_service_class, mock_message_sender_class,
                                     mock_check_password, mock_config):
        """Test login with incorrect password."""
        mock_email_service = mock_email_service_class.return_value
        email_obj = MagicMock(entity_id="email-123")
        mock_email_service.get_email_by_email_address.return_value = email_obj

        mock_login_method_service = mock_login_method_service_class.return_value
        login_method = MagicMock()
        login_method.is_oauth_method = False
        login_method.password = "hashed_password"
        mock_login_method_service.get_login_method_by_email_id.return_value = login_method

        mock_check_password.return_value = False

        auth_service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "wrong_password")  # NOSONAR - Test data

        assert "Incorrect" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_with_oauth_account(self, mock_person_service_class, mock_email_service_class,
                                      mock_login_method_service_class, mock_org_service_class,
                                      mock_por_service_class, mock_message_sender_class, mock_config):
        """Test login attempt on OAuth account."""
        mock_email_service = mock_email_service_class.return_value
        email_obj = MagicMock(entity_id="email-123")
        mock_email_service.get_email_by_email_address.return_value = email_obj

        mock_login_method_service = mock_login_method_service_class.return_value
        login_method = MagicMock()
        login_method.is_oauth_method = True
        login_method.oauth_provider_name = "google"
        mock_login_method_service.get_login_method_by_email_id.return_value = login_method

        auth_service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            auth_service.login_user_by_email_password("test@example.com", "password")  # NOSONAR - Test data

        assert "google" in str(exc_info.value).lower()


class TestGenerateResetPasswordToken:
    """Tests for generate_reset_password_token method."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_generate_reset_token(self, mock_person_service_class, mock_email_service_class,
                                  mock_login_method_service_class, mock_org_service_class,
                                  mock_por_service_class, mock_message_sender_class, mock_config):
        """Test generating password reset token."""
        auth_service = AuthService(mock_config)

        login_method = MagicMock()
        login_method.person_id = "person-123"
        login_method.email_id = "email-123"
        login_method.password = "hashed_password"

        token = auth_service.generate_reset_password_token(login_method, "test@example.com")

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify token
        decoded = jwt.decode(token, "hashed_password", algorithms=['HS256'])
        assert decoded['email'] == "test@example.com"
        assert decoded['email_id'] == "email-123"
        assert decoded['person_id'] == "person-123"
        assert 'exp' in decoded


class TestParseResetPasswordToken:
    """Tests for parse_reset_password_token method."""

    def test_parse_valid_token(self):
        """Test parsing a valid reset token."""
        login_method = MagicMock()
        login_method.password = "secret_key"

        # Create a valid token
        payload = {
            'email': 'test@example.com',
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, "secret_key", algorithm='HS256')

        result = AuthService.parse_reset_password_token(token, login_method)

        assert result is not None
        assert result['email'] == 'test@example.com'

    def test_parse_expired_token(self):
        """Test parsing an expired token."""
        login_method = MagicMock()
        login_method.password = "secret_key"

        # Create an expired token
        payload = {
            'email': 'test@example.com',
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': time.time() - 3600  # Expired
        }
        token = jwt.encode(payload, "secret_key", algorithm='HS256')

        result = AuthService.parse_reset_password_token(token, login_method)

        assert result is None


class TestLoginUserByOAuth:
    """Tests for login_user_by_oauth method."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_oauth_login_existing_user(self, mock_person_service_class, mock_email_service_class,
                                      mock_login_method_service_class, mock_org_service_class,
                                      mock_por_service_class, mock_message_sender_class,
                                      mock_generate_token, mock_config):
        """Test OAuth login for existing user."""
        mock_email_service = mock_email_service_class.return_value
        existing_email = MagicMock(entity_id="email-123", person_id="person-123", is_verified=True)
        mock_email_service.get_email_by_email_address.return_value = existing_email

        mock_person_service = mock_person_service_class.return_value
        person = MagicMock(entity_id="person-123", first_name="John", last_name="Doe")
        mock_person_service.get_person_by_id.return_value = person

        mock_login_method_service = mock_login_method_service_class.return_value
        login_method = MagicMock()
        login_method.is_oauth_method = True
        mock_login_method_service.get_login_method_by_email_id.return_value = login_method

        mock_generate_token.return_value = ("access_token", 1234567890)

        auth_service = AuthService(mock_config)

        token, expiry, returned_person = auth_service.login_user_by_oauth(
            "test@example.com", "John", "Doe", "google", {"sub": "123"}
        )

        assert token == "access_token"
        assert expiry == 1234567890
        assert returned_person == person

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_oauth_login_new_user(self, mock_person_service_class, mock_email_service_class,
                                 mock_login_method_service_class, mock_org_service_class,
                                 mock_por_service_class, mock_message_sender_class,
                                 mock_generate_token, mock_config):
        """Test OAuth login for new user creation."""
        mock_email_service = mock_email_service_class.return_value
        mock_email_service.get_email_by_email_address.return_value = None
        mock_email_service.save_email.return_value = MagicMock(entity_id="email-123", email="test@example.com")

        mock_person_service = mock_person_service_class.return_value
        mock_person_service.save_person.return_value = MagicMock(entity_id="person-123", first_name="John", last_name="Doe")

        mock_login_method_service = mock_login_method_service_class.return_value
        mock_login_method_service.save_login_method.return_value = MagicMock(entity_id="login-123")

        mock_generate_token.return_value = ("access_token", 1234567890)

        auth_service = AuthService(mock_config)

        token, expiry, person = auth_service.login_user_by_oauth(
            "test@example.com", "John", "Doe", "google", {"sub": "123"}
        )

        assert token == "access_token"
        mock_email_service.save_email.assert_called_once()
        mock_person_service.save_person.assert_called_once()


class TestResetUserPassword:
    """Tests for reset_user_password method."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_password_success(self, mock_person_service_class, mock_email_service_class,
                                    mock_login_method_service_class, mock_org_service_class,
                                    mock_por_service_class, mock_message_sender_class,
                                    mock_generate_token, mock_config):
        """Test successful password reset."""
        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes

        mock_login_method_service = mock_login_method_service_class.return_value
        login_method = MagicMock()
        login_method.entity_id = "login-123"
        login_method.person_id = "person-123"
        login_method.email_id = "email-123"
        login_method.password = "old_hashed_password"
        mock_login_method_service.get_login_method_by_id.return_value = login_method
        mock_login_method_service.update_password.return_value = login_method

        mock_email_service = mock_email_service_class.return_value
        email_obj = MagicMock(entity_id="email-123")
        mock_email_service.get_email_by_id.return_value = email_obj
        mock_email_service.verify_email.return_value = email_obj

        mock_person_service = mock_person_service_class.return_value
        person_obj = MagicMock(entity_id="person-123")
        mock_person_service.get_person_by_id.return_value = person_obj

        mock_generate_token.return_value = ("new_token", 1234567890)

        auth_service = AuthService(mock_config)

        # Create a valid token
        payload = {
            'email': 'test@example.com',
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, "old_hashed_password", algorithm='HS256')
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        access_token, expiry, person = auth_service.reset_user_password(token, uidb64, "NewPassword1!")  # NOSONAR - Test data

        assert access_token == "new_token"
        assert expiry == 1234567890
        mock_login_method_service.update_password.assert_called_once()
        mock_email_service.verify_email.assert_called_once()
