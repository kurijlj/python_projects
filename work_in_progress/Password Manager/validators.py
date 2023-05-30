#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2020 Ljubomir Kurij <kurijlj@gmail.com>
#
# This file is part of Radiochromic Denoiser.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================


# =============================================================================
#
# 2020-10-24 Ljubomir Kurij <ljubomir_kurij@protonmail.com.com>
#
# * validators.py: created.
#
# =============================================================================


# ============================================================================
#
# TODO:
#
#
# ============================================================================


# ============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ============================================================================

# =============================================================================
# Modules import section
# =============================================================================

from pathlib import Path


# =============================================================================
# Module level constants
# =============================================================================


# =============================================================================
# Validator classes and functions
# =============================================================================

class ProgramOption():
    """TODO: Put class docstring here.
    """

    def __init__(self, user_input, validator):

        # Typechecking ...
        if not isinstance(user_input, UserInput):
            raise TypeError(
                'Trying to pass non \'UserInput\' object as argument '
                + '\'{1}({2})\''.format(type(user_input).__name__, user_input)
                )

        if not isinstance(validator, ValidateInput):
            raise TypeError(
                'Trying to pass non \'ValidateInput\' object as argument '
                + '\'{1}({2})\''.format(type(validator).__name__, validator)
                )

        # Typechecking passed. Do initialization.
        self._input = user_input
        self._validator = validator

    @property
    def input(self):
        """TODO: Put method docstring here.
        """

        return self._input

    @property
    def validator(self):
        """TODO: Put method docstring here.
        """

        return self._validator

    def validate(self):
        """TODO: Put method docstring here.
        """

        return self._validator.validate(self._input)


class UserInput():
    """TODO: Put class docstring here.
    """

    def __init__(self, data):
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
    def data(self):
        """TODO: Put method docstring here.
        """

        return self._data

    @property
    def len(self):
        """TODO: Put method docstring here.
        """

        return len(self._data)

    def isNone(self):
        """TODO: Put method docstring here.
        """

        if self._data is None:
            return True

        return False


class ValidateArgument():
    """Class for checking existence and validating value type for an arguments
    passed to functions and methods in a keyword objects (kwargs).
    """

    types = {
        'boolean': (bool,),
        'numerical': (int, float,),
        'integer': (int,),
        'iterable': (tuple, list,),
        'string': (str,),
        }

    def __init__(self, arg_name, arg_type, def_val, accept_none):
        self._name = arg_name
        self._type = arg_type
        self._def_val = def_val
        self._accept_none = accept_none

    def _type_check(self, var):
        """TODO: Put method docstring here.
        """

        result = False
        for ttype in ValidateArgument.types[self._type]:
            if isinstance(var, ttype):
                result = True

        return result

    def validate(self, **kwargs):
        """TODO: Put method docstring here.
        """

        if self._name not in kwargs:
            if not self._def_val:
                raise ValueError('Missing argument \'{0}\''.format(self._name))

        elif kwargs[self._name] is None:
            if not self._accept_none:
                raise ValueError('Missing argument \'{0}\''.format(self._name))

        elif not self._type_check(kwargs[self._name]):
            raise TypeError(
                'Trying to pass non {0} value as \'{1}\' '
                .format(
                    self._type,
                    self._name
                    )
                + 'argument \'{0}({1})\''
                .format(
                    type(kwargs[self._name]).__name__,
                    kwargs[self._name]
                    )
                )


class ValidateInput():
    """An abstract base class for all user input validator classes. This class
    is only meant to be used as prototype and must be subclassed.
    """

    def __init__(self):
        self._message = 'Pass'

    @property
    def message(self):
        """Getter for first encountered validation error. Be sure to invoke
        object validation method prior to accessing this property.
        """

        return self._message

    def validate(self, user_input):
        """Virtual method. It has to be overriden in all derived classes.
        """

        if not isinstance(user_input, UserInput):
            raise TypeError(
                'Trying to pass non UserInput object as argument \'{0}({1})\''
                .format(type(user_input).__name__, user_input)
                )

        return True


class ValidateFileInput(ValidateInput):
    """TODO: Put class docstring here.
    """

    def __init__(self, **kwargs):
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

        check_none = ValidateArgument(
            'existent',
            'boolean',
            True,
            False
            )
        check_none.validate(**kwargs)

        check_type = ValidateArgument(
            'file_type',
            'string',
            True,
            True
            )
        check_none.validate(**kwargs)

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

    def validate(self, user_input):
        """TODO: Put method docstring here.
        """

        super().validate(user_input)

        if not user_input.isNone():
            for path_str in user_input.data:
                path = Path(path_str)

                # If file doesn't exist and we do not accept non existent files
                # as valid input return False.
                if not path.exists():
                    if self._existent:
                        self._message = 'File with given path \'{0}\' '\
                            .format(path.resolve())
                            + 'does not exist'

                        return False

                    # We accept non-existent files and further testing is
                    # not applicable.
                    return True

                # Check if we are dealing with file at all.
                if not path.is_file():
                    self._message = Given path \'{0}\' is not a file'\
                    .format(path.resolve())

                    return False

                # If set check if file is of required file type, i.e. file has
                # given extension.
                if self._type is not None and path.suffix[1:] != self._type:
                    self._message = 'File with path \'{0}\' is not of '\
                        .format(path.resolve())
                        + 'required file type ({0})'.format(self._type)

                    return False

            return True

        if self._accept_none:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '\'None\' is not an valid option value'

        return False


class ValidateNumericalInput(ValidateInput):
    """TODO: Put class docstring here.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self._limits = dict()

        # Check if all required arguments are passed to the constructor and if
        # are they of the rquired type.
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

    def assertLowerLimit(self, val):
        """TODO: Put method docstring here.
        """

        if self._limits['incl_min']:
            return bool(self._limits['min'] <= val)

        return bool(self._limits['min'] < val)

    def assertUpperLimit(self, val):
        """TODO: Put method docstring here.
        """

        if self._limits['incl_max']:
            return bool(self._limits['max'] >= val)

        return bool(self._limits['max'] > val)

    def assertWithinLimits(self, val):
        """TODO: Put method docstring here.
        """

        chk_lwr = self.assertLowerLimit(val)
        chk_upr = self.assertUpperLimit(val)

        return bool(chk_lwr and chk_upr)

    def validate(self, user_input):
        """TODO: Put method docstring here.
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
                    self._message = 'Value \'{0}\' is not within required '\
                        .format(num) + 'value range {0}{1}, {2}{3}'\
                        .format(bra, lower, upper, ket)

                    return False

            return True

        if self._accept_none:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '\'None\' is not an valid option value'

        return False


class ValidateUserChoice(ValidateInput):
    """TODO: Put class docstring here.
    """

    def __init__(self, valid_choices, none_is_valid):
        super().__init__()
        self._valid_choices = tuple(valid_choices)
        self._none_is_valid = none_is_valid

    def validate(self, user_input):
        """TODO: Put method docstring here.
        """

        super().validate(user_input)

        if not user_input.isNone():
            for choice in user_input.data:
                if choice not in self._valid_choices:

                    # Format and set validation message.
                    self._message = 'Value \'{0}\' not supported'\
                        .format(choice)

                    return False

            return True

        if self._none_is_valid:
            return True

        # None is not acceptable so we have to format an error message.
        self._message = '\'None\' is not an valid option value'

        return False
