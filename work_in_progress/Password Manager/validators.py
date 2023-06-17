#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
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
# 2020-10-24 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * validators.py: created.
#
# ==============================================================================


# ==============================================================================
# Modules Import Section
# ==============================================================================

from pathlib import Path


# ==============================================================================
# ProgramOption Class Section
# ==============================================================================

class ProgramOption():
    """Wraps UserInput object with proper ValidateInput object.
    """

    def __init__(self: ProgramOption, user_input: UserInput, validator: ValidateInput):

        # Typechecking ...
        if not isinstance(user_input, UserInput):
            raise TypeError(
                'Trying to pass non "UserInput" object as argument '
                + '"{1}({2})"'.format(type(user_input).__name__, user_input)
                )

        if not isinstance(validator, ValidateInput):
            raise TypeError(
                'Trying to pass non "ValidateInput" object as argument '
                + '"{1}({2})"'.format(type(validator).__name__, validator)
                )

        # Typechecking passed. Do initialization.
        self._input = user_input
        self._validator = validator

    @property
    def input(self: ProgramOption) -> UserInput:
        """Return UserInput object stored in ProgramOption object.
        """

        return self._input

    @property
    def validator(self: ProgramOption) -> ValidateInput:
        """Return ValidateInput object stored in ProgramOption object.
        """

        return self._validator

    def validate(self: ProgramOption) -> bool:
        """Execute validation of UserInput object stored in ProgramOption object.
        """

        return self._validator.validate(self._input)


# ==============================================================================
# UserInput Class Section
# ==============================================================================

class UserInput():
    """Store user input data.

    Class for storing user input data. It is used as a container for data passed
    as arguments to program options. It stores all data as tuple even when
    single value is passed. This is done to simplify data processing in the rest
    of the program.

    Use class constructor to create UserInput object from data passed as
    arguments to program options. Data can be passed as tuple or list. If data
    is passed as list, it is converted to tuple. If data is passed as tuple, it
    is stored as is. If no data is passed to constructor, object is initialized
    with None value.

    Use class method 'len()' to get number of elements stored in UserInput. Use
    class method 'at()' to get single element from UserInput. Use class method
    'data()' to get all data stored in UserInput. Use class method 'isNone()' to
    check if UserInput object is initialized with None value.
    """

    def __init__(self: UserInput, data: tuple):
        if data is not None:
            if isinstance(data, tuple):
                self._data = data
            elif isinstance(data, list):
                self._data = tuple(data)
            else:
                self._data = (data, )
        else:
            self._data = None

    @property
    def data(self: UserInput) -> tuple:
        """Retrive data stored in UserInput object.
        """

        return self._data

    @property
    def at(self: UserInput, index: int):
        """Get single element from UserInput object.
        """

        return self._data[index]

    @property
    def len(self: UserInput) -> int:
        """Get number of elements stored in UserInput object.
        """

        return len(self._data)

    def isNone(self: UserInput) -> bool:
        """Return whether or not UserInput object is initialized with None
        value.
        """

        if self._data is None:
            return True

        return False


# ==============================================================================
# ValidateArgument Class Section
# ==============================================================================

class ValidateArgument():
    """Validate argument passed to function or method as key-value pairs (**kwargs).

    Wraps argument name, type, default value and whether or not argument can be
    None into single object. This object can then be passed to function or
    method as argument. When function or method is called, ValidateArgument
    object is used to validate argument passed to function or method as
    key-value pairs (**kwargs). It provides similar facility to Octave's
    'validateattributes()' function.
    """

    # Define types by classes they are instances of.
    types = {
        'boolean': (bool,),
        'numerical': (int, float,),
        'integer': (int,),
        'iterable': (tuple, list,),
        'string': (str,),
        }

    def __init__(self: ValidateArgument, arg_name: str, arg_type: str, def_val: bool, accept_none: bool):
        """Class constructor.
        """

        self._name = arg_name
        self._type = arg_type
        self._def_val = def_val
        self._accept_none = accept_none

    def _type_check(self: ValidateArgument, var) -> bool:
        """Check if argument's value is of supported type.
        """

        result = False
        for ttype in ValidateArgument.types[self._type]:
            if isinstance(var, ttype):
                result = True

        return result

    def validate(self: ValidateArgument, **kwargs):
        """Check if argument passed to function or method as key-value pairs
        (**kwargs) is passed and is of designated type.
        """

        if self._name not in kwargs:
            if not self._def_val:
                raise ValueError('Missing argument "{0}"'.format(self._name))

        elif kwargs[self._name] is None:
            if not self._accept_none:
                raise ValueError('Missing argument "{0}"'.format(self._name))

        elif not self._type_check(kwargs[self._name]):
            raise TypeError(
                'Trying to pass value of type "{0}" as "{1}" '
                .format(type(kwargs[self._name]).__name__, self._name)
                + '(type: "{0}")'.format(self._type)
                )

# ==============================================================================
# ValidateInput Classes Section
# ==============================================================================

class ValidateInput():
    """An abstract base class for all user input validator classes. This class
    is only meant to be used as prototype and must be subclassed.
    """

    def __init__(self: ValidateInput):
        self._message = 'Pass'

    @property
    def message(self: ValidateInput) -> str:
        """Returns message for the first raised eror, describing the validation
        error. Be sure to invoke object validation method prior to calling this
        property.
        """

        return self._message

    def validate(self: ValidateInput, user_input: UserInput) -> bool:
        """Virtual method. It has to be overriden in all derived classes.
        """

        if not isinstance(user_input, UserInput):
            raise TypeError(
                'Trying to pass non UserInput object as argument "{0}({1})"'
                .format(type(user_input).__name__, user_input)
                )

        return True


class ValidateFileInput(ValidateInput):
    """Validates user supplied sytem file path.

    Use key-value pairs (**kwargs) to pass arguments to class constructor. Use
    'accept_none' argument to specify whether or not None value is accepted as
    valid input. Use 'existent' argument to specify whether or not file has to
    exist on the system. Use 'file_type' argument to specify file type. It can
    be either 'file' or 'directory'. If 'file_type' argument is not passed to
    constructor, it is assumed that file of any type is a valid input.
    """

    def __init__(self: ValidateFileInput, **kwargs):
        """Class constructor.

        Use key-value pairs (**kwargs) to pass arguments to class constructor.
        Use 'accept_none' argument to specify whether or not None value is
        accepted as valid input. Use 'existent' argument to specify whether or
        not file has to exist on the system. Use 'file_type' argument to specify
        file type. It can be either 'file' or 'directory'. If 'file_type'
        argument is not passed to constructor, it is assumed that file of any
        type is a valid input.
        """

        # Call base class constructor.
        super().__init__()

        # Check if all required arguments are passed to the constructor and if
        # are they of the required type.
        check_none = ValidateArgument(
            'accept_none',
            'boolean',
            True,
            False
            )
        check_none.validate(**kwargs)

        check_existent = ValidateArgument(
            'existent',
            'boolean',
            True,
            False
            )
        check_existent.validate(**kwargs)

        check_type = ValidateArgument(
            'file_type',
            'string',
            True,
            True
            )
        check_type.validate(**kwargs)

        # Initialize object attributes.
        if 'accept_none' not in kwargs:
            self._accept_none = False
        else:
            self._accept_none = kwargs['accept_none']

        if 'existent' not in kwargs:
            self._existent = True
        else:
            self._existent = kwargs['existent']

        if 'file_type' not in kwargs:
            self._type = None
        else:
            self._type = kwargs['file_type']

    def validate(self: ValidateFileInput, user_input: UserInput) -> bool:
        """Execute code to validate user input.
        """

        super().validate(user_input)

        if not user_input.isNone():
            for path_str in user_input.data:
                path = Path(path_str)

                # If file doesn't exist and we do not accept non existent files
                # as valid input return False.
                if not path.exists():
                    if self._existent:
                        self._message = 'File with given path "{0}" '\
                            .format(path.resolve())\
                            + 'does not exist'

                        return False

                    # We accept non-existent files and further testing is
                    # not applicable.
                    return True

                # Check if we are dealing with file at all.
                if not path.is_file():
                    self._message = 'Given path "{0}" is not a file'\
                    .format(path.resolve())

                    return False

                # If set check if file is of required file type, i.e. file has
                # given extension.
                if self._type is not None and path.suffix[1:] != self._type:
                    self._message = 'File with path "{0}" is not of '\
                        .format(path.resolve())\
                        + 'required file type ({0})'.format(self._type)

                    return False

            return True

        if self._accept_none:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '"None" is not an valid option value'

        return False


class ValidateNumericalInput(ValidateInput):
    """Validates user supplied numerical input.

    Use key-value pairs (**kwargs) to pass arguments to class constructor. Use
    'accept_none' argument to specify whether or not None value is accepted as
    valid input. Use 'min_val' argument to specify minimum value. Use 'max_val'
    argument to specify maximum value. Use 'incl_min' argument to specify
    whether or not minimum value is included in the range. Use 'incl_max'
    argument to specify whether or not maximum value is included in the range.
    If 'incl_min' and 'incl_max' arguments are not passed to constructor, it
    is assumed that both minimum and maximum values are included in the range.
    """

    def __init__(self: ValidateNumericalInput, **kwargs):
        """Class constructor.
        
        Use key-value pairs (**kwargs) to pass arguments to class constructor.
        Use 'accept_none' argument to specify whether or not None value is
        accepted as valid input. Use 'min_val' argument to specify minimum
        value. Use 'max_val' argument to specify maximum value. Use 'incl_min'
        argument to specify whether or not minimum value is included in the
        range. Use 'incl_max' argument to specify whether or not maximum value
        is included in the range. If 'incl_min' and 'incl_max' arguments are
        not passed to constructor, it is assumed that both minimum and maximum
        values are included in the range.
        """
        
        # Call base class constructor.
        super().__init__()

        # Initialize '_limits' as an empty dictionary.
        self._limits = dict()

        # Check if all required arguments are passed to the constructor and if
        # are they of the required type.
        check_none = ValidateArgument(
            'accept_none',
            'boolean',
            True,
            False
            )
        check_none.validate(**kwargs)

        check_min = ValidateArgument(
            'min_val',
            'numerical',
            False,
            False
            )
        check_min.validate(**kwargs)

        check_max = ValidateArgument(
            'max_val',
            'numerical',
            False,
            False
            )
        check_max.validate(**kwargs)

        check_incl_min = ValidateArgument(
            'incl_min',
            'boolean',
            False,
            False
            )
        check_incl_min.validate(**kwargs)

        check_incl_max = ValidateArgument(
            'incl_max',
            'boolean',
            False,
            False
            )
        check_incl_max.validate(**kwargs)

        # Initialize object attributes.
        if 'accept_none' not in kwargs:
            self._accept_none = False
        else:
            self._accept_none = kwargs['accept_none']

        self._limits['min'] = kwargs['min_val']
        self._limits['max'] = kwargs['max_val']
        self._limits['incl_min'] = kwargs['incl_min']
        self._limits['incl_max'] = kwargs['incl_max']

    def assertLowerLimit(self: ValidateNumericalInput, val):
        """Assert that user supplied value is greater or equal to lower limit.
        """

        if self._limits['incl_min']:
            return bool(self._limits['min'] <= val)

        return bool(self._limits['min'] < val)

    def assertUpperLimit(self: ValidateNumericalInput, val):
        """Assert that user supplied value is less or equal to upper limit.
        """

        if self._limits['incl_max']:
            return bool(self._limits['max'] >= val)

        return bool(self._limits['max'] > val)

    def assertWithinLimits(self: ValidateNumericalInput, val):
        """Assert that user supplied value is within required value range.
        """

        chk_lwr = self.assertLowerLimit(val)
        chk_upr = self.assertUpperLimit(val)

        return bool(chk_lwr and chk_upr)

    def validate(self: ValidateNumericalInput, user_input):
        """Execute validation of user supplied input.
        """

        super().validate(user_input)

        if not user_input.isNone():
            for num in user_input.data:
                if not self.assertWithinLimits(num):

                    # Format and set validation message.
                    bra = '[' if self._limits['incl_min'] else '('
                    ket = ']' if self._limits['incl_max'] else ')'
                    lower = str(self._limits['min'])
                    upper = str(self._limits['max'])
                    self._message = 'Value "{0}" is not within required '\
                        .format(num) + 'value range {0}{1}, {2}{3}'\
                        .format(bra, lower, upper, ket)

                    return False

            return True

        if self._accept_none:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '"None" is not an valid option value'

        return False


class ValidateUserChoice(ValidateInput):
    """Validate user supplied choice.
    """

    def __init__(self: ValidateUserChoice, valid_choices, none_is_valid: bool):
        super().__init__()
        self._valid_choices = tuple(valid_choices)
        self._none_is_valid = none_is_valid

    def validate(self: ValidateUserChoice, user_input: UserInput):
        """TODO: Put method docstring here.
        """

        super().validate(user_input)

        if not user_input.isNone():
            for choice in user_input.data:
                if choice not in self._valid_choices:

                    # Format and set validation message.
                    self._message = 'Value "{0}" not supported'\
                        .format(choice)

                    return False

            return True

        if self._none_is_valid:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '"None" is not an valid option value'

        return False


class ValidateStringInput(ValidateInput):
    """Validate user supplied string input.

    Use key-value pairs (**kwargs) to pass arguments to class constructor.
    Use 'accept_none' argument to specify whether or not None value is
    accepted as valid input. Use 'accept_empty' argument to specify whether or
    not empty string is accepted as valid input. If 'accept_none' and
    'accept_empty' arguments are not passed to constructor, it is assumed that
    both None and empty string are accepted as valid input.
    """

    def __init__(self, **kwargs):
        """Class constructor.
        
        Use key-value pairs (**kwargs) to pass arguments to class constructor.
        Use 'accept_none' argument to specify whether or not None value is
        accepted as valid input. Use 'accept_empty' argument to specify whether
        or not empty string is accepted as valid input. If 'accept_none' and
        'accept_empty' arguments are not passed to constructor, it is assumed
        that both None and empty string are accepted as valid input.
        """
        
        # Call base class constructor.
        super().__init__()

        # Check if all required arguments are passed to the constructor and if
        # are they of the rquired type.
        check_none = ValidateArgument(
            'accept_none',
            'boolean',
            True,
            False
            )
        check_none.validate(**kwargs)

        check_empty = ValidateArgument(
            'accept_empty',
            'boolean',
            True,
            False
            )
        check_empty.validate(**kwargs)

        # Initialize object attributes.
        if 'accept_none' not in kwargs:
            self._accept_none = False
        else:
            self._accept_none = kwargs['accept_none']

        if 'accept_empty' not in kwargs:
            self._accept_empty = True
        else:
            self._accept_empty = kwargs['accept_empty']

    def validate(self, user_input):
        """Execute validation of user supplied input.
        """

        super().validate(user_input)

        if not user_input.isNone():

            counter = 1
            for usr_str in user_input.data:
                if not usr_str and not self._accept_empty:

                    # Format and set validation message.
                    self._message = 'For argument {1} empty string is not an'\
                         .format(counter)\
                        + 'valid option'

                    return False

                counter += 1

            return True

        if self._accept_none:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '"None" is not an valid option value'

        return False