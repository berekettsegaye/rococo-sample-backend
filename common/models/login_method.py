from dataclasses import dataclass, field
from typing import Optional, List
import string
import json

from werkzeug.security import generate_password_hash, check_password_hash

from rococo.models.login_method import LoginMethodType
from rococo.models.versioned_model import ModelValidationError
from rococo.models import LoginMethod as BaseLoginMethod


@dataclass
class LoginMethod(BaseLoginMethod):

    raw_password: Optional[str] = field(repr=False, default=None)  # Temporary field

    # Two-Factor Authentication fields
    two_factor_secret: Optional[str] = field(default=None)  # Encrypted TOTP secret
    two_factor_enabled: bool = field(default=False)  # Whether 2FA is active
    two_factor_backup_codes: Optional[str] = field(default=None)  # JSON array of hashed backup codes
    two_factor_backup_codes_used: Optional[str] = field(default=None)  # JSON array of used backup code hashes

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.hash_password()

    def hash_password(self):
        if self.raw_password is not None:
            self.validate_raw_password()
            self.password = generate_password_hash(self.raw_password, method='scrypt')
        del self.raw_password

    def validate_raw_password(self):
        allowed_symbols = '!@#$%&()-_[]{};:"./<>?^*`~\',|=+ '
        whitelist = list(string.ascii_uppercase) + list(string.ascii_lowercase) + list(string.digits) + list(allowed_symbols)

        if self.raw_password is None:
            return
        
        unique_v = set(self.raw_password)
        errors = []
        if len(self.raw_password) < 8:
            errors.append("Password must be at least 8 character long")
        if len(self.raw_password) > 100:
            errors.append("Password must be at max 100 character long")
        if not any(x in unique_v for x in string.ascii_uppercase):
            errors.append("Password must contain a uppercase letter")
        if not any(x in unique_v for x in string.ascii_lowercase):
            errors.append("Password must contain a lowercase letter")
        if not any(x in unique_v for x in string.digits):
            errors.append("Password must contain a digit")
        if not any(x in unique_v for x in allowed_symbols):
            errors.append("Password must contain a special character")
        if not all(x in whitelist for x in unique_v):
            errors.append("Password contains an invalid character")

        if errors:
            raise ModelValidationError(errors)

    @property
    def is_oauth_method(self) -> bool:
        """Check if this is an OAuth login method"""
        if not self.method_type:
            return False
        return self.method_type.startswith('oauth-')

    @property
    def oauth_provider_name(self) -> Optional[str]:
        """Get the OAuth provider name from method_type"""
        if self.is_oauth_method:
            return self.method_type.replace('oauth-', '')
        return None

    @property
    def has_two_factor_enabled(self) -> bool:
        """Check if two-factor authentication is enabled and properly configured"""
        return self.two_factor_enabled and self.two_factor_secret is not None

    def is_backup_code_valid(self, code: str) -> bool:
        """
        Check if a backup code is valid and has not been used.

        Args:
            code: The backup code to validate

        Returns:
            True if the code is valid and unused, False otherwise
        """
        if not self.two_factor_backup_codes:
            return False

        try:
            backup_codes = json.loads(self.two_factor_backup_codes)
            used_codes = json.loads(self.two_factor_backup_codes_used) if self.two_factor_backup_codes_used else []

            # Check each backup code hash
            for hashed_code in backup_codes:
                # Skip if this code was already used
                if hashed_code in used_codes:
                    continue
                # Check if the provided code matches this hash
                if check_password_hash(hashed_code, code):
                    return True

            return False
        except (json.JSONDecodeError, TypeError):
            return False

    def mark_backup_code_used(self, code: str) -> bool:
        """
        Mark a backup code as used.

        Args:
            code: The backup code to mark as used

        Returns:
            True if the code was successfully marked as used, False if code not found
        """
        if not self.two_factor_backup_codes:
            return False

        try:
            backup_codes = json.loads(self.two_factor_backup_codes)
            used_codes = json.loads(self.two_factor_backup_codes_used) if self.two_factor_backup_codes_used else []

            # Find the matching backup code hash
            for hashed_code in backup_codes:
                if hashed_code in used_codes:
                    continue
                if check_password_hash(hashed_code, code):
                    used_codes.append(hashed_code)
                    self.two_factor_backup_codes_used = json.dumps(used_codes)
                    return True

            return False
        except (json.JSONDecodeError, TypeError):
            return False

