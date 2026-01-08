"""
Unit tests for common/helpers/auth.py
"""
import time
import pytest
import jwt
from unittest.mock import MagicMock, patch
from common.helpers.auth import (
    generate_access_token,
    parse_access_token,
    create_person_from_token,
    create_email_from_token
)
from common.models import LoginMethod
from common.models.person import Person
from common.models.email import Email


class TestGenerateAccessToken:
    """Tests for generate_access_token function."""

    def test_generate_access_token_with_person_and_email(self, mock_config):
        """Test token generation with valid login method, person, and email."""
        with patch('common.helpers.auth.config') as config_mock:
            config_mock.ACCESS_TOKEN_EXPIRE = '3600'
            config_mock.AUTH_JWT_SECRET = 'test-secret'

            login_method = MagicMock(spec=LoginMethod)
            login_method.email_id = 'email-123'
            login_method.person_id = 'person-123'

            person = MagicMock(spec=Person)
            person.first_name = 'John'
            person.last_name = 'Doe'
            person.entity_id = 'person-entity-123'

            email = MagicMock(spec=Email)
            email.email = 'john@example.com'
            email.is_verified = True
            email.entity_id = 'email-entity-123'

            token, expiry = generate_access_token(login_method, person, email)

            assert token is not None
            assert expiry > time.time()

            decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
            assert decoded['email_id'] == 'email-123'
            assert decoded['person_id'] == 'person-123'
            assert decoded['person_first_name'] == 'John'
            assert decoded['person_last_name'] == 'Doe'
            assert decoded['person_entity_id'] == 'person-entity-123'
            assert decoded['email_address'] == 'john@example.com'
            assert decoded['email_is_verified'] is True
            assert decoded['email_entity_id'] == 'email-entity-123'

    def test_generate_access_token_without_person_and_email(self, mock_config):
        """Test token generation without person and email (minimal token)."""
        with patch('common.helpers.auth.config') as config_mock:
            config_mock.ACCESS_TOKEN_EXPIRE = '3600'
            config_mock.AUTH_JWT_SECRET = 'test-secret'

            login_method = MagicMock(spec=LoginMethod)
            login_method.email_id = 'email-123'
            login_method.person_id = 'person-123'

            token, expiry = generate_access_token(login_method, None, None)

            assert token is not None
            assert expiry > time.time()

            decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
            assert decoded['email_id'] == 'email-123'
            assert decoded['person_id'] == 'person-123'
            assert 'person_first_name' not in decoded
            assert 'email_address' not in decoded


class TestParseAccessToken:
    """Tests for parse_access_token function."""

    def test_parse_access_token_with_valid_token(self):
        """Test parsing a valid non-expired token."""
        with patch('common.helpers.auth.config') as config_mock:
            config_mock.AUTH_JWT_SECRET = 'test-secret'

            payload = {
                'email_id': 'email-123',
                'person_id': 'person-123',
                'exp': time.time() + 3600
            }
            token = jwt.encode(payload, 'test-secret', algorithm='HS256')

            result = parse_access_token(token)

            assert result is not None
            assert result['email_id'] == 'email-123'
            assert result['person_id'] == 'person-123'

    def test_parse_access_token_with_expired_token(self):
        """Test parsing an expired token returns None."""
        with patch('common.helpers.auth.config') as config_mock:
            config_mock.AUTH_JWT_SECRET = 'test-secret'

            payload = {
                'email_id': 'email-123',
                'person_id': 'person-123',
                'exp': time.time() - 3600
            }
            token = jwt.encode(payload, 'test-secret', algorithm='HS256')

            result = parse_access_token(token)

            assert result is None

    def test_parse_access_token_with_invalid_token(self):
        """Test parsing an invalid token returns None."""
        with patch('common.helpers.auth.config') as config_mock:
            config_mock.AUTH_JWT_SECRET = 'test-secret'

            result = parse_access_token('invalid-token-string')

            assert result is None


class TestCreatePersonFromToken:
    """Tests for create_person_from_token function."""

    def test_create_person_from_token_with_complete_data(self):
        """Test creating Person object with complete token data."""
        token_data = {
            'person_entity_id': 'person-entity-123',
            'person_first_name': 'John',
            'person_last_name': 'Doe'
        }

        person = create_person_from_token(token_data)

        assert isinstance(person, Person)
        assert person.entity_id == 'person-entity-123'
        assert person.first_name == 'John'
        assert person.last_name == 'Doe'

    def test_create_person_from_token_with_minimal_data(self):
        """Test creating Person object with minimal token data."""
        token_data = {
            'person_id': 'person-123'
        }

        person = create_person_from_token(token_data)

        assert isinstance(person, Person)
        assert person.entity_id == 'person-123'
        assert person.first_name == ''
        assert person.last_name == ''


class TestCreateEmailFromToken:
    """Tests for create_email_from_token function."""

    def test_create_email_from_token_with_complete_data(self):
        """Test creating Email object with complete token data."""
        token_data = {
            'email_entity_id': 'email-entity-123',
            'person_id': 'person-123',
            'email_address': 'john@example.com',
            'email_is_verified': True
        }

        email = create_email_from_token(token_data)

        assert isinstance(email, Email)
        assert email.entity_id == 'email-entity-123'
        assert email.person_id == 'person-123'
        assert email.email == 'john@example.com'
        assert email.is_verified is True

    def test_create_email_from_token_with_minimal_data(self):
        """Test creating Email object with minimal token data."""
        token_data = {
            'email_id': 'email-123',
            'person_id': 'person-123'
        }

        email = create_email_from_token(token_data)

        assert isinstance(email, Email)
        assert email.entity_id == 'email-123'
        assert email.person_id == 'person-123'
        assert email.email == ''
        assert email.is_verified is False
