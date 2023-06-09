# !/usr/bin/env python3
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
# 2023-05-30 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * password_manager.py: created.
#
# ==============================================================================


# ==============================================================================
#
# TODO:
#
#
# ==============================================================================


# ==============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ==============================================================================


# ==============================================================================
# Modules import section
# ==============================================================================

import argparse
import actions as ac
import validators as vd


# ==============================================================================
# Utility classes and functions
# ==============================================================================

def _format_epilog(epilog_addition, bug_mail):
    """Format epilogue text.

    Help epilogue text is an additional description of the program that is
    displayed after the description of the arguments. Usually it consists only
    of line informing to which email address to report bugs to, or it can be
    completely omitted.

    Depending on provided parameters function will properly format epilogue text
    and return string containing formatted text. If none of the parameters are
    supplied the function will return None which is default value for epilog
    parameter when constructing parser object.

    Parameters
    ----------
    epilog_addition : str
        Additional description of the program that will be displayed after the
        description of the arguments.

    bug_mail : str
        Email address to which bugs should be reported.

    Returns
    -------
    str
        Formatted epilogue text.
    """

    fmt_mail = None
    fmt_eplg = None

    if epilog_addition is None and bug_mail is None:
        return None

    if bug_mail is not None:
        fmt_mail = 'Report bugs to <{0}>.'.format(bug_mail)
    else:
        fmt_mail = None

    if epilog_addition is None:
        fmt_eplg = fmt_mail

    elif fmt_mail is None:
        fmt_eplg = epilog_addition

    else:
        fmt_eplg = '{0}\n\n{1}'.format(epilog_addition, fmt_mail)

    return fmt_eplg

class AppDoc():
    """Utility class to store and pass application relevant documentation to the
    MainApp class constructor.
    """

    def __init__(self):
        self._docs = dict()

        # Initialize mandatory object attributes with some common values ...
        self._docs['appname'] = 'password_manager'
        self._docs['description'] = 'A simple password management app. \n\n'\
            + 'Mandatory arguments to long options are mandatory for short '\
            + 'options too.'
        self._docs['license'] = 'License GPLv3+: GNU GPL version 3 or later '\
            + '<http://gnu.org/licenses/gpl.html>\n'\
            + 'This is free software: you are free to change and '\
            + 'redistribute it.\n'\
            + 'There is NO WARRANTY, to the extent permitted by law.'
        self._docs['version'] = '0.1'
        self._docs['year'] = '2023'
        self._docs['author'] = 'Ljubomir Kurij'
        self._docs['mail'] = 'ljubomir_kurij@protonmail.com'

        # and optional object attributes with None.
        self._docs['epilog'] = None

    def _new_string_attribute(self, attribute, val):
        """Utility function for setting all instance attributes of the string
        type. This function is only meant to be used from within the class.
        """

        if not isinstance(val, str):
            raise TypeError(
                'Trying to pass non string value as argument \'{0}({1})\''
                .format(type(val).__name__, val)
                )

        self._docs[attribute] = val

    @property
    def appname(self):
        """Getter method for application name attribute.
        """

        return self._docs['appname']

    @property
    def author(self):
        """Getter method for application author attribute.
        """

        return self._docs['author']

    @property
    def bug_mail(self):
        """Getter method for application bug mail attribute.
        """

        return self._docs['mail']

    @property
    def description(self):
        """Getter method for application description attribute.
        """

        return self._docs['description']

    @property
    def epilog(self):
        """Getter method for application epilog attribute.
        """

        return _format_epilog(self._docs['epilog'], self._docs['mail'])

    @property
    def license(self):
        """Getter method for application license attribute.
        """

        return self._docs['license']

    @property
    def release_year(self):
        """Getter method for application release year attribute.
        """

        return self._docs['year']

    @property
    def version(self):
        """Getter method for application version attribute.
        """

        return self._docs['version']

    def newAppDescription(self, description):
        """Setter method for application description attribute. If non string
        value passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('description', description)

    def newAppName(self, name):
        """Setter method for application name attribute. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('appname', name)

    def newAuthorName(self, author_name):
        """Setter method for application author attribute. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('author', author_name)

    def newBugMail(self, bug_mail):
        """Setter method for application bug mail attribute. If non string
        value passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('mail', bug_mail)

    def newEpilog(self, epilog):
        """Setter method for application epilog attribute. It represents
        additional text displayed at the end of help message. If non string
        value passed it raise a TypeError exception.

        This attribute is optional.
        """

        self._new_string_attribute('epilog', epilog)

    def newLicense(self, license):
        """Setter method for application license attribute. If non string
        value passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('license', license)

    def newReleaseYear(self, release_year):
        """Setter method for application release attribute. If non string value
        passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('year', release_year)

    def newVersionString(self, version_string):
        """Setter method for application version string attribute. If non
        string value passed it raise a TypeError exception.

        This attribute is mandatory.
        """

        self._new_string_attribute('version', version_string)


# ==============================================================================
# App class
# ==============================================================================

class MainApp():
    """Application main class.
    
    It is used to set application documentation, instantiate arguments parser
    and parse arguments. Then, depending on the user input it instantiates
    proper application action to handle and process user input.

    Constructor accepts only one mandatory argument of type AppDoc. If non
    AppDoc object passed as argument it raises TypeError.
    """

    def __init__(self: MainApp, doc: AppDoc):

        if not isinstance(doc, AppDoc):
            raise TypeError(
                'Trying to pass object of incompatibile type as argument '
                + '\'{0}({1})\''.format(type(doc).__name__, doc)
                )

        self._doc = doc
        self._parser = argparse.ArgumentParser(
            prog=doc.appname,
            description=doc.description,
            epilog=doc.epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

        # Since we add argument options to groups by calling group
        # method addArgument, we have to store all that group objects
        # somewhere before adding arguments. Since we want to store all
        # application relevant data in our application object we use
        # this list for that purpose.
        self._arg_groups = []

        self._action = None

    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute
        neat and hides implementation details.
        """
        return self._parser.prog

    @property
    def program_description(self):
        """Utility function that makes accessing program description
        attribute neat and hides implementation details.
        """
        return self._parser.description

    def addArgumentGroup(self, title=None, description=None):
        """Adds an argument group to application object.
        At least group title must be provided or method will rise
        NameError exception. This is to prevent creation of titleless
        and descriptionless argument groups. Although this is allowed by
        argparse module I don't see any use of a such utility."""

        if title is None:
            raise NameError('Missing arguments group title')

        group = self._parser.add_argument_group(title, description)
        self._arg_groups.append(group)

        return group

    def _group_by_title(self, title):
        """Returns group object by its title. If group with given title
        doesn't exist return None.
        """

        group = None

        for item in self._arg_groups:
            if title == item.title:
                group = item
                break

        return group

    def addArgument(self, *args, **kwargs):
        """Wrapper for add_argument methods of the argparse module. If
        parameter group is supplied with valid group name, argument will
        be added to that group. If group parameter is omitted argument
        will be added to parser object. In a case of invalid group name
        it rise ValueError exception.
        """

        if 'group' not in kwargs or kwargs['group'] is None:
            self._parser.add_argument(*args, **kwargs)

        else:
            group = self._group_by_title(kwargs['group'])

            if group is None:
                raise ValueError(
                    'Trying to reference nonexisten argument group'
                    )

            kwargsr = {k: kwargs[k] for k in kwargs if k != 'group'}
            group.add_argument(*args, **kwargsr)

    def passArgumentOptions(self, args=None, namespace=None):
        """Wrapper for parse_args method of a parser object. It also
        instantiates action object that will be executed based on a
        input from command line.
        """

        arguments = self._parser.parse_args(args, namespace)

        if arguments.usage:
            self._action = ac.ProgramUsageAction(self._parser.exit)
            self._action.addAppName(self._doc.appname)
            self._action.addUsageMessage(self._parser.format_usage())

        elif arguments.version:
            self._action = ac.ShowVersionAction(self._parser.exit)
            self._action.addAppName(self._doc.appname)
            self._action.addAuthorName(self._doc.author)
            self._action.addLicense(self._doc.license)
            self._action.addReleaseYear(self._doc.release_year)
            self._action.addVersionString(self._doc.version)

        else:
            self._action = ac.MainAction(self._parser.exit)
            self._action.addAppName(self._doc.appname)

            db_file = vd.ProgramOption(
                vd.UserInput(arguments.ps_db_file),
                vd.ValidateFileInput(
                    accept_none=False,
                    existent=True,
                    file_type='bkp',
                    )
                )
            self._action.addUserOption(
                'ps_db_file',
                db_file
                )

            passphrase = vd.ProgramOption(
                vd.UserInput(arguments.passphrase),
                vd.ValidateStringInput()
                )
            self._action.addUserOption(
                'passphrase',
                passphrase
                )

            self._action.validateOptionArguments()

    def run(self):
        """This method executes action code.
        """

        self._action.execute()


# ==============================================================================
# Script main body
# ==============================================================================

if __name__ == '__main__':
    documentation = AppDoc()
    program = MainApp(documentation)

    program.addArgumentGroup('general options')
    program.addArgumentGroup('app specific options')

    # Add optional argument for displaying program version information.
    program.addArgument(
        '-V', '--version',
        action='store_true',
        help='print program version',
        dest='version',
        group='general options'
        )
    program.addArgument(
        '--usage',
        action='store_true',
        help='give a short usage message',
        dest='usage',
        group='general options'
        )
    program.addArgument(
        '-F', '--password-database-file',
        action='store',
        type=str,
        help='Passwords database file (*.bkp)',
        metavar='PS_DB_FILE',
        dest='ps_db_file',
        group='app specific options'
        )
    program.addArgument(
        '-P', '--passphrase',
        action='store',
        type=str,
        help='Passphrase for passwords database file',
        metavar='PASSPHRASE',
        dest='passphrase',
        group='app specific options'
        )

    program.passArgumentOptions()
    program.run()
