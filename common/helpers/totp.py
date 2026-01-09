import pyotp
import qrcode
import io
import base64
from typing import Optional


def generate_totp_secret() -> str:
    """
    Generate a random base32-encoded secret for TOTP.

    Returns:
        str: A base32-encoded secret string suitable for TOTP (minimum 160 bits/32 characters)
    """
    return pyotp.random_base32()


def generate_totp_uri(secret: str, email: str, issuer: str = "Rococo Sample") -> str:
    """
    Generate an otpauth:// URI for TOTP that can be used to generate QR codes.

    Args:
        secret: The base32-encoded TOTP secret
        email: The user's email address (used as the account identifier)
        issuer: The application name to display in authenticator apps (default: "Rococo Sample")

    Returns:
        str: An otpauth:// URI string
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify a TOTP code against a secret.

    Args:
        secret: The base32-encoded TOTP secret
        code: The 6-digit TOTP code to verify

    Returns:
        bool: True if the code is valid, False otherwise
    """
    if not secret or not code:
        return False

    try:
        totp = pyotp.TOTP(secret)
        # valid_window=1 allows codes from 1 step (30 seconds) before/after current time
        # This provides clock skew tolerance
        return totp.verify(code, valid_window=1)
    except Exception:
        return False


def generate_qr_code_base64(uri: str) -> str:
    """
    Generate a base64-encoded QR code image from an otpauth:// URI.

    Args:
        uri: The otpauth:// URI to encode in the QR code

    Returns:
        str: Base64-encoded PNG image of the QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return img_base64


def get_current_totp_code(secret: str) -> Optional[str]:
    """
    Get the current TOTP code for a secret. Useful for testing.

    Args:
        secret: The base32-encoded TOTP secret

    Returns:
        str: The current 6-digit TOTP code, or None if secret is invalid
    """
    if not secret:
        return None

    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception:
        return None
