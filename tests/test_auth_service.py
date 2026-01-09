"""
Unit tests for common/services/auth.py
"""
import pytest
from unittest.mock import MagicMock, patch, call
import time
import jwt


class TestAuthServiceInit:
    """Tests for AuthService initialization."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_init(
        self, mock_person_service, mock_email_service, mock_login_method_service,
        mock_org_service, mock_person_org_role_service, mock_message_sender, mock_config
    ):
        """Test service initialization."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        service = AuthService(mock_config)

        assert service.config == mock_config
        assert service.EMAIL_TRANSMITTER_QUEUE_NAME == "test_email_queue"
        mock_person_service.assert_called_once_with(mock_config)
        mock_email_service.assert_called_once_with(mock_config)
        mock_login_method_service.assert_called_once_with(mock_config)
        mock_org_service.assert_called_once_with(mock_config)
        mock_person_org_role_service.assert_called_once_with(mock_config)
        mock_message_sender.assert_called_once()


class TestAuthServiceSignup:
    """Tests for signup functionality."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_success(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test successful user signup."""
        from common.services.auth import AuthService

        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"
        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Setup service mocks
        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = None
        mock_email_service.save_email.return_value = MagicMock(email="test@example.com")
        mock_email_service_class.return_value = mock_email_service

        mock_person_service = MagicMock()
        mock_person_service.save_person.return_value = MagicMock()
        mock_person_service_class.return_value = mock_person_service

        mock_login_method_service = MagicMock()
        mock_login_method_service.save_login_method.return_value = MagicMock()
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_org_service = MagicMock()
        mock_org_service_class.return_value = mock_org_service

        mock_person_org_role_service = MagicMock()
        mock_person_org_role_service_class.return_value = mock_person_org_role_service

        mock_message_sender = MagicMock()
        mock_message_sender_class.return_value = mock_message_sender

        service = AuthService(mock_config)
        service.signup("test@example.com", "John", "Doe")

        # Verify all services were called
        mock_email_service.save_email.assert_called_once()
        mock_person_service.save_person.assert_called_once()
        mock_login_method_service.save_login_method.assert_called_once()
        mock_org_service.save_organization.assert_called_once()
        mock_person_org_role_service.save_person_organization_role.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_existing_email_with_oauth(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test signup fails when email exists with OAuth."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import InputValidationError

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Setup existing email
        mock_existing_email = MagicMock()
        mock_existing_email.entity_id = "email-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_existing_email
        mock_email_service_class.return_value = mock_email_service

        # Setup OAuth login method
        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = True
        mock_login_method.oauth_provider_name = "Google"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            service.signup("test@example.com", "John", "Doe")

        assert "already registered with Google" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_existing_email_with_password(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test signup fails when email already exists with password."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import InputValidationError

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_existing_email = MagicMock()
        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_existing_email
        mock_email_service_class.return_value = mock_email_service

        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = False

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            service.signup("test@example.com", "John", "Doe")

        assert "already registered" in str(exc_info.value)


class TestAuthServicePasswordReset:
    """Tests for password reset functionality."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_generate_reset_password_token(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test generating password reset token."""
        from common.services.auth import AuthService

        mock_config.RESET_TOKEN_EXPIRE = "3600"
        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_person_service_class.return_value = MagicMock()
        mock_email_service_class.return_value = MagicMock()
        mock_login_method_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        mock_login_method = MagicMock()
        mock_login_method.person_id = "person-123"
        mock_login_method.email_id = "email-123"
        mock_login_method.password = "hashed_password"

        token = service.generate_reset_password_token(mock_login_method, "test@example.com")

        assert token is not None
        assert isinstance(token, str)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.urlsafe_base64_encode')
    @patch('common.services.auth.force_bytes')
    def test_prepare_password_reset_url(
        self, mock_force_bytes, mock_base64_encode,
        mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test preparing password reset URL."""
        from common.services.auth import AuthService

        mock_config.RESET_TOKEN_EXPIRE = "3600"
        mock_config.VUE_APP_URI = "https://app.example.com"
        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_force_bytes.return_value = b"login-method-123"
        mock_base64_encode.return_value = "encoded_uid"

        mock_person_service_class.return_value = MagicMock()
        mock_email_service_class.return_value = MagicMock()
        mock_login_method_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        mock_login_method = MagicMock()
        mock_login_method.entity_id = "login-method-123"
        mock_login_method.person_id = "person-123"
        mock_login_method.email_id = "email-123"
        mock_login_method.password = "hashed_password"

        url = service.prepare_password_reset_url(mock_login_method, "test@example.com")

        assert url is not None
        assert "https://app.example.com/set-password/" in url
        assert "encoded_uid" in url

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_parse_reset_password_token_valid(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test parsing valid reset password token."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_person_service_class.return_value = MagicMock()
        mock_email_service_class.return_value = MagicMock()
        mock_login_method_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_login_method = MagicMock()
        mock_login_method.password = "test_secret"

        # Create a valid token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-123',
                'exp': time.time() + 3600,
            },
            'test_secret',
            algorithm='HS256'
        )

        result = AuthService.parse_reset_password_token(token, mock_login_method)

        assert result is not None
        assert result['email'] == 'test@example.com'
        assert result['email_id'] == 'email-123'
        assert result['person_id'] == 'person-123'

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_parse_reset_password_token_expired(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test parsing expired reset password token."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_person_service_class.return_value = MagicMock()
        mock_email_service_class.return_value = MagicMock()
        mock_login_method_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_login_method = MagicMock()
        mock_login_method.password = "test_secret"

        # Create an expired token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-123',
                'exp': time.time() - 3600,  # Expired 1 hour ago
            },
            'test_secret',
            algorithm='HS256'
        )

        result = AuthService.parse_reset_password_token(token, mock_login_method)

        assert result is None


class TestAuthServiceLogin:
    """Tests for login functionality."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_success(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_check_password, mock_generate_token, mock_config
    ):
        """Test successful login with email and password."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Setup mocks
        mock_email_obj = MagicMock()
        mock_email_obj.entity_id = "email-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email_obj
        mock_email_service_class.return_value = mock_email_service

        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = False
        mock_login_method.password = "hashed_password"
        mock_login_method.person_id = "person-123"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person = MagicMock()
        mock_person_service = MagicMock()
        mock_person_service.get_person_by_id.return_value = mock_person
        mock_person_service_class.return_value = mock_person_service

        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_check_password.return_value = True
        mock_generate_token.return_value = ("access_token", 3600)

        service = AuthService(mock_config)
        token, expiry = service.login_user_by_email_password("test@example.com", "password123")

        assert token == "access_token"
        assert expiry == 3600
        mock_check_password.assert_called_once_with("hashed_password", "password123")

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_email_not_found(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test login fails when email not found."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import InputValidationError

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = None
        mock_email_service_class.return_value = mock_email_service

        mock_person_service_class.return_value = MagicMock()
        mock_login_method_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password123")

        assert "Email is not registered" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_oauth_account(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class, mock_config
    ):
        """Test login fails when trying to use password for OAuth account."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import InputValidationError

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_email_obj = MagicMock()
        mock_email_obj.entity_id = "email-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email_obj
        mock_email_service_class.return_value = mock_email_service

        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = True
        mock_login_method.oauth_provider_name = "Google"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password123")

        assert "created using Google" in str(exc_info.value)

    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_incorrect_password(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_check_password, mock_config
    ):
        """Test login fails with incorrect password."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import InputValidationError

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_email_obj = MagicMock()
        mock_email_obj.entity_id = "email-123"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email_obj
        mock_email_service_class.return_value = mock_email_service

        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = False
        mock_login_method.password = "hashed_password"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_check_password.return_value = False

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "wrong_password")

        assert "Incorrect email or password" in str(exc_info.value)


class TestAuthServiceOAuth:
    """Tests for OAuth login functionality."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_oauth_existing_user(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_generate_token, mock_config
    ):
        """Test OAuth login for existing user."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Setup existing user
        mock_email_obj = MagicMock()
        mock_email_obj.entity_id = "email-123"
        mock_email_obj.person_id = "person-123"
        mock_email_obj.is_verified = True

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = mock_email_obj
        mock_email_service_class.return_value = mock_email_service

        mock_login_method = MagicMock()
        mock_login_method.is_oauth_method = True

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_email_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person = MagicMock()
        mock_person.entity_id = "person-123"
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"

        mock_person_service = MagicMock()
        mock_person_service.get_person_by_id.return_value = mock_person
        mock_person_service_class.return_value = mock_person_service

        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_generate_token.return_value = ("access_token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            "test@example.com", "John", "Doe", "google", {}
        )

        assert token == "access_token"
        assert expiry == 3600
        assert person == mock_person

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_oauth_new_user(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_generate_token, mock_config
    ):
        """Test OAuth login creates new user."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_email_service = MagicMock()
        mock_email_service.get_email_by_email_address.return_value = None
        mock_saved_email = MagicMock()
        mock_email_service.save_email.return_value = mock_saved_email
        mock_email_service_class.return_value = mock_email_service

        mock_saved_person = MagicMock()
        mock_person_service = MagicMock()
        mock_person_service.save_person.return_value = mock_saved_person
        mock_person_service_class.return_value = mock_person_service

        mock_saved_login_method = MagicMock()
        mock_login_method_service = MagicMock()
        mock_login_method_service.save_login_method.return_value = mock_saved_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_org_service = MagicMock()
        mock_org_service_class.return_value = mock_org_service

        mock_person_org_role_service = MagicMock()
        mock_person_org_role_service_class.return_value = mock_person_org_role_service

        mock_message_sender_class.return_value = MagicMock()

        mock_generate_token.return_value = ("access_token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            "newuser@example.com", "Jane", "Smith", "google", {}
        )

        assert token == "access_token"
        assert expiry == 3600
        mock_email_service.save_email.assert_called_once()
        mock_person_service.save_person.assert_called_once()
        mock_login_method_service.save_login_method.assert_called_once()
        mock_org_service.save_organization.assert_called_once()
        mock_person_org_role_service.save_person_organization_role.assert_called_once()


class TestAuthServiceResetPassword:
    """Tests for reset password functionality."""

    @patch('common.services.auth.generate_access_token')
    @patch('common.services.auth.urlsafe_base64_decode')
    @patch('common.services.auth.force_str')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_user_password_success(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_force_str, mock_base64_decode, mock_generate_token, mock_config
    ):
        """Test successful password reset."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_force_str.return_value = "login-method-123"
        mock_base64_decode.return_value = b"login-method-123"

        mock_login_method = MagicMock()
        mock_login_method.password = "old_hashed_password"
        mock_login_method.person_id = "person-123"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_id.return_value = mock_login_method
        mock_login_method_service.update_password.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_email_obj = MagicMock()
        mock_email_service = MagicMock()
        mock_email_service.get_email_by_id.return_value = mock_email_obj
        mock_email_service.verify_email.return_value = mock_email_obj
        mock_email_service_class.return_value = mock_email_service

        mock_person = MagicMock()
        mock_person_service = MagicMock()
        mock_person_service.get_person_by_id.return_value = mock_person
        mock_person_service_class.return_value = mock_person_service

        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        mock_generate_token.return_value = ("access_token", 3600)

        service = AuthService(mock_config)

        # Create a valid token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-123',
                'exp': time.time() + 3600,
            },
            'old_hashed_password',
            algorithm='HS256'
        )

        with patch.object(AuthService, 'parse_reset_password_token') as mock_parse:
            mock_parse.return_value = {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-123'
            }

            access_token, expiry, person = service.reset_user_password(
                token, "encoded_uid", "NewPassword123!"
            )

            assert access_token == "access_token"
            assert expiry == 3600
            mock_login_method_service.update_password.assert_called_once()
            mock_email_service.verify_email.assert_called_once()

    @patch('common.services.auth.urlsafe_base64_decode')
    @patch('common.services.auth.force_str')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_user_password_invalid_token(
        self, mock_person_service_class, mock_email_service_class,
        mock_login_method_service_class, mock_org_service_class,
        mock_person_org_role_service_class, mock_message_sender_class,
        mock_force_str, mock_base64_decode, mock_config
    ):
        """Test password reset with invalid token."""
        from common.services.auth import AuthService
        from common.helpers.exceptions import APIException

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_force_str.return_value = "login-method-123"
        mock_base64_decode.return_value = b"login-method-123"

        mock_login_method = MagicMock()
        mock_login_method.password = "hashed_password"

        mock_login_method_service = MagicMock()
        mock_login_method_service.get_login_method_by_id.return_value = mock_login_method
        mock_login_method_service_class.return_value = mock_login_method_service

        mock_person_service_class.return_value = MagicMock()
        mock_email_service_class.return_value = MagicMock()
        mock_org_service_class.return_value = MagicMock()
        mock_person_org_role_service_class.return_value = MagicMock()
        mock_message_sender_class.return_value = MagicMock()

        service = AuthService(mock_config)

        with patch.object(AuthService, 'parse_reset_password_token') as mock_parse:
            mock_parse.return_value = None

            with pytest.raises(APIException) as exc_info:
                service.reset_user_password("invalid_token", "encoded_uid", "NewPassword123!")

            assert "Invalid reset password token" in str(exc_info.value)
