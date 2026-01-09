#!/usr/bin/env python
"""
Script to run tests for uncovered files and generate JSON results.
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

def run_test_file(test_file):
    """Run a single test file and return results."""
    results = []

    try:
        # Run pytest with json output
        result = subprocess.run(
            ['python', '-m', 'pytest', str(test_file), '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse output
        test_name = test_file.stem
        passed = result.returncode == 0

        # Count passed/failed tests from output
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if 'PASSED' in line or 'FAILED' in line:
                test_func = line.split('::')[-1].split(' ')[0] if '::' in line else test_name
                test_passed = 'PASSED' in line

                results.append({
                    'test_name': f"{test_name}::{test_func}",
                    'passed': test_passed,
                    'execution_command': f"pytest {test_file} -v",
                    'test_purpose': f"Test coverage for {test_name}",
                    'error': None if test_passed else "Test failed - see pytest output"
                })

        if not results:
            # No tests found or parsing failed
            results.append({
                'test_name': test_name,
                'passed': passed,
                'execution_command': f"pytest {test_file} -v",
                'test_purpose': f"Test coverage for {test_name}",
                'error': result.stderr if result.stderr else None
            })

    except subprocess.TimeoutExpired:
        results.append({
            'test_name': test_file.stem,
            'passed': False,
            'execution_command': f"pytest {test_file} -v",
            'test_purpose': f"Test coverage for {test_file.stem}",
            'error': "Test execution timeout"
        })
    except Exception as e:
        results.append({
            'test_name': test_file.stem,
            'passed': False,
            'execution_command': f"pytest {test_file} -v",
            'test_purpose': f"Test coverage for {test_file.stem}",
            'error': str(e)
        })

    return results

def main():
    """Main execution function."""
    tests_dir = Path('tests')

    # Focus on the uncovered files
    priority_tests = [
        'test_auth_service.py',
        'test_email_model.py',
        'test_oauth_client.py',
        'test_person_service.py',
        'test_email_service.py',
        'test_login_method_service.py',
        'test_organization_service.py',
        'test_organization_repository.py',
        'test_base_repository.py',
    ]

    all_results = []

    for test_file_name in priority_tests:
        test_file = tests_dir / test_file_name
        if test_file.exists():
            print(f"Running {test_file}...")
            results = run_test_file(test_file)
            all_results.extend(results)
        else:
            all_results.append({
                'test_name': test_file_name,
                'passed': False,
                'execution_command': f"pytest tests/{test_file_name} -v",
                'test_purpose': f"Test file for {test_file_name}",
                'error': "Test file not found"
            })

    # Output JSON results
    print("\n" + "="*80)
    print("TEST RESULTS JSON:")
    print("="*80)
    print(json.dumps(all_results, indent=2))

    return all_results

if __name__ == '__main__':
    main()
