# !/usr/bin/env python3
from time import perf_counter
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
#  This file is part of Request Priority Queue.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================


# =============================================================================
#
# 2024-01-02 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * RequestClient.py: created.
#
# =============================================================================


# =============================================================================
#
# TODO:
#
# =============================================================================


# =============================================================================
#
# References (this section should be deleted in the release version)
#
# =============================================================================


# =============================================================================
# Modules import section
# =============================================================================


# =============================================================================
# User classes section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: OutgoingRequest
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class OutgoingRequest:
    """TODO: Put class docstring HERE.
    """
    _ip: str
    _tokens: int
    _priority: int

    def __init__(self, ip: str, tokens: int, priority: int) -> None:
        """TODO: Put method docstring HERE.
        """
        self._ip = ip
        self._tokens = tokens
        self._priority = priority

    def __str__(self) -> str:
        """TODO: Put method docstring HERE.
        """
        return f"OutgoingRequest(ip={self._ip}, tokens={self._tokens}, " \
               f"priority={self._priority})"

    def __repr__(self) -> str:
        """TODO: Put method docstring HERE.
        """
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """TODO: Put method docstring HERE.
        """
        if not isinstance(other, OutgoingRequest):
            return NotImplemented

        return self._priority == other._priority

    def __lt__(self, other: object) -> bool:
        """TODO: Put method docstring HERE.
        """
        if not isinstance(other, OutgoingRequest):
            return NotImplemented

        return self._priority < other._priority
    
    def __gt__(self, other: object) -> bool:
        """TODO: Put method docstring HERE.
        """
        if not isinstance(other, OutgoingRequest):
            return NotImplemented

        return self._priority > other._priority
    
    def __le__(self, other: object) -> bool:
        """TODO: Put method docstring HERE.
        """
        if not isinstance(other, OutgoingRequest):
            return NotImplemented

        return self._priority <= other._priority
    
    def __ge__(self, other: object) -> bool:
        """TODO: Put method docstring HERE.
        """
        if not isinstance(other, OutgoingRequest):
            return NotImplemented

        return self._priority >= other._priority
    
    @property
    def ip(self) -> str:
        """TODO: Put method docstring HERE.
        """
        return self._ip
    
    @property
    def tokens(self) -> int:
        """TODO: Put method docstring HERE.
        """
        return self._tokens
    
    @property
    def priority(self) -> int:
        """TODO: Put method docstring HERE.
        """
        return self._priority


# =============================================================================
# User functions section
# =============================================================================


# =============================================================================
# Global constants
# =============================================================================


# =============================================================================
# Global variables
# =============================================================================


# =============================================================================
# Main function
# =============================================================================
def main():
    pass


# =============================================================================
# This is the standard boilerplate that calls the main() function.
# =============================================================================
if __name__ == '__main__':
    main()


# End of file 'RequestClient.py'