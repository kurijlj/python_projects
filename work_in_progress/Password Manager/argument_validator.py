"""argument_validator.py - Utility classes for validating function arguments.

This module defines a utility class 'ArgumentValidator' for validating function
arguments for basic data types. It is used to validate function arguments by
checking if they are present, if they are of the correct type and if they are
required. It is used to validate function arguments in the following way:

>>> def foo(name: str, age: int) -> None:
>>>     ArgumentValidator('name', 'string').validate(name=name)
>>>     ArgumentValidator('age', 'integer').validate(age=age)

The class constructor takes three arguments: name, type and required. The name
argument is the name of the function argument. The type argument is the type of
the function argument. The required argument is a boolean value that indicates
if the function argument is required. If the required argument is set to True,
the function argument can not take None value. If the required argument is set
to False, the function argument can take None value.

Supported types:
    - string
    - integer
    - float
    - numerical (integer or float)
    - boolean

Example:
    >>> def foo(name: str, age: int) -> None:
    >>>     ArgumentValidator('name', 'string').validate(name=name)
    >>>     ArgumentValidator('age', 'integer').validate(age=age)

Todo:
    * Add support for 'complex' type.

Author:
    Ljubomir Kurij <
"""

# ==============================================================================
#
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# argument_validator.py - Utility classes for validating function arguments.
#
# 'argument_validator.py' is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# 'fargs_validator.py' is distributed in the hope that it will be useful, but
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
# 2023-06-18 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * argument_validator.py: created.
#
# ==============================================================================


# ==============================================================================
# Imports Section
# ==============================================================================


# ==============================================================================
# Classes Section
# ==============================================================================
class ArgumentValidator():
    """Validate function arguments.

    A utility class for validating function arguments. It is used to validate
    function arguments by checking if they are present, if they are of the
    correct type and if they are required. It is used to validate function
    arguments in the following way:

    >>> def foo(name: str, age: int) -> None:
    >>>     ArgumentValidator('name', 'string').validate(name=name)
    >>>     ArgumentValidator('age', 'integer').validate(age=age)

    The class constructor takes three arguments: name, type and required. The
    name argument is the name of the function argument. The type argument is the
    type of the function argument. The required argument is a boolean value that
    indicates if the function argument is required. If the required argument is
    set to True, the function argument can not take None value. If the required
    argument is set to False, the function argument can take None value.
    """

    types = {
        'string': (str,),
        'integer': (int,),
        'float': (float,),
        'numerical': (int, float,),
        'boolean': (bool,),
    }

    def __init__(self, name: str, type: str, required: bool = True):
        """Class constructor.

        Args:
            name (str): Argument name.
            type (str): Argument type.
            required (bool, optional): Is the argument required. Defaults
            to True.

        Supported types:
            - string
            - integer
            - float
            - numerical (integer or float)
            - boolean
        """

        # Check if the argument type is supported.
        if type not in ArgumentValidator.types.keys():
            raise TypeError('Type "{type}" is not supported.')

        self._name = name
        self._type = type
        self._required = required
    
    def _check_type(self, argument: object) -> bool:
        """Check if the object given as function argument is of the required
        type.

        Args:
            argument (object): Object to check.

        Returns:
            bool: True if the argument type is of the correct type, False
            otherwise. If the argument is None and the argument is not required,
            True is returned, also.
        """

        result = False
        if isinstance(argument, ArgumentValidator.types[self._type]) or \
            None == argument:
            result = True

        return result

    def _check_required(self, value: object) -> bool:
        """Check if the value is required.

        Args:
            value (object): Value to check.

        Returns:
            bool: False if the value is None and the argument is required, True
            otherwise.
        """
        return not self._required or value is not None

    def validate(self, **kwargs: dict) -> None:
        """Validate the argument.

        Validate the argument by checking if it is present in the kwargs, if it
        is of the correct type and if it is required. All arguments must be
        supplied as key-value pairs. If you are supplying a single argument, you
        must use the following syntax: `validate(name=object)`, where name is
        the argument name passed to the class constructor, and object is the
        actual object passed as a function argument. The same is if a function
        takes multiple positional arguments, i.e. *args. Each object in the
        *args tuple must be passed as a key-value pair, where the key is the
        argument name and the value is the actual object.
        
        If the funtion takes multiple arguments as key-value pairs, you can pass
        them as a dictionary, i.e. `validate(**kwargs)`, where kwargs is a
        dictionary of key-value pairs, where the key is the argument name and
        the value is the actual object.
        
        Args:
            **kwargs (dict): Function arguments.

        Raises:
            ValueError: If the argument is missing.
            TypeError: If the argument is not of the correct type.
            ValueError: If the argument is required and is None.

        Returns:
            None: If the argument is valid.

        Example:
            >>> def foo(name: str, age: int) -> None:
            >>>     ArgumentValidator('name', 'string').validate(name=name)
            >>>     ArgumentValidator('age', 'integer').validate(age=age)
        """

        if self._name not in kwargs:
            raise ValueError(f'Missing argument "{self._name}".')

        elif not self._check_type(kwargs[self._name]):
            raise TypeError(f'Argument "{self._name}" must be of type '
                + f'"{self._type}" (got "{type(kwargs[self._name]).__name__}").'
                )

        elif not self._check_required(kwargs[self._name]):
            raise ValueError(f'Argument "{self._name}" can not take "None" '
                + f'value.'
                )
        
        else:
            return None
        
# End of fargs_validator.py