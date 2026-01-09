"""
Unit tests for common/helpers/auth.py JWT utilities.
"""
import time
import jwt
import pytest
from unittest.mock import patch, MagicMock


class TestGenerateAccessToken:
    """Test generate_access_token function."""

    @patch('common.helpers.auth.config')
    def test_generate_access_token_with_all_data(self, mock_config):
        """Test generate_access_token with login_method, person, and email."""
        from common.helpers.auth import generate_access_token
        from common.models.login_method import LoginMethod
        from common.models.person import Person
        from common.models.email import Email

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR
        mock_config.ACCESS_TOKEN_EXPIRE = 3600

        login_method = LoginMethod(email_id="email-123", person_id="person-123")
        person = Person(entity_id="person-123", first_name="John", last_name="Doe")
        email = Email(entity_id="email-123", email="test@example.com", is_verified=True, person_id="person-123")

        token, expiry = generate_access_token(login_method, person=person, email=email)

        assert isinstance(token, str)
        assert expiry > time.time()

        decoded = jwt.decode(token, "test-secret", algorithms=['HS256'])  # NOSONAR
        assert decoded['email_id'] == "email-123"
        assert decoded['person_first_name'] == "John"

    @patch('common.helpers.auth.config')
    def test_generate_access_token_minimal_data(self, mock_config):
        """Test generate_access_token with login_method only."""
        from common.helpers.auth import generate_access_token
        from common.models.login_method import LoginMethod

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR
        mock_config.ACCESS_TOKEN_EXPIRE = 3600

        login_method = LoginMethod(email_id="email-123", person_id="person-123")
        token, expiry = generate_access_token(login_method)

        assert isinstance(token, str)
        decoded = jwt.decode(token, "test-secret", algorithms=['HS256'])  # NOSONAR
        assert decoded['email_id'] == "email-123"

    @patch('common.helpers.auth.config')
    def test_generate_access_token_with_person_no_email(self, mock_config):
        """Test generate_access_token with person but no email."""
        from common.helpers.auth import generate_access_token
        from common.models.login_method import LoginMethod
        from common.models.person import Person

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR
        mock_config.ACCESS_TOKEN_EXPIRE = 3600

        login_method = LoginMethod(email_id="email-123", person_id="person-123")
        person = Person(entity_id="person-123", first_name="Jane", last_name="Smith")

        token, expiry = generate_access_token(login_method, person=person)

        assert isinstance(token, str)
        decoded = jwt.decode(token, "test-secret", algorithms=['HS256'])  # NOSONAR
        assert decoded['person_first_name'] == "Jane"


class TestParseAccessToken:
    """Test parse_access_token function."""

    @patch('common.helpers.auth.config')
    def test_parse_access_token_valid(self, mock_config):
        """Test parse_access_token with valid token."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR

        payload = {'email_id': 'email-123', 'exp': time.time() + 3600}
        token = jwt.encode(payload, "test-secret", algorithm='HS256')  # NOSONAR

        result = parse_access_token(token)
        assert result is not None
        assert result['email_id'] == 'email-123'

    @patch('common.helpers.auth.config')
    def test_parse_access_token_expired(self, mock_config):
        """Test parse_access_token with expired token."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR

        payload = {'email_id': 'email-123', 'exp': time.time() - 3600}
        token = jwt.encode(payload, "test-secret", algorithm='HS256')  # NOSONAR

        result = parse_access_token(token)
        assert result is None

    @patch('common.helpers.auth.config')
    def test_parse_access_token_invalid(self, mock_config):
        """Test parse_access_token with invalid token."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = "test-secret"  # NOSONAR
        result = parse_access_token("invalid.token")
        assert result is None


class TestCreatePersonFromToken:
    """Test create_person_from_token function."""

    def test_create_person_from_token_full_data(self):
        """Test create_person_from_token with full data."""
        from common.helpers.auth import create_person_from_token

        token_data = {
            'person_entity_id': 'person-123',
            'person_first_name': 'John',
            'person_last_name': 'Doe'
        }
        person = create_person_from_token(token_data)
        assert person.entity_id == 'person-123'
        assert person.first_name == 'John'

    def test_create_person_from_token_minimal(self):
        """Test create_person_from_token with minimal data."""
        from common.helpers.auth import create_person_from_token

        token_data = {'person_id': 'person-456'}
        person = create_person_from_token(token_data)
        assert person.entity_id == 'person-456'


class TestCreateEmailFromToken:
    """Test create_email_from_token function."""

    def test_create_email_from_token_full_data(self):
        """Test create_email_from_token with full data."""
        from common.helpers.auth import create_email_from_token

        token_data = {
            'email_entity_id': 'email-123',
            'person_id': 'person-123',
            'email_address': 'test@example.com',
            'email_is_verified': True
        }
        email = create_email_from_token(token_data)
        assert email.entity_id == 'email-123'
        assert email.email == 'test@example.com'

    def test_create_email_from_token_minimal(self):
        """Test create_email_from_token with minimal data."""
        from common.helpers.auth import create_email_from_token

        token_data = {'email_id': 'email-456', 'person_id': 'person-456'}
        email = create_email_from_token(token_data)
        assert email.entity_id == 'email-456'
