"""
Unit tests for common/services/auth.py
"""
import pytest
import jwt
import time
from unittest.mock import MagicMock, patch, call
from common.helpers.exceptions import InputValidationError, APIException


class TestAuthService:
    """Tests for AuthService."""

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_init(self, mock_sender, mock_por_service, mock_org_service,
                  mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test service initialization."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        service = AuthService(mock_config)

        assert service.config == mock_config
        assert service.EMAIL_TRANSMITTER_QUEUE_NAME == "test_email_queue"

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_success(self, mock_sender, mock_por_service, mock_org_service,
                           mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test successful user signup."""
        from common.services.auth import AuthService
        from common.models import Person, Email, LoginMethod, Organization, PersonOrganizationRole

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"

        # Mock email service to return no existing email
        mock_email_service_instance = MagicMock()
        mock_email_service_instance.get_email_by_email_address.return_value = None
        mock_email_service_instance.save_email.return_value = MagicMock(entity_id="email-id", email="test@example.com")
        mock_email_service.return_value = mock_email_service_instance

        # Mock person service
        mock_person_service_instance = MagicMock()
        mock_person_service_instance.save_person.return_value = MagicMock(
            entity_id="person-id", first_name="John", last_name="Doe"
        )
        mock_person_service.return_value = mock_person_service_instance

        # Mock login method service
        mock_login_service_instance = MagicMock()
        mock_saved_login = MagicMock(spec=['entity_id', 'password', 'person_id', 'email_id'])
        mock_saved_login.entity_id = "login-id"
        mock_saved_login.password = "hashed_password"
        mock_saved_login.person_id = "person-id"
        mock_saved_login.email_id = "email-id"
        mock_login_service_instance.save_login_method.return_value = mock_saved_login
        mock_login_service.return_value = mock_login_service_instance

        # Mock organization service
        mock_org_service_instance = MagicMock()
        mock_org_service.return_value = mock_org_service_instance

        # Mock person organization role service
        mock_por_service_instance = MagicMock()
        mock_por_service.return_value = mock_por_service_instance

        # Mock message sender
        mock_sender_instance = MagicMock()
        mock_sender.return_value = mock_sender_instance

        service = AuthService(mock_config)

        # Call signup
        service.signup("test@example.com", "John", "Doe")

        # Verify services were called
        mock_email_service_instance.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_email_service_instance.save_email.assert_called_once()
        mock_person_service_instance.save_person.assert_called_once()
        mock_login_service_instance.save_login_method.assert_called_once()
        mock_org_service_instance.save_organization.assert_called_once()
        mock_por_service_instance.save_person_organization_role.assert_called_once()

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_existing_email(self, mock_sender, mock_por_service, mock_org_service,
                                   mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test signup with existing email address."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"

        # Mock email service to return existing email
        mock_email_service_instance = MagicMock()
        existing_email = MagicMock(entity_id="existing-email-id")
        mock_email_service_instance.get_email_by_email_address.return_value = existing_email
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service to return non-OAuth method
        mock_login_service_instance = MagicMock()
        existing_login = MagicMock()
        existing_login.is_oauth_method = False
        mock_login_service_instance.get_login_method_by_email_id.return_value = existing_login
        mock_login_service.return_value = mock_login_service_instance

        mock_person_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError, match="already registered"):
            service.signup("test@example.com", "John", "Doe")

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_existing_oauth_email(self, mock_sender, mock_por_service, mock_org_service,
                                         mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test signup with existing OAuth email address."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"

        # Mock email service to return existing email
        mock_email_service_instance = MagicMock()
        existing_email = MagicMock(entity_id="existing-email-id")
        mock_email_service_instance.get_email_by_email_address.return_value = existing_email
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service to return OAuth method
        mock_login_service_instance = MagicMock()
        existing_login = MagicMock()
        existing_login.is_oauth_method = True
        existing_login.oauth_provider_name = "Google"
        mock_login_service_instance.get_login_method_by_email_id.return_value = existing_login
        mock_login_service.return_value = mock_login_service_instance

        mock_person_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError, match="Google"):
            service.signup("test@example.com", "John", "Doe")

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_generate_reset_password_token(self, mock_sender, mock_por_service, mock_org_service,
                                           mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test generating reset password token."""
        from common.services.auth import AuthService
        from common.models import LoginMethod

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
        mock_config.RESET_TOKEN_EXPIRE = "3600"

        mock_email_service.return_value = MagicMock()
        mock_person_service.return_value = MagicMock()
        mock_login_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        login_method = MagicMock()
        login_method.person_id = "person-123"
        login_method.email_id = "email-456"
        login_method.password = "secret_password"

        token = service.generate_reset_password_token(login_method, "test@example.com")

        assert token is not None
        # Verify token can be decoded
        decoded = jwt.decode(token, "secret_password", algorithms=['HS256'])
        assert decoded['email'] == "test@example.com"
        assert decoded['email_id'] == "email-456"
        assert decoded['person_id'] == "person-123"

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.urlsafe_base64_encode')
    def test_prepare_password_reset_url(self, mock_encode, mock_sender, mock_por_service,
                                        mock_org_service, mock_login_service, mock_email_service,
                                        mock_person_service, mock_config):
        """Test preparing password reset URL."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"
        mock_config.RESET_TOKEN_EXPIRE = "3600"
        mock_config.VUE_APP_URI = "http://localhost:3000"

        mock_email_service.return_value = MagicMock()
        mock_person_service.return_value = MagicMock()
        mock_login_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()
        mock_encode.return_value = "encoded_id"

        service = AuthService(mock_config)

        login_method = MagicMock()
        login_method.entity_id = "login-123"
        login_method.person_id = "person-123"
        login_method.email_id = "email-456"
        login_method.password = "secret_password"

        url = service.prepare_password_reset_url(login_method, "test@example.com")

        assert url.startswith("http://localhost:3000/set-password/")
        assert "encoded_id" in url

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_success(self, mock_sender, mock_por_service, mock_org_service,
                                                  mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test successful login with email and password."""
        from common.services.auth import AuthService
        from werkzeug.security import generate_password_hash

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service
        mock_email_service_instance = MagicMock()
        email_obj = MagicMock(entity_id="email-id")
        mock_email_service_instance.get_email_by_email_address.return_value = email_obj
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service
        mock_login_service_instance = MagicMock()
        login_method = MagicMock(
            person_id="person-id",
            is_oauth_method=False,
            password=generate_password_hash("correct_password")
        )
        mock_login_service_instance.get_login_method_by_email_id.return_value = login_method
        mock_login_service.return_value = mock_login_service_instance

        # Mock person service
        mock_person_service_instance = MagicMock()
        person = MagicMock(entity_id="person-id", first_name="John", last_name="Doe")
        mock_person_service_instance.get_person_by_id.return_value = person
        mock_person_service.return_value = mock_person_service_instance

        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with patch('common.services.auth.generate_access_token') as mock_gen_token:
            mock_gen_token.return_value = ("access_token_123", 3600)

            access_token, expiry = service.login_user_by_email_password("test@example.com", "correct_password")

            assert access_token == "access_token_123"
            assert expiry == 3600

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_unregistered_email(self, mock_sender, mock_por_service, mock_org_service,
                                                              mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test login with unregistered email."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service to return None
        mock_email_service_instance = MagicMock()
        mock_email_service_instance.get_email_by_email_address.return_value = None
        mock_email_service.return_value = mock_email_service_instance

        mock_person_service.return_value = MagicMock()
        mock_login_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError, match="not registered"):
            service.login_user_by_email_password("unregistered@example.com", "password")

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_oauth_account(self, mock_sender, mock_por_service, mock_org_service,
                                                         mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test login with OAuth account using email/password."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service
        mock_email_service_instance = MagicMock()
        email_obj = MagicMock(entity_id="email-id")
        mock_email_service_instance.get_email_by_email_address.return_value = email_obj
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service to return OAuth method
        mock_login_service_instance = MagicMock()
        login_method = MagicMock()
        login_method.is_oauth_method = True
        login_method.oauth_provider_name = "Google"
        mock_login_service_instance.get_login_method_by_email_id.return_value = login_method
        mock_login_service.return_value = mock_login_service_instance

        mock_person_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError, match="Google"):
            service.login_user_by_email_password("test@example.com", "password")

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_incorrect_password(self, mock_sender, mock_por_service, mock_org_service,
                                                             mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test login with incorrect password."""
        from common.services.auth import AuthService
        from werkzeug.security import generate_password_hash

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service
        mock_email_service_instance = MagicMock()
        email_obj = MagicMock(entity_id="email-id")
        mock_email_service_instance.get_email_by_email_address.return_value = email_obj
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service
        mock_login_service_instance = MagicMock()
        login_method = MagicMock(
            is_oauth_method=False,
            password=generate_password_hash("correct_password")
        )
        mock_login_service_instance.get_login_method_by_email_id.return_value = login_method
        mock_login_service.return_value = mock_login_service_instance

        mock_person_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with pytest.raises(InputValidationError, match="Incorrect"):
            service.login_user_by_email_password("test@example.com", "wrong_password")

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_oauth_new_user(self, mock_sender, mock_por_service, mock_org_service,
                                          mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test OAuth login for a new user."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service to return no existing email
        mock_email_service_instance = MagicMock()
        mock_email_service_instance.get_email_by_email_address.return_value = None
        mock_email_service_instance.save_email.return_value = MagicMock(
            entity_id="email-id", email="test@example.com", is_verified=True
        )
        mock_email_service.return_value = mock_email_service_instance

        # Mock person service
        mock_person_service_instance = MagicMock()
        person = MagicMock(entity_id="person-id", first_name="John", last_name="Doe")
        mock_person_service_instance.save_person.return_value = person
        mock_person_service.return_value = mock_person_service_instance

        # Mock login method service
        mock_login_service_instance = MagicMock()
        mock_login_service_instance.save_login_method.return_value = MagicMock(entity_id="login-id")
        mock_login_service.return_value = mock_login_service_instance

        mock_org_service_instance = MagicMock()
        mock_org_service.return_value = mock_org_service_instance

        mock_por_service_instance = MagicMock()
        mock_por_service.return_value = mock_por_service_instance

        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with patch('common.services.auth.generate_access_token') as mock_gen_token:
            mock_gen_token.return_value = ("access_token_123", 3600)

            access_token, expiry, returned_person = service.login_user_by_oauth(
                email="test@example.com",
                first_name="John",
                last_name="Doe",
                provider="google",
                provider_data={"sub": "google-123"}
            )

            assert access_token == "access_token_123"
            assert expiry == 3600
            assert returned_person == person

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_oauth_existing_user(self, mock_sender, mock_por_service, mock_org_service,
                                               mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test OAuth login for an existing user."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        # Mock email service to return existing email
        mock_email_service_instance = MagicMock()
        existing_email = MagicMock(entity_id="email-id", person_id="person-id", is_verified=True)
        mock_email_service_instance.get_email_by_email_address.return_value = existing_email
        mock_email_service.return_value = mock_email_service_instance

        # Mock login method service
        mock_login_service_instance = MagicMock()
        login_method = MagicMock(is_oauth_method=True)
        mock_login_service_instance.get_login_method_by_email_id.return_value = login_method
        mock_login_service.return_value = mock_login_service_instance

        # Mock person service
        mock_person_service_instance = MagicMock()
        person = MagicMock(entity_id="person-id", first_name="John", last_name="Doe")
        mock_person_service_instance.get_person_by_id.return_value = person
        mock_person_service.return_value = mock_person_service_instance

        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        service = AuthService(mock_config)

        with patch('common.services.auth.generate_access_token') as mock_gen_token:
            mock_gen_token.return_value = ("access_token_123", 3600)

            access_token, expiry, returned_person = service.login_user_by_oauth(
                email="test@example.com",
                first_name="John",
                last_name="Doe",
                provider="google",
                provider_data={"sub": "google-123"}
            )

            assert access_token == "access_token_123"
            assert expiry == 3600
            assert returned_person == person

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_parse_reset_password_token_valid(self, mock_sender, mock_por_service, mock_org_service,
                                               mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test parsing a valid reset password token."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_email_service.return_value = MagicMock()
        mock_person_service.return_value = MagicMock()
        mock_login_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        login_method = MagicMock()
        login_method.password = "secret_password"

        # Create a valid token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-456',
                'exp': time.time() + 3600
            },
            "secret_password",
            algorithm='HS256'
        )

        result = AuthService.parse_reset_password_token(token, login_method)

        assert result is not None
        assert result['email'] == 'test@example.com'
        assert result['email_id'] == 'email-123'
        assert result['person_id'] == 'person-456'

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_parse_reset_password_token_expired(self, mock_sender, mock_por_service, mock_org_service,
                                                 mock_login_service, mock_email_service, mock_person_service, mock_config):
        """Test parsing an expired reset password token."""
        from common.services.auth import AuthService

        mock_email_service.return_value = MagicMock()
        mock_person_service.return_value = MagicMock()
        mock_login_service.return_value = MagicMock()
        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        login_method = MagicMock()
        login_method.password = "secret_password"

        # Create an expired token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-123',
                'person_id': 'person-456',
                'exp': time.time() - 3600  # Expired 1 hour ago
            },
            "secret_password",
            algorithm='HS256'
        )

        result = AuthService.parse_reset_password_token(token, login_method)

        assert result is None

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.urlsafe_base64_decode')
    def test_reset_user_password_success(self, mock_decode, mock_sender, mock_por_service,
                                         mock_org_service, mock_login_service, mock_email_service,
                                         mock_person_service, mock_config):
        """Test successful password reset."""
        from common.services.auth import AuthService

        mock_config.QUEUE_NAME_PREFIX = "test_"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email_queue"

        mock_decode.return_value = "login-123"

        # Mock login method service
        mock_login_service_instance = MagicMock()
        login_method = MagicMock()
        login_method.entity_id = "login-123"
        login_method.password = "old_hashed_password"
        mock_login_service_instance.get_login_method_by_id.return_value = login_method
        mock_login_service_instance.update_password.return_value = login_method
        mock_login_service.return_value = mock_login_service_instance

        # Mock email service
        mock_email_service_instance = MagicMock()
        email_obj = MagicMock(entity_id="email-id")
        mock_email_service_instance.get_email_by_id.return_value = email_obj
        mock_email_service_instance.verify_email.return_value = email_obj
        mock_email_service.return_value = mock_email_service_instance

        # Mock person service
        mock_person_service_instance = MagicMock()
        person = MagicMock(entity_id="person-id")
        mock_person_service_instance.get_person_by_id.return_value = person
        mock_person_service.return_value = mock_person_service_instance

        mock_org_service.return_value = MagicMock()
        mock_por_service.return_value = MagicMock()
        mock_sender.return_value = MagicMock()

        # Create a valid token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'email_id': 'email-id',
                'person_id': 'person-id',
                'exp': time.time() + 3600
            },
            "old_hashed_password",
            algorithm='HS256'
        )

        service = AuthService(mock_config)

        with patch('common.services.auth.generate_access_token') as mock_gen_token:
            mock_gen_token.return_value = ("access_token_123", 3600)

            access_token, expiry, returned_person = service.reset_user_password(
                token, "encoded_uid", "NewPassword123!"
            )

            assert access_token == "access_token_123"
            assert expiry == 3600
            assert returned_person == person
