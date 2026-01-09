# Chore: Generate tests for uncovered code

## Metadata
issue_number: `8`
adw_id: `c104b9bd`
issue_json: `{"number": 8, "title": "Generate tests for uncovered code", "body": "adw_plan_build_test_iso.py\n\nGenerate test for uncovered code. The coverage must reach 100%."}`

## Chore Description
This chore involves generating comprehensive test coverage for the `adw_plan_build_test_iso.py` script and all other uncovered code in the codebase to achieve 100% code coverage. Based on the current coverage report, the following files have significantly low coverage and require tests:

**Priority Files (Below 50% Coverage):**
- `common/services/auth.py` - 15% coverage (137 uncovered lines)
- `common/helpers/auth.py` - 28% coverage (21 uncovered lines)
- `common/helpers/string_utils.py` - 34% coverage (25 uncovered lines)
- `common/models/email.py` - 31% coverage (11 uncovered lines)
- `common/services/email.py` - 42% coverage (11 uncovered lines)
- `common/services/login_method.py` - 42% coverage (11 uncovered lines)
- `common/services/oauth.py` - 22% coverage (36 uncovered lines)
- `common/services/organization.py` - 44% coverage (9 uncovered lines)
- `common/services/person.py` - 33% coverage (14 uncovered lines)
- `common/tasks/send_message.py` - 31% coverage (25 uncovered lines)
- `flask/app/__init__.py` - 30% coverage (26 uncovered lines)

**Secondary Files (50-90% Coverage):**
- `common/repositories/organization.py` - 50% coverage (5 uncovered lines)
- `common/app_logger.py` - 76% coverage (10 uncovered lines)
- `flask/logger.py` - 75% coverage (11 uncovered lines)
- `common/repositories/base.py` - 83% coverage (2 uncovered lines)
- `common/app_config.py` - 90% coverage (5 uncovered lines)
- `tests/conftest.py` - 90% coverage (9 uncovered lines)

The goal is to create comprehensive test suites that cover all edge cases, error conditions, and normal operation paths for these files, ultimately achieving 100% test coverage for the entire codebase.

## Relevant Files
Use these files to resolve the chore:

- `adws/adw_plan_build_test_iso.py` - Main script that needs testing. It orchestrates the ADW workflow by calling plan, build, and test scripts sequentially. Key functionality includes:
  - Command-line argument parsing (issue number and optional ADW ID)
  - Sequential execution of three workflow steps with error handling
  - Automatic ADW ID extraction from state files when not provided
  - Exit code handling and user feedback

- `common/services/auth.py` - Authentication service with extensive uncovered logic including signup, login (email/password and OAuth), password reset, token generation, and email notifications. Requires comprehensive testing.

- `common/helpers/auth.py` - Helper functions for JWT token operations including generation, parsing, and object creation from token data.

- `common/helpers/string_utils.py` - String utility functions for encoding/decoding operations.

- `common/models/email.py` - Email model definition requiring validation tests.

- `common/services/email.py` - Email service CRUD operations.

- `common/services/login_method.py` - Login method service operations.

- `common/services/oauth.py` - OAuth integration service.

- `common/services/organization.py` - Organization service operations.

- `common/services/person.py` - Person service operations.

- `common/tasks/send_message.py` - Message queue sending functionality.

- `flask/app/__init__.py` - Flask application factory with initialization logic.

- `common/repositories/organization.py` - Organization repository data access layer.

- `common/app_logger.py` - Application logging configuration.

- `flask/logger.py` - Flask-specific logging configuration.

- `common/repositories/base.py` - Base repository class with common functionality.

- `common/app_config.py` - Application configuration management.

- `tests/conftest.py` - Pytest configuration and fixtures.

- `tests/test_decorators.py` - Existing test file that can serve as a reference for testing patterns (97% coverage).

- `tests/test_factory.py` - Existing test file demonstrating comprehensive repository testing (100% coverage).

### New Files
- `tests/test_adw_plan_build_test_iso.py` - New test file for the ADW orchestration script
- `tests/test_auth_service.py` - New comprehensive test suite for AuthService
- `tests/test_auth_helpers.py` - New test suite for auth helper functions
- `tests/test_string_utils.py` - New test suite for string utility functions
- `tests/test_email_model.py` - New test suite for Email model
- `tests/test_email_service.py` - New test suite for EmailService
- `tests/test_login_method_service.py` - New test suite for LoginMethodService
- `tests/test_oauth_service.py` - New test suite for OAuthService
- `tests/test_organization_service.py` - New test suite for OrganizationService
- `tests/test_person_service.py` - New test suite for PersonService
- `tests/test_send_message.py` - New test suite for message sending functionality
- `tests/test_flask_app_init.py` - New test suite for Flask app initialization
- `tests/test_organization_repository.py` - New test suite for organization repository
- `tests/test_app_logger.py` - New test suite for app logging
- `tests/test_flask_logger.py` - New test suite for Flask logging
- `tests/test_base_repository.py` - New test suite for base repository
- `tests/test_app_config.py` - New test suite for app configuration

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Analyze existing test patterns and coverage gaps
- Read the existing high-coverage test files (`test_decorators.py`, `test_factory.py`, `test_login_method.py`) to understand testing patterns, mocking strategies, and fixtures used in the project
- Run pytest with coverage to get detailed coverage report showing exact uncovered lines
- Document the specific uncovered lines and edge cases for each file that needs testing

### Step 2: Create tests for helper modules (foundational code)
- Create `tests/test_string_utils.py` to test all string utility functions including encoding/decoding operations, edge cases with empty strings, special characters, and error handling
- Create `tests/test_auth_helpers.py` to test JWT token generation, parsing, expiration handling, invalid token scenarios, and object creation from token data
- Run pytest to verify new tests pass and check coverage improvement for `common/helpers/` modules

### Step 3: Create tests for data models
- Create `tests/test_email_model.py` to test Email model validation, required fields, optional fields, and edge cases
- Run pytest to verify model tests pass and check coverage for `common/models/email.py`

### Step 4: Create tests for repository layer
- Create `tests/test_base_repository.py` to test base repository functionality including common database operations
- Create `tests/test_organization_repository.py` to test organization-specific repository methods
- Run pytest to verify repository tests pass and check coverage improvement

### Step 5: Create tests for service layer (core business logic)
- Create `tests/test_email_service.py` to test email CRUD operations, validation, and error handling
- Create `tests/test_login_method_service.py` to test login method operations including password hashing and validation
- Create `tests/test_person_service.py` to test person CRUD operations
- Create `tests/test_organization_service.py` to test organization operations
- Create `tests/test_oauth_service.py` to test OAuth provider integration, token validation, and user profile mapping
- Run pytest to verify service tests pass and check incremental coverage improvement

### Step 6: Create comprehensive tests for authentication service
- Create `tests/test_auth_service.py` with comprehensive test coverage for:
  - User signup flow (email/password)
  - Login with email/password
  - OAuth login/signup flows
  - Password reset token generation and validation
  - Email sending (welcome emails, password reset emails)
  - Token generation and validation
  - Edge cases: duplicate emails, OAuth vs email/password conflicts, expired tokens, invalid credentials
- Use mocking for external dependencies (email sending, message queue)
- Run pytest to verify AuthService tests pass and check coverage for `common/services/auth.py`

### Step 7: Create tests for messaging and tasks
- Create `tests/test_send_message.py` to test message queue operations, message formatting, error handling, and connection management
- Run pytest to verify messaging tests pass and check coverage for `common/tasks/send_message.py`

### Step 8: Create tests for Flask application initialization
- Create `tests/test_flask_app_init.py` to test Flask app factory function, blueprint registration, configuration loading, database initialization, and error handling
- Run pytest to verify Flask app tests pass and check coverage for `flask/app/__init__.py`

### Step 9: Create tests for logging modules
- Create `tests/test_app_logger.py` to test application logging configuration, log levels, formatters, and handlers
- Create `tests/test_flask_logger.py` to test Flask-specific logging configuration
- Run pytest to verify logging tests pass and check coverage improvement

### Step 10: Create tests for configuration module
- Create `tests/test_app_config.py` to test configuration loading, environment variable parsing, default values, and validation
- Update `tests/conftest.py` to add any missing fixtures needed for 100% coverage
- Run pytest to verify configuration tests pass

### Step 11: Create tests for ADW orchestration script
- Create `tests/test_adw_plan_build_test_iso.py` to test:
  - Command-line argument parsing (valid and invalid inputs)
  - Sequential workflow execution (plan → build → test)
  - Error handling for each step failure
  - ADW ID extraction from state files
  - Exit code behavior
- Use subprocess mocking to test script execution without actually running ADW workflows
- Run pytest to verify ADW script tests pass

### Step 12: Final coverage verification and gap filling
- Run comprehensive pytest with coverage report to identify any remaining uncovered lines
- Add additional test cases to cover any remaining gaps (edge cases, error conditions, branch coverage)
- Ensure all tests are passing and coverage reaches 100% for all target files
- Generate final coverage report showing 100% coverage achievement

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/ -v` - Run all tests to ensure no regressions and all new tests pass
- `pytest tests/ --cov=common --cov=flask --cov=adws --cov-report=term-missing` - Generate coverage report showing 100% coverage for all modules
- `pytest tests/ --cov=common/services/auth.py --cov-report=term-missing` - Verify 100% coverage for auth service
- `pytest tests/ --cov=common/helpers/auth.py --cov-report=term-missing` - Verify 100% coverage for auth helpers
- `pytest tests/ --cov=adws/adw_plan_build_test_iso.py --cov-report=term-missing` - Verify 100% coverage for ADW script
- `pytest tests/ --cov=. --cov-report=html` - Generate HTML coverage report for detailed review

## Notes
- Follow existing test patterns from `test_decorators.py` and `test_factory.py` which demonstrate proper mocking, fixture usage, and comprehensive test coverage
- Use pytest fixtures from `conftest.py` for database connections, app configuration, and common test data
- Mock external dependencies (RabbitMQ, email sending, HTTP requests) to ensure tests are fast and isolated
- Each test file should use descriptive test class names (e.g., `TestAuthServiceSignup`, `TestAuthServiceLogin`) and test method names that clearly describe what is being tested
- Test both happy paths and error conditions for each function
- Use parametrized tests where appropriate to test multiple input scenarios efficiently
- Ensure tests are deterministic and can run in any order
- The ADW script test should mock subprocess calls to avoid actually executing the workflow scripts
- Consider using `unittest.mock.patch` for mocking dependencies and `pytest.raises` for testing exception scenarios
- After each step, verify that coverage is improving and no existing tests are breaking
