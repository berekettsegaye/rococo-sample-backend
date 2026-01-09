# Feature: Two-Factor Authentication (2FA)

## Metadata
issue_number: `21`
adw_id: `24f5407d`
issue_json: `{"number": 21, "title": "Implement 2FA", "body": "using adw_plan_build_test_iso.py create two factor authentication."}`

## Feature Description
This feature implements Two-Factor Authentication (2FA) for the rococo-sample-backend application using Time-based One-Time Password (TOTP) authentication. Users will be able to enable 2FA on their accounts, generating a secret key that can be used with authenticator apps (Google Authenticator, Authy, etc.). After enabling 2FA, users will need to provide both their password and a valid TOTP code during login. This adds an additional layer of security beyond traditional email/password authentication.

## User Story
As a security-conscious user
I want to enable two-factor authentication on my account
So that I can protect my account from unauthorized access even if my password is compromised

## Problem Statement
The current authentication system only relies on email/password credentials, which can be compromised through phishing, data breaches, or weak passwords. Once an attacker obtains valid credentials, they have full access to the account with no additional verification steps. This presents a significant security risk, especially for accounts with administrative privileges or sensitive data.

## Solution Statement
Implement TOTP-based 2FA that integrates seamlessly with the existing authentication flow. Users can opt-in to enable 2FA through a dedicated endpoint that generates a secret key and QR code. The secret will be stored securely in the database. During login, users with 2FA enabled will be required to provide a valid 6-digit TOTP code in addition to their credentials. The implementation will use industry-standard libraries (pyotp) and follow best practices for TOTP implementation, including proper secret generation, QR code generation, and time-based validation.

## Relevant Files
Use these files to implement the feature:

- **common/models/person.py** - Person model that needs a new field to store 2FA secret and enabled status
- **common/repositories/person.py** - Repository layer for persisting Person model changes to database
- **common/services/person.py** - Service layer for Person-related business logic, will need methods to enable/disable 2FA
- **common/services/auth.py** - Authentication service that handles login flow, needs modification to validate TOTP codes during login
- **common/helpers/auth.py** - Helper functions for token generation/parsing, may need TOTP validation helpers
- **flask/app/views/auth.py** - API endpoints for authentication, needs new endpoints for 2FA setup and TOTP validation
- **flask/app/helpers/decorators.py** - Contains authentication decorators that may need updates for 2FA flow
- **tests/test_login_method.py** - Existing test file for login methods, good reference for testing patterns
- **flask/pyproject.toml** - Dependencies file where we'll add pyotp and qrcode libraries

### New Files

- **common/helpers/totp.py** - New helper module for TOTP generation, validation, and QR code creation
- **common/services/totp.py** - New service layer for 2FA business logic (enable, disable, verify)
- **tests/test_totp.py** - Unit tests for TOTP helper functions
- **tests/test_2fa_auth.py** - Integration tests for 2FA authentication flow

## Implementation Plan

### Phase 1: Foundation
Add necessary dependencies and create the core TOTP functionality. Update the Person model to store 2FA configuration (secret key and enabled status). Create database migrations to add new columns. Build helper functions for TOTP generation, validation, and QR code generation using industry-standard libraries.

### Phase 2: Core Implementation
Implement service layer methods for enabling and disabling 2FA. Create API endpoints for 2FA setup (generating secret and QR code) and verification. Integrate TOTP validation into the existing login flow, ensuring users with 2FA enabled must provide valid codes. Handle both initial setup and ongoing verification scenarios.

### Phase 3: Integration
Modify the existing login endpoint to check for 2FA status and require TOTP codes when enabled. Ensure backward compatibility for users without 2FA. Add proper error handling and validation messages. Update authentication decorators if needed to support 2FA flow. Test end-to-end flow from 2FA setup through login with TOTP codes.

## Step by Step Tasks

### 1. Install Required Dependencies
- Add `pyotp` library to flask/pyproject.toml for TOTP generation and validation
- Add `qrcode[pil]` library to flask/pyproject.toml for QR code generation
- Run `uv add pyotp qrcode[pil]` in the flask directory to install dependencies
- Verify dependencies are correctly installed

### 2. Create TOTP Helper Module
- Create common/helpers/totp.py with the following functions:
  - `generate_totp_secret()` - generates a random base32 secret
  - `generate_totp_uri(secret, email)` - creates otpauth:// URI for QR codes
  - `verify_totp_code(secret, code)` - validates a TOTP code against a secret
  - `generate_qr_code_base64(uri)` - generates base64-encoded QR code image
- Add comprehensive docstrings explaining each function's purpose and parameters
- Follow existing code patterns in common/helpers/auth.py

### 3. Write Unit Tests for TOTP Helpers
- Create tests/test_totp.py
- Test `generate_totp_secret()` returns valid base32 strings
- Test `generate_totp_uri()` creates properly formatted otpauth URIs
- Test `verify_totp_code()` validates correct codes and rejects incorrect ones
- Test `verify_totp_code()` handles edge cases (expired codes, invalid formats)
- Test `generate_qr_code_base64()` returns valid base64 image data
- Run tests to ensure all helpers work correctly

### 4. Update Person Model with 2FA Fields
- Modify common/models/person.py to add two new fields:
  - `totp_secret` (Optional[str]) - stores the encrypted TOTP secret
  - `is_2fa_enabled` (bool, default=False) - tracks if 2FA is active
- Ensure the fields use proper type hints and defaults
- Follow existing patterns in the Person model

### 5. Update Person Repository
- Verify common/repositories/person.py supports the new Person model fields
- Ensure save_person() method will persist the new fields
- Test that the repository can read/write 2FA fields correctly

### 6. Create 2FA Service Layer
- Create common/services/totp.py with a TotpService class
- Implement `enable_2fa(person)` method that:
  - Generates a new TOTP secret
  - Creates a QR code URI
  - Returns the secret and QR code (but doesn't save yet)
- Implement `confirm_enable_2fa(person, secret, code)` method that:
  - Verifies the provided code against the secret
  - Updates person.totp_secret and person.is_2fa_enabled
  - Saves the person record
- Implement `disable_2fa(person, password)` method that:
  - Verifies the user's password
  - Clears person.totp_secret
  - Sets person.is_2fa_enabled to False
- Implement `verify_2fa_code(person, code)` helper for login flow
- Follow patterns from common/services/auth.py

### 7. Add 2FA Setup API Endpoint
- Add new route in flask/app/views/auth.py: POST /auth/2fa/enable
- Require authentication using @login_required() decorator
- Call TotpService.enable_2fa() to generate secret and QR code
- Return JSON response with:
  - `secret` - the base32 secret for manual entry
  - `qr_code` - base64-encoded QR code image
  - `backup_codes` - future enhancement, can return empty array for now
- Add proper error handling and validation

### 8. Add 2FA Confirmation API Endpoint
- Add new route in flask/app/views/auth.py: POST /auth/2fa/confirm
- Require authentication using @login_required() decorator
- Accept `secret` and `code` in request body
- Call TotpService.confirm_enable_2fa() to verify and save
- Return success/failure response
- Handle invalid codes with appropriate error messages

### 9. Add 2FA Disable API Endpoint
- Add new route in flask/app/views/auth.py: POST /auth/2fa/disable
- Require authentication using @login_required() decorator
- Accept `password` in request body for verification
- Call TotpService.disable_2fa() to turn off 2FA
- Return success/failure response
- Require password confirmation for security

### 10. Modify Login Endpoint for 2FA Validation
- Update the POST /auth/login endpoint in flask/app/views/auth.py
- After validating email/password, check if person.is_2fa_enabled is True
- If 2FA is enabled:
  - Check if `totp_code` is provided in request body
  - If not provided, return a special response indicating 2FA is required
  - If provided, validate using TotpService.verify_2fa_code()
  - Only generate access token if TOTP code is valid
- Maintain backward compatibility for users without 2FA
- Add proper error messages for invalid TOTP codes

### 11. Add 2FA Status Check Endpoint
- Add new route in flask/app/views/auth.py: GET /auth/2fa/status
- Require authentication using @login_required() decorator
- Return JSON response with:
  - `is_2fa_enabled` - boolean indicating if 2FA is active
  - `has_totp_secret` - boolean indicating if secret exists
- Useful for frontend to determine if user has 2FA enabled

### 12. Write Integration Tests for 2FA Flow
- Create tests/test_2fa_auth.py
- Test complete 2FA setup flow:
  - Enable 2FA and receive secret/QR code
  - Confirm with valid TOTP code
  - Verify person.is_2fa_enabled is True
- Test 2FA login flow:
  - Login with email/password/TOTP for 2FA-enabled user
  - Verify access token is generated
  - Test login fails with invalid TOTP code
  - Test login fails without TOTP code when 2FA is enabled
- Test 2FA disable flow:
  - Disable 2FA with password verification
  - Verify person.is_2fa_enabled is False
- Test backward compatibility:
  - Users without 2FA can still login normally
- Follow patterns from existing test files

### 13. Add Edge Case Tests
- Test 2FA setup with invalid confirmation code
- Test 2FA login with expired TOTP code (time-based edge cases)
- Test 2FA disable without valid password
- Test enabling 2FA twice (idempotency)
- Test disabling 2FA when already disabled
- Test login flow interruption scenarios
- Ensure all edge cases return appropriate error messages

### 14. Update Error Handling
- Ensure all 2FA endpoints return consistent error messages
- Add specific error codes for:
  - Invalid TOTP code
  - 2FA required but not provided
  - 2FA not enabled
  - Invalid secret
- Follow existing error handling patterns from common/helpers/exceptions.py

### 15. Run Full Test Suite and Validation
- Execute `pytest tests/ -v` to run all tests
- Verify all existing tests still pass (no regressions)
- Verify all new 2FA tests pass
- Test manual end-to-end flow:
  - Sign up a new user
  - Enable 2FA and scan QR code with authenticator app
  - Confirm 2FA with code from app
  - Logout and login with email/password/TOTP
  - Disable 2FA
  - Login again without TOTP (should work)
- Check test coverage for new 2FA code
- Fix any failing tests or bugs discovered

## Testing Strategy

### Unit Tests
- **TOTP Helper Tests** (tests/test_totp.py):
  - Test secret generation produces valid base32 strings
  - Test URI generation follows otpauth:// spec
  - Test code verification with valid and invalid codes
  - Test QR code generation produces valid base64 images
  - Test time window validation (codes valid for ~30 seconds)

- **Service Layer Tests**:
  - Test TotpService.enable_2fa() generates unique secrets
  - Test TotpService.confirm_enable_2fa() validates correctly
  - Test TotpService.disable_2fa() requires password
  - Test TotpService.verify_2fa_code() with various scenarios

- **Model Tests**:
  - Test Person model with new 2FA fields
  - Test default values for is_2fa_enabled and totp_secret
  - Test field persistence through repository layer

### Integration Tests
- **2FA Setup Flow** (tests/test_2fa_auth.py):
  - POST /auth/2fa/enable returns secret and QR code
  - POST /auth/2fa/confirm with valid code enables 2FA
  - POST /auth/2fa/confirm with invalid code fails
  - GET /auth/2fa/status reflects correct state

- **2FA Login Flow**:
  - POST /auth/login requires TOTP when 2FA is enabled
  - POST /auth/login succeeds with valid email/password/TOTP
  - POST /auth/login fails with invalid TOTP
  - POST /auth/login fails without TOTP when required
  - POST /auth/login works normally for non-2FA users

- **2FA Disable Flow**:
  - POST /auth/2fa/disable with valid password succeeds
  - POST /auth/2fa/disable with invalid password fails
  - Disabling 2FA allows login without TOTP again

### Edge Cases
- Multiple rapid 2FA enable/disable cycles
- Using same TOTP code twice (replay protection)
- Time synchronization edge cases (codes near 30-second boundary)
- Attempting to enable 2FA when already enabled
- Attempting to disable 2FA when already disabled
- Login attempts with malformed TOTP codes (not 6 digits)
- QR code generation with special characters in email
- Secret storage and retrieval edge cases
- Concurrent login attempts during 2FA setup
- Password reset flow with 2FA enabled (should disable 2FA or require TOTP)

## Acceptance Criteria
- [ ] Users can enable 2FA by generating a secret and scanning a QR code
- [ ] Users must confirm 2FA setup by entering a valid TOTP code
- [ ] Users with 2FA enabled must provide TOTP code during login
- [ ] Invalid TOTP codes prevent login and return clear error messages
- [ ] Users without 2FA can still login with just email/password (backward compatible)
- [ ] Users can disable 2FA by providing their password
- [ ] TOTP codes are validated using standard TOTP algorithm (30-second window)
- [ ] QR codes are generated in base64 format for easy frontend integration
- [ ] All 2FA endpoints require authentication (except login)
- [ ] Person model stores TOTP secret securely in database
- [ ] All existing tests pass without regression
- [ ] New test coverage for 2FA functionality is comprehensive (>90%)
- [ ] Error messages are clear and actionable for all failure scenarios
- [ ] 2FA setup, confirmation, login, and disable flows work end-to-end
- [ ] Manual testing with authenticator app (Google Authenticator/Authy) succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd flask && uv add pyotp qrcode[pil]` - Install required dependencies
- `pytest tests/test_totp.py -v` - Run TOTP helper unit tests
- `pytest tests/test_2fa_auth.py -v` - Run 2FA integration tests
- `pytest tests/ -v` - Run full test suite to ensure no regressions
- `pytest tests/ --cov=common --cov=flask --cov-report=term-missing` - Check test coverage (if pytest-cov is available)

## Notes

### Security Considerations
- Store TOTP secrets encrypted in database (future enhancement - for now store base32 directly)
- Consider rate limiting on TOTP verification endpoints to prevent brute force
- Implement backup codes for account recovery (future enhancement)
- Consider requiring TOTP for sensitive operations beyond login (future enhancement)
- Log 2FA enable/disable events for security auditing

### Future Enhancements
- Backup/recovery codes in case user loses authenticator device
- SMS-based 2FA as alternative to TOTP
- Email-based 2FA for less technical users
- WebAuthn/FIDO2 support for hardware security keys
- Require 2FA for all admin users (policy enforcement)
- 2FA setup reminder for users who haven't enabled it
- Trusted devices that skip 2FA for a period

### Implementation Notes
- Use `pyotp` library version ^2.9.0 for TOTP implementation
- Use `qrcode[pil]` library version ^7.4.2 for QR code generation
- TOTP window is 30 seconds (standard)
- TOTP codes are 6 digits (standard)
- Allow 1 step variance for clock skew tolerance (pyotp default)
- QR codes should be 200x200 pixels minimum for readability
- Base32 secrets should be at least 160 bits (32 characters)
- Follow existing patterns from common/services/auth.py for consistency
- Ensure all new code has type hints and docstrings
- No decorators should be used (per project conventions)

### Database Migration
- The Person model changes will require adding columns to the persons table:
  - `totp_secret` VARCHAR(255) NULL
  - `is_2fa_enabled` BOOLEAN DEFAULT FALSE
- Rococo framework should handle migrations automatically through the model changes
- Test with a fresh database to ensure migrations work correctly

### Frontend Integration Notes
- Frontend will need to display QR code image from base64 data
- Frontend should provide manual entry option for secret (not just QR code)
- Login form needs conditional TOTP input field based on initial auth response
- Should implement "trust this device" checkbox (future enhancement)
- Consider showing TOTP code countdown timer (30-second window)
