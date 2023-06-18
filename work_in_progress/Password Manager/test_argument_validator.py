"""Unit tests for argument_validator.py
"""

# ==============================================================================
# Imports Section
# ==============================================================================
import unittest
from argument_validator import ArgumentValidator

# ==============================================================================
# Classes Section
# ==============================================================================
class TestArgumentValidator(unittest.TestCase):
    """Unit tests for ArgumentValidator class."""

    def test_argument_validator(self):
        """Test ArgumentValidator class."""

        # Test required argument.
        ArgumentValidator('name', 'string').validate(name='John')
        ArgumentValidator('age', 'integer').validate(age=30)
        ArgumentValidator('height', 'float').validate(height=1.75)
        ArgumentValidator('weight', 'numerical').validate(weight=75)
        ArgumentValidator('is_married', 'boolean').validate(is_married=True)

        # Test optional argument.
        ArgumentValidator('name', 'string', required=False).validate(name=None)
        ArgumentValidator('age', 'integer', required=False).validate(age=None)
        ArgumentValidator('height', 'float', required=False)\
            .validate(height=None)
        ArgumentValidator('weight', 'numerical', required=False)\
            .validate(weight=None)
        ArgumentValidator('is_married', 'boolean', required=False)\
            .validate(is_married=None)

        # Test invalid argument type.
        with self.assertRaises(TypeError):
            ArgumentValidator('name', 'invalid').validate(name='John')

        # Test required argument with None value.
        with self.assertRaises(ValueError):
            ArgumentValidator('name', 'string').validate(name=None)

        # Test optional argument with None value.
        ArgumentValidator('name', 'string', required=False).validate(name=None)

        # Test required argument with invalid type.
        with self.assertRaises(TypeError):
            ArgumentValidator('name', 'string').validate(name=30)

        # Test optional argument with invalid type.
        with self.assertRaises(TypeError):
            ArgumentValidator('name', 'string', required=False)\
                .validate(name=30)

        # Test required argument with invalid type and None value.
        with self.assertRaises(TypeError):
            ArgumentValidator('name', 'invalid').validate(name=None)

        # Test optional argument with invalid type and None value.
        with self.assertRaises(TypeError):
            ArgumentValidator('name', 'invalid', required=False)\
                .validate(name=None)
            

# ==============================================================================
# Main Section
# ==============================================================================
if __name__ == '__main__':
    unittest.main()

# ==============================================================================
# End of Code
# ==============================================================================