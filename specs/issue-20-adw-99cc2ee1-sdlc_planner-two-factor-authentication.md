# Feature: Two-Factor Authentication (2FA)

## Metadata
issue_number: `20`
adw_id: `99cc2ee1`
issue_json: `{"number": 20, "title": "2FA", "body": "create two factor authentication"}`

## Feature Description
Implement a comprehensive two-factor authentication (2FA) system that adds an extra layer of security to user accounts. Users will be able to enable 2FA on their accounts using Time-based One-Time Password (TOTP) authentication. When enabled, users must provide both their password and a time-sensitive code from an authenticator app (like Google Authenticator or Authy) to log in. This feature enhances account security by requiring something the user knows (password) and something the user has (authenticator device).

## User Story
As a security-conscious user
I want to enable two-factor authentication on my account
So that my account is protected from unauthorized access even if my password is compromised

## Problem Statement
The current authentication system relies solely on email/password credentials and OAuth providers. While OAuth provides some security benefits, email/password accounts are vulnerable to credential theft, phishing attacks, and brute-force attempts. Users need an additional security layer to protect their accounts, especially for sensitive operations and accounts with elevated privileges.

## Solution Statement
Implement a TOTP-based two-factor authentication system that integrates seamlessly with the existing authentication flow. Users will be able to:
1. Enable 2FA by scanning a QR code with their authenticator app
2. Verify the setup by entering a code from their authenticator
3. Log in using both password and TOTP code when 2FA is enabled
4. Disable 2FA when needed (with proper authentication)
5. Use backup codes in case they lose access to their authenticator device

The solution will extend the existing LoginMethod model to store 2FA secrets, add new API endpoints for 2FA management, and modify the login flow to handle TOTP verification when required.

## Relevant Files
Use these files to implement the feature:

- `common/models/login_method.py` - Extend LoginMethod model to store 2FA configuration (secret key, backup codes, enabled status)
- `common/repositories/login_method.py` - Update repository to handle 2FA-related fields
- `common/services/login_method.py` - Add service methods for 2FA operations
- `common/services/auth.py` - Modify authentication flow to check and verify 2FA codes
- `common/helpers/auth.py` - Add helper functions for TOTP generation, QR code creation, and verification
- `flask/app/views/auth.py` - Add endpoints for 2FA enable, disable, verify, and login with 2FA
- `flask/pyproject.toml` - Add required dependencies (pyotp for TOTP, qrcode for QR generation)
- `common/app_config.py` - Add 2FA-related configuration (issuer name, backup code count)
- `tests/test_login_method.py` - Extend existing tests to cover 2FA functionality
- `docker-compose.yml` - No changes needed, existing services sufficient

### New Files
- `common/helpers/two_factor.py` - New helper module for 2FA-specific utilities (TOTP operations, backup code generation)
- `tests/test_two_factor_auth.py` - Comprehensive test suite for 2FA functionality
- `tests/test_two_factor_endpoints.py` - Integration tests for 2FA API endpoints

## Implementation Plan

### Phase 1: Foundation
Add the necessary infrastructure for 2FA including database schema extensions, configuration, and core cryptographic utilities. This phase establishes the data model and installs required dependencies for TOTP generation and QR code creation.

### Phase 2: Core Implementation
Implement the core 2FA logic including secret generation, TOTP verification, backup code management, and QR code generation. Create service layer methods that handle 2FA enable/disable operations and integrate TOTP verification into the authentication flow.

### Phase 3: Integration
Integrate 2FA into the existing authentication endpoints, add new dedicated 2FA management endpoints, and ensure the login flow seamlessly handles 2FA-enabled accounts. Add comprehensive test coverage for all 2FA scenarios including edge cases.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Install Required Dependencies
- Add `pyotp` library (version ^2.9.0) to `flask/pyproject.toml` for TOTP generation and verification
- Add `qrcode` library (version ^8.0) with pillow support to `flask/pyproject.toml` for QR code generation
- Run `cd flask && uv add pyotp qrcode[pil]` to install the dependencies
- Verify installation by importing both libraries in a test script

### 2. Add 2FA Configuration to App Config
- Add `TWO_FACTOR_ISSUER_NAME` field to `common/app_config.py` Config class (default: "Rococo Sample App")
- Add `TWO_FACTOR_BACKUP_CODE_COUNT` field (default: 10)
- Add `TWO_FACTOR_ENABLED` feature flag (default: True)
- Document each configuration option with inline comments

### 3. Extend LoginMethod Model for 2FA
- Add `two_factor_secret` field (Optional[str]) to store encrypted TOTP secret in `common/models/login_method.py`
- Add `two_factor_enabled` field (bool, default False) to track if 2FA is active
- Add `two_factor_backup_codes` field (Optional[str]) to store hashed backup codes (JSON array stored as string)
- Add `two_factor_backup_codes_used` field (Optional[str]) to track which backup codes have been used
- Add property `has_two_factor_enabled` that returns True if both secret exists and 2FA is enabled
- Add method `is_backup_code_valid(code: str)` to check if a backup code is valid and unused
- Add method `mark_backup_code_used(code: str)` to mark a backup code as used

### 4. Create Two-Factor Authentication Helper Module
- Create new file `common/helpers/two_factor.py`
- Implement `generate_totp_secret()` - generates a new random TOTP secret
- Implement `generate_totp_uri(secret: str, email: str, issuer: str)` - creates otpauth:// URI for QR codes
- Implement `generate_qr_code_base64(uri: str)` - generates QR code as base64-encoded PNG image
- Implement `verify_totp_code(secret: str, code: str, valid_window: int = 1)` - verifies TOTP code with time window tolerance
- Implement `generate_backup_codes(count: int = 10)` - generates random backup codes (8 characters, alphanumeric)
- Implement `hash_backup_code(code: str)` - hashes backup codes using werkzeug.security
- Implement `verify_backup_code(code: str, hashed: str)` - verifies backup code against hash
- Add comprehensive docstrings for all functions
- Add unit tests for each helper function in the same step

### 5. Update LoginMethod Repository
- Update `common/repositories/login_method.py` to handle new 2FA fields in queries
- Ensure `save_login_method` persists all 2FA fields correctly
- Ensure `get_login_method_by_*` methods return 2FA fields
- Test repository methods with 2FA-enabled login methods

### 6. Extend LoginMethod Service
- Add method `enable_two_factor(login_method: LoginMethod, secret: str, backup_codes: List[str])` to `common/services/login_method.py`
- Add method `disable_two_factor(login_method: LoginMethod)` to clear 2FA settings
- Add method `verify_two_factor_code(login_method: LoginMethod, code: str)` to verify TOTP or backup code
- Add method `regenerate_backup_codes(login_method: LoginMethod)` to generate new backup codes
- Implement proper error handling for invalid codes and disabled 2FA

### 7. Update AuthService for 2FA Support
- Modify `login_user_by_email_password` in `common/services/auth.py` to check if 2FA is enabled
- If 2FA is enabled and no code provided, return error indicating 2FA code is required
- If 2FA is enabled and code provided, verify the code before generating access token
- Support both TOTP codes and backup codes during login
- Add method `setup_two_factor(email: str)` to initiate 2FA setup (generates secret and QR)
- Add method `verify_and_enable_two_factor(email: str, code: str)` to complete 2FA setup
- Add method `disable_two_factor_for_user(email: str, password: str)` to disable 2FA with password confirmation

### 8. Add 2FA Management Endpoints
- Add `/auth/2fa/setup` POST endpoint in `flask/app/views/auth.py` (requires authentication)
  - Generates TOTP secret, QR code URI, and backup codes
  - Returns QR code as base64 image, secret (for manual entry), and backup codes
  - Does not enable 2FA yet (requires verification first)
- Add `/auth/2fa/verify-and-enable` POST endpoint (requires authentication)
  - Takes TOTP code as input
  - Verifies code against secret from setup phase
  - If valid, enables 2FA on the account
  - Returns success message
- Add `/auth/2fa/disable` POST endpoint (requires authentication)
  - Requires password confirmation
  - Disables 2FA and clears all 2FA data
  - Returns success message
- Add `/auth/2fa/regenerate-backup-codes` POST endpoint (requires authentication)
  - Requires TOTP code or existing backup code
  - Generates new backup codes
  - Returns new backup codes
- Add `/auth/2fa/status` GET endpoint (requires authentication)
  - Returns whether 2FA is enabled for the current user
  - Returns success message with status

### 9. Modify Login Endpoint for 2FA
- Update `/auth/login` POST endpoint in `flask/app/views/auth.py`
- Add optional `two_factor_code` field to request body schema
- Check if user has 2FA enabled after password validation
- If 2FA enabled and no code provided, return error with `two_factor_required: true` flag
- If 2FA enabled and code provided, verify code before generating token
- Support both 6-digit TOTP codes and 8-character backup codes
- Return appropriate error messages for invalid codes
- Ensure OAuth login flow is not affected by 2FA (OAuth accounts use provider's 2FA)

### 10. Create Comprehensive Unit Tests
- Create `tests/test_two_factor_auth.py` for testing helper functions
  - Test `generate_totp_secret` produces valid base32 secrets
  - Test `verify_totp_code` with valid and invalid codes
  - Test `verify_totp_code` with different time windows
  - Test `generate_backup_codes` produces unique codes
  - Test `hash_backup_code` and `verify_backup_code` work correctly
  - Test `generate_qr_code_base64` produces valid base64 image data
  - Test `generate_totp_uri` creates properly formatted URIs
- Extend `tests/test_login_method.py` to cover 2FA model properties
  - Test `has_two_factor_enabled` property returns correct values
  - Test `is_backup_code_valid` with valid and invalid codes
  - Test `mark_backup_code_used` correctly updates used codes
- Test edge cases: expired codes, reused backup codes, missing secrets

### 11. Create Integration Tests for 2FA Endpoints
- Create `tests/test_two_factor_endpoints.py`
- Test complete 2FA setup flow (setup -> verify -> enable)
- Test login with 2FA enabled using TOTP code
- Test login with 2FA enabled using backup code
- Test login fails with invalid TOTP code
- Test login fails when 2FA required but no code provided
- Test 2FA disable endpoint with password confirmation
- Test backup code regeneration
- Test 2FA status endpoint
- Test that backup codes cannot be reused
- Test that OAuth accounts are not affected by 2FA
- Mock time-sensitive operations to avoid flaky tests

### 12. Add 2FA Documentation
- Update inline code comments to explain 2FA flow
- Add docstrings to all new methods explaining parameters and return values
- Document the 2FA setup process in code comments
- Document backup code usage and regeneration process

### 13. Validation and Testing
- Run `pytest tests/ -v` to ensure all tests pass including new 2FA tests
- Verify zero regressions in existing authentication tests
- Test complete 2FA setup flow manually if needed
- Test edge cases: clock skew, expired codes, reused backup codes
- Verify QR code generation works correctly
- Verify backup code generation produces valid codes
- Ensure OAuth login still works without 2FA interference

## Testing Strategy

### Unit Tests
- **Helper Functions**: Test all TOTP generation, verification, QR code creation, and backup code utilities independently
- **Model Extensions**: Test LoginMethod 2FA properties and methods with various states (enabled/disabled, with/without secrets)
- **Service Layer**: Test AuthService and LoginMethodService 2FA methods with mocked repositories
- **Repository Layer**: Test that 2FA fields are properly persisted and retrieved

### Integration Tests
- **2FA Setup Flow**: Test the complete flow from setup initiation to verification and enablement
- **2FA Login Flow**: Test login with TOTP codes and backup codes for 2FA-enabled accounts
- **2FA Disable Flow**: Test disabling 2FA with password confirmation
- **Backup Code Management**: Test backup code regeneration and validation of used codes
- **Error Handling**: Test all error scenarios (invalid codes, missing codes, disabled 2FA attempts)
- **OAuth Compatibility**: Ensure OAuth login is unaffected by 2FA implementation

### Edge Cases
- Clock skew tolerance (verify TOTP codes within ±30 seconds)
- Reused backup codes are rejected
- Invalid TOTP codes (wrong length, non-numeric, expired)
- Attempting to use 2FA when not enabled
- Attempting to enable 2FA multiple times
- Disabling 2FA without proper authentication
- QR code generation with special characters in email/issuer name
- Backup code exhaustion (all codes used)
- Concurrent login attempts with same TOTP code
- Password change while 2FA is enabled (ensure 2FA persists)

## Acceptance Criteria
- [ ] Users can initiate 2FA setup and receive a QR code and backup codes
- [ ] Users can scan the QR code with authenticator apps (Google Authenticator, Authy, etc.)
- [ ] Users must verify a TOTP code before 2FA is enabled on their account
- [ ] Users with 2FA enabled must provide a valid TOTP code or backup code to log in
- [ ] Users receive clear error messages when 2FA code is required but not provided
- [ ] Users receive clear error messages when provided 2FA code is invalid
- [ ] Users can disable 2FA by providing their password for confirmation
- [ ] Users can regenerate backup codes when needed
- [ ] Backup codes can only be used once and are marked as used
- [ ] The 2FA system tolerates reasonable clock skew (±30 seconds)
- [ ] OAuth login flows are not affected by 2FA (OAuth providers handle their own 2FA)
- [ ] All existing authentication tests continue to pass (zero regressions)
- [ ] New comprehensive test suite for 2FA achieves >90% code coverage
- [ ] QR codes are properly formatted and scannable by standard authenticator apps
- [ ] TOTP secrets are securely stored (never logged or exposed in responses except during setup)
- [ ] Backup codes are securely hashed before storage

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd flask && uv sync` - Install all dependencies including new 2FA libraries
- `pytest tests/test_two_factor_auth.py -v` - Run 2FA helper function unit tests
- `pytest tests/test_two_factor_endpoints.py -v` - Run 2FA endpoint integration tests
- `pytest tests/test_login_method.py -v` - Run extended LoginMethod tests including 2FA
- `pytest tests/ -v` - Run full test suite to validate zero regressions
- `pytest tests/ -v --cov=common/helpers/two_factor --cov=common/services/auth --cov=flask/app/views/auth --cov-report=term-missing` - Verify test coverage for 2FA code

## Notes

### Security Considerations
- TOTP secrets must be stored securely in the database (consider encryption at rest)
- Backup codes must be hashed using werkzeug.security before storage (never store plaintext)
- Rate limiting should be implemented on 2FA verification endpoints to prevent brute force attacks
- Consider implementing account lockout after multiple failed 2FA attempts
- Ensure 2FA secrets are never logged or included in error messages
- Use constant-time comparison for backup code verification to prevent timing attacks

### Dependencies Added
- `pyotp` (version ^2.9.0) - TOTP generation and verification library
- `qrcode[pil]` (version ^8.0) - QR code generation with PIL/Pillow support

### Future Enhancements
- Add support for WebAuthn/FIDO2 as an alternative 2FA method
- Implement SMS-based 2FA as a fallback option
- Add trusted device management (remember this device for 30 days)
- Implement 2FA enforcement at organization level (require all users to enable 2FA)
- Add audit logging for 2FA enable/disable events
- Support for multiple 2FA devices per user
- Add 2FA recovery flow for users who lose both their device and backup codes

### Implementation Notes
- The TOTP implementation uses 6-digit codes with 30-second time steps (industry standard)
- Backup codes are 8 characters (alphanumeric) for ease of typing
- QR codes are generated as base64-encoded PNG images for easy frontend integration
- The time window for TOTP verification is set to ±1 step (±30 seconds) to handle clock skew
- OAuth accounts should NOT require 2FA since OAuth providers handle their own security
- Consider adding a grace period after enabling 2FA before enforcement (optional)
- The login endpoint should return a specific error code when 2FA is required to help frontend distinguish from other authentication errors
