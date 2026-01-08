# Chore: Generate Tests for 100% Code Coverage

## Metadata
issue_number: `5`
adw_id: `04e2062e`
issue_json: `{"number": 5, "title": "Generate tests", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
Generate comprehensive test coverage for all uncovered code in the rococo-sample-backend project. The current coverage is 77% (1268 covered lines out of 1644 total statements). The goal is to achieve 100% code coverage by writing tests for the following uncovered modules:

**High Priority (Low Coverage <50%):**
- `common/services/auth.py` (15% coverage, 137 uncovered lines)
- `common/helpers/auth.py` (28% coverage, 21 uncovered lines)
- `common/models/email.py` (31% coverage, 11 uncovered lines)
- `common/tasks/send_message.py` (31% coverage, 25 uncovered lines)
- `common/services/person.py` (33% coverage, 14 uncovered lines)
- `common/helpers/string_utils.py` (34% coverage, 25 uncovered lines)
- `flask/app/__init__.py` (30% coverage, 26 uncovered lines)
- `common/services/email.py` (42% coverage, 11 uncovered lines)
- `common/services/login_method.py` (42% coverage, 11 uncovered lines)
- `common/services/organization.py` (44% coverage, 9 uncovered lines)
- `common/services/oauth.py` (22% coverage, 36 uncovered lines)

**Medium Priority (Moderate Coverage 50-90%):**
- `common/repositories/organization.py` (50% coverage, 5 uncovered lines)
- `common/app_logger.py` (76% coverage, 10 uncovered lines)
- `flask/logger.py` (75% coverage, 11 uncovered lines)
- `common/repositories/base.py` (83% coverage, 2 uncovered lines)
- `common/app_config.py` (90% coverage, 5 uncovered lines)
- `tests/conftest.py` (90% coverage, 9 uncovered lines)
- `tests/test_decorators.py` (97% coverage, 8 uncovered lines)

## Relevant Files
Use these files to resolve the chore:

- `tests/conftest.py` - Test fixtures and configuration for pytest, provides database connections and mock objects
- `tests/test_decorators.py` - Existing decorator tests showing testing patterns
- `tests/test_factory.py` - Existing factory tests demonstrating repository mocking patterns
- `tests/test_login_method.py` - Existing login method tests showing model testing approach
- `tests/test_person_org_role_service.py` - Existing service tests demonstrating service testing patterns
- `tests/test_response.py` - Existing response helper tests
- `tests/test_version.py` - Existing version utility tests
- `pyproject.toml` - Contains pytest and coverage configuration including test paths and coverage settings
- `common/services/auth.py` - Main authentication service with signup, login, OAuth, and token management (needs tests)
- `common/helpers/auth.py` - JWT token generation and parsing utilities (needs tests)
- `common/helpers/string_utils.py` - String encoding/decoding utilities (needs tests)
- `common/models/email.py` - Email model (needs tests)
- `common/tasks/send_message.py` - Message sending task for RabbitMQ (needs tests)
- `common/services/person.py` - Person service (needs tests)
- `common/services/email.py` - Email service (needs tests)
- `common/services/login_method.py` - Login method service (needs tests)
- `common/services/organization.py` - Organization service (needs tests)
- `common/services/oauth.py` - OAuth service (needs tests)
- `common/repositories/organization.py` - Organization repository (needs tests)
- `common/repositories/base.py` - Base repository (needs tests)
- `common/app_logger.py` - Application logger configuration (needs tests)
- `flask/app/__init__.py` - Flask app initialization (needs tests)
- `flask/logger.py` - Flask logger configuration (needs tests)
- `common/app_config.py` - Application configuration (needs tests)

### New Files

- `tests/test_auth_helpers.py` - Tests for common/helpers/auth.py JWT functions
- `tests/test_string_utils.py` - Tests for common/helpers/string_utils.py encoding functions
- `tests/test_email_model.py` - Tests for common/models/email.py
- `tests/test_send_message.py` - Tests for common/tasks/send_message.py
- `tests/test_auth_service.py` - Tests for common/services/auth.py authentication flows
- `tests/test_person_service.py` - Tests for common/services/person.py
- `tests/test_email_service.py` - Tests for common/services/email.py
- `tests/test_login_method_service.py` - Tests for common/services/login_method.py
- `tests/test_organization_service.py` - Tests for common/services/organization.py
- `tests/test_oauth_service.py` - Tests for common/services/oauth.py
- `tests/test_organization_repository.py` - Tests for common/repositories/organization.py
- `tests/test_base_repository.py` - Tests for common/repositories/base.py
- `tests/test_app_logger.py` - Tests for common/app_logger.py
- `tests/test_flask_app.py` - Tests for flask/app/__init__.py
- `tests/test_flask_logger.py` - Tests for flask/logger.py
- `tests/test_app_config.py` - Tests for common/app_config.py

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Generate tests for helper utilities (string_utils.py and auth.py)
- Create `tests/test_string_utils.py` to test all string encoding/decoding functions:
  - `normal_url_safe_b64_decode()` - test with valid and invalid base64 strings
  - `normal_url_safe_b64_encode()` - test with various string inputs
  - `is_protected_type()` - test with protected types (None, int, float, Decimal, datetime, date, time) and non-protected types
  - `urlsafe_base64_encode()` - test encoding with padding stripping
  - `urlsafe_base64_decode()` - test decoding with padding restoration and error handling
  - `force_str()` - test with strings, bytes, protected types, and strings_only flag
  - `force_bytes()` - test with bytes, strings, memoryview, protected types, and encoding options
- Create `tests/test_auth_helpers.py` to test JWT token functions:
  - `generate_access_token()` - test with login_method only, with person data, with email data, and with both
  - `parse_access_token()` - test with valid token, expired token, invalid token, and malformed token
  - `create_person_from_token()` - test creating Person object from token data with complete and partial data
  - `create_email_from_token()` - test creating Email object from token data with complete and partial data

### Step 2: Generate tests for models (email.py)
- Create `tests/test_email_model.py` to test Email model:
  - Test Email model instantiation with all fields
  - Test Email model with minimal required fields
  - Test Email model field validation
  - Test Email model serialization/deserialization if applicable
  - Test Email model edge cases (empty strings, special characters in email)

### Step 3: Generate tests for repositories (organization.py and base.py)
- Create `tests/test_organization_repository.py` to test OrganizationRepository:
  - Test `create_organization()` method
  - Test `get_organization_by_id()` method
  - Test `get_organization_by_entity_id()` method
  - Test `update_organization()` method
  - Test error handling for database connection issues
- Create `tests/test_base_repository.py` to test BaseRepository:
  - Test `get_connection()` method
  - Test `close_connection()` method with different connection types
  - Test connection resolver functionality
  - Test connection closer functionality

### Step 4: Generate tests for services (person, email, login_method, organization, oauth)
- Create `tests/test_person_service.py` to test PersonService:
  - Test `create_person()` method
  - Test `get_person_by_id()` method
  - Test `get_person_by_entity_id()` method
  - Test `update_person()` method
  - Test `delete_person()` method
  - Test error handling and validation
- Create `tests/test_email_service.py` to test EmailService:
  - Test `create_email()` method
  - Test `get_email_by_id()` method
  - Test `get_email_by_email_address()` method
  - Test `get_emails_by_person_id()` method
  - Test `update_email()` method
  - Test email validation
- Create `tests/test_login_method_service.py` to test LoginMethodService:
  - Test `create_login_method()` method
  - Test `get_login_method_by_id()` method
  - Test `get_login_method_by_email_id()` method
  - Test `update_login_method()` method
  - Test password hashing integration
- Create `tests/test_organization_service.py` to test OrganizationService:
  - Test `create_organization()` method
  - Test `get_organization_by_id()` method
  - Test `get_organization_by_entity_id()` method
  - Test `update_organization()` method
  - Test organization validation
- Create `tests/test_oauth_service.py` to test OAuthService:
  - Test `get_oauth_authorization_url()` for Google provider
  - Test `get_oauth_authorization_url()` for Microsoft provider
  - Test `exchange_code_for_token()` for both providers
  - Test `get_user_info()` for both providers
  - Test error handling for invalid provider
  - Test error handling for API failures
  - Mock external OAuth API calls

### Step 5: Generate tests for AuthService (auth.py - most complex)
- Create `tests/test_auth_service.py` to test AuthService:
  - Test `signup()` method with new email
  - Test `signup()` method with existing email (should raise error)
  - Test `signup()` method with OAuth-registered email (should raise specific error)
  - Test `login()` method with valid credentials
  - Test `login()` method with invalid credentials
  - Test `login()` method with unverified email
  - Test `oauth_signup()` method for Google
  - Test `oauth_signup()` method for Microsoft
  - Test `oauth_login()` method with existing OAuth user
  - Test `oauth_login()` method with non-existent user
  - Test `verify_email()` method with valid token
  - Test `verify_email()` method with invalid token
  - Test `verify_email()` method with expired token
  - Test `send_verification_email()` method
  - Test `request_password_reset()` method
  - Test `reset_password()` method with valid token
  - Test `reset_password()` method with invalid token
  - Test `change_password()` method
  - Test organization creation flows
  - Test person-organization-role assignments
  - Mock MessageSender for email sending tests
  - Mock all repository interactions

### Step 6: Generate tests for tasks (send_message.py)
- Create `tests/test_send_message.py` to test MessageSender:
  - Test `get_connection()` method
  - Test `close_connection()` method
  - Test `send_message()` method with RabbitMQ
  - Test `send_message()` method with different message types
  - Test connection pooling behavior
  - Test error handling for connection failures
  - Mock RabbitMQ connection using pika library

### Step 7: Generate tests for Flask app initialization (flask/app/__init__.py)
- Create `tests/test_flask_app.py` to test Flask app factory:
  - Test `create_app()` function creates Flask app
  - Test app configuration loading
  - Test blueprint registration
  - Test error handler registration
  - Test CORS configuration
  - Test database connection initialization
  - Test Rollbar integration initialization
  - Mock external dependencies

### Step 8: Generate tests for logging modules (app_logger.py and flask/logger.py)
- Create `tests/test_app_logger.py` to test common/app_logger.py:
  - Test logger initialization
  - Test log level configuration from environment
  - Test Rollbar handler integration
  - Test logging in different environments (dev, prod, test)
  - Test log formatting
- Create `tests/test_flask_logger.py` to test flask/logger.py:
  - Test Flask logger setup
  - Test request logging middleware
  - Test error logging
  - Test log level configuration
  - Mock Flask request context

### Step 9: Generate tests for app configuration (app_config.py)
- Create `tests/test_app_config.py` to test common/app_config.py:
  - Test configuration loading from environment variables
  - Test default values for optional configuration
  - Test configuration validation
  - Test required fields raise errors when missing
  - Test database URL construction
  - Test RabbitMQ configuration
  - Mock environment variables using monkeypatch

### Step 10: Increase coverage in existing test files
- Update `tests/conftest.py` to cover uncovered lines (lines 85, 91, 97, 103, 109-113)
- Update `tests/test_decorators.py` to cover uncovered lines (lines 55, 80, 196, 218, 223, 254, 292, 333)
- Ensure edge cases and error paths are tested

### Step 11: Run validation commands
- Run `pytest tests/ --cov --cov-report=term-missing` to verify 100% coverage is achieved
- Run `pytest tests/ -v` to ensure all tests pass
- Review coverage report to identify any remaining gaps
- If coverage is not 100%, identify missing lines and add targeted tests

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/ -v` - Run all tests to validate they pass with zero failures
- `pytest tests/ --cov --cov-report=term-missing` - Run tests with coverage report to validate 100% coverage is achieved
- `pytest tests/ --cov --cov-report=term-missing | grep "TOTAL.*100%"` - Verify coverage reaches exactly 100%

## Notes
- Follow existing test patterns in `tests/test_factory.py` and `tests/test_decorators.py` for mocking and fixture usage
- Use pytest fixtures from `tests/conftest.py` for database connections and common test objects
- Mock external dependencies (RabbitMQ, OAuth APIs, email sending) to ensure tests are isolated and fast
- Pay special attention to `common/services/auth.py` as it has the most uncovered code (137 lines)
- Use `monkeypatch` fixture for mocking environment variables and configuration
- Use `unittest.mock.patch` or `pytest-mock` for mocking external API calls
- Test both happy paths and error scenarios to ensure comprehensive coverage
- Ensure all edge cases are covered (null values, empty strings, invalid inputs, expired tokens, etc.)
- Run tests frequently during development to catch issues early
- The coverage configuration in `pyproject.toml` includes specific paths - ensure tests cover only the included modules
