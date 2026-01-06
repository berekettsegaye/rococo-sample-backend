"""
Unit tests for common/models/person.py
"""
import pytest
from common.models.person import Person


class TestPersonModel:
    """Tests for Person model."""

    def test_person_initialization_with_all_fields(self):
        """Test Person initialization with all fields set correctly."""
        person = Person(
            entity_id='person-123',
            first_name='John',
            last_name='Doe'
        )

        assert person.entity_id == 'person-123'
        assert person.first_name == 'John'
        assert person.last_name == 'Doe'

    def test_person_initialization_with_minimal_fields(self):
        """Test Person initialization with minimal fields generates entity_id."""
        person = Person(
            first_name='Jane',
            last_name='Smith'
        )

        assert person.first_name == 'Jane'
        assert person.last_name == 'Smith'
        assert person.entity_id is not None

    def test_person_use_type_checking_enabled(self):
        """Test that use_type_checking is enabled for Person model."""
        assert Person.use_type_checking is True
