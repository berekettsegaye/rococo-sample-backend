# Test package
import os

# Set up environment variables before any other imports
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
