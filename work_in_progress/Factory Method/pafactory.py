#!/usr/bin/env python3
# ==============================================================================
#
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# This file is part of the Program Action Factry.
#
# Factory Method Demo is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Factory Method Demo is distributed in the hope that it will be useful, but
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
# 2023-09-23 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * pafactory.py: created.
#
# ==============================================================================


# ==============================================================================
#
# REFERENCES (this section should be deleted in the release version):
#
# [1] [PEP 8 -- Style Guide for Python Code]
#     (https://www.python.org/dev/peps/pep-0008/)
#
# [2] [PEP 257 -- Docstring Conventions]
#     (https://www.python.org/dev/peps/pep-0257/)
#
# [3] [PEP 484 -- Type Hints]
#     (https://www.python.org/dev/peps/pep-0484/)
#
# [4] [PEP 526 -- Syntax for Variable Annotations]
#     (https://www.python.org/dev/peps/pep-0526/)
#
# [5] [PEP 3107 -- Function Annotations]
#     (https://www.python.org/dev/peps/pep-3107/)
#
# [6] [Factory Method in Python]
#     (https://refactoring.guru/design-patterns/factory-method/python/example)
#
# ==============================================================================


# ==============================================================================
# Module docstring
# ==============================================================================
"""
The pafactory Module

This module simplifies the process of mapping user-supplied inputs to the execution of application business logic. It provides an interface for defining program action classes, each encapsulating the specific business logic for a corresponding user input. Additionally, the module offers a factory method class for registering program actions to their associated parameters and generating the appropriate program action based on user input.

Usage:
1. Define custom program action classes by subclassing `ProgramAction`.
2. Register these program actions using the
   `ProgramActionFactory.register_action` method.
3. Configure argparse to accept the desired user inputs and parameters.
4. Use `ProgramActionFactory.spawn_action` to obtain the program action
   based on user input.
5. Execute the selected program action using `ProgramAction.run()`.

Example:
```python
from pafactory import ProgramActionFactory, ProgramAction

# Define a custom program action class
class MyCustomAction(ProgramAction):
    def run(self):
        # Implement the business logic for this action
        pass

# Configure argparse and parse user input
# ...

# Register the custom program action
ProgramActionFactory.register_action(
                                     ProgramAction(argparser.ArgumentParser()),
                                     comando_name,
                                     action_params_dict
                                    )

# Get the appropriate program action based on user input
selected_action = ProgramActionFactory.spawn_action(argparser.ArgumentParser())

# Execute the selected program action
selected_action.run()

This module enhances code organization and maintainability by separating user
input handling from business logic, making it easier to expand and manage
application functionality.
"""

# ==============================================================================
# Module import section
# ==============================================================================
from abc import ABC, abstractmethod
import argparse as ap
from typing import Dict, Any


# ==============================================================================
# Constants definition section
# ==============================================================================
APP_NAME             = 'pafactory'
APP_VERSION          = '1.0.0'
APP_AUTHOR           = 'Ljubomir Kurij'
APP_EMAIL            = 'ljubomir_kurij@protonmail.com'
APP_COPYRIGHT_YEAR   = '2023'
APP_COPYRIGHT_HOLDER = APP_AUTHOR
APP_LICENSE          = 'GPLv3+'
APP_LICENSE_URL      = 'https://www.gnu.org/licenses/gpl-3.0.en.html'
APP_DESCRIPTION      = 'Streamline app buiness logic based on the user input'
APP_EPILOG           = 'Rport bugs to: {0} <{1}>'.format(APP_AUTHOR, APP_EMAIL)
APP_VERSION_INFO     = ''\
    .join([
          '{0} {1} Copyright (c) {2} {3}\n',
          'License {4}: GNU GPL version 3 or later <{5}>\n',
          'This is free software: you are free to change ',
          'and redistribute it.\n',
          'There is NO WARRANTY, to the extent permitted by law.\n'
         ]).format(
                  APP_NAME,
                  APP_VERSION,
                  APP_COPYRIGHT_YEAR,
                  APP_AUTHOR,
                  APP_LICENSE,
                  APP_LICENSE_URL
                 )


# ==============================================================================
# Classes definition section
# ==============================================================================

# ------------------------------------------------------------------------------
# Interface: ProgramAction
# ------------------------------------------------------------------------------
#
# Description: The ProgramAction class represents the base class for all program
#              actions. It declares the operations that all concrete program
#              actions must implement.
#
# ------------------------------------------------------------------------------
class ProgramAction(ABC):
    """The ProgramAction class represents the base class for all program
    actions. It declares the operations that all concrete program actions must
    implement.

    A program action is responsible for executing a specific program task, based
    on the user supplied command line arguments. ProgramAction constructor takes
    an argparse.ArgumentParser object as an argument.

    The action code is executed by calling the run() method. All the business
    logic of the action must be implemented in the run() method of the derived
    class.
    
    The run() method must exit the program by calling the exit() method of the
    ArgumentParser object passed to the ProgramAction constructor. The exit()
    method takes an integer argument that represents the exit code. The
    ProgramAction class provides a set of predefined exit codes. The predefined
    exit codes are defined as class attributes. The predefined exit codes are:
    
        EX_OK          = 0  # successful termination
        EX__BASE       = 64 # base value for error messages
        EX_USAGE       = 64 # command line usage error
        EX_DATAERR     = 65 # data format error
        EX_NOINPUT     = 66 # cannot open input
        EX_NOUSER      = 67 # addressee unknown
        EX_NOHOST      = 68 # host name unknown
        EX_UNAVAILABLE = 69 # service unavailable
        EX_SOFTWARE    = 70 # internal software error
        EX_OSERR       = 71 # system error
        EX_OSFILE      = 72 # critical OS file missing
        EX_CANTCREAT   = 73 # can't create (user)
        EX_IOERR       = 74 # input/output error
        EX_TEMPFAIL    = 75 # temp failure;
        EX_PROTOCOL    = 76 # remote error in protocol
        EX_NOPERM      = 77 # permission denied
        EX_CONFIG      = 78 # configuration error
        EX__MAX        = 78 # maximum listed value

    The given exit codes are taken from the BSD sysexits.h header file. User
    can supply additinal exit codes by calling the add_exit_code() method from
    the derived class. If additional exit codes are supplied, then the user must
    ensure that the exit codes are unique. Also, the user must ensure that
    EX__MAX is updated to reflect the maximum exit code value.
    
    The user is also responsible for validating the command line arguments,
    beyond the failities provided by the ArgumentParser object.
    
    ProgramAction is an abstract base class (ABC) and cannot be instantiated.
    """
    
    def __init__(self, parser: ap.ArgumentParser) -> None:
        """Class constructor.

        The constructor takes an argparse.ArgumentParser object as an argument.

        It also, initializes the exit codes dictionary. The dictionary contains
        the predefined exit codes. The dictionary is indexed by the exit code
        name. The exit code name must follow the naming convention 'EX_<NAME>',
        where <NAME> is the name of the exit code. The predefined exit codes are
        defined as class attributes.
        """

        # Initialize the exit codes dictionary.
        self._exit_codes = dict()

        # Defne common exit codes.
        self._exit_codes['EX_OK']          = 0  # successful termination
        self._exit_codes['EX__BASE']       = 64  # base value for error messages
        self._exit_codes['EX_USAGE']       = 64  # command line usage error
        self._exit_codes['EX_DATAERR']     = 65  # data format error
        self._exit_codes['EX_NOINPUT']     = 66  # cannot open input
        self._exit_codes['EX_NOUSER']      = 67  # addressee unknown
        self._exit_codes['EX_NOHOST']      = 68  # host name unknown
        self._exit_codes['EX_UNAVAILABLE'] = 69  # service unavailable
        self._exit_codes['EX_SOFTWARE']    = 70  # internal software error
        self._exit_codes['EX_OSERR']       = 71  # system error
                                                 # (e.g., can't fork)
        self._exit_codes['EX_OSFILE']      = 72  # critical OS file missing
        self._exit_codes['EX_CANTCREAT']   = 73  # can't create (user)
                                                 # output file
        self._exit_codes['EX_IOERR']       = 74  # input/output error
        self._exit_codes['EX_TEMPFAIL']    = 75  # temp failure;
                                                 # user is invited to retry
        self._exit_codes['EX_PROTOCOL']    = 76  # remote error in protocol
        self._exit_codes['EX_NOPERM']      = 77  # permission denied
        self._exit_codes['EX_CONFIG']      = 78  # configuration error

        self._exit_codes['EX__MAX']        = 78  # maximum listed value

        # Validate input arguments.

        # Check if the 'parser' argument is an ArgumentParser object.
        if not isinstance(parser, ap.ArgumentParser):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2} instance.'
                             ])\
                            .format(
                                    '__init__',
                                    'parser',
                                    'argparse.ArgumentParser'
                                   )
            raise TypeError(err_msg)

        # Store the parser object.
        self._parser = parser

    def add_exit_code(self, code_name: str, code_val: int):
        """Add a new exit code.

        All exit codes must be added before the run() method is called. Also,
        all exit codes must follow the naming convention 'EX_<NAME>', where
        <NAME> is the name of the exit code. The user is responsible for
        ensuring that the exit code is unique.

        All user added exit codes must have value greater than EX__MAX. Also,
        the user is responsible for updating the value of EX__MAX to reflect the
        maximum exit code value.
        """
        # Validate input arguments.

        # Check if the 'code_val' argument is an integer.
        if not isinstance(code_val, int):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2}.'
                             ])\
                            .format(
                                    'add_exit_code',
                                    'code_val',
                                    'integer'
                                   )
            raise TypeError(err_msg)

        self._exit_codes[code_name] = code_val

    @abstractmethod
    def run(self) -> None:
        """The run() method is responsible for executing the action code.
        
        All action business logic must be implemented in the run() method of the
        derived class. The run() method must exit the program by calling the
        exit() method of the ArgumentParser object passed to the ProgramAction
        constructor. The exit() method takes an integer argument that represents
        the exit code. The ProgramAction class provides a set of predefined exit
        codes. The predefined exit codes are defined as class attributes.

        Also, all validation routines for the command line arguments must be
        implemented in the run() method of the derived class.
        """
        
        err_msg = ''.join([
                          'A call to the abstract method {0}. ',
                          'The method must be implemented in the derived class.'
                         ])\
                        .format(
                                'run'
                               )
        raise NotImplementedError(err_msg)


# ------------------------------------------------------------------------------
# Class: ProgramUsageAction
# ------------------------------------------------------------------------------
#
# Description: The ProgramUsageAction class implements the ProgramAction
#              interface. It is responsible for printing the program usage
#              information.
#
#              Since the argparse facilities does not provide a switch for
#              printing the program usage information, we need to implement this
#              functionality ourselves.
#
# ------------------------------------------------------------------------------
class ProgramUsageAction(ProgramAction):
    """The ProgramUsageAction class implements the ProgramAction interface. It
    is responsible for printing the program usage information.

    Since the argparse facilities does not provide a switch for printing the
    program usage information, we need to implement this functionality ourselves.
    """

    def __init__(self, parser: ap.ArgumentParser) -> None:
        """Class constructor.

        The constructor takes an argparse.ArgumentParser object as an argument.
        """

        # Validate input arguments.

        # Call the base class constructor. The base class constructor will
        # validate the parser argument.
        super().__init__(parser)

    def run(self) -> None:
        """This method implements the business logic of the action. It is
        responsible for printing the program usage information.
        """

        # Print the program usage information.
        self._parser.print_usage()

        # Exit the program. Note that the only situation in which we exit the
        # program with a EX_OK is when the user requests the program usage.
        self._parser.exit(self._exit_codes['EX_OK'])


class ProgramReadFileAction(ProgramAction):
    """The ProgramReadFileAction class is a demo class that implements the
    ProgramAction interface. Purpose of the class is to demonstrate how passing typing.Any as action parameter value works.
    """

    def __init__(self, parser: ap.ArgumentParser) -> None:
        super().__init__(parser)

    def run(self) -> None:
        """This method implements the business logic of the action. It is
        responsible for demonstrating how passing typing.Any as action parameter value works.
        """

        # Print the program usage information.
        parsed = self._parser.parse_args()
        print('{0}: Input file: {1}'.format(self._parser.prog, parsed.FILE[0]))
        if parsed.dest_file is not None:
            print('{0}: Input file: {1}'.format(
                                                self._parser.prog,
                                                parsed.dest_file[0]
                                               ))

        # Exit the program. Note that the only situation in which we exit the
        # program with a EX_OK is when the user requests the program usage.
        self._parser.exit(self._exit_codes['EX_OK'])

# ------------------------------------------------------------------------------
# Class: ProgramDefaultAction
# ------------------------------------------------------------------------------
#
# Description: The ProgramDefaultAction class implements the ProgramAction
#              interface. It is responsible for printing the simple 'Hello
#              World!' message.
#
# ------------------------------------------------------------------------------
class ProgramDefaultAction(ProgramAction):
    """The ProgramDefaultAction class is a demo class that implements the
    ProgramAction interface. It is responsible for printing the simple 'Hello
    World!' message.
    """

    def __init__(self, parser: ap.ArgumentParser) -> None:
        """Class constructor.

        The constructor takes an argparse.ArgumentParser object as an argument.
        """

        # Validate input arguments.

        # Call the base class constructor. The base class constructor will
        # validate the parser argument.
        super().__init__(parser)

    def run(self) -> None:
        """This method implements the business logic of the action. It is
        responsible for printing the simple 'Hello World!' message to the
        standard output.
        """

        # Print the 'Hello World!' message to the standard output, preceded by
        # the program name.
        print('{0}: Hello World!'.format(self._parser.prog))

        # Exit the program.
        self._parser.exit(self._exit_codes['EX_OK'])


class ProgramActionFactory(object):
    """The ProgramActionFactory class is responsible for creating ProgramAction
    objects. It is a factory class that implements the factory method design
    pattern.

    Before the factory class can be used, the user must register all program
    actions using the register_action() method. The register_action() method
    takes three arguments:

        1. action:        A ProgramAction object.
        2. command_name:  A string that represents the command name. The command
                          name is the name of the sub-command that the user must
                          supply on the command line in order to execute the
                          action. If the action is the top-level command, then
                          the command name must be 'main'.
        3. action_params: A dictionary that contains the action parameters. The
                          action parameters are the command line arguments that
                          the user must supply in order to execute the action.
                          The keys in the dictionary are the names of the
                          command line arguments. The values in the dictionary
                          are the values for the concrete action that is
                          trigerred. If None is used as the parmeter value, then
                          the action is triggered for any value of the given
                          parameter. If action_params is an empty dictionary,
                          then the action is triggered for any set of command
                          line arguments.

    Note that the order in which the actions are registered is important. The
    first action that matches the given set of command line arguments is
    executed. If no action matches the given set of command line arguments, then
    an exception is raised. It is advised that last action registered for a
    given command is the action that matches any set of command line arguments.
    """

    def __init__(self) -> None:
        """Class constructor.

        The constructor initializes the list of actions.
        """
        self._actions = list()

    def register_action(
                        self,
                        action: ProgramAction,
                        command_name: str,
                        action_params: Dict[str, Any]
                       ) -> None:
        """Register a new action.

        The method takes three arguments:

            1. action:        A ProgramAction object.
            2. command_name:  A string that represents the command name. The
                              command name is the name of the sub-command that
                              the user must supply on the command line in order
                              to execute the action. If the action is the
                              top-level command, then the command name must be
                              'main'.
            3. action_params: A dictionary that contains the action parameters.
                              The action parameters are the command line
                              arguments that the user must supply in order to
                              execute the action. The keys in the dictionary
                              are the names of the command line arguments. The
                              values in the dictionary are the values for the
                              concrete action that is trigerred. If None is used
                              as the parmeter value, then the action is
                              triggered for any value of the given parameter. If
                              action_params is an empty dictionary, then the
                              action is triggered for any set of command line
                              arguments.
        
        Note that the order in which the actions are registered is important.
        The first action that matches the given set of command line arguments is
        executed. If no action matches the given set of command line arguments,
        then an exception is raised. It is advised that last action registered
        for a given command is the action that matches any set of command line
        arguments.
        """

        # Validate input arguments.

        # Check if the 'action' argument is a ProgramAction object.
        if not isinstance(action, ProgramAction):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2}.'
                             ])\
                            .format(
                                    'register_action',
                                    'action',
                                    'ProgramAction'
                                   )
            raise TypeError(err_msg)
        
        # Check if the 'command_name' argument is a string.
        if not isinstance(command_name, str):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2}.'
                             ])\
                            .format(
                                    'register_action',
                                    'command_name',
                                    'string'
                                   )
            raise TypeError(err_msg)

        # Check if the 'action_params' argument is a dictionary.
        if not isinstance(action_params, Dict):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2}.'
                             ])\
                            .format(
                                    'register_action',
                                    'action_params',
                                    'Dict'
                                   )
            raise TypeError(err_msg)
        
        # Check if the keys in the 'action_params' dict are strings.
        if 0 != len(action_params):
            for param in action_params.keys():
                if not isinstance(param, str):
                    err_msg = ''.join([
                                      'Invalid call to {0} method. ',
                                      'Parameter "{1}" must be a {2}.'
                                     ])\
                                    .format(
                                            'register_action',
                                            param,
                                            'string'
                                           )
                    raise TypeError(err_msg)
        
        # If we are dealing with command other than the top-level command, then
        # we need to append 'command' to the list of action parameters.
        if 'main' != command_name:
            action_params['command'] = command_name

        # Append the action to the list of actions.
        self._actions.append((command_name, action, action_params))

    def spawn_action(self, parser: ap.ArgumentParser) -> ProgramAction:
        """Spawn a new action.

        The method takes one argument:

            1. parser: An argparse.ArgumentParser object.

        The method returns a ProgramAction object that matches the given set of
        command line arguments.
        """

        # Validate input arguments.

        # Check if the 'parser' argument is an ArgumentParser object.
        if not isinstance(parser, ap.ArgumentParser):
            err_msg = ''.join([
                              'Invalid call to {0} method. ',
                              'Argument "{1}" must be a {2} instance.'
                             ])\
                            .format(
                                    'spawn_action',
                                    'parser',
                                    'argparse.ArgumentParser'
                                   )
            raise TypeError(err_msg)
        
        # Parse the command line arguments.
        parsed = parser.parse_args()

        # Get the command name.
        # By default we assign the name 'main' for the top-level command.
        command_name = 'main'
        if hasattr(parsed, 'command'):
            command_name = parsed.command

        # Get the action.

        # Get all registered actions for the given command.
        reg_actions = [\
            action for action in self._actions \
                if action[0] == command_name\
                    ]
        
        # If there are no registered actions for the given command, then we
        # raise an exception.
        if 0 == len(reg_actions):
            err_msg = ''.join([
                              'In {0}: No action registered for the command ', 
                              '"{1}".'
                             ])\
                            .format(
                                    'spawn_action',
                                    command_name
                                   )
            raise IndexError(err_msg)

        # Try to find an action that matches the given set of action parameters.
        action = None
        for entry in reg_actions:
            # Check if the action is registered with an empty set of parameters.
            # If so, we have found the action.
            if 0 == len(entry[2]):
                action = entry[1]
                break

            # Get all matching action parameters. We match paremeters by
            # comparing the keys (i.e. 'names') in the 'entry[2]' dictionary
            # with the keys in the 'parsed' object.
            matching_params = {\
                key:val for key, val in parsed._get_kwargs() \
                    if key in entry[2].keys()\
                        }

            # Set values of all matching parameters that can take any value to
            # Any.
            matching_params = {\
                key:Any if Any == entry[2][key] else val \
                    for key, val in matching_params.items()\
                        }

            # If the dictionary of matching parameters is not empty, and if the
            # dictionary of matching parameters is equal to the dictionary of
            # action parameters, then we have found the action.
            if 0 != len(matching_params) and matching_params == entry[2]:
                action = entry[1]
                break

        # If we have not found an action, then we raise an exception.
        if None == action:
            err_msg = ''.join([
                              'In {0}: No action registered for the command ', 
                              '"{1}" and given set of arguments {2}.'
                             ])\
                            .format(
                                    'spawn_action',
                                    command_name,
                                    parsed
                                   )
            raise IndexError(err_msg)

        return action


# ==============================================================================
# Main function
# ==============================================================================
if __name__ == '__main__':

    # Create the main parser.
    main_parser = ap.ArgumentParser(
                                    prog=APP_NAME,
                                    description=APP_DESCRIPTION,
                                    epilog=APP_EPILOG,
                                    formatter_class=ap.\
                                        RawDescriptionHelpFormatter
                                   )
    
    # Add the program version information.
    main_parser.add_argument(
                             '-V',
                             '--version',
                             action='version',
                             version=APP_VERSION_INFO,
                             dest='version'
                            )
    
    # Add the usage switch.
    main_parser.add_argument(
                             '-U',
                             '--usage',
                             action='store_true',
                             default=False,
                             help='print program usage information',
                             dest='usage'
                            )

    # Add positional file argument.
    main_parser.add_argument(
                             'FILE',
                             action='store',
                             # type=ap.FileType('r'),
                             type=str,
                             nargs=1,
                             help='file to process',
                             default=None
                            )

    # Add optional file argument.
    main_parser.add_argument(
                             '-f',
                             '--dest-file',
                             dest='dest_file',
                             action='store',
                             type=str,
                             nargs=1,
                             help='destination file',
                             default=None
                            )

    # Create the program action factory.
    action_factory = ProgramActionFactory()

    # Register the program usage action.
    action_factory.register_action(
                                   ProgramUsageAction(main_parser),
                                   'main',
                                   {'usage': True}
                                  )
    
    # Register the file read action.
    action_factory.register_action(
                                   ProgramReadFileAction(main_parser),
                                   'main',
                                   {'FILE': Any, 'dest_file': Any}
                                  )

    # Register the program default action.
    action_factory.register_action(
                                   ProgramDefaultAction(main_parser),
                                   'main',
                                   dict()
                                  )
    
    # Spawn the program action.
    action = action_factory.spawn_action(main_parser)

    # Execute the action code.
    action.run()