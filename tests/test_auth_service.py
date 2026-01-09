"""
Unit tests for the AuthService.
"""
import pytest
import time
import jwt
from unittest.mock import MagicMock, patch
from common.services.auth import AuthService
from common.models import Person, Email, LoginMethod, Organization, PersonOrganizationRole
from common.models.login_method import LoginMethodType
from common.helpers.exceptions import InputValidationError, APIException


class TestAuthService:
    """Test AuthService methods."""

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_auth_service_init(self, mock_person_svc, mock_email_svc, mock_login_svc,
                                mock_org_svc, mock_role_svc, mock_msg_sender):
        """Test AuthService initialization."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = "test-"
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        service = AuthService(mock_config)

        assert service.config == mock_config
        assert service.EMAIL_TRANSMITTER_QUEUE_NAME == "test-email-queue"
        mock_person_svc.assert_called_once_with(mock_config)
        mock_email_svc.assert_called_once_with(mock_config)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_new_user_success(self, mock_person_svc_class, mock_email_svc_class,
                                      mock_login_svc_class, mock_org_svc_class,
                                      mock_role_svc_class, mock_msg_sender_class):
        """Test signup with new user (success case)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"  # NOSONAR

        # Setup mock services
        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()
        mock_org_svc = MagicMock()
        mock_role_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc
        mock_org_svc_class.return_value = mock_org_svc
        mock_role_svc_class.return_value = mock_role_svc

        # Email doesn't exist yet
        mock_email_svc.get_email_by_email_address.return_value = None

        # Mock saved entities
        saved_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        saved_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        saved_login = LoginMethod(entity_id="login-123", email_id="email-123", person_id="person-123")

        mock_email_svc.save_email.return_value = saved_email
        mock_person_svc.save_person.return_value = saved_person
        mock_login_svc.save_login_method.return_value = saved_login

        service = AuthService(mock_config)
        service.signup("test@example.com", "John", "Doe")

        mock_email_svc.get_email_by_email_address.assert_called_once_with("test@example.com")
        mock_email_svc.save_email.assert_called_once()
        mock_person_svc.save_person.assert_called_once()
        mock_login_svc.save_login_method.assert_called_once()
        mock_org_svc.save_organization.assert_called_once()
        mock_role_svc.save_person_organization_role.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_existing_email_oauth(self, mock_person_svc_class, mock_email_svc_class,
                                          mock_login_svc_class, mock_org_svc_class,
                                          mock_role_svc_class, mock_msg_sender_class):
        """Test signup with existing email (OAuth conflict case)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"  # NOSONAR

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        # Email exists
        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        mock_email_svc.get_email_by_email_address.return_value = existing_email

        # Login method is OAuth
        oauth_login = LoginMethod(
            entity_id="login-123",
            method_type="oauth-google",
            email_id="email-123",
            person_id="person-123"
        )
        mock_login_svc.get_login_method_by_email_id.return_value = oauth_login

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.signup("test@example.com", "John", "Doe")

        assert "already registered with" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_signup_existing_email_non_oauth(self, mock_person_svc_class, mock_email_svc_class,
                                               mock_login_svc_class, mock_org_svc_class,
                                               mock_role_svc_class, mock_msg_sender_class):
        """Test signup with existing email (non-OAuth case)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.DEFAULT_USER_PASSWORD = "DefaultPass123!"  # NOSONAR

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        # Email exists
        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        mock_email_svc.get_email_by_email_address.return_value = existing_email

        # Login method is NOT OAuth
        local_login = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123"
        )
        mock_login_svc.get_login_method_by_email_id.return_value = local_login

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.signup("test@example.com", "John", "Doe")

        assert "already registered" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_email_password_success(self, mock_gen_token, mock_check_hash,
                                                   mock_person_svc_class, mock_email_svc_class,
                                                   mock_login_svc_class, mock_org_svc_class,
                                                   mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password with valid credentials."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        person_obj = Person(entity_id="person-123", first_name="John", last_name="Doe")
        login_method = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123",
            password="hashed_password"  # NOSONAR
        )

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = login_method
        mock_person_svc.get_person_by_id.return_value = person_obj
        mock_check_hash.return_value = True
        mock_gen_token.return_value = ("test-token", 3600)

        service = AuthService(mock_config)
        token, expiry = service.login_user_by_email_password("test@example.com", "password123")  # NOSONAR

        assert token == "test-token"
        assert expiry == 3600
        mock_check_hash.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_invalid_email(self, mock_person_svc_class, mock_email_svc_class,
                                                          mock_login_svc_class, mock_org_svc_class,
                                                          mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password with invalid email."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_email_svc_class.return_value = mock_email_svc

        mock_email_svc.get_email_by_email_address.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("nonexistent@example.com", "password")  # NOSONAR

        assert "not registered" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.check_password_hash')
    def test_login_user_by_email_password_incorrect_password(self, mock_check_hash,
                                                              mock_person_svc_class, mock_email_svc_class,
                                                              mock_login_svc_class, mock_org_svc_class,
                                                              mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password with incorrect password."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        login_method = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123",
            password="hashed_password"  # NOSONAR
        )

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = login_method
        mock_check_hash.return_value = False

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "wrongpassword")  # NOSONAR

        assert "Incorrect" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_oauth_account(self, mock_person_svc_class, mock_email_svc_class,
                                                          mock_login_svc_class, mock_org_svc_class,
                                                          mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password on OAuth account (should fail)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        oauth_login = LoginMethod(
            entity_id="login-123",
            method_type="oauth-google",
            email_id="email-123",
            person_id="person-123"
        )

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = oauth_login

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password")  # NOSONAR

        assert "OAuth" in str(exc_info.value) or "created using" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_no_password_set(self, mock_person_svc_class, mock_email_svc_class,
                                                            mock_login_svc_class, mock_org_svc_class,
                                                            mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password with no password set."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        login_method = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123",
            password=None
        )

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = login_method

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password")  # NOSONAR

        assert "password" in str(exc_info.value).lower()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_new_user(self, mock_gen_token, mock_person_svc_class,
                                           mock_email_svc_class, mock_login_svc_class,
                                           mock_org_svc_class, mock_role_svc_class,
                                           mock_msg_sender_class):
        """Test login_user_by_oauth for new user (Google)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()
        mock_org_svc = MagicMock()
        mock_role_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc
        mock_org_svc_class.return_value = mock_org_svc
        mock_role_svc_class.return_value = mock_role_svc

        # Email doesn't exist
        mock_email_svc.get_email_by_email_address.return_value = None

        saved_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=True)
        saved_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        saved_login = LoginMethod(entity_id="login-123", method_type="oauth-google", email_id="email-123", person_id="person-123")

        mock_email_svc.save_email.return_value = saved_email
        mock_person_svc.save_person.return_value = saved_person
        mock_login_svc.save_login_method.return_value = saved_login
        mock_gen_token.return_value = ("test-token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            provider="google",
            provider_data={"sub": "123456"}
        )

        assert token == "test-token"
        assert expiry == 3600
        assert person.entity_id == "person-123"
        mock_email_svc.save_email.assert_called_once()
        mock_person_svc.save_person.assert_called_once()
        mock_login_svc.save_login_method.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_existing_user(self, mock_gen_token, mock_person_svc_class,
                                                 mock_email_svc_class, mock_login_svc_class,
                                                 mock_org_svc_class, mock_role_svc_class,
                                                 mock_msg_sender_class):
        """Test login_user_by_oauth for existing user (Microsoft)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        # Email exists
        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=True)
        existing_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        existing_login = LoginMethod(entity_id="login-123", method_type="oauth-microsoft", email_id="email-123", person_id="person-123")

        mock_email_svc.get_email_by_email_address.return_value = existing_email
        mock_person_svc.get_person_by_id.return_value = existing_person
        mock_login_svc.get_login_method_by_email_id.return_value = existing_login
        mock_gen_token.return_value = ("test-token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            provider="microsoft",
            provider_data={"id": "ms-123"}
        )

        assert token == "test-token"
        assert expiry == 3600
        assert person.entity_id == "person-123"
        # Should not create new user
        mock_email_svc.save_email.assert_not_called()
        mock_person_svc.save_person.assert_not_called()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_existing_user_no_login_method(self, mock_gen_token,
                                                                 mock_person_svc_class,
                                                                 mock_email_svc_class,
                                                                 mock_login_svc_class,
                                                                 mock_org_svc_class,
                                                                 mock_role_svc_class,
                                                                 mock_msg_sender_class):
        """Test login_user_by_oauth for existing user without login_method (edge case)."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=True)
        existing_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        new_login = LoginMethod(entity_id="login-123", method_type="oauth-google", email_id="email-123", person_id="person-123")

        mock_email_svc.get_email_by_email_address.return_value = existing_email
        mock_person_svc.get_person_by_id.return_value = existing_person
        mock_login_svc.get_login_method_by_email_id.return_value = None
        mock_login_svc.save_login_method.return_value = new_login
        mock_gen_token.return_value = ("test-token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            provider="google",
            provider_data={"sub": "123"}
        )

        assert token == "test-token"
        mock_login_svc.save_login_method.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_convert_local_to_oauth(self, mock_gen_token,
                                                          mock_person_svc_class,
                                                          mock_email_svc_class,
                                                          mock_login_svc_class,
                                                          mock_org_svc_class,
                                                          mock_role_svc_class,
                                                          mock_msg_sender_class):
        """Test login_user_by_oauth for non-OAuth account conversion."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=False)
        existing_person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        local_login = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123",
            password="hashed_pass"  # NOSONAR
        )
        updated_login = LoginMethod(entity_id="login-123", method_type="oauth-google", email_id="email-123", person_id="person-123", password=None)

        mock_email_svc.get_email_by_email_address.return_value = existing_email
        mock_person_svc.get_person_by_id.return_value = existing_person
        mock_login_svc.get_login_method_by_email_id.return_value = local_login
        mock_login_svc.save_login_method.return_value = updated_login
        mock_email_svc.verify_email.return_value = Email(entity_id="email-123", email="test@example.com", person_id="person-123", is_verified=True)
        mock_gen_token.return_value = ("test-token", 3600)

        service = AuthService(mock_config)
        token, expiry, person = service.login_user_by_oauth(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            provider="google",
            provider_data={"sub": "123"}
        )

        assert token == "test-token"
        mock_login_svc.save_login_method.assert_called_once()
        mock_email_svc.verify_email.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_generate_reset_password_token(self, mock_person_svc_class, mock_email_svc_class,
                                             mock_login_svc_class, mock_org_svc_class,
                                             mock_role_svc_class, mock_msg_sender_class):
        """Test generate_reset_password_token."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.RESET_TOKEN_EXPIRE = 3600

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )

        service = AuthService(mock_config)
        token = service.generate_reset_password_token(login_method, "test@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_prepare_password_reset_url(self, mock_person_svc_class, mock_email_svc_class,
                                          mock_login_svc_class, mock_org_svc_class,
                                          mock_role_svc_class, mock_msg_sender_class):
        """Test prepare_password_reset_url."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.RESET_TOKEN_EXPIRE = 3600
        mock_config.VUE_APP_URI = "http://localhost:3000"

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )

        service = AuthService(mock_config)
        url = service.prepare_password_reset_url(login_method, "test@example.com")

        assert "http://localhost:3000/set-password/" in url
        assert isinstance(url, str)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_send_welcome_email(self, mock_person_svc_class, mock_email_svc_class,
                                  mock_login_svc_class, mock_org_svc_class,
                                  mock_role_svc_class, mock_msg_sender_class):
        """Test send_welcome_email."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.RESET_TOKEN_EXPIRE = 3600
        mock_config.VUE_APP_URI = "http://localhost:3000"

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )
        person = Person(entity_id="person-123", first_name="John", last_name="Doe")

        service = AuthService(mock_config)
        service.send_welcome_email(login_method, person, "test@example.com")

        # Should call message sender
        assert service.message_sender.send_message.call_count >= 1

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_parse_reset_password_token_valid(self, mock_person_svc_class, mock_email_svc_class,
                                                mock_login_svc_class, mock_org_svc_class,
                                                mock_role_svc_class, mock_msg_sender_class):
        """Test parse_reset_password_token with valid token."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )

        # Create a valid token
        payload = {
            "email": "test@example.com",
            "email_id": "email-123",
            "person_id": "person-123",
            "exp": time.time() + 3600
        }
        token = jwt.encode(payload, "secret_key", algorithm='HS256')  # NOSONAR

        service = AuthService(mock_config)
        result = service.parse_reset_password_token(token, login_method)

        assert result is not None
        assert result["email"] == "test@example.com"

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_parse_reset_password_token_expired(self, mock_person_svc_class, mock_email_svc_class,
                                                  mock_login_svc_class, mock_org_svc_class,
                                                  mock_role_svc_class, mock_msg_sender_class):
        """Test parse_reset_password_token with expired token."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )

        # Create an expired token
        payload = {
            "email": "test@example.com",
            "email_id": "email-123",
            "person_id": "person-123",
            "exp": time.time() - 3600  # Expired
        }
        token = jwt.encode(payload, "secret_key", algorithm='HS256')  # NOSONAR

        service = AuthService(mock_config)
        result = service.parse_reset_password_token(token, login_method)

        assert result is None

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_trigger_forgot_password_email_valid_email(self, mock_person_svc_class,
                                                         mock_email_svc_class,
                                                         mock_login_svc_class,
                                                         mock_org_svc_class,
                                                         mock_role_svc_class,
                                                         mock_msg_sender_class):
        """Test trigger_forgot_password_email with valid email."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.RESET_TOKEN_EXPIRE = 3600
        mock_config.VUE_APP_URI = "http://localhost:3000"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", person_id="person-123", email="test@example.com")
        person_obj = Person(entity_id="person-123", first_name="John", last_name="Doe")
        login_method = LoginMethod(entity_id="login-123", email_id="email-123", person_id="person-123", password="secret")  # NOSONAR

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_person_svc.get_person_by_id.return_value = person_obj
        mock_login_svc.get_login_method_by_email_id.return_value = login_method

        service = AuthService(mock_config)
        service.trigger_forgot_password_email("test@example.com")

        # Should call message sender
        assert service.message_sender.send_message.call_count >= 1

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_trigger_forgot_password_email_invalid_email(self, mock_person_svc_class,
                                                           mock_email_svc_class,
                                                           mock_login_svc_class,
                                                           mock_org_svc_class,
                                                           mock_role_svc_class,
                                                           mock_msg_sender_class):
        """Test trigger_forgot_password_email with invalid email."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_email_svc_class.return_value = mock_email_svc

        mock_email_svc.get_email_by_email_address.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.trigger_forgot_password_email("nonexistent@example.com")

        assert "not registered" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_send_password_reset_email(self, mock_person_svc_class, mock_email_svc_class,
                                         mock_login_svc_class, mock_org_svc_class,
                                         mock_role_svc_class, mock_msg_sender_class):
        """Test send_password_reset_email."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"
        mock_config.RESET_TOKEN_EXPIRE = 3600
        mock_config.VUE_APP_URI = "http://localhost:3000"

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="secret_key"  # NOSONAR
        )

        service = AuthService(mock_config)
        service.send_password_reset_email("test@example.com", login_method)

        # Should call message sender
        assert service.message_sender.send_message.call_count >= 1

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_reset_user_password_valid_token(self, mock_gen_token, mock_person_svc_class,
                                               mock_email_svc_class, mock_login_svc_class,
                                               mock_org_svc_class, mock_role_svc_class,
                                               mock_msg_sender_class):
        """Test reset_user_password with valid token."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="old_password_hash"  # NOSONAR
        )
        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        person_obj = Person(entity_id="person-123", first_name="John", last_name="Doe")
        updated_login = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="new_password_hash"  # NOSONAR
        )

        # Create valid token
        payload = {
            "email": "test@example.com",
            "email_id": "email-123",
            "person_id": "person-123",
            "exp": time.time() + 3600
        }
        token = jwt.encode(payload, "old_password_hash", algorithm='HS256')  # NOSONAR

        # Encode uidb64
        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        mock_login_svc.get_login_method_by_id.return_value = login_method
        mock_email_svc.get_email_by_id.return_value = email_obj
        mock_person_svc.get_person_by_id.return_value = person_obj
        mock_login_svc.update_password.return_value = updated_login
        mock_email_svc.verify_email.return_value = email_obj
        mock_gen_token.return_value = ("new-access-token", 3600)

        service = AuthService(mock_config)
        access_token, expiry, person = service.reset_user_password(token, uidb64, "NewPassword123!")  # NOSONAR

        assert access_token == "new-access-token"
        assert expiry == 3600
        mock_login_svc.update_password.assert_called_once()
        mock_email_svc.verify_email.assert_called_once()

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_user_password_invalid_token(self, mock_person_svc_class, mock_email_svc_class,
                                                 mock_login_svc_class, mock_org_svc_class,
                                                 mock_role_svc_class, mock_msg_sender_class):
        """Test reset_user_password with invalid token."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_login_svc = MagicMock()
        mock_login_svc_class.return_value = mock_login_svc

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="password_hash"  # NOSONAR
        )

        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        mock_login_svc.get_login_method_by_id.return_value = login_method

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.reset_user_password("invalid-token", uidb64, "NewPassword123!")  # NOSONAR

        assert "Invalid" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_user_password_invalid_uidb64(self, mock_person_svc_class, mock_email_svc_class,
                                                  mock_login_svc_class, mock_org_svc_class,
                                                  mock_role_svc_class, mock_msg_sender_class):
        """Test reset_user_password with invalid uidb64."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        service = AuthService(mock_config)
        with pytest.raises(Exception):
            service.reset_user_password("token", "invalid-uidb64!!!", "NewPassword123!")  # NOSONAR

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_trigger_forgot_password_email_no_person(self, mock_person_svc_class,
                                                       mock_email_svc_class,
                                                       mock_login_svc_class,
                                                       mock_org_svc_class,
                                                       mock_role_svc_class,
                                                       mock_msg_sender_class):
        """Test trigger_forgot_password_email when person doesn't exist."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc

        email_obj = Email(entity_id="email-123", person_id="person-123", email="test@example.com")

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_person_svc.get_person_by_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.trigger_forgot_password_email("test@example.com")

        assert "Person does not exist" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_trigger_forgot_password_email_no_login_method(self, mock_person_svc_class,
                                                             mock_email_svc_class,
                                                             mock_login_svc_class,
                                                             mock_org_svc_class,
                                                             mock_role_svc_class,
                                                             mock_msg_sender_class):
        """Test trigger_forgot_password_email when login method doesn't exist."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", person_id="person-123", email="test@example.com")
        person_obj = Person(entity_id="person-123", first_name="John", last_name="Doe")

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_person_svc.get_person_by_id.return_value = person_obj
        mock_login_svc.get_login_method_by_email_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.trigger_forgot_password_email("test@example.com")

        assert "Login method does not exist" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_login_user_by_email_password_no_login_method(self, mock_person_svc_class, mock_email_svc_class,
                                                            mock_login_svc_class, mock_org_svc_class,
                                                            mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password when no login method exists."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password")  # NOSONAR

        assert "Login method not found" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_existing_user_person_not_found(self, mock_gen_token,
                                                                  mock_person_svc_class,
                                                                  mock_email_svc_class,
                                                                  mock_login_svc_class,
                                                                  mock_org_svc_class,
                                                                  mock_role_svc_class,
                                                                  mock_msg_sender_class):
        """Test login_user_by_oauth when person is not found."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        existing_email = Email(entity_id="email-123", email="test@example.com", person_id="person-123")

        mock_email_svc.get_email_by_email_address.return_value = existing_email
        mock_person_svc.get_person_by_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.login_user_by_oauth(
                email="test@example.com",
                first_name="John",
                last_name="Doe",
                provider="google",
                provider_data={"sub": "123"}
            )

        assert "Person not found" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_email_password_no_person(self, mock_gen_token, mock_check_hash,
                                                      mock_person_svc_class, mock_email_svc_class,
                                                      mock_login_svc_class, mock_org_svc_class,
                                                      mock_role_svc_class, mock_msg_sender_class):
        """Test login_user_by_email_password when person doesn't exist."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")
        login_method = LoginMethod(
            entity_id="login-123",
            method_type=LoginMethodType.EMAIL_PASSWORD,
            email_id="email-123",
            person_id="person-123",
            password="hashed_password"  # NOSONAR
        )

        mock_email_svc.get_email_by_email_address.return_value = email_obj
        mock_login_svc.get_login_method_by_email_id.return_value = login_method
        mock_person_svc.get_person_by_id.return_value = None
        mock_check_hash.return_value = True

        service = AuthService(mock_config)
        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password("test@example.com", "password123")  # NOSONAR

        assert "Could not find complete user profile" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_reset_user_password_no_email_found(self, mock_gen_token, mock_person_svc_class,
                                                  mock_email_svc_class, mock_login_svc_class,
                                                  mock_org_svc_class, mock_role_svc_class,
                                                  mock_msg_sender_class):
        """Test reset_user_password when email is not found."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_login_svc_class.return_value = mock_login_svc

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="old_password_hash"  # NOSONAR
        )

        payload = {
            "email": "test@example.com",
            "email_id": "email-123",
            "person_id": "person-123",
            "exp": time.time() + 3600
        }
        token = jwt.encode(payload, "old_password_hash", algorithm='HS256')  # NOSONAR

        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        mock_login_svc.get_login_method_by_id.return_value = login_method
        mock_email_svc.get_email_by_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.reset_user_password(token, uidb64, "NewPassword123!")  # NOSONAR

        assert "Email not found" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.generate_access_token')
    def test_reset_user_password_no_person_found(self, mock_gen_token, mock_person_svc_class,
                                                   mock_email_svc_class, mock_login_svc_class,
                                                   mock_org_svc_class, mock_role_svc_class,
                                                   mock_msg_sender_class):
        """Test reset_user_password when person is not found."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_email_svc = MagicMock()
        mock_person_svc = MagicMock()
        mock_login_svc = MagicMock()

        mock_email_svc_class.return_value = mock_email_svc
        mock_person_svc_class.return_value = mock_person_svc
        mock_login_svc_class.return_value = mock_login_svc

        login_method = LoginMethod(
            entity_id="login-123",
            email_id="email-123",
            person_id="person-123",
            password="old_password_hash"  # NOSONAR
        )
        email_obj = Email(entity_id="email-123", email="test@example.com", person_id="person-123")

        payload = {
            "email": "test@example.com",
            "email_id": "email-123",
            "person_id": "person-123",
            "exp": time.time() + 3600
        }
        token = jwt.encode(payload, "old_password_hash", algorithm='HS256')  # NOSONAR

        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        mock_login_svc.get_login_method_by_id.return_value = login_method
        mock_email_svc.get_email_by_id.return_value = email_obj
        mock_person_svc.get_person_by_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.reset_user_password(token, uidb64, "NewPassword123!")  # NOSONAR

        assert "Person with email not found" in str(exc_info.value)

    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.PersonService')
    def test_reset_user_password_no_login_method_found(self, mock_person_svc_class,
                                                         mock_email_svc_class, mock_login_svc_class,
                                                         mock_org_svc_class, mock_role_svc_class,
                                                         mock_msg_sender_class):
        """Test reset_user_password when login method is not found."""
        mock_config = MagicMock()
        mock_config.QUEUE_NAME_PREFIX = ""
        mock_config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = "email-queue"

        mock_login_svc = MagicMock()
        mock_login_svc_class.return_value = mock_login_svc

        from common.helpers.string_utils import urlsafe_base64_encode, force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes("login-123"))

        mock_login_svc.get_login_method_by_id.return_value = None

        service = AuthService(mock_config)
        with pytest.raises(APIException) as exc_info:
            service.reset_user_password("token", uidb64, "NewPassword123!")  # NOSONAR

        assert "Invalid password reset URL" in str(exc_info.value)
