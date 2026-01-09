"""
Unit tests for the Person model.
"""
from common.models.person import Person


class TestPersonModel:
    """Test Person model."""

    def test_person_instantiation(self):
        """Test basic Person instantiation."""
        person = Person(
            entity_id="person-123",
            first_name="John",
            last_name="Doe"
        )
        assert person.entity_id == "person-123"
        assert person.first_name == "John"
        assert person.last_name == "Doe"

    def test_person_with_minimal_fields(self):
        """Test Person with only required fields."""
        person = Person(first_name="Jane", last_name="Smith")
        assert person.first_name == "Jane"
        assert person.last_name == "Smith"

    def test_person_type_checking_enabled(self):
        """Test that Person has type checking enabled."""
        assert hasattr(Person, 'use_type_checking')
        assert Person.use_type_checking is True

    def test_person_inheritance(self):
        """Test that Person properly inherits from BasePerson."""
        from rococo.models import Person as BasePerson
        person = Person(first_name="Test", last_name="User")
        assert isinstance(person, BasePerson)
