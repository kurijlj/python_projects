"""user_input.py

This module provides a wrapper class for user input. It is used to store user
input in a tuple, and to provide a way to iterate over the tuple. It also
provides properties to access the tuple and its length.

Examples:
    >>> user_input = UserInput('foo', 'bar')
    >>> print(user_input)
    ('foo', 'bar')
"""

# ==============================================================================
#
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# This file is part of Password Manager.
#
# Password Manager is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Password Manager is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Foobar. If not, see <https://www.gnu.org/licenses/>.
#
# ==============================================================================


# ==============================================================================
#
# 2023-06-17 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * user_input.py: created.
#
# ==============================================================================


# ==============================================================================
# Imports Section
# ==============================================================================

# ==============================================================================
# User Input Class Section
# ==============================================================================
class UserInput():
    """Wrapper class for user input.

    This class is a wrapper for user input. It is used to store user input in a
    tuple, and to provide a way to iterate over the tuple. It also provides
    properties to access the tuple and its length.

    Examples:
        >>> user_input = UserInput('foo', 'bar')
        >>> print(user_input)
        ('foo', 'bar')
    """

    def __init__(self, *args):
        """A constructor for the UserInput class.

        Examples:
            >>> user_input = UserInput(val1, val2, val3, ...)
        """

        # Keeps track of the next item in the user input data. It is used by the
        # __next__ method.
        self._next_item = 0

        if 0 == len(args):
            self._data = tuple()

        else:
            self._data = tuple(args)
    
    def __str__(self) -> str:
        """Returns a string representation of the user input data.

        It invokes the __str__ method of the tuple that stores the user input data, to format the string representation of the data.

        Returns:
            str: A string representation of the user input data.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> print(user_input)
            ('foo', 'bar')
        """

        return str(self._data)
    
    def __repr__(self) -> str:
        """Returns a string representation of the UserInput object.

        Returns:
            str: A string representation of the UserInput object.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> user_input.__repr__()
            UserInput('foo', 'bar')
        """

        return "UserInput{}".format(self._data)
    
    def __iter__(self):
        """Returns an iterator for the user input data.

        Returns:
            iterator: An iterator for the user input data.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> for item in user_input:
            ...     print(item)
            ...
            foo
            bar
        """

        return self._data.__iter__()
    
    def __next__(self):
        """Returns the next item in the user input data.

        Returns:
            object: The next item in the user input data.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> print(user_input.__next__())
            foo
            >>> print(user_input.__next__())
            bar
        """

        if self._next_item < len(self._data):
            item = self._data[self._next_item]
            self._next_item += 1
            return item
        
        else:
            raise StopIteration

    
    def __getitem__(self, key):
        """Returns the item at the specified index in the user input data.

        Args:
            key (int): The index of the item to return.

        Returns:
            object: The item at the specified index in the user input data.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> print(user_input[0])
            foo
            >>> print(user_input[1])
            bar
        """

        return self._data.__getitem__(key)
    
    @property
    def data(self) -> tuple:
        """Returns the user input data stored in the UserInput object.

        Returns:
            None: If the UserInput object is empty.
            object: If the UserInput object contains a single item.
            tuple: If the UserInput object contains multiple items.

        Examples:
            >>> ui1 = UserInput('foo', 'bar')
            >>> ui2 = UserInput('foo')
            >>> ui3 = UserInput()
            >>> print(ui1.data)
            ('foo', 'bar')
            >>> print(ui2.data)
            foo
            >>> print(ui3.data)
            None
        """

        if 0 == len(self._data):
            return None
        
        elif 1 == len(self._data):
            return self._data[0]
        
        else:
            return self._data
    
    @property
    def length(self) -> int:
        """Returns the length of the user input data.

        Returns:
            int: The length of the user input data.

        Examples:
            >>> user_input = UserInput('foo', 'bar')
            >>> print(user_input.length)
            2
        """

        return len(self._data)
    
    @property
    def is_empty(self) -> bool:
        """Returns True if the UserInput object is empty, False otherwise.

        Returns:
            bool: True if the UserInput object is empty, False otherwise.

        Examples:
            >>> ui1 = UserInput('foo', 'bar')
            >>> ui2 = UserInput('foo')
            >>> ui3 = UserInput()
            >>> print(ui1.is_empty)
            False
            >>> print(ui2.is_empty)
            False
            >>> print(ui3.is_empty)
            True
        """

        return 0 == len(self._data)