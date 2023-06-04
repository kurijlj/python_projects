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
# 2023-05-30 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * program.py: created.
#
# ==============================================================================


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
# Modules Import Section
# =============================================================================

import argparse as ap


#==============================================================================
# Program Documentation Functions and Classes Section
#==============================================================================

def _format_epilog(epilog_addition: str, bug_mail: str) -> str:
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

class ProgramDoc():
    """Wraps program documentation text and provides methods for setting
    and getting documentation attributes.
    """

    def __init__(self: ProgramDoc, progname: str, description: str,
                 license: str, version: str, year: str, author: str,
                 mail: str, epilog: str = None):
        self._docs = dict()

        # Initialize class attributes
        self._progname    = progname
        self._description = description
        self._license     = license
        self._version     = version
        self._year        = year
        self._author      = author
        self._mail        = mail
        self._epilog      = epilog

    def _modify_string_attribute(self: ProgramDoc, attribute: str, val: str):
        """Validate and modify string type instance attributes.

        Utility function for modifying all instance attributes of the string
        type. This function is only meant to be used from within the class.
        """

        if not isinstance(val, str):
            raise TypeError(
                'Trying to pass "{0}" value as "{1}" attribute'
                'value. Only string values are allowed.'.format(
                    type(val).__name__,
                    attribute
                )
            )

        setattr(self, attribute, val)

    @property
    def progname(self: ProgramDoc):
        """Return program name.
        """

        return self._progname

    @property
    def author(self: ProgramDoc):
        """Return program author name.
        """

        return self._author

    @property
    def bug_mail(self: ProgramDoc):
        """Return program bug mail.
        """

        return self._mail

    @property
    def description(self: ProgramDoc):
        """Return program description.
        """

        return self._description

    @property
    def epilog(self: ProgramDoc):
        """Return program epilogue.
        """

        return _format_epilog(self._epilog, self._mail)

    @property
    def license(self: ProgramDoc):
        """Return program license.
        """

        return self._license

    @property
    def release_year(self: ProgramDoc):
        """Return program release year.
        """

        return self._year

    @property
    def version(self: ProgramDoc):
        """Return program version.
        """

        return self._version

    def modify_prog_description(self: ProgramDoc, description: str):
        """Modify program description.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('description', description)

    def modify_prog_name(self: ProgramDoc, name: str):
        """Modify program name.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('appname', name)

    def modify_prog_author(self: ProgramDoc, author: str):
        """Modify program author name.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('author', author)

    def modify_bug_mail(self: ProgramDoc, bug_mail: str):
        """Modify program bug mail.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('mail', bug_mail)

    def modify_prog_epilog(self: ProgramDoc, epilog: str):
        """Modify program epilogue.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('epilog', epilog)

    def modify_prog_license(self: ProgramDoc, license: str):
        """Modify program license.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('license', license)

    def modify_release_year(self: ProgramDoc, year: str):
        """Modify program release year.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('year', year)

    def modify_prog_version(self: ProgramDoc, version: str):
        """Modify program version.

        It raises TypeError exception if non string value is passed.
        """

        self._modify_string_attribute('version', version)


#==============================================================================
# Program Classes Section
#==============================================================================

class Program():
    """Abstract base class for MainProgram and SubProgram classes.

    Every app can be divided into main program and number of subprograms
    (subcommands). This class defines common properties for both types of
    objects.
    """

    def __init__(self: Program, program_doc: ProgramDoc):

        # Do some sanity checks first.
        if not isinstance(program_doc, ProgramDoc):
            raise ValueError(
                'Trying to pass object of type "{0}" or "None" as '
                'argument "program_doc" (type: "{1}").'.format(
                    type(program_doc).__name__,
                    ProgramDoc.__name__
                )
            )

        self._doc = doc
        self._parser = ap.ArgumentParser(
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

    def _group_by_title(self: Program, title: str) -> ap._ArgumentGroup:
        """Return argument group object for given group title.

        If group with given title does not exist in the group list
        return None.
        """

        group = None

        for item in self._arg_groups:
            if title == item.title:
                group = item
                break

        return group


    def add_argument_group(self: Program, title: str, description=None):
        """Adds an argument group to the program object.

        Group "title" is mandatory argument. If "description" is not
        provided it will be set to None. If group with given title
        already exists in the group list, method will return that group
        object. Otherwise it will create new group object and return it.
        """

        if title is None:
            raise ValueError(
                'Trying to pass "None" as argument "title" (type: "str").'
                )

        if not isinstance(title, str) or not title:
            raise ValueError(
                'Trying to pass empty string or not an string object as ' 'argument "title" (type: "str").'
                )

        group = self._parser.add_argument_group(title, description)
        self._arg_groups.append(group)


    def add_argument(self, *args, **kwargs):
        """Adds an argument to the program object.

        It wraps add_argument method of argparse module. If parameter
        group is supplied with valid group name, argument will be added
        to that group. If group parameter is omitted argument will be
        added to the parser object. In a case of invalid group name it rises
        ValueError exception.

        Group must be passed as key-value pair group='groupname'.
        """

        group = kwargs.pop('group', None)

        if group is None:
            self._parser.add_argument(*args, **kwargs)

        else:
            gobj = self._group_by_title(group)

            if gobj is None:
                raise ValueError(
                    'Trying to reference nonexisten argument group.'
                    )

            gobj.add_argument(*args, **kwargs)


class _MainProgram(_Program):
    """Class to wrap main parser object, created using argparse.ArgumentParser()
    constructor. It provides an access to basic parser properties, parse_args
    method, as well to subparsers action object.

    In a multiparser application there is no need to attach an action factory
    method to the main progarm instance because it will never be called.
    """

    def __init__(self,
        app_instance=None,
        epilog=None
    ):

        _Program.__init__(self, app_instance)

        fmt_epilog = _format_epilog(epilog, self._app_instance.author_mail)

        self._parser = _argparse.ArgumentParser(
            prog = self._app_instance.program_name,
            description = self._app_instance.program_description,
            epilog = fmt_epilog,
            formatter_class = _argparse.RawDescriptionHelpFormatter
            )

        self._sub_parsers = None


    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute neat
        and hides implementation details.
        """
        return self._parser.prog


    @property
    def program_description(self):
        """Utility function that makes accessing program description attribute
        neat and hides implementation details.
        """
        return self._parser.description


    def add_subparsers(self, title=None):
        """Wrapper for add_parsers method of ArgumentParser class. This
        method is provided to enable custom subparsers title setup. If
        'title' parameter is not provided (None) default value is used.
        """

        if not isinstance(title, str):
            raise ValueError('Invalid parameter type.')

        if not title:
            title = \
            'The {0} can be called with following commands'\
            .format(self._parser.prog.strip('.py'))

        self._sub_parsers = self._parser.add_subparsers(
            title=title,
            dest='command',
            metavar=''
        )


    @property
    def sub_parsers_object(self):
        """Provides access to subparsers object which have to be provided when
        instantiating subprogram objects.
        """

        return self._sub_parsers


    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of the parser object.
        """

        return self._parser.parse_args(args, namespace)


class _SubProgram(_Program):
    """Class to wrap subparser objects, created using
    _subParsersAction.ArgumentParser() constructor.
    """

    def __init__(self,
        app_instance=None,
        sub_parsers_object=None,
        name=None,
        description=None,
        help=None,
        epilog=None
    ):

        _Program.__init__(self, app_instance)

        # Do some sanity checks first.
        if not isinstance(sub_parsers_object, _argparse._SubParsersAction):
            raise ValueError(
                'Subparsers object not initialized or invalid \
                object type.'.replace('\t','')
            )

        if name is None:
            raise NameError('Missing command name.')

        if not isinstance(name, str) or not name:
            raise ValueError('Empty string or not an string object.')

        fmtd_eplg = _format_epilog(epilog, self._app_instance.author_mail)

        self._parser = sub_parsers_object.add_parser(
            name,
            description = description,
            epilog = fmtd_eplg,
            help = help,
            formatter_class=_argparse.RawDescriptionHelpFormatter
        )


#==============================================================================
# Command line app class
#==============================================================================

class CommandLineApp(object):
    """Actual command line app object containing all relevant application
    information (NAME, VERSION, DESCRIPTION, ...) and which instantiates through
    attached program objects action that will be executed depending on the user
    input from command line.
    """

    def __init__(self,
        name=None,
        description=None,
        license=None,
        version=None,
        year=None,
        author=None,
        mail=None
    ):
        self._program_name = name
        self._program_description = description
        self._program_license = license
        self._version_string = version
        self._year_string = year
        self._author_name = author
        self._author_mail = mail
        self._action = None
        self.main = None


    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute neat
        and hides implementation details.
        """

        # If main program is attached get program name from its property.
        if self.main:
            return self.main.program_name

        return self._program_name


    @property
    def program_description(self):
        """Utility function that makes accessing program description attribute
        neat and hides implementation details.
        """

        # If main program is attached get program description from its property.
        if self.main:
            return self.main.program_description

        return self._program_description


    @property
    def program_license(self):
        """Provide access to licence text property.
        """

        return self._program_license


    @property
    def version_string(self):
        """Provide access to program's version string property.
        """

        return self._version_string


    @property
    def year_string(self):
        """Provide access to program's year string property.
        """

        return self._year_string


    @property
    def author_name(self):
        """Provide access to author's name string.
        """

        return self._author_name


    @property
    def author_mail(self):
        """Provide access to author's/bug mail string.
        """

        return self._author_mail


    def attach_program(self, program, obj):
        """Attach program/subprogram object to application instance. It attach
        program object as named attribute to the app object, setting the name of
        an attribute according to variable 'program'. 'program' variable must be
        nonempty 'string', or else method will rise ValueError. 'obj' must be
        instance of _Program subclass, or else ValueError will be risen.
        """

        # Do some basic sanity checks first.
        if not isinstance(program, str) or not program:
            raise ValueError('Empty string or not an string object.')
        if not issubclass(type(obj), _Program)\
                or not isinstance(obj, _Program):
            raise ValueError('Invalid object type.')

        setattr(self, program, obj)


    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of the main program instance.
        """

        args = self.main.parse_args(args, namespace)
        self._action = args.func(args)


    def run(self):
        """Execute proper application action. This method should be called after
        a call to parse_args method.
        """

        self._action.execute()


#==============================================================================
# Program action classes
#
# ProgramAction class is the abstract base class for all program action classes
# an should not be modified. To define new action class subclass from
# ProgramAction class.
#==============================================================================

class ProgramAction():
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        self._exit_app()


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def __init__(self, prog, ver, year, author, license, exitf):
        super().__init__(exitf)
        self._version_message = '{0} {1} Copyright (C) {2} {3}\n{4}'\
                .format(prog, ver, year, author, license)

    def execute(self):
        print(self._version_message)
        super().execute()


class DefaultAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    def __init__(self, prog, exitf):
        super().__init__(exitf)
        self._program_name = prog

    def execute(self):
        print('{0}: Hello World!\n'.format(self._program_name))
        super().execute()


#==============================================================================
# Action factories
#
# Action factory methods must accept two arguments, 'obj' holding program object
# to which method is attached and 'args' holding parsed command line arguments.
# When proper program action object is formulated and instantiated, method
# returns this object to the caller.
#==============================================================================

def about_action_factory(obj, args):

    return _formulate_action(
        ShowVersionAction,
        prog=obj._parser.prog,
        ver=obj._app.versionString,
        year=obj._app.yearString,
        author=obj._app.authorName,
        license=obj._app.programLicense,
        exitf=obj._parser.exit,
    )


#==============================================================================
# Script main body
#==============================================================================

if __name__ == '__main__':

    # Create an application and feed in relevant application data.
    app = CommandLineApp(
        description='Framework for application development \
            implementing argp option parsing engine.\n\n\
            Mandatory arguments to long options are mandatory for \
            short options too.'\
            .replace('\t',''),
        license='License GPLv3+: GNU GPL version 3 or later \
            <http://gnu.org/licenses/gpl.html>\n\
            This is free software: you are free to change and \
            redistribute it.\n\
            There is NO WARRANTY, to the extent permitted by law.'\
            .replace('\t',''),
        version='i.i',
        year='yyyy',
        author='Author Name',
        mail='author@mail.com'
    )

    # We need at least main program, so let's attach it to our app.
    app.attach_program('main', _MainProgram(app_instance=app, epilog=None))

    # We want for main program to show version info.
    app.main.add_argument(
        '-V', '--version',
        action='version',
        help='print program version',
        version='%(prog)s i.i'
    )

    # If we instantiate subprograms (subparsers) we don't need to attach action
    # factory to main program, since that code wil never be executed.

    # We want for our app to have subprograms.
    app.main.add_subparsers()

    # Our only subprogram will show some short application and licence info.
    app.attach_program('about', _SubProgram(
            app_instance=app,
            sub_parsers_object=app.main.sub_parsers_object,
            name='about',
            description='Command to print application info to standard output.',
            help='Show application info.',
            epilog=None
        )
    )

    # Now we can parse command line arguments.
    app.parse_args()

    # Run generated code.
    app.run()
