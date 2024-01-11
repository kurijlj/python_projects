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
# * ClientBot.py: created.
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
from time import perf_counter
from typing import Generator


# =============================================================================
# Logging configuration section
# =============================================================================
logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
    )


# =============================================================================
# User classes section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: TimedResourceBucket
# -----------------------------------------------------------------------------
#
# Description:
#
# Attributes:
#
# Methods:
#
# -----------------------------------------------------------------------------
class TimedResourceBucket:
    """TODO: Put class docstring HERE.
    """
    _capacity: int
    _bucket: int
    _timer_cycle: float
    _timer: float

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
    def __init__(self, capacity: int, timer_cycle: float) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        class Validator(BaseModel):
            capacity: int = Field(default=1, ge=1)
            timer_cycle: float = Field(default=60.0, ge=1.0)
        validator = Validator(capacity=capacity, timer_cycle=timer_cycle)

        # Assign the validated data --------------------------------------------
        self._capacity = validator.capacity
        self._bucket = validator.capacity
        self._timer_cycle = validator.timer_cycle
    
    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def bucket(self) -> int:
        return self._bucket
    
    @property
    def timer_cycle(self) -> float:
        return self._timer_cycle
    
    @property
    def timer(self) -> float:
        if "_timer" not in self.__dict__:
            return self._timer_cycle
        else:
            return self._timer_cycle - (perf_counter() - self._timer)
    
    def init_timer(self) -> None:
        if "_timer" not in self.__dict__:
            self._timer = perf_counter()
    
    def reset(self) -> None:
        if "_timer" in self.__dict__:
            if self.timer <= 0:
                self._timer += (
                    (perf_counter() - self._timer)
                    // self._timer_cycle
                    ) * self._timer_cycle
                self._bucket = self._capacity
    
    def consume(self, tokens: int) -> None:
        if self._bucket - tokens < 0:
            self._bucket = 0
        else:
            self._bucket -= tokens

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
    _max_rpm: int
    _request_bucket: int
    _max_tpm: int
    _token_bucket: int
    _timer_cycle: float = 60.0  # 1 minute
    _request_timer: float
    _token_timer: float

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
    # Method: __len__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._queue)

    # -------------------------------------------------------------------------
    # Method: __iter__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __iter__(self) -> Generator[PendingTask, None, None]:
        """TODO: Put method docstring HERE."""
        for task in self._queue:
            yield task

    # -------------------------------------------------------------------------
    # Method: __getitem__
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def __getitem__(self, index: int) -> PendingTask:
        """TODO: Put method docstring HERE."""

        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Return the task ------------------------------------------------------
        if self.is_empty():
            return PendingTask()
        else:
            return self._queue[index]
    
    # -------------------------------------------------------------------------
    # Method: _get_parent_index
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _get_parent_index(self, index: int) -> int:
        """TODO: Put method docstring HERE."""
        
        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Return the parent index ----------------------------------------------
        if self.is_empty():
            return -1
        else:
            return (index - 1) // 2
    
    # -------------------------------------------------------------------------
    # Method: _get_left_child_index
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _get_left_child_index(self, index: int) -> int:
        """TODO: Put method docstring HERE."""
        
        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Return the left child index ------------------------------------------
        if self.is_empty() and len(self._queue) - 1 == index:
            return -1
        else:
            return 2 * index + 1
    
    # -------------------------------------------------------------------------
    # Method: _get_right_child_index
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _get_right_child_index(self, index: int) -> int:
        """TODO: Put method docstring HERE."""
        
        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Return the right child index -----------------------------------------
        if self.is_empty() and len(self._queue) - 1 == index:
            return -1
        else:
            return 2 * index + 2
    
    # -------------------------------------------------------------------------
    # Method: _swap
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _swap(self, index1: int, index2: int) -> None:
        """TODO: Put method docstring HERE."""

        # Check if the indices are valid ---------------------------------------
        if not isinstance(index1, int):
            raise TypeError("index1 must be an integer")
        if index1 < 0 or index1 >= len(self._queue):
            raise IndexError("index1 out of range")
        if not isinstance(index2, int):
            raise TypeError("index2 must be an integer")
        if index2 < 0 or index2 >= len(self._queue):
            raise IndexError("index2 out of range")
        
        # Swap the tasks -------------------------------------------------------
        if not self.is_empty() and index1 != index2:
            self._queue[index1], self._queue[index2] = \
                self._queue[index2], self._queue[index1]
    
    # -------------------------------------------------------------------------
    # Method: _heapify_up
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _heapify_up(self, index: int) -> None:
        """"TODO: Put method docstring HERE."""

        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Heapify the queue ----------------------------------------------------
        if not self.is_empty():
            parent_index = self._get_parent_index(index)
            if parent_index >= 0 \
                    and self._queue[index] > self._queue[parent_index]:
                self._swap(index, parent_index)
                self._heapify_up(parent_index)

    # -------------------------------------------------------------------------
    # Method: _heapify_down
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _heapify_down(self, index: int) -> None:
        """TODO: Put method docstring HERE."""

        # Check if the index is valid ------------------------------------------
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._queue):
            raise IndexError("index out of range")
        
        # Heapify the queue ----------------------------------------------------
        if not self.is_empty() and index != len(self._queue) - 1:
            left_child_index = self._get_left_child_index(index)
            right_child_index = self._get_right_child_index(index)
            if left_child_index >= 0 \
                    and self._queue[index] < self._queue[left_child_index]:
                self._swap(index, left_child_index)
                self._heapify_down(left_child_index)
            elif right_child_index >= 0 \
                    and self._queue[index] < self._queue[right_child_index]:
                self._swap(index, right_child_index)
                self._heapify_down(right_child_index)

    # -------------------------------------------------------------------------
    # Method: _init_request_timer
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _init_request_timer(self) -> None:
        """TODO: Put method docstring HERE."""
        if "_request_timer" not in self.__dict__:
            self._request_timer = perf_counter()

    # -------------------------------------------------------------------------
    # Method: _init_token_timer
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _init_token_timer(self) -> None:
        """TODO: Put method docstring HERE."""
        if "_token_timer" not in self.__dict__:
            self._token_timer = perf_counter()

    # -------------------------------------------------------------------------
    # Method: _request_timer_counter
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _request_timer_counter(self) -> float:
        """TODO: Put method docstring HERE."""

        if "_request_timer" not in self.__dict__:
            return self._timer_cycle
        else:
            return self._timer_cycle - (perf_counter() - self._request_timer)

    # -------------------------------------------------------------------------
    # Method: _token_timer_counter
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _token_timer_counter(self) -> float:
        """TODO: Put method docstring HERE."""

        if "_token_timer" not in self.__dict__:
            return self._timer_cycle
        else:
            return self._timer_cycle - (perf_counter() - self._token_timer)

    # -------------------------------------------------------------------------
    # Property: _reset_request_counters
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _reset_request_counters(self) -> None:
        """TODO: Put method docstring HERE."""

        if "_request_timer" in self.__dict__:
            if self._request_timer_counter() <= 0:
                self._request_timer += (
                    (perf_counter() - self._request_timer)
                    // self._timer_cycle
                    ) * self._timer_cycle
                self._request_bucket = self._max_rpm

    # -------------------------------------------------------------------------
    # Property: _reset_token_counters
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    def _reset_token_counters(self) -> None:
        """TODO: Put method docstring HERE."""

        if "_token_timer" in self.__dict__:
            if self._token_timer_counter() <= 0:
                self._token_timer += (
                    (perf_counter() - self._token_timer)
                    // self._timer_cycle
                    ) * self._timer_cycle
                self._token_bucket = self._max_tpm

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
    def add(self, task: PendingTask) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        if not isinstance(task, PendingTask):
            raise TypeError(
                "task must be an instance of PendingTask"
                )

        # Add the task to the queue --------------------------------------------
        self._queue.append(task)
        self._heapify_up(len(self._queue) - 1)

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
        """TODO: Put method docstring HERE."""

        # Pop the task from the queue ------------------------------------------
        if self.is_empty():
            return PendingTask()
        else:
            self._swap(0, len(self._queue) - 1)
            task = self._queue.pop()
            self._heapify_down(0)
            return task

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
    # Method: consume_top
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def consume_top(self) -> None:
        """TODO: Put method docstring HERE."""

        # Check if the queue is empty ------------------------------------------
        if self.is_empty():
            return

        # Initialize the time counters if first time consuming the queue ------
        self._init_request_timer()
        self._init_token_timer()

        # Update the RPM -------------------------------------------------------
        current_time = perf_counter()
        rpm_elapsed_time = current_time - self._request_timer
        logging.debug(f"RPM elapsed time: {rpm_elapsed_time:.2f} seconds")
        if rpm_elapsed_time > self._timer_cycle:
            logging.debug("Resetting RPM bucket")
            self._request_bucket = self._max_rpm
            # Ensure time counting is performed in equidistant intervals
            self._request_timer += self._timer_cycle
            rpm_elapsed_time = current_time - self._request_timer

        # Update the TPM -------------------------------------------------------
        current_time = perf_counter()
        tpm_elapsed_time = current_time - self._token_timer
        logging.debug(f"TPM elapsed time: {tpm_elapsed_time:.2f} seconds")
        if tpm_elapsed_time > self._timer_cycle:
            logging.debug("Resetting TPM bucket")
            self._token_bucket = self._max_tpm
            # Ensure time counting is performed in equidistant intervals
            self._token_timer += self._timer_cycle
            tpm_elapsed_time = current_time - self._token_timer

        # Get current task -----------------------------------------------------
        current = self.peek()

        # Pause consumation if limits are reached ------------------------------
        if 0 > self._request_bucket - 1 \
                and 0 > self._token_bucket - current.request_tokens:
            # Both limits exceeded. Wait until both reset.
            logging.debug(
                f"Both limits exceeded: "\
                f"Request bucket: {self._request_bucket}, "\
                f"Pending requests: {1}, "\
                f"Token bucket: {self._token_bucket}, "\
                f"Pending tokens: {current.request_tokens}"
                )
            elapsed = min(rpm_elapsed_time, tpm_elapsed_time)
            logging.debug(
                "Waiting {:.2f} seconds for bucket refresh"\
                    .format(self._timer_cycle - elapsed + 10)
                )
            # Add 10 seconds to counteract the possible missmatch between the
            # server and the client clocks.
            await asyncio.sleep(self._timer_cycle - elapsed + 10)

            # Reset the time counters and buckets to prevent resetting the
            # buckets at the beginning of the next iteration, and after the
            # dispatching of the current task.
            self._request_timer += self._timer_cycle
            self._token_timer += self._timer_cycle
            self._request_bucket = self._max_rpm
            self._token_bucket = self._max_tpm
        
        elif 0 > self._request_bucket - 1:
            # RPM limit exceeded. Wait until reset.
            logging.debug(
                f"RPM limit exceeded: "\
                f"Request bucket: {self._request_bucket}, "\
                f"Pending requests: {1}"
                )
            elapsed = rpm_elapsed_time
            logging.debug(
                "Waiting {:.2f} seconds for bucket refresh"\
                    .format(self._timer_cycle - elapsed + 10)
                )
            # Add 10 seconds to counteract the possible missmatch between the
            # server and the client clocks.
            await asyncio.sleep(self._timer_cycle - elapsed + 10)
        
            # Reset the time counter and bucket to prevent resetting the
            # bucket at the beginning of the next iteration, and after the
            # dispatching of the current task.
            self._request_timer += self._timer_cycle
            self._request_bucket = self._max_rpm
        
        elif 0 > self._token_bucket - current.request_tokens:
            # TPM limit exceeded. Wait until tokens reset.
            logging.debug(
                f"TPM limit exceeded: "\
                f"Token bucket: {self._token_bucket}, "\
                f"Pending tokens: {current.request_tokens}"
                )
            elapsed = tpm_elapsed_time
            logging.debug(
                "Waiting {:.2f} seconds for bucket refresh"\
                    .format(self._timer_cycle - elapsed + 10)
                )
            # Add 10 seconds to counteract the possible missmatch between the
            # server and the client clocks.
            await asyncio.sleep(self._timer_cycle - elapsed + 10)

            # Reset the time counter and bucket to prevent resetting the
            # bucket at the beginning of the next iteration, and after the
            # dispatching of the current task.
            self._token_timer += self._timer_cycle
            self._token_bucket = self._max_tpm
        
        else:
            logging.debug(
                f"No limits exceeded: "\
                f"Request bucket: {self._request_bucket}, "\
                f"Pending requests: {1}, "\
                f"Token bucket: {self._token_bucket}, "\
                f"Pending tokens: {current.request_tokens}"
                )
        
        # Fetch the task to a server -------------------------------------------
        async with aiohttp.ClientSession() as session:
            logging.debug(
                f"Fetching: "\
                f"Target: {current.target}, "\
                f"Tokens: {current.request_tokens}, "\
                f"Priotity: {current.priority}"
                )
            try:
                result = await current.post(session)

            except aiohttp.ClientError as error:
                logging.error(error)

            else:
                logging.debug("Status: {}".format(result))

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
                self.pop()

                # Log bucket status -----------------------------------------
                logging.debug(
                    f"Request bucket: {self._request_bucket}, "\
                    f"Token bucket: {self._token_bucket}"
                    )

        # Zero-sleep to allow underlying connections to close ------------------
        await asyncio.sleep(0)
    
    # -------------------------------------------------------------------------
    # Method: consume_top_n
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def consume_top_n(self) -> None:
        """TODO: Put method docstring HERE."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Method: consume_all
    # -------------------------------------------------------------------------
    #
    # Description:
    #
    # Parameters:
    #
    # Returns:
    #
    # -------------------------------------------------------------------------
    async def consume_all(self) -> None:
        """TODO: Put method docstring HERE."""
        raise NotImplementedError

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
    task_queue.add(PendingTask(priority=0, target=target))
    task_queue.add(PendingTask(
        priority=2,
        target=target,
        total_tokens=5,
        request_tokens=5
        ))
    task_queue.add(PendingTask(
        priority=1,
        target=target,
        total_tokens=2,
        request_tokens=2
        ))
    task_queue.add(PendingTask(
        priority=3,
        target=target,
        total_tokens=4,
        request_tokens=4
        ))
    
    # Print the task queue -----------------------------------------------------
    task_queue.print_queue()

    # Consume the task queue ---------------------------------------------------
    while not task_queue.is_empty():
        await task_queue.consume_top()


# =============================================================================
# Main program section
# =============================================================================
if __name__ == "__main__":
    asyncio.run(main())


# End of file: 'ClientBot.py'