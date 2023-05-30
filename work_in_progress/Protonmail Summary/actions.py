# !/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2020 Ljubomir Kurij <kurijlj@gmail.com>
#
# This file is part of <program name>.
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
# <Put documentation here>
#
# <yyyy>-<mm>-<dd> <Author Name> <author@mail.com>
#
# * actions.py: created.
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

from sys import stderr
import validators as vd


# =============================================================================
# Module level constants
# =============================================================================


# =============================================================================
# Module utility classes and functions
# =============================================================================


# =============================================================================
# App action classes
# =============================================================================

class ProgramAction():
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf
        self._attributes = dict()
        self._exit_codes = dict()

        self._exit_codes['noerr'] = 0
        self._exit_codes['unknown_error'] = 1

    def _new_attribute(self, attribute, atype, val):
        """Utility function for setting instance attributes. It also does type
        checking of the passed value.

        This function is only meant to be used from within the class.
        """

        if not isinstance(val, atype):
            raise TypeError(
                'Trying to pass non \'{0}\' value as argument \'{1}({2})\''
                .format(atype.__name__, type(val).__name__, val)
                )

        self._attributes[attribute] = val

    def execute(self):
        """Virtual method to execute astion object code. It has to be overriden
        in all derived classes.
        """

        raise NotImplementedError(
            'Override this method in derived class'
            )


class ProgramUsageAction(ProgramAction):
    """Program action that formats and displays usage message to the stdout.
    """

    def addAppName(self, name):
        """Setter method for application name string. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('name', str, name)

    def addUsageMessage(self, usage):
        """Setter method for application usage message. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('usage', str, usage)

    def execute(self):
        """Execute program usage action code.
        """

        compiled = '{0}Try \'{1} --help\' for more information.'.format(
            self._attributes['usage'],
            self._attributes['name']
            )

        print(compiled)

        self._exit_app(self._exit_codes['noerr'])


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def addAppName(self, name):
        """Setter method for application name string. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('appname', str, name)

    def addAuthorName(self, author):
        """Setter method for application author info. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('author', str, author)

    def addLicense(self, license):
        """Setter method for application license info. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('license', str, license)

    def addReleaseYear(self, year):
        """Setter method for application release year info. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('year', str, year)

    def addVersionString(self, version):
        """Setter method for application version info. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('version', str, version)

    def execute(self):
        """Execute show version action code.
        """

        compiled = '{0} {1} Copyright (C) {2} {3}\n{4}'.format(
            self._attributes['appname'],
            self._attributes['version'],
            self._attributes['year'],
            self._attributes['author'],
            self._attributes['license'],
            )

        print(compiled)

        self._exit_app(self._exit_codes['noerr'])


class MainAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    required_options = (
        'single_choice',
        'multi_choice',
        'number_option',
        )

    def __init__(self, exitf):
        super().__init__(exitf)
        self._user_options = dict()

    def addAppName(self, name):
        """Setter method for application name string. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_attribute('appname', str, name)

    def addUserOption(self, name, option, error_code=None):
        """Method for adding user input options passed as command line
        arguments and accompanying validators.
        """
        # Typechecking ...
        if not isinstance(name, str):
            raise TypeError(
                'Trying to pass non \'string\' value as argument '
                + '\'{0}({1})\''.format(type(name).__name__, name)
                )

        if not isinstance(option, vd.ProgramOption):
            raise TypeError(
                'Trying to pass non \'ProgramOption\' object as argument '
                + '\'{0}({1})\''.format(type(option).__name__, option)
                )

        if error_code is not None:
            if not isinstance(error_code, int):
                raise TypeError(
                    'Trying to pass non \'int\' value as argument '
                    + '\'{0}({1})\''.format(
                        type(error_code).__name__,
                        error_code
                        )
                    )

            if error_code in self._exit_codes.values():
                raise ValueError(
                    'Exit code with given value \'{0}\' already exists'\
                    .format(error_code)
                    )

            self._exit_codes[name] = error_code

        else:
            self._exit_codes[name] = None

        self._user_options[name] = option

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        print('{0}: Hello World!\n'.format(self._attributes['appname']))

        self._exit_app(self._exit_codes['noerr'])

    def validateOptionArguments(self):
        """TODO: Put method docstring HERE.
        """

        # Check if all required program options are supplied.
        for required in MainAction.required_options:
            if not required in self._user_options.keys():
                raise ValueError('Missing program option \'{0}\''
                    .format(required)
                    )

        for name, option in self._user_options.items():
            if not option.validate():
                print(
                    '{0}: Invalid option argument for option \'{1}\'. {2}'\
                    .format(
                        self._attributes['appname'],
                        name,
                        option.validator.message
                        ),
                    file=stderr
                    )

                if self._exit_codes[name] is None:
                    self._exit_app(self._exit_codes['unknown_error'])
                else:
                    self._exit_app(self._exit_codes[name])
