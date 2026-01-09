from typing import List
import json

from common.repositories.factory import RepositoryFactory, RepoType
from common.models import LoginMethod
from common.helpers.two_factor import verify_totp_code, hash_backup_code


class LoginMethodService:

    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.login_method_repo = self.repository_factory.get_repository(RepoType.LOGIN_METHOD)

    def save_login_method(self, login_method: LoginMethod):
        login_method = self.login_method_repo.save(login_method)
        return login_method

    def get_login_method_by_email_id(self, email_id: str):
        login_method = self.login_method_repo.get_one({"email_id": email_id})
        return login_method
    
    def get_login_method_by_id(self, entity_id: str):
        login_method = self.login_method_repo.get_one({"entity_id": entity_id})
        return login_method

    def update_password(self, login_method: LoginMethod, password: str) -> LoginMethod:
        login_method.password = password
        return self.login_method_repo.save(login_method)

    def enable_two_factor(self, login_method: LoginMethod, secret: str, backup_codes: List[str]) -> LoginMethod:
        """
        Enable two-factor authentication for a login method.

        Args:
            login_method: The login method to enable 2FA for
            secret: The TOTP secret
            backup_codes: List of plaintext backup codes (will be hashed)

        Returns:
            The updated login method with 2FA enabled
        """
        # Hash all backup codes
        hashed_codes = [hash_backup_code(code) for code in backup_codes]

        # Update login method
        login_method.two_factor_secret = secret
        login_method.two_factor_enabled = True
        login_method.two_factor_backup_codes = json.dumps(hashed_codes)
        login_method.two_factor_backup_codes_used = json.dumps([])

        return self.login_method_repo.save(login_method)

    def disable_two_factor(self, login_method: LoginMethod) -> LoginMethod:
        """
        Disable two-factor authentication for a login method.

        Args:
            login_method: The login method to disable 2FA for

        Returns:
            The updated login method with 2FA disabled
        """
        login_method.two_factor_secret = None
        login_method.two_factor_enabled = False
        login_method.two_factor_backup_codes = None
        login_method.two_factor_backup_codes_used = None

        return self.login_method_repo.save(login_method)

    def verify_two_factor_code(self, login_method: LoginMethod, code: str) -> bool:
        """
        Verify a two-factor authentication code (TOTP or backup code).

        Args:
            login_method: The login method to verify against
            code: The code to verify (6-digit TOTP or 8-character backup code)

        Returns:
            True if the code is valid, False otherwise
        """
        if not login_method.has_two_factor_enabled:
            return False

        # Check if it's a TOTP code (6 digits)
        if len(code) == 6 and code.isdigit():
            return verify_totp_code(login_method.two_factor_secret, code)

        # Check if it's a backup code (8 characters)
        if len(code) == 8:
            is_valid = login_method.is_backup_code_valid(code)
            if is_valid:
                # Mark the backup code as used
                login_method.mark_backup_code_used(code)
                self.login_method_repo.save(login_method)
            return is_valid

        return False

    def regenerate_backup_codes(self, login_method: LoginMethod, new_backup_codes: List[str]) -> LoginMethod:
        """
        Regenerate backup codes for a login method.

        Args:
            login_method: The login method to regenerate codes for
            new_backup_codes: List of new plaintext backup codes (will be hashed)

        Returns:
            The updated login method with new backup codes
        """
        if not login_method.has_two_factor_enabled:
            raise ValueError("Two-factor authentication is not enabled")

        # Hash all backup codes
        hashed_codes = [hash_backup_code(code) for code in new_backup_codes]

        # Update backup codes
        login_method.two_factor_backup_codes = json.dumps(hashed_codes)
        login_method.two_factor_backup_codes_used = json.dumps([])

        return self.login_method_repo.save(login_method)
