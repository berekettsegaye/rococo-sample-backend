# Feature: Implement Two-Factor Authentication (2FA)

## Metadata
issue_number: `21`
adw_id: `60a42740`
issue_json: `{"number": 21, "title": "Implement 2FA", "body": "using adw_plan_build_test_iso.py create two factor authentication."}`

## Feature Description
Implement Two-Factor Authentication (2FA) using Time-based One-Time Password (TOTP) to add an extra layer of security to user accounts. Users will be able to enable 2FA on their accounts, requiring them to provide a verification code from an authenticator app (like Google Authenticator or Authy) in addition to their password during login. This feature will support both email/password and OAuth authentication flows, providing account recovery mechanisms and allowing users to enable/disable 2FA at will.

## User Story
As a user
I want to enable two-factor authentication on my account
So that I can add an extra layer of security and protect my account from unauthorized access even if my password is compromised

## Problem Statement
The current authentication system relies solely on email/password or OAuth providers for user authentication. While OAuth provides reasonable security, email/password accounts are vulnerable to credential theft, phishing attacks, and brute force attempts. There is no additional verification layer to protect accounts even when credentials are compromised. Users have no way to add an extra security layer to their accounts, leaving them exposed to security threats.

## Solution Statement
Implement TOTP-based two-factor authentication that integrates seamlessly with the existing authentication system. The solution will:
- Add a `two_factor_secret` field to the Person model to store encrypted TOTP secrets
- Add `two_factor_enabled` flag to Person model to track 2FA status
- Provide API endpoints for enabling/disabling 2FA
- Modify the login flow to verify TOTP codes when 2FA is enabled
- Generate QR codes for easy setup with authenticator apps
- Provide backup codes for account recovery
- Support 2FA for both email/password and OAuth authentication methods

## Relevant Files
Use these files to implement the feature:

- `common/models/person.py` - Person model extending from BasePerson
  - Will need to add two_factor_secret and two_factor_enabled fields
  - Core model representing users in the system

- `common/services/auth.py` - AuthService handling authentication logic
  - Contains login_user_by_email_password and login_user_by_oauth methods
  - Will need to add 2FA verification in login flows
  - Will need methods to enable/disable 2FA

- `common/helpers/auth.py` - Auth helper functions for token generation
  - Contains generate_access_token function
  - May need to add 2FA-related token claims

- `flask/app/views/auth.py` - Auth API endpoints
  - Contains /login, /signup, and OAuth endpoints
  - Will need new endpoints for 2FA setup and verification

- `common/repositories/person.py` - Person repository for database operations
  - Will be used to persist 2FA settings

- `common/services/person.py` - PersonService for business logic
  - May need methods to update 2FA settings

- `tests/test_login_method.py` - Existing tests for login methods
  - Pattern reference for creating new 2FA tests

- `flask/pyproject.toml` - Python dependencies
  - Will need to add pyotp library for TOTP generation
  - Will need qrcode library for QR code generation

### New Files

- `common/models/two_factor_backup_code.py` - Model for storing backup codes
  - Store hashed backup codes for account recovery
  - Track usage of backup codes

- `common/repositories/two_factor_backup_code.py` - Repository for backup codes
  - CRUD operations for backup codes

- `common/services/two_factor.py` - Service for 2FA operations
  - Generate TOTP secrets
  - Verify TOTP codes
  - Generate and verify backup codes
  - Generate QR codes for authenticator app setup

- `tests/test_two_factor.py` - Unit tests for 2FA functionality
  - Test TOTP generation and verification
  - Test backup code generation and verification
  - Test 2FA enable/disable flows

- `tests/test_two_factor_auth.py` - Integration tests for 2FA auth flows
  - Test login with 2FA enabled
  - Test 2FA setup flow
  - Test backup code recovery

- `flask/app/migrations/0000000006_0000000005_migration.py` - Database migration
  - Add two_factor_secret column to Person table
  - Add two_factor_enabled column to Person table
  - Create two_factor_backup_codes table

## Implementation Plan

### Phase 1: Foundation
Establish the data model and core infrastructure for 2FA by adding database schema changes, installing required libraries (pyotp for TOTP, qrcode for QR generation), and creating the basic service layer for 2FA operations. This phase focuses on the foundational pieces needed before implementing the user-facing features.

### Phase 2: Core Implementation
Build the core 2FA functionality including TOTP secret generation, code verification, backup code generation and management, and QR code generation. Create the TwoFactorService to handle all 2FA-related business logic and integrate it with the existing AuthService for seamless authentication flows.

### Phase 3: Integration
Integrate 2FA into the existing authentication flows by modifying login endpoints to check for 2FA requirements, creating new API endpoints for enabling/disabling 2FA, and updating the auth service to verify TOTP codes during login. Add comprehensive error handling and ensure backward compatibility with existing authentication flows.

## Step by Step Tasks

### Create database migration for 2FA schema changes
- Create migration file `flask/app/migrations/0000000006_0000000005_migration.py`
- Add `two_factor_secret` column (encrypted text, nullable) to Person table
- Add `two_factor_enabled` column (boolean, default false) to Person table
- Create `two_factor_backup_codes` table with columns:
  - entity_id (primary key)
  - person_id (foreign key to Person)
  - code_hash (text, hashed backup code)
  - used (boolean, default false)
  - created_at (timestamp)
  - used_at (timestamp, nullable)
- Add indexes on person_id and used columns for backup codes table

### Install required Python dependencies
- Add `pyotp` to `flask/pyproject.toml` for TOTP generation and verification
- Add `qrcode[pil]` to `flask/pyproject.toml` for QR code generation
- Add `cryptography` to `flask/pyproject.toml` for encrypting 2FA secrets (if not already present)
- Run dependency installation to update lock file

### Create TwoFactorBackupCode model
- Create `common/models/two_factor_backup_code.py`
- Define TwoFactorBackupCode model extending rococo base model
- Add fields: person_id, code_hash, used, used_at
- Add method to verify backup code against hash
- Add property to check if code is unused

### Create TwoFactorBackupCode repository
- Create `common/repositories/two_factor_backup_code.py`
- Extend BaseRepository with MODEL = TwoFactorBackupCode
- Add method to get all unused backup codes for a person
- Add method to mark backup code as used

### Create TwoFactorService
- Create `common/services/two_factor.py`
- Initialize service with config and TwoFactorBackupCodeRepository
- Implement `generate_totp_secret()` method to create random base32 secret
- Implement `verify_totp_code(secret, code)` method using pyotp
- Implement `generate_qr_code_uri(secret, email)` method for authenticator app setup
- Implement `generate_backup_codes(person_id, count=10)` method to create recovery codes
- Implement `verify_backup_code(person_id, code)` method to check and mark code as used
- Implement `get_unused_backup_codes_count(person_id)` method
- Add proper error handling and logging

### Update Person model for 2FA fields
- Update `common/models/person.py` to add two_factor_secret field (optional string)
- Add two_factor_enabled field (boolean, default False)
- Add property `has_two_factor_enabled` to check 2FA status
- Ensure fields are properly serialized in as_dict() method

### Create unit tests for TwoFactorService
- Create `tests/test_two_factor.py`
- Test TOTP secret generation returns valid base32 string
- Test TOTP code verification with valid and invalid codes
- Test TOTP code verification with expired codes
- Test QR code URI generation format
- Test backup code generation creates correct number of codes
- Test backup codes are properly hashed
- Test backup code verification marks code as used
- Test backup code can only be used once
- Test unused backup codes count

### Update AuthService to support 2FA in login flows
- Update `common/services/auth.py` to import TwoFactorService
- Add `verify_two_factor_code` method that checks TOTP or backup code
- Update `login_user_by_email_password` to check if person has 2FA enabled
- If 2FA enabled, require totp_code parameter and verify it before generating token
- Update `login_user_by_oauth` to check if person has 2FA enabled for OAuth users
- Add proper error messages for invalid 2FA codes
- Add logging for 2FA verification attempts

### Create API endpoint to enable 2FA
- Add new route `/auth/2fa/enable` in `flask/app/views/auth.py`
- Require authentication via @login_required decorator
- Generate new TOTP secret using TwoFactorService
- Generate QR code URI for the secret
- Generate backup codes
- Return QR code URI, secret (for manual entry), and backup codes
- Do not enable 2FA yet (require verification first)

### Create API endpoint to verify and activate 2FA
- Add new route `/auth/2fa/verify` in `flask/app/views/auth.py`
- Require authentication via @login_required decorator
- Accept totp_code and secret in request body
- Verify the TOTP code against the provided secret
- If valid, update person's two_factor_enabled to true and save two_factor_secret
- Return success message
- If invalid, return error without saving

### Create API endpoint to disable 2FA
- Add new route `/auth/2fa/disable` in `flask/app/views/auth.py`
- Require authentication via @login_required decorator
- Require password or current TOTP code for verification
- Clear person's two_factor_secret and set two_factor_enabled to false
- Delete all backup codes for the person
- Return success message

### Create API endpoint to get 2FA status
- Add new route `/auth/2fa/status` in `flask/app/views/auth.py`
- Require authentication via @login_required decorator
- Return whether 2FA is enabled for current user
- Return count of remaining backup codes if 2FA is enabled

### Create API endpoint to regenerate backup codes
- Add new route `/auth/2fa/backup-codes/regenerate` in `flask/app/views/auth.py`
- Require authentication via @login_required decorator
- Require current TOTP code for verification
- Delete all existing backup codes
- Generate new set of backup codes
- Return new backup codes

### Update login endpoint to handle 2FA
- Update `/auth/login` route in `flask/app/views/auth.py`
- Modify to accept optional `totp_code` parameter
- After email/password validation, check if user has 2FA enabled
- If 2FA enabled and no totp_code provided, return special response indicating 2FA required
- If 2FA enabled and totp_code provided, verify code before generating access token
- If verification fails, return appropriate error message
- Add rate limiting considerations for 2FA code attempts

### Update OAuth login endpoint to handle 2FA
- Update OAuth exchange endpoint in `flask/app/views/auth.py`
- After OAuth authentication, check if user has 2FA enabled
- If 2FA enabled, return response indicating 2FA required with session token
- Create temporary session token that can be exchanged for access token after 2FA
- Add separate endpoint `/auth/2fa/complete-oauth` to complete OAuth login with 2FA
- Verify TOTP code and exchange session token for access token

### Create integration tests for 2FA authentication flows
- Create `tests/test_two_factor_auth.py`
- Test complete 2FA setup flow: enable → verify → activate
- Test login with 2FA enabled using valid TOTP code
- Test login with 2FA enabled using invalid TOTP code
- Test login with 2FA using backup code
- Test backup code becomes invalid after use
- Test 2FA disable flow with password verification
- Test 2FA status endpoint
- Test backup code regeneration
- Test OAuth login with 2FA enabled
- Test rate limiting on 2FA verification attempts

### Add 2FA error handling and edge cases
- Add error handling in TwoFactorService for invalid secrets
- Add validation for TOTP code format (6 digits)
- Handle clock drift in TOTP verification (allow 1-step window)
- Add proper error messages for all failure scenarios
- Handle case where backup codes are exhausted
- Add logging for security events (failed 2FA attempts, backup code usage)

### Update documentation and add logging
- Add comments to new 2FA-related code
- Log 2FA enablement and disablement events
- Log 2FA verification attempts (success and failure)
- Log backup code usage
- Ensure no sensitive data (secrets, codes) are logged

### Run validation commands to ensure zero regressions
- Run `pytest tests/ -v` to execute all tests
- Verify all existing tests pass
- Verify new 2FA tests pass
- Check for any migration issues
- Manually test login flow with and without 2FA
- Test OAuth flow with 2FA enabled
- Verify backward compatibility with existing accounts

## Testing Strategy

### Unit Tests
- TwoFactorService methods (generate secret, verify code, backup codes)
- TwoFactorBackupCode model (verification, usage tracking)
- Person model 2FA-related properties
- TOTP generation and verification with various inputs
- QR code URI format validation
- Backup code hashing and verification
- Edge cases: expired codes, invalid formats, used backup codes

### Integration Tests
- Complete 2FA setup flow from enable to activation
- Login with 2FA enabled (email/password)
- Login with 2FA enabled (OAuth)
- 2FA verification with TOTP codes
- 2FA verification with backup codes
- Backup code exhaustion and regeneration
- 2FA disable flow
- Concurrent login attempts with 2FA
- Session management with 2FA

### Edge Cases
- User attempts to enable 2FA when already enabled
- User attempts to verify with expired TOTP code
- User attempts to use already-used backup code
- User attempts to login without providing TOTP code when 2FA enabled
- User provides invalid TOTP code format
- Clock drift scenarios (TOTP time window)
- Multiple failed 2FA verification attempts (rate limiting)
- User loses access to authenticator app (backup code recovery)
- OAuth user enables 2FA then attempts OAuth login
- Database connection failures during 2FA operations

## Acceptance Criteria
- Users can enable 2FA on their accounts and receive a QR code for authenticator apps
- Users must verify a TOTP code before 2FA is activated on their account
- Users can scan QR code with Google Authenticator, Authy, or similar apps
- Login flow requires TOTP code when 2FA is enabled for email/password accounts
- Login flow requires TOTP code when 2FA is enabled for OAuth accounts
- Users receive 10 backup codes when enabling 2FA for account recovery
- Backup codes can only be used once and are marked as used
- Users can regenerate backup codes after verifying current TOTP code
- Users can disable 2FA by providing their password or current TOTP code
- Failed 2FA attempts are logged for security monitoring
- 2FA status endpoint returns whether 2FA is enabled and backup codes remaining
- All existing authentication flows work without regression
- TOTP codes are valid for 30 seconds with 1-step clock drift tolerance
- All tests pass with 100% of 2FA-related code covered
- Database migrations run successfully without data loss
- API returns clear error messages for all 2FA-related failures

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd flask && uv sync` - Install new dependencies (pyotp, qrcode)
- `pytest tests/ -v` - Run all tests to validate the feature works with zero regressions
- `pytest tests/test_two_factor.py -v` - Run 2FA unit tests specifically
- `pytest tests/test_two_factor_auth.py -v` - Run 2FA integration tests specifically
- `pytest tests/ --cov=common/services/two_factor --cov=common/models/two_factor_backup_code --cov-report=term-missing` - Verify test coverage for 2FA code
- `cd .. && docker compose down && docker compose up -d --build` - Rebuild and restart services to apply migrations
- `curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"Password123!"}'` - Manually test login without 2FA
- `curl -X GET http://localhost:5000/api/auth/2fa/status -H "Authorization: Bearer <token>"` - Test 2FA status endpoint

## Notes
- Use `pyotp` library for TOTP implementation as it's well-maintained and widely used
- Use 30-second time step for TOTP (industry standard)
- Allow 1-step window for clock drift (pyotp valid_window parameter)
- Store TOTP secrets encrypted in database using app encryption key
- Backup codes should be generated using cryptographically secure random generator
- Display backup codes only once during setup and regeneration
- Consider adding rate limiting to 2FA verification endpoints to prevent brute force
- QR codes should use otpauth:// URI format for compatibility with authenticator apps
- Person model changes will require database migration - ensure migration is tested
- Consider future enhancement: SMS-based 2FA as alternative to TOTP
- Consider future enhancement: Remember trusted devices to reduce 2FA prompts
- OAuth users should still be able to enable 2FA for additional security
- Frontend will need to handle 2FA required responses and show TOTP input UI
- Document the 2FA setup process for end users in API documentation
