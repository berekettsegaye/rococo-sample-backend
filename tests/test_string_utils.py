"""
Unit tests for common/helpers/string_utils.py encoding/decoding utilities.
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
    """Test normal_url_safe_b64_encode and normal_url_safe_b64_decode functions."""

    def test_normal_url_safe_b64_encode(self):
        """Test encoding a string to base64."""
        result = normal_url_safe_b64_encode("test-string")
        assert isinstance(result, str)
        assert result != "test-string"

    def test_normal_url_safe_b64_decode(self):
        """Test decoding a base64 string."""
        encoded = normal_url_safe_b64_encode("test-string")
        decoded = normal_url_safe_b64_decode(encoded)
        assert decoded == "test-string"

    def test_normal_url_safe_b64_encode_decode_roundtrip(self):
        """Test encode/decode roundtrip with various strings."""
        test_strings = [
            "hello world",
            "test@example.com",
            "special-chars!@#$%",
            "123456789",
            "unicode: 你好"
        ]
        for test_str in test_strings:
            encoded = normal_url_safe_b64_encode(test_str)
            decoded = normal_url_safe_b64_decode(encoded)
            assert decoded == test_str


class TestIsProtectedType:
    """Test is_protected_type function."""

    def test_is_protected_type_none(self):
        """Test None is a protected type."""
        assert is_protected_type(None) is True

    def test_is_protected_type_int(self):
        """Test int is a protected type."""
        assert is_protected_type(42) is True
        assert is_protected_type(0) is True
        assert is_protected_type(-10) is True

    def test_is_protected_type_float(self):
        """Test float is a protected type."""
        assert is_protected_type(3.14) is True
        assert is_protected_type(0.0) is True

    def test_is_protected_type_decimal(self):
        """Test Decimal is a protected type."""
        assert is_protected_type(Decimal("10.5")) is True

    def test_is_protected_type_datetime(self):
        """Test datetime is a protected type."""
        assert is_protected_type(datetime.now()) is True

    def test_is_protected_type_date(self):
        """Test date is a protected type."""
        assert is_protected_type(date.today()) is True

    def test_is_protected_type_time(self):
        """Test time is a protected type."""
        assert is_protected_type(time(12, 30, 45)) is True

    def test_is_protected_type_string_not_protected(self):
        """Test string is not a protected type."""
        assert is_protected_type("test") is False

    def test_is_protected_type_list_not_protected(self):
        """Test list is not a protected type."""
        assert is_protected_type([1, 2, 3]) is False

    def test_is_protected_type_dict_not_protected(self):
        """Test dict is not a protected type."""
        assert is_protected_type({"key": "value"}) is False


class TestUrlsafeBase64Encode:
    """Test urlsafe_base64_encode function."""

    def test_urlsafe_base64_encode_with_bytestring(self):
        """Test encoding a bytestring."""
        result = urlsafe_base64_encode(b"test-data")
        assert isinstance(result, str)
        assert result != "test-data"

    def test_urlsafe_base64_encode_strips_padding(self):
        """Test that padding is stripped from encoded result."""
        # String that would have padding
        result = urlsafe_base64_encode(b"a")
        # Should not end with '='
        assert not result.endswith('=')

    def test_urlsafe_base64_encode_various_data(self):
        """Test encoding various byte strings."""
        test_data = [
            b"hello",
            b"test@example.com",
            b"123456789",
            b"\x00\x01\x02\x03"
        ]
        for data in test_data:
            result = urlsafe_base64_encode(data)
            assert isinstance(result, str)
            assert len(result) > 0


class TestUrlsafeBase64Decode:
    """Test urlsafe_base64_decode function."""

    def test_urlsafe_base64_decode_valid_input(self):
        """Test decoding a valid encoded string."""
        encoded = urlsafe_base64_encode(b"test-data")
        decoded = urlsafe_base64_decode(encoded)
        assert decoded == b"test-data"

    def test_urlsafe_base64_decode_with_padding(self):
        """Test decoding handles missing padding correctly."""
        # Encode and decode should work
        original = b"hello world"
        encoded = urlsafe_base64_encode(original)
        decoded = urlsafe_base64_decode(encoded)
        assert decoded == original

    def test_urlsafe_base64_decode_invalid_string(self):
        """Test decoding an invalid string raises ValueError."""
        with pytest.raises(ValueError):
            urlsafe_base64_decode("!!!invalid-base64!!!")

    def test_urlsafe_base64_decode_roundtrip(self):
        """Test encode/decode roundtrip."""
        test_data = [
            b"test",
            b"longer test string",
            b"123",
            b"special-chars-!@#"
        ]
        for data in test_data:
            encoded = urlsafe_base64_encode(data)
            decoded = urlsafe_base64_decode(encoded)
            assert decoded == data


class TestForceStr:
    """Test force_str function."""

    def test_force_str_with_string_input(self):
        """Test force_str with string input returns same string."""
        result = force_str("test string")
        assert result == "test string"
        assert isinstance(result, str)

    def test_force_str_with_bytes_input(self):
        """Test force_str with bytes input converts to string."""
        result = force_str(b"test bytes")
        assert result == "test bytes"
        assert isinstance(result, str)

    def test_force_str_with_bytes_and_encoding(self):
        """Test force_str with different encoding."""
        # UTF-8 encoded bytes
        utf8_bytes = "hello".encode('utf-8')
        result = force_str(utf8_bytes, encoding='utf-8')
        assert result == "hello"

    def test_force_str_with_strings_only_true_and_protected_type(self):
        """Test force_str with strings_only=True and protected type."""
        result = force_str(42, strings_only=True)
        assert result == 42
        assert isinstance(result, int)

        result2 = force_str(None, strings_only=True)
        assert result2 is None

    def test_force_str_with_non_string_input(self):
        """Test force_str with non-string input converts to string."""
        result = force_str(123)
        assert result == "123"
        assert isinstance(result, str)

        result2 = force_str([1, 2, 3])
        assert result2 == "[1, 2, 3]"

    def test_force_str_with_strings_only_false(self):
        """Test force_str with strings_only=False converts everything."""
        result = force_str(42, strings_only=False)
        assert result == "42"
        assert isinstance(result, str)


class TestForceBytes:
    """Test force_bytes function."""

    def test_force_bytes_with_bytes_input(self):
        """Test force_bytes with bytes input returns same bytes."""
        result = force_bytes(b"test bytes")
        assert result == b"test bytes"
        assert isinstance(result, bytes)

    def test_force_bytes_with_string_input(self):
        """Test force_bytes with string input converts to bytes."""
        result = force_bytes("test string")
        assert result == b"test string"
        assert isinstance(result, bytes)

    def test_force_bytes_with_different_encoding(self):
        """Test force_bytes with different encoding."""
        result = force_bytes("hello", encoding='utf-8')
        assert result == b"hello"

        # Test with bytes that need re-encoding
        utf8_bytes = "hello".encode('utf-8')
        result2 = force_bytes(utf8_bytes, encoding='utf-8')
        assert result2 == b"hello"

    def test_force_bytes_with_memoryview_input(self):
        """Test force_bytes with memoryview input."""
        mv = memoryview(b"test data")
        result = force_bytes(mv)
        assert result == b"test data"
        assert isinstance(result, bytes)

    def test_force_bytes_with_strings_only_true_and_protected_type(self):
        """Test force_bytes with strings_only=True and protected type."""
        result = force_bytes(42, strings_only=True)
        assert result == 42
        assert isinstance(result, int)

        result2 = force_bytes(None, strings_only=True)
        assert result2 is None

    def test_force_bytes_with_non_string_input(self):
        """Test force_bytes with non-string input converts to bytes."""
        result = force_bytes(123)
        assert result == b"123"
        assert isinstance(result, bytes)

    def test_force_bytes_encoding_conversion(self):
        """Test force_bytes converts between encodings."""
        # Create UTF-8 bytes
        utf8_bytes = "hello".encode('utf-8')
        # Request latin-1 encoding (should decode utf-8, re-encode as latin-1)
        result = force_bytes(utf8_bytes, encoding='latin-1')
        assert isinstance(result, bytes)
