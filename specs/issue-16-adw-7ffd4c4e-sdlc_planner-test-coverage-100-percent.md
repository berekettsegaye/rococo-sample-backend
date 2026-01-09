# Chore: Generate test for uncovered code

## Metadata
issue_number: `16`
adw_id: `7ffd4c4e`
issue_json: `{"number": 16, "title": "Generage test for uncovered code", "body": "Generate test for uncovered code. the test coverage must reach 100%\n"}`

## Chore Description
Generate comprehensive test coverage for all uncovered code in the rococo-sample-backend project. The current test coverage is at 77% (376 out of 1644 statements are not covered). The goal is to achieve 100% test coverage by creating tests for all uncovered modules, focusing on:

1. **High-priority uncovered modules** (critical business logic with low coverage):
   - `common/services/auth.py` - 15% coverage (137 uncovered statements)
   - `common/helpers/auth.py` - 28% coverage (21 uncovered statements)
   - `common/helpers/string_utils.py` - 34% coverage (25 uncovered statements)
   - `common/services/oauth.py` - 22% coverage (36 uncovered statements)
   - `common/tasks/send_message.py` - 31% coverage (25 uncovered statements)

2. **Medium-priority uncovered modules**:
   - `common/models/email.py` - 31% coverage (11 uncovered statements)
   - `common/services/email.py` - 42% coverage (11 uncovered statements)
   - `common/services/login_method.py` - 42% coverage (11 uncovered statements)
   - `common/services/organization.py` - 44% coverage (9 uncovered statements)
   - `common/services/person.py` - 33% coverage (14 uncovered statements)

3. **Flask application modules**:
   - `flask/app/__init__.py` - 30% coverage (26 uncovered statements)
   - `flask/logger.py` - 75% coverage (11 uncovered statements)

4. **Supporting modules**:
   - `common/app_config.py` - 90% coverage (5 uncovered statements)
   - `common/app_logger.py` - 76% coverage (10 uncovered statements)
   - `common/repositories/base.py` - 83% coverage (2 uncovered statements)
   - `common/repositories/organization.py` - 50% coverage (5 uncovered statements)
   - `tests/conftest.py` - 90% coverage (9 uncovered statements)

## Relevant Files
Use these files to resolve the chore:

- `pyproject.toml` - Contains pytest and coverage configuration, defines which modules to include in coverage reporting
- `tests/conftest.py` - Contains test fixtures and setup for database connections, repositories, and mocks
- `common/models/*.py` - Data models that need to be tested
- `common/repositories/*.py` - Repository layer for database operations
- `common/services/*.py` - Business logic services (auth, email, person, organization, oauth)
- `common/helpers/*.py` - Helper utilities (auth, string_utils, exceptions)
- `common/tasks/*.py` - Background task handlers (send_message)
- `common/utils/*.py` - Utility functions (version)
- `common/app_config.py` - Application configuration
- `common/app_logger.py` - Logging configuration
- `flask/app/__init__.py` - Flask application factory
- `flask/app/helpers/*.py` - Flask-specific helpers (response, decorators)
- `flask/logger.py` - Flask logger setup
- `tests/*.py` - Existing test files to understand patterns and fixtures

### New Files
- `tests/test_auth_helpers.py` - Tests for `common/helpers/auth.py` token generation and parsing
- `tests/test_string_utils.py` - Tests for `common/helpers/string_utils.py` encoding/decoding functions
- `tests/test_auth_service.py` - Tests for `common/services/auth.py` authentication workflows
- `tests/test_oauth_service.py` - Tests for `common/services/oauth.py` OAuth provider integration
- `tests/test_send_message.py` - Tests for `common/tasks/send_message.py` message queue tasks
- `tests/test_email_model.py` - Tests for `common/models/email.py` email model validation
- `tests/test_email_service.py` - Tests for `common/services/email.py` email operations
- `tests/test_login_method_service.py` - Tests for `common/services/login_method.py` login method operations
- `tests/test_organization_service.py` - Tests for `common/services/organization.py` organization operations
- `tests/test_person_service.py` - Tests for `common/services/person.py` person operations
- `tests/test_organization_repository.py` - Tests for `common/repositories/organization.py` organization data access
- `tests/test_base_repository.py` - Tests for `common/repositories/base.py` base repository functionality
- `tests/test_flask_app.py` - Tests for `flask/app/__init__.py` Flask application factory
- `tests/test_flask_logger.py` - Tests for `flask/logger.py` Flask logging setup
- `tests/test_app_config.py` - Tests for `common/app_config.py` configuration loading
- `tests/test_app_logger.py` - Tests for `common/app_logger.py` logger setup

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create tests for helper modules
Create comprehensive tests for helper utilities that are used across the application:

- Create `tests/test_auth_helpers.py` to test:
  - `generate_access_token()` with various combinations of login_method, person, and email
  - `parse_access_token()` with valid tokens, expired tokens, and invalid tokens
  - `create_person_from_token()` with complete and partial token data
  - `create_email_from_token()` with complete and partial token data
  - Edge cases: missing fields, malformed tokens, expired tokens

- Create `tests/test_string_utils.py` to test:
  - `normal_url_safe_b64_decode()` and `normal_url_safe_b64_encode()` for base64 encoding/decoding
  - `urlsafe_base64_encode()` and `urlsafe_base64_decode()` for URL-safe base64 operations
  - `is_protected_type()` with different object types
  - `force_str()` with strings, bytes, protected types, and various encodings
  - `force_bytes()` with bytes, strings, memoryview, and various encodings
  - Edge cases: invalid base64, encoding errors, special characters

### Step 2: Create tests for model classes
Create tests for model validation and behavior:

- Create `tests/test_email_model.py` to test:
  - Email model instantiation with valid data
  - Email model validation rules
  - Email model property access
  - Edge cases: invalid email formats, missing required fields

### Step 3: Create tests for repository layer
Create tests for database operations:

- Create `tests/test_base_repository.py` to test:
  - BaseRepository initialization
  - Database connection handling
  - Transaction management
  - Error handling for database operations

- Create `tests/test_organization_repository.py` to test:
  - Organization repository CRUD operations
  - Query methods specific to organization repository
  - Edge cases: duplicate organizations, invalid IDs

### Step 4: Create tests for service layer (high priority)
Create comprehensive tests for critical business logic services:

- Create `tests/test_auth_service.py` to test:
  - `signup()` with valid email, first_name, last_name
  - `signup()` with existing email (should raise InputValidationError)
  - `signup()` with email already registered via OAuth (should raise InputValidationError with provider name)
  - `login()` with valid credentials
  - `login()` with invalid credentials
  - `verify_email()` flow
  - `reset_password()` flow
  - `change_password()` flow
  - Token generation and validation
  - Email sending for verification and password reset
  - Edge cases: expired tokens, invalid tokens, missing fields

- Create `tests/test_oauth_service.py` to test:
  - OAuth provider initialization (Google, Microsoft)
  - OAuth authorization URL generation
  - OAuth token exchange
  - User profile retrieval from OAuth providers
  - OAuth signup/login flow
  - Linking existing accounts with OAuth
  - Edge cases: invalid OAuth codes, expired tokens, API errors

### Step 5: Create tests for service layer (medium priority)
Create tests for supporting service modules:

- Create `tests/test_email_service.py` to test:
  - `get_email_by_email_address()` for existing and non-existing emails
  - `get_email_by_entity_id()` for valid and invalid IDs
  - `save_email()` for creating and updating emails
  - `delete_email()` operations
  - Edge cases: duplicate emails, invalid email formats

- Create `tests/test_login_method_service.py` to test:
  - `get_login_method_by_email_id()` for valid and invalid email IDs
  - `save_login_method()` for creating and updating login methods
  - `delete_login_method()` operations
  - Password hashing and validation
  - Edge cases: missing person_id, invalid method types

- Create `tests/test_organization_service.py` to test:
  - `get_organization_by_entity_id()` for valid and invalid IDs
  - `save_organization()` for creating and updating organizations
  - `get_organizations_by_person_id()` to retrieve all organizations for a person
  - Edge cases: duplicate organization names, missing required fields

- Create `tests/test_person_service.py` to test:
  - `get_person_by_entity_id()` for valid and invalid IDs
  - `save_person()` for creating and updating persons
  - `get_person_by_email()` to retrieve person by email address
  - `update_person()` operations
  - Edge cases: missing required fields, invalid entity IDs

### Step 6: Create tests for background tasks
Create tests for asynchronous message processing:

- Create `tests/test_send_message.py` to test:
  - `MessageSender` initialization
  - `send_message()` with valid queue and payload
  - `send_message()` with RabbitMQ adapter
  - Message serialization and deserialization
  - Connection error handling
  - Retry logic
  - Edge cases: invalid queue names, connection failures, malformed messages

### Step 7: Create tests for Flask application
Create tests for Flask app initialization and configuration:

- Create `tests/test_flask_app.py` to test:
  - Flask app factory creation
  - Database connection pooling setup
  - Blueprint registration
  - Error handler registration
  - CORS configuration
  - Application context setup
  - Edge cases: missing configuration, invalid database connection

- Create `tests/test_flask_logger.py` to test:
  - Logger initialization
  - Log level configuration
  - Log formatting
  - Log output destinations
  - Edge cases: invalid log levels, missing configuration

### Step 8: Create tests for configuration and logging modules
Create tests for application setup modules:

- Create `tests/test_app_config.py` to test:
  - Configuration loading from environment variables
  - Default configuration values
  - Configuration validation
  - Edge cases: missing required environment variables, invalid values

- Create `tests/test_app_logger.py` to test:
  - Logger setup and initialization
  - Custom log handlers
  - Log level management
  - Logger retrieval
  - Edge cases: invalid log configurations

### Step 9: Run comprehensive test coverage analysis
Execute tests with coverage reporting to identify any remaining gaps:

- Run `pytest tests/ -v --cov --cov-report=term-missing` to get detailed coverage report
- Review coverage report to identify any remaining uncovered lines
- Analyze why certain lines are not covered (unreachable code, edge cases, error conditions)
- Add additional test cases for any remaining uncovered code paths

### Step 10: Validate 100% test coverage achievement
Execute validation commands to confirm the chore is complete:

- Run `pytest tests/ -v` to ensure all tests pass
- Run `pytest tests/ --cov --cov-report=term` to verify 100% coverage (or as close as practically achievable)
- Review any remaining uncovered lines and document why they cannot be covered (if applicable)
- Ensure no regressions were introduced by running the full test suite

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `pytest tests/ -v` - Run all tests to ensure they pass without errors
- `pytest tests/ --cov --cov-report=term-missing` - Generate coverage report showing detailed line-by-line coverage
- `pytest tests/ --cov --cov-report=html` - Generate HTML coverage report for detailed review
- `pytest tests/ -k "test_" --tb=short` - Run all tests with short traceback format for quick error identification

## Notes

### Coverage Scope
According to `pyproject.toml`, coverage is configured to track:
- `common/models/*`
- `common/repositories/*`
- `common/services/*`
- `common/utils/*`
- `flask/app/helpers/*`

### Current Test Infrastructure
The project already has:
- pytest configuration in `pyproject.toml`
- Test fixtures in `tests/conftest.py` for database mocking and repository setup
- Existing test patterns in files like `test_decorators.py`, `test_factory.py`, `test_login_method.py`
- Mock objects for database connections, RabbitMQ, and external services

### Testing Approach
- Follow existing test patterns in the codebase (use pytest classes, fixtures, mocks)
- Use `unittest.mock` for mocking external dependencies (database, RabbitMQ, email)
- Test both success paths and failure paths (exceptions, edge cases)
- Use fixtures from `conftest.py` where applicable
- Mock time-dependent operations (JWT expiry, token generation)
- Mock external API calls (OAuth providers, email sending)

### Prioritization Rationale
Tests are prioritized based on:
1. **Business criticality**: Auth and OAuth are core features
2. **Coverage gap**: Modules with lowest coverage get highest priority
3. **Statement count**: Modules with most uncovered statements addressed first
4. **Dependencies**: Helpers and models tested before services that depend on them

### Practical Coverage Goals
While the goal is 100% coverage, some code may be legitimately difficult to test:
- Error handling for rare system failures
- Code paths that are unreachable due to defensive programming
- Third-party library integration edge cases

Document any lines that cannot be practically covered and the rationale for why they should remain untested.
