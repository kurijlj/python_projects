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
# 2024-01-09 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * AsynchronousTaskPriorityQueueClientDemo.py: created.
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
            pattern = r"(^$)|"\
                      r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]"\
                      r"{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*"\
                      r"\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]"\
                      r"{};:'\".,<?«»“”‘’]))"
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
            total_tokens: int = 1,
            request_tokens: int = 1
            ) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        validator = self.Validator(
            priority=priority,
            target=target,
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
        return f"PendingTask("\
               f"priority={self._priority}, "\
               f"target={self._target}, " \
               f"total_tokens={self._total_tokens}, "\
               f"request_tokens={self._request_tokens}"\
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
        return f"PendingTask("\
               f"{self._priority}, "\
               f"{self._target}, "\
               f"{self._total_tokens}, "\
               f"{self._request_tokens}"\
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
        # Validate the input data
        validator = self.Validator(
            priority=value,
            target=self._target,
            total_tokens=self._total_tokens,
            request_tokens=self._request_tokens
            )
        
        # Assign the validated data
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
    # Method: post
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def post(self, session: aiohttp.ClientSession) -> dict:
        """TODO: Put method docstring HERE."""

        # Validate the input data
        if not isinstance(session, aiohttp.ClientSession):
            raise TypeError(
                "session must be an instance of "\
                "aiohttp.ClientSession"
                )

        result = {}

        if self.not_none():
            if not session.closed:
                async with session.post(
                        self._target,
                        json={"tokens": self.request_tokens}
                        ) as response:
                    response.raise_for_status()
                    result = await response.json()
        
        return result


# -----------------------------------------------------------------------------
# Class: TaskPriorityQueue
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class TaskPriorityQueue:
    """TODO: Put class docstring HERE.
    """
    _queue: list
    _time_limit: float = 60.0  # 1 minute
    _max_rpm: int
    _request_bucket: int
    _max_tpm: int
    _token_bucket: int
    _rpm_last_refresh_time: float
    _tpm_last_refresh_time: float

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
    def __init__(self, max_rpm: int, max_tpm: int) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        class Validator(BaseModel):
            max_rpm: int = Field(default=1, ge=1)
            max_tpm: int = Field(default=1, ge=1)
        validator = Validator(max_rpm=max_rpm, max_tpm=max_tpm)

        # Assign the validated data --------------------------------------------
        self._queue = []
        self._max_rpm = validator.max_rpm
        self._request_bucket = validator.max_rpm
        self._max_tpm = validator.max_tpm
        self._token_bucket = validator.max_tpm
    
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
        result = f"TaskPriorityQueue("\
                 f"max_rpm={self._max_rpm}, "\
                 f"max_tpm={self._max_tpm}"\
                 f"queue=["\

        for task in self._queue:
            result += f"{task.__repr__()}, "

        result = result[:-2] + f"])"
    
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
        return f"TaskPriorityQueue("\
               f"{self._max_rpm}, "\
               f"{self._max_tpm}, "\
               f"{len(self._queue)}"\
               f")"
    
    # -------------------------------------------------------------------------
    # Method: add_task
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def add_task(self, task: PendingTask) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        if not isinstance(task, PendingTask):
            raise TypeError(
                "task must be an instance of PendingTask"
                )

        # Add the task to the queue --------------------------------------------
        heapq.heappush(self._queue, task)

    # -------------------------------------------------------------------------
    # Method: pop_task
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def pop_task(self) -> PendingTask:
        """TODO: Put method docstring HERE."""

        # Pop the task from the queue ------------------------------------------
        return heapq.heappop(self._queue)

    # -------------------------------------------------------------------------
    # Method: peek_task
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def peek_task(self) -> PendingTask:
        """TODO: Put method docstring HERE."""

        # Peek the task from the queue -----------------------------------------
        return self._queue[0]
    
    # -------------------------------------------------------------------------
    # Method: is_empty
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def is_empty(self) -> bool:
        """TODO: Put method docstring HERE."""
        return 0 == len(self._queue)

    # -------------------------------------------------------------------------
    # Method: consume
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def consume(self) -> None:
        """TODO: Put method docstring HERE."""

        # Initialize the time counters if first time consuming the queue ------
        if "_rpm_last_refresh_time" not in self.__dict__:
            print(f"{strftime('%Y-%m-%d %H:%M:%S')} Initializing counters")
            self._rpm_last_refresh_time = perf_counter()
            self._tpm_last_refresh_time = perf_counter()

        # Update the RPM -------------------------------------------------------
        current_time = perf_counter()
        rpm_elapsed_time = current_time - self._rpm_last_refresh_time
        print("{} RPM elapsed time: {}"\
              .format(strftime("%Y-%m-%d %H:%M:%S"), rpm_elapsed_time))
        if rpm_elapsed_time > self._time_limit:
            print("{} Resetting RPM bucket"\
                  .format(strftime("%Y-%m-%d %H:%M:%S")))
            self._request_bucket = self._max_rpm
            self._rpm_last_refresh_time = current_time
            rpm_elapsed_time = 0

        # Update the TPM -------------------------------------------------------
        current_time = perf_counter()
        tpm_elapsed_time = current_time - self._tpm_last_refresh_time
        print("{} TPM elapsed time: {}"\
              .format(strftime("%Y-%m-%d %H:%M:%S"), tpm_elapsed_time))
        if tpm_elapsed_time > self._time_limit:
            print("{} Resetting TPM bucket"\
                  .format(strftime("%Y-%m-%d %H:%M:%S")))
            self._token_bucket = self._max_tpm
            self._tpm_last_refresh_time = current_time
            tpm_elapsed_time = 0

        # Get current task -----------------------------------------------------
        current = self.peek_task()

        # Pause consumation if limits are reached ------------------------------
        if 0 > self._request_bucket - 1 \
                and 0 > self._token_bucket - current.request_tokens:
            # Both limits exceeded. Wait until both reset.
            print(
                "{} Both limits exceeded ({} - {}, {} - {})."\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._request_bucket,
                        1,
                        self._token_bucket,
                        current.request_tokens
                    )
                )
            elapsed = max(rpm_elapsed_time, tpm_elapsed_time)
            print(
                "{} Waiting {} seconds for bucket refresh\t{}\t{}"\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    self._time_limit - elapsed,
                    self._request_bucket,
                    self._token_bucket
                    )
                )
            await asyncio.sleep(self._time_limit - elapsed)
        
        elif 0 > self._request_bucket - 1:
            # RPM limit exceeded. Wait until reset.
            print("{} RPM limit exceeded ({} - {})."\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    self._request_bucket,
                    1
                    )
                )
            elapsed = rpm_elapsed_time
            print(
                "{} Waiting {} seconds for bucket refresh\t{}\t{}"\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    self._time_limit - elapsed,
                    self._request_bucket,
                    self._token_bucket
                    )
                )
            await asyncio.sleep(self._time_limit - elapsed)
        
        elif 0 > self._token_bucket - current.request_tokens:
            # TPM limit exceeded. Wait until tokens reset.
            print("{} TPM limit exceeded ({} - {})."\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    self._token_bucket,
                    current.request_tokens
                    )
                )
            elapsed = tpm_elapsed_time
            print(
                "{} Waiting {} seconds for bucket refresh\t{}\t{}"\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._time_limit - elapsed,
                        self._request_bucket,
                        self._token_bucket
                        )
                )
            await asyncio.sleep(self._time_limit - elapsed)

        else:
            print(
                "{} No limits exceeded ({} - {}, {} - {})."\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._request_bucket,
                        1,
                        self._token_bucket,
                        current.request_tokens
                        )
                )
        
        # Fetch the task to a server -------------------------------------------
        async with aiohttp.ClientSession() as session:
            try:
                result = await current.post(session)

            except aiohttp.ClientError as error:
                print(
                    "{}\t{}\t{}"\
                        .format(
                            strftime("%Y-%m-%d %H:%M:%S"),
                            current.__repr__(),
                            error
                            )
                    )
            else:
                print(
                    "{}\t{}\t{}"\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        current.__repr__(),
                        result
                        )
                    )

                # Update buckets ----------------------------------------------
                if 0 > self._request_bucket - 1:
                    self._request_bucket = 0
                else:
                    self._request_bucket -= 1
                
                if 0 > self._token_bucket - current.request_tokens:
                    self._token_bucket = 0
                else:
                    self._token_bucket -= current.request_tokens
                
                # Remove the task from the queue -------------------------------
                self.pop_task()

                # Print bucket status -----------------------------------------
                print("{}\t{}\t{}"\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._request_bucket,
                        self._token_bucket
                        )
                    )
                
                await asyncio.sleep(0.5)


        # Zero-sleep to allow underlying connections to close ------------------
        await asyncio.sleep(0)
    
    # -------------------------------------------------------------------------
    # Method: print_queue
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def print_queue(self) -> None:
        """TODO: Put method docstring HERE."""
        print("TaskPriorityQueue(")
        print(f"\tmax_rpm={self._max_rpm},")
        print(f"\tmax_tpm={self._max_tpm},")
        print(f"\tqueue=[")
        for task in self._queue:
            print(f"\t\t{task.__repr__()},")
        print(f"\t]")
        print(")")


# =============================================================================
# Main function section
# =============================================================================
async def main():
    max_rpm = 5
    max_tpm = 5
    target = "http://localhost:8000/post"

    # Create the task queue ----------------------------------------------------
    task_queue = TaskPriorityQueue(max_rpm, max_tpm)

    # Add tasks to the queue ---------------------------------------------------
    task_queue.add_task(PendingTask(priority=0, target=target))
    task_queue.add_task(PendingTask(
        priority=2,
        target=target,
        total_tokens=5,
        request_tokens=5
        ))
    task_queue.add_task(PendingTask(
        priority=1,
        target=target,
        total_tokens=2,
        request_tokens=2
        ))
    task_queue.add_task(PendingTask(
        priority=3,
        target=target,
        total_tokens=4,
        request_tokens=4
        ))
    
    # Print the task queue -----------------------------------------------------
    task_queue.print_queue()

    # Consume the task queue ---------------------------------------------------
    while not task_queue.is_empty():
        await task_queue.consume()


# =============================================================================
# Main program section
# =============================================================================
if __name__ == "__main__":
    asyncio.run(main())


# End of file: 'AsynchronousTaskPriorityQueueClientDemo.py'