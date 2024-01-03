# !/usr/bin/env python3
from ipaddress import ip_address
import queue
import re
from time import perf_counter, sleep

from sympy import O, Ge
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
# * For developing HTTP clients with Requests, see:
#   <https://requests.readthedocs.io/en/master/user/quickstart/>
#
# =============================================================================


# =============================================================================
# Modules import section
# =============================================================================
import requests
from typing import Generator


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

    def __init__(
                 self, ip: str = "",
                 tokens: int = 0,
                 priority: int = 0
                ) -> None:
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
    
    @priority.setter
    def priority(self, new_priority: int) -> None:
        """TODO: Put method docstring HERE.
        """
        self._priority = new_priority
    
    def none(self) -> bool:
        """TODO: Put method docstring HERE.
        """
        return self._ip == ""
    
    def not_none(self) -> bool:
        """TODO: Put method docstring HERE.
        """
        return not self.none()


# -----------------------------------------------------------------------------
# Class: RequestPriorityQueue
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class RequestPriorityQueue:
    """TODO: Put class docstring HERE.
    """
    _queue: list[OutgoingRequest]
    _target: str

    def __init__(self, target) -> None:
        """TODO: Put method docstring HERE.
        """
        self._queue = []
        self._target = target

    def __str__(self) -> str:
        """TODO: Put method docstring HERE.
        """
        return f"RequestPriorityQueue(queue={self._queue})"

    def __repr__(self) -> str:
        """TODO: Put method docstring HERE.
        """
        return self.__str__()

    def __len__(self) -> int:
        """TODO: Put method docstring HERE.
        """
        return len(self._queue)

    def __iter__(self) -> Generator[OutgoingRequest, None, None]:
        """TODO: Put method docstring HERE.
        """
        for request in self._queue:
            yield request

    def __getitem__(self, index: int) -> OutgoingRequest:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if self._queue[index]:
            return self._queue[index]
        else:
            return OutgoingRequest()
    
    def _get_parent_index(self, index: int) -> int:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if self._queue:
            return (index - 1) // 2
        else:
            return -1

    def _get_left_child_index(self, index: int) -> int:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if self._queue:
            return 2 * index + 1
        else:
            return -1
    
    def _get_right_child_index(self, index: int) -> int:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if self._queue:
            return 2 * index + 2
        else:
            return -1
    
    def _swap(self, index1: int, index2: int) -> None:
        """TODO: Put method docstring HERE.
        """
        if index1 < 0 or index1 >= len(self._queue):
            raise IndexError("'index1' out of range")
        
        if index2 < 0 or index2 >= len(self._queue):
            raise IndexError("'index2' out of range")
        
        if self._queue and index1 != index2:
            self._queue[index1], self._queue[index2] = \
                self._queue[index2], self._queue[index1]
    
    def _heapify_up(self, index: int) -> None:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if 0 < index:
            parent_index = self._get_parent_index(index)
        
            if self._queue[index] > self._queue[parent_index]:
                self._swap(index, parent_index)
                self._heapify_up(parent_index)
    
    def _heapify_down(self, index: int) -> None:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if len(self._queue) - 1 > index:
            left_child_index = self._get_left_child_index(index)
            right_child_index = self._get_right_child_index(index)
        
            if left_child_index < len(self._queue) and \
                self._queue[index] < self._queue[left_child_index]:
                self._swap(index, left_child_index)
                self._heapify_down(left_child_index)
        
            if right_child_index < len(self._queue) and \
                self._queue[index] < self._queue[right_child_index]:
                self._swap(index, right_child_index)
                self._heapify_down(right_child_index)
            
    def add(self, request: OutgoingRequest) -> None:
        """TODO: Put method docstring HERE.
        """
        self._queue.append(request)
        self._heapify_up(len(self._queue) - 1)

    def remove(self) -> OutgoingRequest:
        """TODO: Put method docstring HERE.
        """
        if len(self._queue) == 0:
            raise IndexError("queue is empty")
        
        # Try to post the request to the server. If the server is not available,
        # return None.
        result = requests.post(
            self._target,
            json={"ip": self._queue[0].ip, "tokens": self._queue[0].tokens}
            )
        if 201 == result.status_code:
            self._swap(0, len(self._queue) - 1)
            request = self._queue.pop()
            self._heapify_down(0)
        
            return request
        
        return OutgoingRequest()
    
    def peek(self) -> OutgoingRequest:
        """TODO: Put method docstring HERE.
        """
        if len(self._queue) == 0:
            raise IndexError("queue is empty")
        
        return self._queue[0]
    
    def is_empty(self) -> bool:
        """TODO: Put method docstring HERE.
        """
        return len(self._queue) == 0
    
    def modify_priority(self, index: int, new_priority: int) -> None:
        """TODO: Put method docstring HERE.
        """
        if index < 0 or index >= len(self._queue):
            raise IndexError("'index' out of range")
        
        if self._queue:
            if 'OutgoingRequest' != type(self._queue[index]):
                raise TypeError("'index' does not point to an OutgoingRequest")
            self._queue[index].priority = new_priority
            self._heapify_up(index)
            self._heapify_down(index)
    
    def promote_next(self) -> None:
        """TODO: Put method docstring HERE.
        """
        if self._queue:
            current_tokens = self._queue[0].tokens
            current_priority = self._queue[0].priority
            for index, request in enumerate(self._queue):
                if request.tokens < current_tokens:
                    request.priority = current_priority + 1
                    self._heapify_up(index)


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
    import os
    from random import randint
    from time import sleep, strftime
    import logging
    
    os.environ['NO_PROXY'] = '127.0.0.1'
    url = "http://localhost:8000/request"
    ip_addresses = [
        "192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4",
        "192.168.0.31", "192.168.0.32", "192.168.0.33", "192.168.0.34",
        "192.168.0.71", "192.168.0.72", "192.168.0.73", "192.168.0.74"
        ]
    
    # Set the logging level.
    logging.basicConfig(
        filename="client_requests.log",
        encoding="utf-8",
        level=logging.DEBUG
        )
        
    # Create a priority queue and add some requests to it.
    queue = RequestPriorityQueue(url)
    for i in range(100):
        queue.add(OutgoingRequest(
            ip_addresses[randint(0, len(ip_addresses) - 1)],
            randint(1, 5),
            randint(1, 5)
            ))
    
    # Loop until the queue is empty.
    while not queue.is_empty():
        # Remove the request from the queue.
        request = queue.remove()
        
        # If the request is not None, print it.
        if request.not_none():
            print("{0},{1},{2},{3}"\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    request.tokens,
                    request.ip,
                    request.priority
                    ))
            logging.info(f"{0},{1},{2},{3}"\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    request.tokens,
                    request.ip,
                    request.priority
                    ))
        else:
            # Promote the next request in the queue with the same IP address.
            print("{} Promoting next request ..."\
                .format(strftime("%Y-%m-%d %H:%M:%S")))
            queue.promote_next()


# =============================================================================
# This is the standard boilerplate that calls the main() function.
# =============================================================================
if __name__ == "__main__":
    main()


# End of file 'RequestClient.py'