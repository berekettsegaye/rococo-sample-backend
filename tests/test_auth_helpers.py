"""
Unit tests for common/helpers/auth.py
"""
import pytest
import time
import jwt
from unittest.mock import MagicMock, patch
from common.models import LoginMethod
from common.models.person import Person
from common.models.email import Email


class TestGenerateAccessToken:
    """Tests for generate_access_token function."""

    @patch('common.helpers.auth.config')
    def test_generate_token_with_person_and_email(self, mock_config):
        """Test generating token with person and email data."""
        from common.helpers.auth import generate_access_token

        mock_config.ACCESS_TOKEN_EXPIRE = 3600
        mock_config.AUTH_JWT_SECRET = 'test-secret'

        login_method = MagicMock(spec=LoginMethod)
        login_method.email_id = 'email-123'
        login_method.person_id = 'person-123'

        person = MagicMock(spec=Person)
        person.first_name = 'John'
        person.last_name = 'Doe'
        person.entity_id = 'person-123'

        email = MagicMock(spec=Email)
        email.email = 'john@example.com'
        email.is_verified = True
        email.entity_id = 'email-123'

        token, expiry = generate_access_token(login_method, person=person, email=email)

        assert isinstance(token, str)
        assert expiry > time.time()

        # Verify token can be decoded
        decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
        assert decoded['email_id'] == 'email-123'
        assert decoded['person_id'] == 'person-123'
        assert decoded['person_first_name'] == 'John'
        assert decoded['person_last_name'] == 'Doe'
        assert decoded['email_address'] == 'john@example.com'
        assert decoded['email_is_verified'] is True

    @patch('common.helpers.auth.config')
    def test_generate_token_without_person_and_email(self, mock_config):
        """Test generating token without person and email data."""
        from common.helpers.auth import generate_access_token

        mock_config.ACCESS_TOKEN_EXPIRE = 3600
        mock_config.AUTH_JWT_SECRET = 'test-secret'

        login_method = MagicMock(spec=LoginMethod)
        login_method.email_id = 'email-123'
        login_method.person_id = 'person-123'

        token, expiry = generate_access_token(login_method)

        assert isinstance(token, str)
        assert expiry > time.time()

        decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
        assert decoded['email_id'] == 'email-123'
        assert decoded['person_id'] == 'person-123'
        assert 'person_first_name' not in decoded
        assert 'email_address' not in decoded

    @patch('common.helpers.auth.config')
    def test_generate_token_with_null_person_names(self, mock_config):
        """Test generating token with None values in person names."""
        from common.helpers.auth import generate_access_token

        mock_config.ACCESS_TOKEN_EXPIRE = 3600
        mock_config.AUTH_JWT_SECRET = 'test-secret'

        login_method = MagicMock(spec=LoginMethod)
        login_method.email_id = 'email-123'
        login_method.person_id = 'person-123'

        person = MagicMock(spec=Person)
        person.first_name = None
        person.last_name = None
        person.entity_id = 'person-123'

        token, expiry = generate_access_token(login_method, person=person)

        decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
        assert decoded['person_first_name'] == ''
        assert decoded['person_last_name'] == ''

    @patch('common.helpers.auth.config')
    @patch('common.helpers.auth.time')
    def test_token_expiry_calculation(self, mock_time, mock_config):
        """Test that token expiry is calculated correctly."""
        from common.helpers.auth import generate_access_token

        mock_time.time.return_value = 1000.0
        mock_config.ACCESS_TOKEN_EXPIRE = 3600
        mock_config.AUTH_JWT_SECRET = 'test-secret'

        login_method = MagicMock(spec=LoginMethod)
        login_method.email_id = 'email-123'
        login_method.person_id = 'person-123'

        token, expiry = generate_access_token(login_method)

        assert expiry == 4600.0  # 1000 + 3600


class TestParseAccessToken:
    """Tests for parse_access_token function."""

    @patch('common.helpers.auth.config')
    def test_parse_valid_token(self, mock_config):
        """Test parsing a valid, non-expired token."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = 'test-secret'

        payload = {
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': time.time() + 3600  # Not expired
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')

        result = parse_access_token(token)

        assert result is not None
        assert result['email_id'] == 'email-123'
        assert result['person_id'] == 'person-123'

    @patch('common.helpers.auth.config')
    @patch('common.helpers.auth.time')
    def test_parse_expired_token(self, mock_time, mock_config):
        """Test parsing an expired token returns None."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = 'test-secret'
        mock_time.time.return_value = 2000.0

        payload = {
            'email_id': 'email-123',
            'person_id': 'person-123',
            'exp': 1000.0  # Expired
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')

        result = parse_access_token(token)

        assert result is None

    @patch('common.helpers.auth.config')
    def test_parse_invalid_token(self, mock_config):
        """Test parsing an invalid token returns None."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = 'test-secret'

        result = parse_access_token('invalid-token-string')

        assert result is None

    @patch('common.helpers.auth.config')
    def test_parse_token_wrong_secret(self, mock_config):
        """Test parsing token with wrong secret returns None."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = 'test-secret'

        payload = {
            'email_id': 'email-123',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, 'wrong-secret', algorithm='HS256')

        result = parse_access_token(token)

        assert result is None

    @patch('common.helpers.auth.config')
    def test_parse_token_returns_none_if_not_expired(self, mock_config):
        """Test that token parsing checks time properly."""
        from common.helpers.auth import parse_access_token

        mock_config.AUTH_JWT_SECRET = 'test-secret'

        # Create token that will be expired by JWT library check but not our check
        # JWT library validates exp at decode time, so we need future exp
        payload = {
            'email_id': 'email-123',
            'exp': time.time() + 3600
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')

        result = parse_access_token(token)

        # Should be valid
        assert result is not None
        assert result['email_id'] == 'email-123'


class TestCreatePersonFromToken:
    """Tests for create_person_from_token function."""

    def test_create_person_with_all_fields(self):
        """Test creating person with all token fields."""
        from common.helpers.auth import create_person_from_token

        token_data = {
            'person_entity_id': 'person-123',
            'person_first_name': 'John',
            'person_last_name': 'Doe'
        }

        person = create_person_from_token(token_data)

        assert person.entity_id == 'person-123'
        assert person.first_name == 'John'
        assert person.last_name == 'Doe'

    def test_create_person_with_fallback_id(self):
        """Test creating person using person_id as fallback."""
        from common.helpers.auth import create_person_from_token

        token_data = {
            'person_id': 'person-456',
            'person_first_name': 'Jane',
            'person_last_name': 'Smith'
        }

        person = create_person_from_token(token_data)

        assert person.entity_id == 'person-456'

    def test_create_person_with_empty_names(self):
        """Test creating person with empty names."""
        from common.helpers.auth import create_person_from_token

        token_data = {
            'person_entity_id': 'person-123'
        }

        person = create_person_from_token(token_data)

        assert person.entity_id == 'person-123'
        assert person.first_name == ''
        assert person.last_name == ''

    def test_create_person_minimal_data(self):
        """Test creating person with minimal token data."""
        from common.helpers.auth import create_person_from_token

        token_data = {}

        person = create_person_from_token(token_data)

        assert person.entity_id is None
        assert person.first_name == ''
        assert person.last_name == ''


class TestCreateEmailFromToken:
    """Tests for create_email_from_token function."""

    def test_create_email_with_all_fields(self):
        """Test creating email with all token fields."""
        from common.helpers.auth import create_email_from_token

        token_data = {
            'email_entity_id': 'email-123',
            'person_id': 'person-123',
            'email_address': 'test@example.com',
            'email_is_verified': True
        }

        email = create_email_from_token(token_data)

        assert email.entity_id == 'email-123'
        assert email.person_id == 'person-123'
        assert email.email == 'test@example.com'
        assert email.is_verified is True

    def test_create_email_with_fallback_id(self):
        """Test creating email using email_id as fallback."""
        from common.helpers.auth import create_email_from_token

        token_data = {
            'email_id': 'email-456',
            'person_id': 'person-123',
            'email_address': 'test2@example.com',
            'email_is_verified': False
        }

        email = create_email_from_token(token_data)

        assert email.entity_id == 'email-456'
        assert email.is_verified is False

    def test_create_email_with_minimal_data(self):
        """Test creating email with minimal token data."""
        from common.helpers.auth import create_email_from_token

        token_data = {
            'person_id': 'person-123'
        }

        email = create_email_from_token(token_data)

        assert email.person_id == 'person-123'
        assert email.email == ''
        assert email.is_verified is False

    def test_create_email_empty_token(self):
        """Test creating email with empty token data."""
        from common.helpers.auth import create_email_from_token

        token_data = {}

        email = create_email_from_token(token_data)

        assert email.entity_id is None
        assert email.person_id is None
        assert email.email == ''
        assert email.is_verified is False
