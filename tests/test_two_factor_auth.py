"""
Unit tests for two-factor authentication helper functions.
"""

import base64
import time
from unittest.mock import patch

import pytest
import pyotp

from common.helpers.two_factor import (
    generate_totp_secret,
    generate_totp_uri,
    generate_qr_code_base64,
    verify_totp_code,
    generate_backup_codes,
    hash_backup_code,
    verify_backup_code
)


class TestTOTPSecretGeneration:
    """Tests for TOTP secret generation."""

    def test_generate_totp_secret_returns_string(self):
        """Test that generate_totp_secret returns a string."""
        secret = generate_totp_secret()
        assert isinstance(secret, str)

    def test_generate_totp_secret_is_base32(self):
        """Test that generated secret is valid base32."""
        secret = generate_totp_secret()
        # base32 alphabet is A-Z and 2-7
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret)

    def test_generate_totp_secret_has_valid_length(self):
        """Test that generated secret has reasonable length."""
        secret = generate_totp_secret()
        # pyotp.random_base32() typically generates 32 character secrets
        assert len(secret) == 32

    def test_generate_totp_secret_is_unique(self):
        """Test that multiple calls generate different secrets."""
        secrets = [generate_totp_secret() for _ in range(10)]
        # All secrets should be unique
        assert len(set(secrets)) == 10


class TestTOTPURIGeneration:
    """Tests for TOTP URI generation."""

    def test_generate_totp_uri_format(self):
        """Test that URI has correct format."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"
        issuer = "Test App"

        uri = generate_totp_uri(secret, email, issuer)

        assert uri.startswith("otpauth://totp/")
        # Email may be URL-encoded (@ becomes %40)
        assert "test" in uri and "example.com" in uri
        assert "Test" in uri and "App" in uri
        assert secret in uri

    def test_generate_totp_uri_with_special_characters(self):
        """Test URI generation with special characters in email/issuer."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test+tag@example.com"
        issuer = "Test App & Co."

        uri = generate_totp_uri(secret, email, issuer)

        assert "otpauth://totp/" in uri
        # Special characters should be URL-encoded or handled properly


class TestQRCodeGeneration:
    """Tests for QR code generation."""

    def test_generate_qr_code_returns_base64(self):
        """Test that QR code is returned as base64 string."""
        uri = "otpauth://totp/Test:test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"
        qr_code = generate_qr_code_base64(uri)

        assert isinstance(qr_code, str)
        # Should be valid base64
        try:
            base64.b64decode(qr_code)
        except Exception:
            pytest.fail("QR code is not valid base64")

    def test_generate_qr_code_is_png(self):
        """Test that generated QR code is a PNG image."""
        uri = "otpauth://totp/Test:test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"
        qr_code = generate_qr_code_base64(uri)

        # Decode and check PNG signature
        img_bytes = base64.b64decode(qr_code)
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        assert img_bytes[:8] == b'\x89PNG\r\n\x1a\n'

    def test_generate_qr_code_different_for_different_uris(self):
        """Test that different URIs produce different QR codes."""
        uri1 = "otpauth://totp/Test:test1@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"
        uri2 = "otpauth://totp/Test:test2@example.com?secret=ABCDEFGHIJKLMNOP&issuer=Test"

        qr1 = generate_qr_code_base64(uri1)
        qr2 = generate_qr_code_base64(uri2)

        assert qr1 != qr2


class TestTOTPVerification:
    """Tests for TOTP code verification."""

    def test_verify_totp_code_with_valid_code(self):
        """Test verification with a valid TOTP code."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()

        assert verify_totp_code(secret, code) is True

    def test_verify_totp_code_with_invalid_code(self):
        """Test verification with an invalid TOTP code."""
        secret = generate_totp_secret()

        assert verify_totp_code(secret, "000000") is False

    def test_verify_totp_code_with_wrong_length(self):
        """Test verification fails with wrong code length."""
        secret = generate_totp_secret()

        assert verify_totp_code(secret, "12345") is False  # Too short
        assert verify_totp_code(secret, "1234567") is False  # Too long

    def test_verify_totp_code_with_non_numeric(self):
        """Test verification fails with non-numeric code."""
        secret = generate_totp_secret()

        assert verify_totp_code(secret, "abcdef") is False
        assert verify_totp_code(secret, "12345a") is False

    def test_verify_totp_code_with_empty_string(self):
        """Test verification fails with empty string."""
        secret = generate_totp_secret()

        assert verify_totp_code(secret, "") is False

    def test_verify_totp_code_with_none(self):
        """Test verification fails with None."""
        secret = generate_totp_secret()

        assert verify_totp_code(secret, None) is False

    def test_verify_totp_code_with_time_window(self):
        """Test verification works within time window."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)

        # Get code from previous time step
        previous_code = totp.at(time.time() - 30)

        # Should verify with window=1
        assert verify_totp_code(secret, previous_code, valid_window=1) is True

    def test_verify_totp_code_outside_window(self):
        """Test verification fails outside time window."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)

        # Get code from 2 steps ago (60 seconds)
        old_code = totp.at(time.time() - 60)

        # Should fail with window=1 (only checks ±30 seconds)
        assert verify_totp_code(secret, old_code, valid_window=1) is False


class TestBackupCodeGeneration:
    """Tests for backup code generation."""

    def test_generate_backup_codes_returns_list(self):
        """Test that generate_backup_codes returns a list."""
        codes = generate_backup_codes()
        assert isinstance(codes, list)

    def test_generate_backup_codes_default_count(self):
        """Test that default generates 10 codes."""
        codes = generate_backup_codes()
        assert len(codes) == 10

    def test_generate_backup_codes_custom_count(self):
        """Test that custom count works."""
        codes = generate_backup_codes(count=5)
        assert len(codes) == 5

        codes = generate_backup_codes(count=20)
        assert len(codes) == 20

    def test_generate_backup_codes_length(self):
        """Test that backup codes are 8 characters long."""
        codes = generate_backup_codes()
        for code in codes:
            assert len(code) == 8

    def test_generate_backup_codes_alphanumeric(self):
        """Test that backup codes are alphanumeric uppercase."""
        codes = generate_backup_codes()
        for code in codes:
            # Should only contain A-Z and 0-9
            assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in code)

    def test_generate_backup_codes_are_different(self):
        """Test that all generated codes are unique."""
        codes = generate_backup_codes(count=20)
        # All codes should be unique
        assert len(set(codes)) == 20


class TestBackupCodeHashing:
    """Tests for backup code hashing and verification."""

    def test_hash_backup_code_returns_string(self):
        """Test that hash_backup_code returns a string."""
        code = "ABC12345"
        hashed = hash_backup_code(code)
        assert isinstance(hashed, str)

    def test_hash_backup_code_different_for_different_codes(self):
        """Test that different codes produce different hashes."""
        code1 = "ABC12345"
        code2 = "XYZ67890"

        hash1 = hash_backup_code(code1)
        hash2 = hash_backup_code(code2)

        assert hash1 != hash2

    def test_hash_backup_code_same_code_different_hashes(self):
        """Test that same code hashed twice produces different hashes (salt)."""
        code = "ABC12345"

        hash1 = hash_backup_code(code)
        hash2 = hash_backup_code(code)

        # Due to salting, hashes should be different
        assert hash1 != hash2

    def test_verify_backup_code_with_valid_code(self):
        """Test verification with correct backup code."""
        code = "ABC12345"
        hashed = hash_backup_code(code)

        assert verify_backup_code(code, hashed) is True

    def test_verify_backup_code_with_invalid_code(self):
        """Test verification with incorrect backup code."""
        code = "ABC12345"
        hashed = hash_backup_code(code)

        assert verify_backup_code("WRONG123", hashed) is False

    def test_verify_backup_code_with_empty_code(self):
        """Test verification fails with empty code."""
        hashed = hash_backup_code("ABC12345")

        assert verify_backup_code("", hashed) is False

    def test_verify_backup_code_with_empty_hash(self):
        """Test verification fails with empty hash."""
        assert verify_backup_code("ABC12345", "") is False

    def test_verify_backup_code_with_none_values(self):
        """Test verification fails with None values."""
        hashed = hash_backup_code("ABC12345")

        assert verify_backup_code(None, hashed) is False
        assert verify_backup_code("ABC12345", None) is False
        assert verify_backup_code(None, None) is False

    def test_verify_backup_code_case_sensitive(self):
        """Test that backup code verification is case-sensitive."""
        code = "ABC12345"
        hashed = hash_backup_code(code)

        # Lowercase version should not match
        assert verify_backup_code("abc12345", hashed) is False
