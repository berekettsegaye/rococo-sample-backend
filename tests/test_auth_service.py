"""
Unit tests for common/services/auth.py
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from common.services.auth import AuthService
from common.models import Person, Email, LoginMethod, Organization, PersonOrganizationRole
from common.helpers.exceptions import InputValidationError, APIException


class TestAuthService:
    """Tests for AuthService."""

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_auth_service_initialization(self, mock_msg, mock_por, mock_org, mock_lm, mock_email, mock_person):
        """Test AuthService initializes correctly."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        assert service.config == config
        assert service.EMAIL_TRANSMITTER_QUEUE_NAME == 'test_email_queue'

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_with_new_user(self, mock_msg, mock_por, mock_org, mock_lm, mock_email_svc, mock_person_svc):
        """Test signup with new user creates all entities."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'
        config.DEFAULT_USER_PASSWORD = 'TempPass123!'

        service = AuthService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)
        service.email_service.save_email = MagicMock(return_value=Email(email='new@example.com'))
        service.person_service.save_person = MagicMock(return_value=Person(first_name='New', last_name='User'))
        service.login_method_service.save_login_method = MagicMock(return_value=LoginMethod())
        service.organization_service.save_organization = MagicMock()
        service.person_organization_role_service.save_person_organization_role = MagicMock()
        service.send_welcome_email = MagicMock()

        service.signup('new@example.com', 'New', 'User')

        service.email_service.get_email_by_email_address.assert_called_once_with('new@example.com')
        service.email_service.save_email.assert_called_once()
        service.person_service.save_person.assert_called_once()
        service.login_method_service.save_login_method.assert_called_once()
        service.organization_service.save_organization.assert_called_once()
        service.person_organization_role_service.save_person_organization_role.assert_called_once()
        service.send_welcome_email.assert_called_once()

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_with_existing_email(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test signup with existing email raises InputValidationError."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)
        existing_email = Email(entity_id='email-123', email='existing@example.com')
        existing_login_method = LoginMethod(method_type='email-password')

        service.email_service.get_email_by_email_address = MagicMock(return_value=existing_email)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=existing_login_method)

        with pytest.raises(InputValidationError) as exc_info:
            service.signup('existing@example.com', 'Test', 'User')

        assert "already registered" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_signup_with_oauth_email(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test signup with OAuth email raises InputValidationError with provider message."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)
        existing_email = Email(entity_id='email-123', email='oauth@example.com')
        oauth_login_method = MagicMock()
        oauth_login_method.is_oauth_method = True
        oauth_login_method.oauth_provider_name = 'google'

        service.email_service.get_email_by_email_address = MagicMock(return_value=existing_email)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=oauth_login_method)

        with pytest.raises(InputValidationError) as exc_info:
            service.signup('oauth@example.com', 'Test', 'User')

        assert "google" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.check_password_hash')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_email_password_success(self, mock_gen_token, mock_check_hash, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test login with valid credentials returns token."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        email_obj = Email(entity_id='email-123', person_id='person-123', email='test@example.com')
        login_method = MagicMock()
        login_method.is_oauth_method = False
        login_method.password = 'hashed_password'
        login_method.person_id = 'person-123'
        person = Person(entity_id='person-123', first_name='Test', last_name='User')

        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=login_method)
        service.person_service.get_person_by_id = MagicMock(return_value=person)
        mock_check_hash.return_value = True
        mock_gen_token.return_value = ('token-123', 1234567890)

        token, expiry = service.login_user_by_email_password('test@example.com', 'password')

        assert token == 'token-123'
        assert expiry == 1234567890

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_invalid_email(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test login with invalid email raises InputValidationError."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password('invalid@example.com', 'password')

        assert "not registered" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.check_password_hash')
    def test_login_user_by_email_password_incorrect_password(self, mock_check_hash, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test login with incorrect password raises InputValidationError."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        email_obj = Email(entity_id='email-123', email='test@example.com')
        login_method = MagicMock()
        login_method.is_oauth_method = False
        login_method.password = 'hashed_password'

        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=login_method)
        mock_check_hash.return_value = False

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password('test@example.com', 'wrong_password')

        assert "Incorrect" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_login_user_by_email_password_oauth_account(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test login for OAuth account raises InputValidationError with provider message."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        email_obj = Email(entity_id='email-123', email='oauth@example.com')
        oauth_login_method = MagicMock()
        oauth_login_method.is_oauth_method = True
        oauth_login_method.oauth_provider_name = 'google'

        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=oauth_login_method)

        with pytest.raises(InputValidationError) as exc_info:
            service.login_user_by_email_password('oauth@example.com', 'password')

        assert "google" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_new_user(self, mock_gen_token, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test OAuth login with new user creates all entities and returns token."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)
        service.email_service.save_email = MagicMock(return_value=Email(email='new@example.com'))
        service.person_service.save_person = MagicMock(return_value=Person(first_name='New', last_name='User'))
        service.login_method_service.save_login_method = MagicMock(return_value=LoginMethod())
        service.organization_service.save_organization = MagicMock()
        service.person_organization_role_service.save_person_organization_role = MagicMock()
        mock_gen_token.return_value = ('token-123', 1234567890)

        token, expiry, person = service.login_user_by_oauth('new@example.com', 'New', 'User', 'google', {})

        assert token == 'token-123'
        assert expiry == 1234567890
        service.email_service.save_email.assert_called_once()
        service.person_service.save_person.assert_called_once()

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.generate_access_token')
    def test_login_user_by_oauth_existing_user(self, mock_gen_token, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test OAuth login with existing user returns token."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        existing_email = Email(entity_id='email-123', person_id='person-123', email='existing@example.com', is_verified=True)
        existing_person = Person(entity_id='person-123', first_name='Existing', last_name='User')
        existing_login = MagicMock()
        existing_login.is_oauth_method = True

        service.email_service.get_email_by_email_address = MagicMock(return_value=existing_email)
        service.person_service.get_person_by_id = MagicMock(return_value=existing_person)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=existing_login)
        service.email_service.verify_email = MagicMock(return_value=existing_email)
        mock_gen_token.return_value = ('token-456', 1234567890)

        token, expiry, person = service.login_user_by_oauth('existing@example.com', 'Existing', 'User', 'google', {})

        assert token == 'token-456'
        assert person == existing_person

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.jwt')
    def test_generate_reset_password_token(self, mock_jwt, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test generate_reset_password_token creates valid token."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'
        config.RESET_TOKEN_EXPIRE = '3600'

        service = AuthService(config)

        login_method = MagicMock()
        login_method.person_id = 'person-123'
        login_method.email_id = 'email-123'
        login_method.password = 'hashed_password'

        mock_jwt.encode.return_value = 'reset-token-123'

        token = service.generate_reset_password_token(login_method, 'test@example.com')

        assert token == 'reset-token-123'
        mock_jwt.encode.assert_called_once()

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_trigger_forgot_password_email_with_valid_email(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test trigger_forgot_password_email sends email for valid user."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        email_obj = MagicMock()
        email_obj.entity_id = 'email-123'
        email_obj.person_id = 'person-123'
        email_obj.email = 'test@example.com'

        person = Person(entity_id='person-123', first_name='Test', last_name='User')
        login_method = MagicMock()

        service.email_service.get_email_by_email_address = MagicMock(return_value=email_obj)
        service.person_service.get_person_by_id = MagicMock(return_value=person)
        service.login_method_service.get_login_method_by_email_id = MagicMock(return_value=login_method)
        service.send_password_reset_email = MagicMock()

        service.trigger_forgot_password_email('test@example.com')

        service.send_password_reset_email.assert_called_once()

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    def test_trigger_forgot_password_email_with_invalid_email(self, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test trigger_forgot_password_email raises APIException for non-existent email."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)
        service.email_service.get_email_by_email_address = MagicMock(return_value=None)

        with pytest.raises(APIException) as exc_info:
            service.trigger_forgot_password_email('nonexistent@example.com')

        assert "not registered" in str(exc_info.value)

    @patch('common.services.auth.PersonService')
    @patch('common.services.auth.EmailService')
    @patch('common.services.auth.LoginMethodService')
    @patch('common.services.auth.OrganizationService')
    @patch('common.services.auth.PersonOrganizationRoleService')
    @patch('common.services.auth.MessageSender')
    @patch('common.services.auth.generate_access_token')
    def test_reset_user_password_with_valid_token(self, mock_gen_token, mock_msg, mock_por, mock_org, mock_lm_svc, mock_email_svc, mock_person_svc):
        """Test reset_user_password updates password and returns token."""
        config = MagicMock()
        config.QUEUE_NAME_PREFIX = 'test_'
        config.EMAIL_SERVICE_PROCESSOR_QUEUE_NAME = 'email_queue'

        service = AuthService(config)

        login_method = MagicMock()
        login_method.entity_id = 'login-123'
        email_obj = Email(entity_id='email-123', person_id='person-123', email='test@example.com')
        person_obj = Person(entity_id='person-123', first_name='Test', last_name='User')

        service.login_method_service.get_login_method_by_id = MagicMock(return_value=login_method)
        service.parse_reset_password_token = MagicMock(return_value={'email_id': 'email-123', 'person_id': 'person-123'})
        service.email_service.get_email_by_id = MagicMock(return_value=email_obj)
        service.person_service.get_person_by_id = MagicMock(return_value=person_obj)
        service.login_method_service.update_password = MagicMock(return_value=login_method)
        service.email_service.verify_email = MagicMock(return_value=email_obj)
        mock_gen_token.return_value = ('token-789', 1234567890)

        token, expiry, person = service.reset_user_password('valid-token', 'valid-uid', 'NewPass123!')

        assert token == 'token-789'
        assert person == person_obj

    @patch('common.services.auth.jwt')
    def test_parse_reset_password_token_with_valid_token(self, mock_jwt):
        """Test parse_reset_password_token returns decoded payload for valid token."""
        login_method = MagicMock()
        login_method.password = 'hashed_password'

        payload = {'email': 'test@example.com', 'exp': time.time() + 3600}
        mock_jwt.decode.return_value = payload

        result = AuthService.parse_reset_password_token('valid-token', login_method)

        assert result == payload

    @patch('common.services.auth.jwt')
    def test_parse_reset_password_token_with_expired_token(self, mock_jwt):
        """Test parse_reset_password_token returns None for expired token."""
        login_method = MagicMock()
        login_method.password = 'hashed_password'

        payload = {'email': 'test@example.com', 'exp': time.time() - 3600}
        mock_jwt.decode.return_value = payload

        result = AuthService.parse_reset_password_token('expired-token', login_method)

        assert result is None
