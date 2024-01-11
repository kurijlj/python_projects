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
from math import log
import re
import token
from turtle import left
from urllib import request
import aiohttp
import asyncio
import heapq
import logging
from pprint import pprint
from matplotlib.pylab import f
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
    def tokens_left(self) -> int:
        return self._bucket
    
    @property
    def tokens_consumed(self) -> int:
        return self._capacity - self._bucket
    
    @property
    def timer_cycle(self) -> float:
        return self._timer_cycle
    
    @property
    def time_elapsed(self) -> float:
        if "_timer" in self.__dict__:
            return perf_counter() - self._timer
        else:
            return 0.0
    
    @property
    def time_remaining(self) -> float:
        if "_timer" in self.__dict__:
            return self._timer_cycle - self.time_elapsed
        else:
            return self._timer_cycle
        
    def start_timer(self) -> None:
        if "_timer" not in self.__dict__:
            self._timer = perf_counter()
    
    def reset(self) -> None:
        if "_timer" in self.__dict__:
            if self.time_remaining <= 0:
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
    _request_bucket: TimedResourceBucket
    _token_bucket: TimedResourceBucket

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
    def __init__(self,
            request_timer_cycle: float,
            token_timer_cycle: float,
            request_capacity: int,
            token_capacity: int
            ) -> None:
        """TODO: Put method docstring HERE."""

        # Validate the input data ----------------------------------------------
        class Validator(BaseModel):
            request_timer_cycle: float = Field(default=60.0, ge=1.0)
            token_timer_cycle: float = Field(default=60.0, ge=1.0)
            request_capacity: int = Field(default=1, ge=1)
            token_capacity: int = Field(default=1, ge=1)
        v = Validator(
            request_timer_cycle=request_timer_cycle,
            token_timer_cycle=token_timer_cycle,
            request_capacity=request_capacity,
            token_capacity=token_capacity
            )

        # Assign the validated data --------------------------------------------
        self._queue = []
        self._request_bucket = TimedResourceBucket(
            capacity=v.request_capacity,
            timer_cycle=v.request_timer_cycle
            )
        self._token_bucket = TimedResourceBucket(
            capacity=v.token_capacity,
            timer_cycle=v.token_timer_cycle
            )
    
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
        result = \
            f"TaskPriorityQueue("\
            f"\"Requests capacity\"={self._request_bucket.capacity}, "\
            f"\"Requests timer cycle\"={self._request_bucket.timer_cycle}, "\
            f"\"Tokens capacity\"={self._token_bucket.capacity}, "\
            f"\"Tokens timer cycle\"={self._token_bucket.timer_cycle}, "\
            f"queue=["\

        if not self.is_empty():
            for task in self._queue:
                result += f"{task.__repr__()}, "
            result = result[:-2] + f"])"
        else:
            result += f"])"
        
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
        return f"TaskPriorityQueue("\
            f"{self._request_bucket.capacity}, "\
            f"{self._request_bucket.timer_cycle}, "\
            f"{self._token_bucket.capacity}, "\
            f"{self._token_bucket.timer_cycle}, "\
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
        left_child_index = 2 * index + 1
        if self.is_empty() or len(self._queue) <= left_child_index:
            return -1
        else:
            return left_child_index
    
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
        right_child_index = 2 * index + 2
        if self.is_empty() or len(self._queue) <= right_child_index:
            return -1
        else:
            return right_child_index
    
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
        if not self.is_empty() and len(self._queue) - 1 > index:
            left_child_index = self._get_left_child_index(index)
            right_child_index = self._get_right_child_index(index)
            if left_child_index >= 0 \
                    and self._queue[left_child_index] > self._queue[index]:
                self._swap(index, left_child_index)
                if 0 > left_child_index and len(self._queue) - 1 > left_child_index:
                    self._heapify_down(left_child_index)
            elif right_child_index >= 0 \
                    and self._queue[right_child_index] > self._queue[index]:
                self._swap(index, right_child_index)
                if 0 > right_child_index and len(self._queue) - 1 > right_child_index:
                    self._heapify_down(right_child_index)

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
        logging.debug("Consuming the queue")
        self._request_bucket.start_timer()
        self._token_bucket.start_timer()

        # Check bucket timers --------------------------------------------------
        if 0 > self._request_bucket.time_remaining:
            logging.debug("Resetting the request bucket")
            self._request_bucket.reset()
        if 0 > self._token_bucket.time_remaining:
            logging.debug("Resetting the token bucket")
            self._token_bucket.reset()
        logging.debug(
            f"Timers: [{self._request_bucket.time_remaining:.2f}, "\
            f"{self._token_bucket.time_remaining:.2f}], "\
            f"Tokens: [{self._request_bucket.tokens_left}, "\
            f"{self._token_bucket.tokens_left}]"
            )

        # Get current task -----------------------------------------------------
        current = self.peek()

        # Pause consumation if not enough tokens -------------------------------
        if 0 > self._request_bucket.tokens_left - 1:
            # Add 10 seconds to counteract the possible missmatch between the
            # server and the client clocks.
            logging.debug(
                f"Request bucket exhausted. Pausing for "\
                f"{self._request_bucket.time_remaining + 10:.2f} seconds."
                )
            await asyncio.sleep(self._request_bucket.time_remaining + 10)
        
            # Reset the time counters and buckets to prevent resetting the
            # buckets at the beginning of the next iteration, and after the
            # dispatching of the current task.
            self._request_bucket.reset()
        
        elif 0 > self._token_bucket.tokens_left - current.request_tokens:
            # Add 10 seconds to counteract the possible missmatch between the
            # server and the client clocks.
            logging.debug(
                f"Token bucket exhausted. Pausing for "\
                f"{self._token_bucket.time_remaining + 10:.2f} seconds."
                )
            await asyncio.sleep(self._token_bucket.time_remaining + 10)

            # Reset the time counters and buckets to prevent resetting the
            # buckets at the beginning of the next iteration, and after the
            # dispatching of the current task.
            self._token_bucket.reset()
        
        else:
            pass

        # Dispatch the task to the server -------------------------------------
        async with aiohttp.ClientSession() as session:
            logging.debug(
                f"Dispatching: "\
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
                self._request_bucket.consume(1)
                self._token_bucket.consume(current.request_tokens)
                
                # Remove the task from the queue -------------------------------
                self.pop()

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


# =============================================================================
# Main function section
# =============================================================================
async def main():
    target = "http://localhost:8000/post"
    request_timer_cycle = 60.0
    token_timer_cycle = 60.0
    request_capacity = 5
    token_capacity = 5

    # Create the task queue ----------------------------------------------------
    task_queue = TaskPriorityQueue(
        request_timer_cycle,
        token_timer_cycle,
        request_capacity,
        token_capacity
        )

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
    logging.debug(task_queue._queue)

    # Consume the task queue ---------------------------------------------------
    while not task_queue.is_empty():
        await task_queue.consume_top()


# =============================================================================
# Main program section
# =============================================================================
if __name__ == "__main__":
    asyncio.run(main())


# End of file: 'ClientBot.py'