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

    def test_getitem_error(self):
        """Tests the __getitem__ method when an invalid key is used."""

        user_input = UserInput('foo', 'bar')

        with self.assertRaises(IndexError):
            user_input[2]
    
    def test_len(self):
        """Tests the __len__ method."""

        user_input = UserInput('foo', 'bar')

        self.assertEqual(len(user_input), 2)
    
    def test_len_error(self):
        """Tests the __len__ method when an invalid key is used."""

        user_input = UserInput('foo', 'bar')

        with self.assertRaises(TypeError):
            len(user_input, 2)
    
    def test_is_empty(self):
        """Tests the is_empty method."""

        user_input = UserInput('foo', 'bar')

        self.assertFalse(user_input.is_empty())
    
    def test_is_empty_true(self):
        """Tests the is_empty method when the user input is empty."""

        user_input = UserInput()

        self.assertTrue(user_input.is_empty())


if __name__ == '__main__':
    unittest.main()