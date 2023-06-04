# !/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# ==============================================================================
#
# Copyright (C) 2020 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
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
# 2020-10-24 Ljubomir Kurij <ljubomir_kurij@protonmail.com.com>
#
# * actions.py: created.
#
# ==============================================================================


# ==============================================================================
# Modules import section
# ==============================================================================

from cryptography.fernet import Fernet
from sys import stderr
import base64 as b64
import hashlib as hl
import validators as vd


# ==============================================================================
# Encryption Utilities Section
# ==============================================================================
def _get_hashed_password(password: str) -> str:
    """Returns hashed password string.

    This function takes a password string and returns a hashed version of it.
    The hashing algorithm used is sha256.

    Args:
        password (str): password string to be hashed.

    Returns:
        str: hashed password string.
    """

    return hl.sha256(password.encode('utf-8')).hexdigest()

def _get_fernet_key(password: str) -> bytes:
    """Returns Fernet key from password string.

    This function takes a password string and returns a Fernet key from it.
    The hashing algorithm used is sha256.

    Args:
        password (str): password string to be hashed.

    Returns:
        bytes: Fernet key.
    """
    hlib = hl.md5()
    hlib.update(_get_hashed_password(password).encode('utf-8'))
    return b64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))

def _encrypt_content(content: str, password: str) -> bytes:
    """Returns encrypted content.

    This function takes a content string and a password string and returns
    encrypted content. The encryption algorithm used is Fernet.

    Args:
        content (str): content string to be encrypted.
        password (str): password string to be used for encryption.

    Returns:
        bytes: encrypted content.
    """

    return Fernet(_get_fernet_key(password)).encrypt(content.encode('utf-8'))

def _decrypt_content(content: bytes, password: str) -> str:
    """Returns decrypted content.

    This function takes a content string and a password string and returns
    decrypted content. The decryption algorithm used is Fernet.

    Args:
        content (bytes): content string to be decrypted.
        password (str): password string to be used for decryption.

    Returns:
        str: decrypted content.
    """

    return Fernet(_get_fernet_key(password)).decrypt(content).decode('utf-8')


# ==============================================================================
# App action classes
# ==============================================================================

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


class CreateDatabaseAction(ProgramAction):
    """Program action that creates new database file.
    """

    required_options = (
        'ps_db_file',
        'passphrase',
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
        """Execute create database action code.
        """

        print('{0}: Password databse file: {1}'.format(
            self._attributes['appname'],
            self._user_options['ps_db_file'].input.data[0],
            ))
        print('{0}: Password: {1}'.format(
            self._attributes['appname'],
            self._user_options['passphrase'].input.data[0],
            ))


class MainAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    required_options = (
        'ps_db_file',
        'passphrase',
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

        print('{0}: Password databse file: {1}'.format(
            self._attributes['appname'],
            self._user_options['ps_db_file'].input.data[0],
            ))
        print('{0}: Password: {1}'.format(
            self._attributes['appname'],
            self._user_options['passphrase'].input.data[0],
            ))

        content = 'Hello World!'

        print('{0}: Content: {1}'.format(self._attributes['appname'], content))
        print('{0}: Hashed password: {1}'.format(
            self._attributes['appname'],
            _get_hashed_password(
                self._user_options['passphrase'].input.data[0]
                )
            ))
        print('{0}: Fernet key: {1}'.format(
            self._attributes['appname'],
            _get_fernet_key(
                self._user_options['passphrase'].input.data[0]
                ).decode('utf-8')
            ))

        encrypted_content = _encrypt_content(
            content,
            self._user_options['passphrase'].input.data[0]
            )

        print('{0}: Encrypted content: {1}'.format(
            self._attributes['appname'],
            encrypted_content.decode('utf-8')
            ))

        decrypted_content = _decrypt_content(
            encrypted_content,
            self._user_options['passphrase'].input.data[0]
            )

        print('{0}: Decrypted content: {1}'.format(
            self._attributes['appname'],
            decrypted_content
            ))

        # Exit with no error.
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
