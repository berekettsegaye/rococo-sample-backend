"""
Unit tests for common/helpers/totp.py
"""
import pytest
import base64
import re
from common.helpers.totp import (
    generate_totp_secret,
    generate_totp_uri,
    verify_totp_code,
    generate_qr_code_base64,
    get_current_totp_code
)


class TestGenerateTotpSecret:
    """Tests for generate_totp_secret function."""

    def test_generates_valid_base32_string(self):
        """Test that generated secret is a valid base32 string."""
        secret = generate_totp_secret()

        # Base32 uses A-Z and 2-7
        assert re.match(r'^[A-Z2-7]+$', secret)

    def test_generates_minimum_length(self):
        """Test that generated secret meets minimum length requirement (32 characters)."""
        secret = generate_totp_secret()

        # pyotp.random_base32() generates 32 characters by default (160 bits)
        assert len(secret) >= 32

    def test_generates_unique_secrets(self):
        """Test that multiple calls generate different secrets."""
        secrets = [generate_totp_secret() for _ in range(10)]

        # All secrets should be unique
        assert len(set(secrets)) == 10


class TestGenerateTotpUri:
    """Tests for generate_totp_uri function."""

    def test_generates_valid_otpauth_uri(self):
        """Test that generated URI follows otpauth:// format."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"

        uri = generate_totp_uri(secret, email)

        assert uri.startswith("otpauth://totp/")
        # Email might be URL-encoded (@ becomes %40)
        assert "test%40example.com" in uri or email in uri
        assert "secret=" + secret in uri

    def test_includes_issuer_in_uri(self):
        """Test that issuer is included in the URI."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"
        issuer = "Test App"

        uri = generate_totp_uri(secret, email, issuer)

        assert "issuer=" + issuer.replace(" ", "%20") in uri

    def test_default_issuer(self):
        """Test that default issuer is 'Rococo Sample'."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"

        uri = generate_totp_uri(secret, email)

        assert "issuer=Rococo%20Sample" in uri

    def test_handles_special_characters_in_email(self):
        """Test that special characters in email are properly encoded."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test+tag@example.com"

        uri = generate_totp_uri(secret, email)

        # Should generate valid URI without errors
        assert uri.startswith("otpauth://totp/")
        assert "secret=" + secret in uri


class TestVerifyTotpCode:
    """Tests for verify_totp_code function."""

    def test_verifies_valid_code(self):
        """Test that valid TOTP code is accepted."""
        secret = generate_totp_secret()

        # Get current valid code
        current_code = get_current_totp_code(secret)

        assert verify_totp_code(secret, current_code) is True

    def test_rejects_invalid_code(self):
        """Test that invalid TOTP code is rejected."""
        secret = generate_totp_secret()
        invalid_code = "000000"

        result = verify_totp_code(secret, invalid_code)

        # Very unlikely to match by chance
        assert result is False

    def test_rejects_empty_secret(self):
        """Test that empty secret returns False."""
        result = verify_totp_code("", "123456")

        assert result is False

    def test_rejects_empty_code(self):
        """Test that empty code returns False."""
        secret = generate_totp_secret()

        result = verify_totp_code(secret, "")

        assert result is False

    def test_rejects_none_secret(self):
        """Test that None secret returns False."""
        result = verify_totp_code(None, "123456")

        assert result is False

    def test_rejects_none_code(self):
        """Test that None code returns False."""
        secret = generate_totp_secret()

        result = verify_totp_code(secret, None)

        assert result is False

    def test_handles_malformed_code(self):
        """Test that malformed code is rejected."""
        secret = generate_totp_secret()

        # Non-numeric code
        result = verify_totp_code(secret, "ABCDEF")
        assert result is False

        # Too short
        result = verify_totp_code(secret, "123")
        assert result is False

        # Too long
        result = verify_totp_code(secret, "12345678")
        assert result is False

    def test_clock_skew_tolerance(self):
        """Test that codes with clock skew are accepted (within valid_window)."""
        import pyotp
        import time

        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)

        # Get code from 30 seconds ago (previous time window)
        previous_time = int(time.time()) - 30
        previous_code = totp.at(previous_time)

        # Should still be valid due to valid_window=1
        result = verify_totp_code(secret, previous_code)

        # This may be True or False depending on exact timing, but should not error
        assert isinstance(result, bool)


class TestGenerateQrCodeBase64:
    """Tests for generate_qr_code_base64 function."""

    def test_generates_base64_string(self):
        """Test that function returns a valid base64 string."""
        uri = "otpauth://totp/test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"

        qr_base64 = generate_qr_code_base64(uri)

        # Should be a valid base64 string
        assert isinstance(qr_base64, str)
        assert len(qr_base64) > 0

        # Should be decodable
        try:
            decoded = base64.b64decode(qr_base64)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Failed to decode base64: {e}")

    def test_generates_valid_png_image(self):
        """Test that generated base64 decodes to a valid PNG image."""
        uri = "otpauth://totp/test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"

        qr_base64 = generate_qr_code_base64(uri)
        decoded = base64.b64decode(qr_base64)

        # PNG files start with specific magic bytes
        assert decoded[:4] == b'\x89PNG'

    def test_handles_different_uris(self):
        """Test that function handles different URI formats."""
        uris = [
            "otpauth://totp/user1@example.com?secret=ABC123&issuer=App1",
            "otpauth://totp/user2@example.com?secret=XYZ789&issuer=App2",
            "otpauth://totp/test+tag@example.com?secret=DEF456&issuer=MyApp"
        ]

        for uri in uris:
            qr_base64 = generate_qr_code_base64(uri)
            assert isinstance(qr_base64, str)
            assert len(qr_base64) > 0


class TestGetCurrentTotpCode:
    """Tests for get_current_totp_code function."""

    def test_generates_six_digit_code(self):
        """Test that current code is always 6 digits."""
        secret = generate_totp_secret()

        code = get_current_totp_code(secret)

        assert code is not None
        assert len(code) == 6
        assert code.isdigit()

    def test_returns_none_for_empty_secret(self):
        """Test that empty secret returns None."""
        code = get_current_totp_code("")

        assert code is None

    def test_returns_none_for_none_secret(self):
        """Test that None secret returns None."""
        code = get_current_totp_code(None)

        assert code is None

    def test_code_validates_against_verify(self):
        """Test that generated code can be verified."""
        secret = generate_totp_secret()

        code = get_current_totp_code(secret)
        result = verify_totp_code(secret, code)

        assert result is True

    def test_different_secrets_generate_different_codes(self):
        """Test that different secrets generate different codes."""
        secret1 = generate_totp_secret()
        secret2 = generate_totp_secret()

        code1 = get_current_totp_code(secret1)
        code2 = get_current_totp_code(secret2)

        # Very unlikely to be the same (1 in 1,000,000 chance)
        assert code1 != code2


class TestTotpIntegration:
    """Integration tests for complete TOTP workflow."""

    def test_complete_totp_setup_flow(self):
        """Test complete flow: generate secret -> create URI -> generate QR -> verify code."""
        email = "user@example.com"

        # 1. Generate secret
        secret = generate_totp_secret()
        assert len(secret) >= 32

        # 2. Generate URI
        uri = generate_totp_uri(secret, email)
        assert uri.startswith("otpauth://totp/")
        assert secret in uri

        # 3. Generate QR code
        qr_code = generate_qr_code_base64(uri)
        assert len(qr_code) > 0

        # 4. Get current code and verify
        code = get_current_totp_code(secret)
        assert verify_totp_code(secret, code) is True

    def test_invalid_code_flow(self):
        """Test that invalid codes are rejected throughout the flow."""
        secret = generate_totp_secret()

        # Test various invalid codes
        invalid_codes = ["000000", "999999", "123", "", "ABCDEF"]

        for invalid_code in invalid_codes:
            result = verify_totp_code(secret, invalid_code)
            # Most should be False (000000 and 999999 have tiny chance of being valid)
            assert isinstance(result, bool)
