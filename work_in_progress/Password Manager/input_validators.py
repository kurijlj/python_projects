"""Write an elaborate description of the module here.
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
# 2023-06-18 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * input_validators.py: created.
#
# ==============================================================================


# ==============================================================================
# Imports Section
# ==============================================================================

from pathlib import Path
from user_input import UserInput


# ==============================================================================
# Classes Section
# ==============================================================================
class UserInputValidator():
    """Abstract base class for user input validators.

    This class is used to validate user input. It is an abstract base class and
    must be subclassed to be used. Subclasses must implement the '__init__' and
    'validate' method.

    Attributes:
        _message (str): Error message to be displayed if validation fails.
    """

    def __init__(self):
        """Class constructor.

        Call the super().__init__() from the subclass constructor to properly
        initialize the class.

        Args:
            None.

        Example:
            class MyValidator(UserInputValidator):
                def __init__(self):
                    super().__init__()
                    self._message = "My error message."

                def validate(self, user_input: UserInput) -> bool:
                    if user_input == "my_input":
                        return True
                    else:
                        return False
        """
        self._message = None

    @property
    def message(self) -> str:
        """Return the error message.

        Args:
            None.

        Returns:
            str: The error message.

        Example:
            class MyValidator(UserInputValidator):
                def __init__(self):
                    super().__init__()
                    self._message = "My error message."

                def validate(self, user_input: UserInput) -> bool:
                    if user_input == "my_input":
                        return True
                    else:
                        return False

            validator = MyValidator()
            print(validator.message)
        """

        return self._message
    
    def validate(self, user_input: UserInput) -> bool:
        """Virtual method to validate user input.

        This method must be implemented in the subclass.
        """

        raise NotImplementedError("Method 'validate' not implemented.")

# End of input_validators.py