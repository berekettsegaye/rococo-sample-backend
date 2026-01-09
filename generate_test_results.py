#!/usr/bin/env python
"""
Generate JSON test results for /test skill output.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# Set required environment variables
os.environ.setdefault('APP_ENV', 'test')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('SECURITY_PASSWORD_SALT', 'test-salt')
os.environ.setdefault('VUE_APP_URI', 'http://localhost:3000')
os.environ.setdefault('POSTGRES_HOST', 'localhost')
os.environ.setdefault('POSTGRES_PORT', '5432')
os.environ.setdefault('POSTGRES_USER', 'test')
os.environ.setdefault('POSTGRES_PASSWORD', 'test')
os.environ.setdefault('POSTGRES_DB', 'testdb')
os.environ.setdefault('RABBITMQ_HOST', 'localhost')
os.environ.setdefault('RABBITMQ_PORT', '5672')
os.environ.setdefault('RABBITMQ_USER', 'guest')
os.environ.setdefault('RABBITMQ_PASSWORD', 'guest')
os.environ.setdefault('AUTH_JWT_SECRET', 'test-jwt-secret')

def main():
    """Generate test results JSON."""
    # Map coverage files to test files
    coverage_file_to_tests = {
        'common/services/auth.py': {
            'test_file': 'tests/test_auth_service.py',
            'test_purpose': 'Test AuthService class with signup, login, password reset, and OAuth flows'
        },
        'common/models/email.py': {
            'test_file': 'tests/test_email_model.py',
            'test_purpose': 'Test Email model validation and constraints'
        },
        'common/services/oauth.py': {
            'test_file': 'tests/test_oauth_client.py',
            'test_purpose': 'Test OAuthClient for Google and Microsoft OAuth token exchange and user info retrieval'
        },
        'common/services/person.py': {
            'test_file': 'tests/test_person_service.py',
            'test_purpose': 'Test PersonService for saving and retrieving person records'
        },
        'common/services/email.py': {
            'test_file': 'tests/test_email_service.py',
            'test_purpose': 'Test EmailService for email CRUD operations and verification'
        },
        'common/services/login_method.py': {
            'test_file': 'tests/test_login_method_service.py',
            'test_purpose': 'Test LoginMethodService for managing authentication methods'
        },
        'common/services/organization.py': {
            'test_file': 'tests/test_organization_service.py',
            'test_purpose': 'Test OrganizationService for organization CRUD and person-role associations'
        },
        'common/repositories/organization.py': {
            'test_file': 'tests/test_organization_repository.py',
            'test_purpose': 'Test OrganizationRepository for database operations and custom queries'
        },
        'common/repositories/base.py': {
            'test_file': 'tests/test_base_repository.py',
            'test_purpose': 'Test BaseRepository initialization and MODEL requirement'
        },
    }

    # Run pytest with JSON output
    result = subprocess.run(
        ['python', '-m', 'pytest', 'tests/', '-v', '--tb=no', '-q'],
        capture_output=True,
        text=True,
        timeout=120
    )

    all_results = []

    # Parse pytest output
    test_lines = result.stdout.split('\n')

    for source_file, test_info in coverage_file_to_tests.items():
        test_file = test_info['test_file']
        test_purpose = test_info['test_purpose']

        # Run individual test file to get detailed results
        test_result = subprocess.run(
            ['python', '-m', 'pytest', test_file, '-v', '--tb=line'],
            capture_output=True,
            text=True,
            timeout=30
        )

        passed = test_result.returncode == 0

        # Count passed/failed tests
        output = test_result.stdout
        passed_count = output.count(' PASSED')
        failed_count = output.count(' FAILED')
        error_count = output.count(' ERROR')

        # Extract test names
        test_names = []
        for line in output.split('\n'):
            if '::' in line and (' PASSED' in line or ' FAILED' in line or ' ERROR' in line):
                # Extract test name (e.g., tests/test_auth_service.py::TestClass::test_name)
                test_name = line.split(' ')[0].strip()
                test_passed = ' PASSED' in line
                test_names.append({
                    'name': test_name,
                    'passed': test_passed
                })

        if test_names:
            # Report individual test results
            for test in test_names[:5]:  # Limit to first 5 tests per file for brevity
                all_results.append({
                    'test_name': test['name'],
                    'passed': test['passed'],
                    'execution_command': f"pytest {test_file}::{test['name'].split('::')[-1]} -v",
                    'test_purpose': test_purpose,
                    'error': None if test['passed'] else f"Test failed - run command for details"
                })
        else:
            # Report summary for the file
            all_results.append({
                'test_name': test_file.replace('tests/', '').replace('.py', ''),
                'passed': passed,
                'execution_command': f"pytest {test_file} -v",
                'test_purpose': test_purpose,
                'error': None if passed else f"{failed_count} failed, {error_count} errors" if (failed_count + error_count) > 0 else "No tests collected"
            })

    # Add summary result
    all_results.insert(0, {
        'test_name': 'comprehensive_coverage_test_suite',
        'passed': result.returncode == 0,
        'execution_command': 'pytest tests/ -v --cov=common --cov-report=term',
        'test_purpose': 'Comprehensive test suite covering all low-coverage files identified in coverage report',
        'error': None if result.returncode == 0 else 'Some tests failed - see individual test results'
    })

    # Output JSON
    print(json.dumps(all_results, indent=2))

if __name__ == '__main__':
    main()
