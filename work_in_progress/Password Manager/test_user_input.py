"""Unit tests for user_input.py"""

import unittest
from unittest.mock import patch
from user_input import UserInput

class TestUserInput(unittest.TestCase):
    """Tests the UserInput class."""

    def test_user_input(self):
        """Tests the UserInput class."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(user_input.data, ('foo', 'bar'))

    def test_str(self):
        """Tests the __str__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(str(user_input), "('foo', 'bar')")

    def test_repr(self):
        """Tests the __repr__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(user_input.__repr__(), "UserInput('foo', 'bar')")

    def test_iter(self):
        """Tests the __iter__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(list(user_input), ['foo', 'bar'])

    def test_next(self):
        """Tests the __next__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(user_input.__next__(), 'foo')
        self.assertEqual(user_input.__next__(), 'bar')

    def test_getitem(self):
        """Tests the __getitem__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(user_input[0], 'foo')
        self.assertEqual(user_input[1], 'bar')

if __name__ == '__main__':
    unittest.main()