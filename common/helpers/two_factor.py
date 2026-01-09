"""
Two-Factor Authentication Helper Module

This module provides utilities for TOTP-based two-factor authentication including:
- TOTP secret generation
- QR code generation for authenticator apps
- TOTP code verification
- Backup code generation and verification
"""

import base64
import io
import random
import string
from typing import List

import pyotp
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash


def generate_totp_secret() -> str:
    """
    Generate a new random TOTP secret.

    Returns:
        A base32-encoded random secret suitable for TOTP use
    """
    return pyotp.random_base32()


def generate_totp_uri(secret: str, email: str, issuer: str) -> str:
    """
    Generate an otpauth:// URI for QR code generation.

    Args:
        secret: The TOTP secret (base32-encoded)
        email: The user's email address (used as account identifier)
        issuer: The application name displayed in authenticator apps

    Returns:
        An otpauth:// URI string that can be encoded into a QR code
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code_base64(uri: str) -> str:
    """
    Generate a QR code image as a base64-encoded PNG.

    Args:
        uri: The otpauth:// URI to encode in the QR code

    Returns:
        Base64-encoded PNG image data (without data URI prefix)
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret.

    Args:
        secret: The TOTP secret (base32-encoded)
        code: The 6-digit code to verify
        valid_window: Number of time steps to check before/after current time (default: 1)
                     This allows for clock skew tolerance (±30 seconds per step)

    Returns:
        True if the code is valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False

    # TOTP codes should be 6 digits
    if len(code) != 6 or not code.isdigit():
        return False

    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=valid_window)


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate random backup codes for 2FA recovery.

    Args:
        count: Number of backup codes to generate (default: 10)

    Returns:
        A list of unique 8-character alphanumeric backup codes
    """
    codes = []
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9

    for _ in range(count):
        # Generate 8-character code
        code = ''.join(random.choices(characters, k=8))
        codes.append(code)

    return codes


def hash_backup_code(code: str) -> str:
    """
    Hash a backup code for secure storage.

    Args:
        code: The plaintext backup code

    Returns:
        A hashed version of the backup code using scrypt
    """
    return generate_password_hash(code, method='scrypt')


def verify_backup_code(code: str, hashed: str) -> bool:
    """
    Verify a backup code against its hash.

    Args:
        code: The plaintext backup code to verify
        hashed: The hashed backup code to compare against

    Returns:
        True if the code matches the hash, False otherwise
    """
    if not code or not hashed:
        return False
    return check_password_hash(hashed, code)
