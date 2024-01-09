# !/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
#  This file is part of Asynchronous Request Priority Queue.
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
# 2024-01-07 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * AsynchronousRequestClient.py: created.
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
# * For developing custom priority queues, see:
#   <https://docs.python.org/3/library/heapq.html>
#
# * For developing concurrent code with asyncio, see:
#   <https://docs.python.org/3/library/asyncio-protocol.html#tcp-echo-client>
#
# * For developing asynchronous HTTP clients with aiohttp, see:
#   <https://docs.aiohttp.org/en/stable/client_quickstart.html>
#
# * For data validation using pydantic, see:
#   <https://pydantic-docs.helpmanual.io/usage/validators/>
#
# * For regular expressions pattern to validate URLs, see:
#   <https://daringfireball.net/2010/07/improved_regex_for_matching_urls>
#
# =============================================================================


# =============================================================================
# Modules import section
# =============================================================================
import aiohttp
import asyncio
import heapq
import logging
from pprint import pprint
from pydantic import BaseModel, Field
from time import perf_counter, strftime


# =============================================================================
# User classes section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: PendingTask
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class PendingTask:
    """TODO: Put class docstring HERE.
    """
    _priority: int
    _target: str
    _source: str
    _total_tokens: int
    _request_tokens: int

    # -------------------------------------------------------------------------
    # Nested class: Validator
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    class Validator(BaseModel):
        priority: int = Field(default=0, ge=0, le=5)
        target: str = Field(
            # pattern=r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$"
            pattern = r"(^$)|"\
                      r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]"\
                      r"{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*"\
                      r"\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]"\
                      r"{};:'\".,<?«»“”‘’]))"
            )
        source: str = Field(
            pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"\
                      r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            )
        total_tokens: int = Field(default=1, ge=1)
        request_tokens: int = Field(default=1, ge=1)

    # -------------------------------------------------------------------------
    # Method: __init__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __init__(
            self,
            priority: int = 0,
            target: str = "",
            source: str = "",
            total_tokens: int = 1,
            request_tokens: int = 1
            ) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        validator = self.Validator(
            priority=priority,
            target=target,
            source=source,
            total_tokens=total_tokens,
            request_tokens=request_tokens
            )
        
        # Validate the request tokens. We use another nested class to complete
        # the validation of the request tokens. This is because the request
        # tokens must be less than or equal to the total tokens.
        class RequestTokensValidator(BaseModel):
            request_tokens: int = Field(
                default=1,
                ge=1,
                le=validator.total_tokens
                )
        RequestTokensValidator(request_tokens=request_tokens)

        # Assign the validated data --------------------------------------------
        self._priority = validator.priority
        self._target = validator.target
        self._source = validator.source
        self._total_tokens = validator.total_tokens
        self._request_tokens = validator.request_tokens

    # -------------------------------------------------------------------------
    # Method: __repr__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """TODO: Put method docstring HERE."""
        return f"PendingTask("\
               f"{self._priority}, "\
               f"{self._target}, "\
               f"{self._source}, "\
               f"{self._total_tokens}, "\
               f"{self._request_tokens}"\
               f")"
    
    # -------------------------------------------------------------------------
    # Method: __str__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        """TODO: Put method docstring HERE."""
        return f"PendingTask("\
               f"priority={self._priority}, "\
               f"target={self._target}, " \
               f"{self._source}, "\
               f"total_tokens={self._total_tokens}, "\
               f"request_tokens={self._request_tokens}"\
               f")"
    
    # -------------------------------------------------------------------------
    # Method: __eq__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        """TODO: Put method docstring HERE."""
        if isinstance(other, PendingTask):
            return self._priority == other._priority
        else:
            return False
    
    # -------------------------------------------------------------------------
    # Method: __lt__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __lt__(self, other: object) -> bool:
        """TODO: Put method docstring HERE."""
        if isinstance(other, PendingTask):
            return self._priority < other._priority
        else:
            return False
    
    # -------------------------------------------------------------------------
    # Method: __gt__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __gt__(self, other: object) -> bool:
        """TODO: Put method docstring HERE."""
        if isinstance(other, PendingTask):
            return self._priority > other._priority
        else:
            return False
    
    # -------------------------------------------------------------------------
    # Method: __le__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __le__(self, other: object) -> bool:
        """TODO: Put method docstring HERE."""
        if isinstance(other, PendingTask):
            return self._priority <= other._priority
        else:
            return False
    
    # -------------------------------------------------------------------------
    # Method: __ge__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __ge__(self, other: object) -> bool:
        """TODO: Put method docstring HERE."""
        if isinstance(other, PendingTask):
            return self._priority >= other._priority
        else:
            return False
    
    # -------------------------------------------------------------------------
    # Property: priority
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @property
    def priority(self) -> int:
        return self._priority
    
    # -------------------------------------------------------------------------
    # Property: target
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @property
    def target(self) -> str:
        return self._target
    
    # -------------------------------------------------------------------------
    # Property: source
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @property
    def source(self) -> str:
        return self._source

    # -------------------------------------------------------------------------
    # Property: total_tokens
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @property
    def total_tokens(self) -> int:
        return self._total_tokens
    
    # -------------------------------------------------------------------------
    # Property: request_tokens
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @property
    def request_tokens(self) -> int:
        return self._request_tokens
    
    # -------------------------------------------------------------------------
    # Setter: priority
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    @priority.setter
    def priority(self, value: int):
        self._priority = value
    
    # -------------------------------------------------------------------------
    # Method: none
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def none(self) -> bool:
        """TODO: Put method docstring HERE."""
        return "" == self._target
    
    # -------------------------------------------------------------------------
    # Method: not_none
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def not_none(self) -> bool:
        """TODO: Put method docstring HERE."""
        return "" != self._target
    
    # -------------------------------------------------------------------------
    # Method: payload_as_dict
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def payload_as_dict(self) -> dict:
        """TODO: Put method docstring HERE."""
        return {
            "ip": self._source,
            "tokens": self._request_tokens
            }
    
    # -------------------------------------------------------------------------
    # Method: payload_as_json
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def payload_as_json(self) -> str:
        """TODO: Put method docstring HERE."""
        return f"{{"\
               f"\"ip\": \"{self._source}\", "\
               f"\"tokens\": {self._request_tokens}"\
               f"}}"


class PendingTaskQueue:
    """TODO: Put class docstring HERE.
    """
    _queue: list

    # -------------------------------------------------------------------------
    # Method: __init__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self._queue = []
    
    # -------------------------------------------------------------------------
    # Method: __repr__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        result = "PendingTaskQueue(\n"
        if 0 < len(self._queue):
            for task in self._queue:
                result += f"{task},\n"
            result = result[:-1]  # Remove the last comma and space
        result += ")"

        return result
    
    # -------------------------------------------------------------------------
    # Method: __str__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        result = "PendingTaskQueue("
        if 0 < len(self._queue):
            if 3 >= len(self._queue):
                for task in self._queue:
                    result += f"{task}, "
                result = result[:-2]
            else:
                for task in self._queue[:3]:
                    result += f"{task}, "
                result = result[:-2] + ", ..."
        result += ")"

        return result
    
    # -------------------------------------------------------------------------
    # Method: add
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def push(self, task: PendingTask) -> None:
        heapq.heappush(self._queue, task)
    
    # -------------------------------------------------------------------------
    # Method: pop
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def pop(self) -> PendingTask:
        return heapq.heappop(self._queue)
    
    # -------------------------------------------------------------------------
    # Method: peek
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def peek(self) -> PendingTask:
        return self._queue[0]
    
    # -------------------------------------------------------------------------
    # Method: size
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def size(self) -> int:
        return len(self._queue)
    
    # -------------------------------------------------------------------------
    # Method: empty
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def empty(self) -> bool:
        return 0 == len(self._queue)
    
    # -------------------------------------------------------------------------
    # Method: clear
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def clear(self) -> None:
        self._queue.clear()
    
    # -------------------------------------------------------------------------
    # Method: tasks
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def tasks(self) -> list:
        return self._queue


# -----------------------------------------------------------------------------
# Class: ServerRequestManager
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class ServerRequestManager:
    """TODO: Put class docstring HERE.
    """
    _max_rpm: int
    _rpm: int
    _rpm_interval: float
    _rpm_interval_start: float
    _rpm_semaphore: asyncio.Semaphore
    _max_tpm: int
    _tpm: int
    _tpm_interval: float
    _tpm_interval_start: float
    _tpm_semaphore: asyncio.Semaphore

    # -------------------------------------------------------------------------
    # Nested class: Validator
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # -------------------------------------------------------------------------
    class Validator(BaseModel):
        max_rpm: int = Field(default=0, ge=0)
        max_tpm: int = Field(default=0, ge=0)

    # -------------------------------------------------------------------------
    # Method: __init__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __init__(self, max_rpm: int = 0, max_tpm: int = 0) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        validator = self.Validator(max_rpm=max_rpm, max_tpm=max_tpm)

        self._max_rpm = validator.max_rpm
        self._rpm = 0
        self._rpm_interval = 60.0
        self._rpm_interval_start = 0.0
        self._max_tpm = validator.max_tpm
        self._tpm = 0
        self._tpm_interval = 60.0
        self._tpm_interval_start = 0.0

    # -------------------------------------------------------------------------
    # Method: __repr__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """TODO: Put method docstring HERE."""
        return f"ServerRequestManager("\
            f"{self._max_rpm},"\
            f"{self._rpm},"\
            f"{self._max_tpm}"\
            f"{self._tpm}"\
            f")"
    
    # -------------------------------------------------------------------------
    # Method: __str__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        """TODO: Put method docstring HERE."""
        return f"ServerRequestManager(max_rpm={self._max_rpm}, "\
               f"rpm={self._rpm}, "\
               f"max_tpm={self._max_tpm}, "\
               f"tpm={self._tpm})"
    
    # -------------------------------------------------------------------------
    # Method: fetch_task
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def fetch_task(self, task: PendingTask) -> None:
        """TODO: Put method docstring HERE."""
        
        # Initialize semaphores (if not initialized yet) ----------------------
        if "_rpm_semaphore" not in self.__dict__:
            self._rpm_semaphore = asyncio.Semaphore(self._max_rpm)
        if "_tpm_semaphore" not in self.__dict__:
            self._tpm_semaphore = asyncio.Semaphore(self._max_tpm)

        # Check if semaphores need to be reset --------------------------------
        current_time = perf_counter()
        if self._rpm_interval_start + self._rpm_interval < current_time:
            self._rpm_interval_start = current_time
            self._rpm = 0
        if self._tpm_interval_start + self._tpm_interval < current_time:
            self._tpm_interval_start = current_time
            self._tpm = 0
        
        async with self._rpm_semaphore, self._tpm_semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        task.target,
                        json=task.payload_as_dict()
                        ) as response:
                    print("{} fetching task: {}"\
                          .format(strftime("%H:%M:%S"), task.__repr__()))
                    print("{} response status: {}"\
                          .format(strftime("%H:%M:%S"), response.status))
                    pprint(await response.json())


# =============================================================================
# User functions section
# =============================================================================


# =============================================================================
# Main program section
# =============================================================================
async def main():
    # Modules import section --------------------------------------------------
    from random import randint

    # Define the target URL for the server and Max RPM and Max TPM ----------
    target = "http://localhost:8000"
    max_rpm = 5
    max_tpm = 5

    # Set client pool --------------------------------------------------------
    client_pool = [
        "192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4",
        "192.168.0.31", "192.168.0.32", "192.168.0.33", "192.168.0.34",
        "192.168.0.71", "192.168.0.72", "192.168.0.73", "192.168.0.74"
    ]

    # Create a ServerRequestManager object -----------------------------------
    manager = ServerRequestManager(max_rpm, max_tpm)

    # Create a PendingTaskQueue object ---------------------------------------
    queue = PendingTaskQueue()

    # Populate the queue -----------------------------------------------------
    for i in range(100):
        total_tokens = randint(1, 5)
        task = PendingTask(
            randint(0, 5),
            target + "/request",
            client_pool[randint(0, len(client_pool) - 1)],
            total_tokens,
            randint(1, total_tokens)
            )
        queue.push(task)
    
    # Print the queue --------------------------------------------------------
    print(queue.__repr__() + "\n")

    # Fetch tasks from the queue ---------------------------------------------
    while 0 < len(queue._queue):
        task = queue.pop()
        await manager.fetch_task(task)


# =============================================================================
#  __main__ section
# =============================================================================
if __name__ == "__main__":
    asyncio.run(main())


# End of file "AsynchronousRequestClient.py"