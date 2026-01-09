from typing import Tuple, Optional
from werkzeug.security import check_password_hash

from common.models import Person, LoginMethod
from common.helpers.totp import (
    generate_totp_secret,
    generate_totp_uri,
    generate_qr_code_base64,
    verify_totp_code
)
from common.helpers.exceptions import InputValidationError, APIException


class TotpService:
    """Service for handling Two-Factor Authentication (2FA) operations."""

    def __init__(self, config):
        self.config = config

        from common.services import PersonService, LoginMethodService, EmailService
        self.person_service = PersonService(config)
        self.login_method_service = LoginMethodService(config)
        self.email_service = EmailService(config)

    def enable_2fa(self, person: Person) -> Tuple[str, str, str]:
        """
        Generate TOTP secret and QR code for 2FA setup.

        This method generates a new TOTP secret and creates a QR code URI.
        It does NOT save the secret to the database yet - that happens in confirm_enable_2fa.

        Args:
            person: The Person object for whom to enable 2FA

        Returns:
            Tuple[str, str, str]: (secret, qr_code_base64, uri) - The TOTP secret,
                                  base64-encoded QR code image, and the otpauth URI
        """
        if not person:
            raise APIException("Person not found.")

        # Get person's email for the QR code
        email_obj = self.email_service.get_email_by_person_id(person.entity_id)
        if not email_obj:
            raise APIException("No email found for this user.")

        # Generate new TOTP secret
        secret = generate_totp_secret()

        # Generate URI for QR code
        uri = generate_totp_uri(secret, email_obj.email)

        # Generate QR code image
        qr_code = generate_qr_code_base64(uri)

        return secret, qr_code, uri

    def confirm_enable_2fa(self, person: Person, secret: str, code: str) -> Person:
        """
        Confirm and activate 2FA by verifying a TOTP code.

        This method verifies that the user can generate valid TOTP codes with the secret,
        then saves the secret to the database and enables 2FA for the account.

        Args:
            person: The Person object to enable 2FA for
            secret: The TOTP secret to verify and save
            code: The TOTP code to verify

        Returns:
            Person: The updated Person object with 2FA enabled

        Raises:
            InputValidationError: If the TOTP code is invalid
            APIException: If person is not found
        """
        if not person:
            raise APIException("Person not found.")

        if not secret or not code:
            raise InputValidationError("Secret and verification code are required.")

        # Verify the provided code against the secret
        if not verify_totp_code(secret, code):
            raise InputValidationError("Invalid verification code. Please try again.")

        # Save the secret and enable 2FA
        person.totp_secret = secret
        person.is_2fa_enabled = True

        # Save to database
        person = self.person_service.save_person(person)

        return person

    def disable_2fa(self, person: Person, password: str) -> Person:
        """
        Disable 2FA for a user after verifying their password.

        Args:
            person: The Person object to disable 2FA for
            password: The user's password for verification

        Returns:
            Person: The updated Person object with 2FA disabled

        Raises:
            InputValidationError: If password is invalid or 2FA is not enabled
            APIException: If person or login method is not found
        """
        if not person:
            raise APIException("Person not found.")

        if not person.is_2fa_enabled:
            raise InputValidationError("2FA is not enabled for this account.")

        if not password:
            raise InputValidationError("Password is required to disable 2FA.")

        # Get person's email to verify password
        email_obj = self.email_service.get_email_by_person_id(person.entity_id)
        if not email_obj:
            raise APIException("No email found for this user.")

        # Get login method to verify password
        login_method = self.login_method_service.get_login_method_by_email_id(email_obj.entity_id)
        if not login_method:
            raise APIException("Login method not found.")

        # Verify password
        if not login_method.password or not check_password_hash(login_method.password, password):
            raise InputValidationError("Invalid password.")

        # Disable 2FA and clear secret
        person.totp_secret = None
        person.is_2fa_enabled = False

        # Save to database
        person = self.person_service.save_person(person)

        return person

    def verify_2fa_code(self, person: Person, code: str) -> bool:
        """
        Verify a TOTP code for a person with 2FA enabled.

        This is used during login to verify the second factor.

        Args:
            person: The Person object to verify the code for
            code: The TOTP code to verify

        Returns:
            bool: True if the code is valid, False otherwise

        Raises:
            APIException: If 2FA is not enabled for this person
        """
        if not person:
            return False

        if not person.is_2fa_enabled or not person.totp_secret:
            raise APIException("2FA is not enabled for this account.")

        return verify_totp_code(person.totp_secret, code)

    def get_2fa_status(self, person: Person) -> dict:
        """
        Get the 2FA status for a person.

        Args:
            person: The Person object to check status for

        Returns:
            dict: Dictionary with 2FA status information
        """
        if not person:
            return {
                "is_2fa_enabled": False,
                "has_totp_secret": False
            }

        return {
            "is_2fa_enabled": person.is_2fa_enabled,
            "has_totp_secret": person.totp_secret is not None
        }
