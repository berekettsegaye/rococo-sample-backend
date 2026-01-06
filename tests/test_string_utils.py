"""
Unit tests for common/helpers/string_utils.py
"""
import pytest
from datetime import datetime, date, time
from decimal import Decimal
from common.helpers.string_utils import (
    normal_url_safe_b64_decode,
    normal_url_safe_b64_encode,
    is_protected_type,
    urlsafe_base64_encode,
    urlsafe_base64_decode,
    force_str,
    force_bytes
)


class TestNormalUrlSafeB64:
    """Tests for normal_url_safe_b64_encode and normal_url_safe_b64_decode."""

    def test_normal_url_safe_b64_encode(self):
        """Test encoding a string with base64 URL-safe encoding."""
        result = normal_url_safe_b64_encode('hello world')
        assert result is not None
        assert isinstance(result, str)

    def test_normal_url_safe_b64_decode(self):
        """Test decoding a valid base64 URL-safe encoded string."""
        encoded = normal_url_safe_b64_encode('hello world')
        decoded = normal_url_safe_b64_decode(encoded)
        assert decoded == 'hello world'


class TestIsProtectedType:
    """Tests for is_protected_type function."""

    def test_is_protected_type_with_none(self):
        """Test that None is a protected type."""
        assert is_protected_type(None) is True

    def test_is_protected_type_with_int(self):
        """Test that int is a protected type."""
        assert is_protected_type(42) is True

    def test_is_protected_type_with_float(self):
        """Test that float is a protected type."""
        assert is_protected_type(3.14) is True

    def test_is_protected_type_with_decimal(self):
        """Test that Decimal is a protected type."""
        assert is_protected_type(Decimal('10.5')) is True

    def test_is_protected_type_with_datetime(self):
        """Test that datetime is a protected type."""
        assert is_protected_type(datetime.now()) is True

    def test_is_protected_type_with_date(self):
        """Test that date is a protected type."""
        assert is_protected_type(date.today()) is True

    def test_is_protected_type_with_time(self):
        """Test that time is a protected type."""
        assert is_protected_type(time()) is True

    def test_is_protected_type_with_string(self):
        """Test that string is not a protected type."""
        assert is_protected_type('hello') is False

    def test_is_protected_type_with_list(self):
        """Test that list is not a protected type."""
        assert is_protected_type([1, 2, 3]) is False

    def test_is_protected_type_with_dict(self):
        """Test that dict is not a protected type."""
        assert is_protected_type({'key': 'value'}) is False


class TestUrlsafeBase64Encode:
    """Tests for urlsafe_base64_encode function."""

    def test_urlsafe_base64_encode_with_bytestring(self):
        """Test encoding a bytestring without padding."""
        result = urlsafe_base64_encode(b'hello')
        assert result is not None
        assert isinstance(result, str)
        assert '=' not in result  # Verify padding is stripped


class TestUrlsafeBase64Decode:
    """Tests for urlsafe_base64_decode function."""

    def test_urlsafe_base64_decode_with_valid_string(self):
        """Test decoding a valid encoded string."""
        encoded = urlsafe_base64_encode(b'hello world')
        decoded = urlsafe_base64_decode(encoded)
        assert decoded == b'hello world'

    def test_urlsafe_base64_decode_with_invalid_string(self):
        """Test decoding an invalid string raises ValueError."""
        with pytest.raises(ValueError):
            urlsafe_base64_decode('!!!invalid!!!')


class TestForceStr:
    """Tests for force_str function."""

    def test_force_str_with_string(self):
        """Test that string is returned as-is."""
        result = force_str('hello')
        assert result == 'hello'
        assert isinstance(result, str)

    def test_force_str_with_bytes(self):
        """Test that bytes are converted to string."""
        result = force_str(b'hello')
        assert result == 'hello'
        assert isinstance(result, str)

    def test_force_str_with_protected_type_and_strings_only(self):
        """Test that protected types are returned as-is when strings_only=True."""
        result = force_str(42, strings_only=True)
        assert result == 42
        assert isinstance(result, int)

    def test_force_str_with_none_and_strings_only(self):
        """Test that None is returned as-is when strings_only=True."""
        result = force_str(None, strings_only=True)
        assert result is None

    def test_force_str_with_int(self):
        """Test that int is converted to string."""
        result = force_str(42)
        assert result == '42'
        assert isinstance(result, str)

    def test_force_str_with_list(self):
        """Test that list is converted to string."""
        result = force_str([1, 2, 3])
        assert result == '[1, 2, 3]'
        assert isinstance(result, str)


class TestForceBytes:
    """Tests for force_bytes function."""

    def test_force_bytes_with_bytes(self):
        """Test that bytes are returned as-is."""
        result = force_bytes(b'hello')
        assert result == b'hello'
        assert isinstance(result, bytes)

    def test_force_bytes_with_string(self):
        """Test that string is converted to bytes."""
        result = force_bytes('hello')
        assert result == b'hello'
        assert isinstance(result, bytes)

    def test_force_bytes_with_protected_type_and_strings_only(self):
        """Test that protected types are returned as-is when strings_only=True."""
        result = force_bytes(42, strings_only=True)
        assert result == 42
        assert isinstance(result, int)

    def test_force_bytes_with_none_and_strings_only(self):
        """Test that None is returned as-is when strings_only=True."""
        result = force_bytes(None, strings_only=True)
        assert result is None

    def test_force_bytes_with_memoryview(self):
        """Test that memoryview is converted to bytes."""
        mv = memoryview(b'hello')
        result = force_bytes(mv)
        assert result == b'hello'
        assert isinstance(result, bytes)

    def test_force_bytes_with_int(self):
        """Test that int is converted to bytes."""
        result = force_bytes(42)
        assert result == b'42'
        assert isinstance(result, bytes)
