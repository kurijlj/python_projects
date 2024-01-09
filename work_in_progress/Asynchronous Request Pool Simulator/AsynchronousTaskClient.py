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
# 2024-01-08 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * AsynchronousTaskClient.py: created.
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

class RateLimiter:
    def __init__(self, max_rpm, max_tpm):
        self.request_bucket = RequestBucket(max_rpm)
        self.token_bucket = TokenBucket(max_tpm)

    async def make_request(self, ip, tokens):
        async with aiohttp.ClientSession() as session:
            # await self.token_bucket.consume(tokens)
            # await self.request_bucket.consume()
            await asyncio.gather(
                                 self.request_bucket.consume(),
                                 self.token_bucket.consume(tokens)
                                )
            async with session.post(
                         "http://localhost:8000/request",
                         json={
                               "ip": ip,
                               "tokens": tokens
                              }
                        ) as response:
                print("{} response status: {}"\
                      .format(strftime("%H:%M:%S"), response.status))
                pprint(await response.json())

class RequestBucket:
    time_limit = 60  # 1 minute

    def __init__(self, max_rpm):
        self.max_rpm = max_rpm
        self.requests = 0
        self.last_refresh_time = asyncio.get_event_loop().time()

    async def consume(self):
        current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - self.last_refresh_time
        if elapsed_time > self.time_limit:
            self.requests = 0
            self.last_refresh_time = current_time
            elapsed_time = 0

        if self.max_rpm < self.requests + 1:
            # Wait until next request bucket refresh
            print(
                  "{} Waiting {} seconds for request bucket refresh"\
                    .format(
                            strftime("%Y-%m-%d %H:%M:%S"),
                            self.time_limit - elapsed_time
                           )
                 )
            await asyncio.sleep(elapsed_time)

        self.requests += 1

class TokenBucket:
    time_limit = 60  # 1 minute

    def __init__(self, max_tpm):
        self.max_tpm = max_tpm
        self.tokens = 0
        self.last_refresh_time = asyncio.get_event_loop().time()

    async def consume(self, tokens):
        current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - self.last_refresh_time
        if elapsed_time > self.time_limit:
            self.tokens = 0
            self.last_refresh_time = current_time
            elapsed_time = 0

        if self.max_tpm < self.tokens + tokens:
            # Wait until next token bucket refresh
            print(
                  "{} Waiting {} seconds for token bucket refresh"\
                    .format(
                            strftime("%Y-%m-%d %H:%M:%S"),
                            self.time_limit - elapsed_time
                           )
                 )
            await asyncio.sleep(elapsed_time)

        self.tokens += tokens


# =============================================================================
# Main program section
# =============================================================================
async def main():
    # Instantiate the rate limiter
    rate_limiter = RateLimiter(max_rpm=1, max_tpm=5)

    ip = "192.168.0.1"
    tokens = 2

    tasks = []
    for i in range(10):  # Simulating 10 requests
        task = asyncio.create_task(rate_limiter.make_request(ip, tokens))
        tasks.append(task)

    await asyncio.gather(*tasks)


# =============================================================================
# Run

if __name__ == "__main__":
    asyncio.run(main())