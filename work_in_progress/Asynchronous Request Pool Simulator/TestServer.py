# !/usr/bin/env python3
"""TODO: Add module docstring.
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
# 2024-01-09 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * TestServer.py: created.
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
# * For developing OpenAPI with FastAPI, see:
#   <https://fastapi.tiangolo.com/>.
#
# * For developing web servers with Uvicorn, see:
#   <https://www.uvicorn.org/>.
#
# * For developing web servers with Starlette, see:
#   <https://www.starlette.io/>.
#
# * For developing threaded applications with threading, see:
#   <https://docs.python.org/3/library/threading.html>.
#
# * For date and time operations, see:
#   <https://docs.python.org/3/library/datetime.html>.
#
# * For data validation, see:
#   <https://pydantic-docs.helpmanual.io/>.
#
# =============================================================================


# =============================================================================
# Modules import section
# =============================================================================
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from starlette import status
from time import perf_counter
import asyncio
import logging


# =============================================================================
# Logging section
# =============================================================================
# Create a logger object ------------------------------------------------------
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_logger.propagate = False
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.DEBUG)
_console_handler.setFormatter(
    logging.Formatter(
        fmt="%(levelname)s:\t%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
_logger.addHandler(_console_handler)


# =============================================================================
# User classes section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: TokenBucket
# -----------------------------------------------------------------------------
#
# Description:
#   This class implements a token bucket algorithm for rate limiting.
#
# Attributes:
#   * max_tpm: Maximum number of tokens per minute.
#   * tokens: Number of tokens in the bucket.
#   * last_refresh_time: Time of the last token bucket refresh.
#
# Methods:
#   * consume: Consumes tokens from the bucket.
#
# -----------------------------------------------------------------------------
class TokenBucket:
    _time_limit: float = 60
    _max_tpm: int
    _status: int
    _last_refresh_time: float

    def __init__(self, max_tpm):
        """TODO: Add method docstring."""

        # Validate input parameters -------------------------------------------
        class Validator(BaseModel):
            max_tpm: int = Field(
                default=5,
                gt=0,
                lt=1000,
                description="Maximum number of tokens per minute."
                )
        Validator(max_tpm=max_tpm)

        # Initialize attributes -----------------------------------------------
        self._max_tpm = max_tpm
        self._status = max_tpm

    @property
    def time_limit(self):
        return self._time_limit

    @property
    def max_tpm(self):
        return self._max_tpm

    @property
    def status(self):
        return self._status

    async def consume(self, tokens: int):
        """TODO: Add method docstring."""

        # Validate input parameters -------------------------------------------
        class Validator(BaseModel):
            tokens: int = Field(
                default=1,
                gt=0,
                le=self._max_tpm,
                description="Number of tokens to consume."
                )
        Validator(tokens=tokens)

        # Intialize the time counter if first time consuming tokens ----------
        if "_last_refresh_time" not in self.__dict__:
            self._last_refresh_time = perf_counter()
            # self._last_refresh_time = asyncio.get_event_loop().time()
            _logger.debug(
                "Time counter initialized to {}."\
                    .format(self._last_refresh_time)
                )


        # Reset the token bucket if time limit has passed --------------------
        current_time = perf_counter()
        # current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - self._last_refresh_time
        _logger.debug(f"Elapsed time: {elapsed_time:.2f} sec.")

        if elapsed_time > self._time_limit:
            _logger.debug("Token bucket reset.")
            self._status = self._max_tpm
            # Ensure time counting is performed in equidistant intervals
            self._last_refresh_time +=  self._time_limit
            elapsed_time = current_time - self._last_refresh_time

        if 0 > self._status - tokens:
            # Raise an exception if not enough tokens available
            _logger.debug(
                f"Token limit exceeded: "\
                f"Token bucket status: {self._status}, "\
                f"Tokens requested: {tokens}."
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token limit exceeded: Not enough tokens available."
                )

        else:
            # Consume tokens
            _logger.debug(f"Consuming {tokens} tokens.")

            self._status -= tokens
    
# -----------------------------------------------------------------------------
# Class: ClientPost
# -----------------------------------------------------------------------------
#
# Description:
#   This class represents a post data model. The ClientPost data model is used
#   to validate the post data.
#
# Attributes:
#   - tokens: the number of tokens spent in the request.
#
# Methods:
#   - __init__:    initialize the Request object.
#   - __str__:     return a string representation of the Request object.
#   - model_dump:  return a dictionary representation of the Request object.
#
# -----------------------------------------------------------------------------
class ClientPost(BaseModel):
    """ClientPost data model."""
    tokens: int = Field(gt=0)

    class Config:
        json_schema_extra = {
            'example': {
                'tokens': 5
            }
        }


# =============================================================================
# Global constants
# =============================================================================
TPM = 5


# =============================================================================
# Global variables
# =============================================================================

_bucket_table = {}  # Keeps track of the number of tokens per IP address


# =============================================================================
# Web app initialization
# =============================================================================

# Create FastAPI application object -------------------------------------------
_app = FastAPI()

# Create the API entry for retrieving the list of requests --------------------
@_app.get('/buckets', response_class=HTMLResponse)
async def queue_status():
    """TODO: Add function docstring."""
    result = """<html>
                    <head>
                        <title>Request Queue Status</title>
                        <style>
                            body {
                                font-family: Arial, Helvetica, sans-serif;
                            }
                            h1 {
                                text-align: center;
                            }
                            table, th, td {
                                border: 1px solid black;
                                border-collapse: collapse;
                                padding: 5px;
                                text-align: center;
                                margin-left: auto;
                                margin-right: auto;
                                width: 50%;
                            }
                        </style>
                    </head>
                    <body>
                        <h1>Request Queue Status</h1>
                        <table>
                            <tr>
                                <th>IP</th>
                                <th>Tokens</th>
                            </tr>"""
    for ip, bucket in _bucket_table.items():
        result += f"""<tr>
                          <td>{ip}</td>
                          <td>{bucket.status}</td>
                      </tr>"""
    result += """           </table>
                        </body>
                    </html>"""

    return result
        
# Create the API entry for adding requests to the pool ------------------------
@_app.post('/post', status_code=status.HTTP_201_CREATED)
async def process_post(post: ClientPost, request: Request):
    """TODO: Add function docstring."""

    # If the IP address is not in the bucket table, add it
    if request.client.host not in _bucket_table:
        _bucket_table[request.client.host] = TokenBucket(TPM)

    # Consume tokens from the bucket
    _logger.debug(f"Consuming {post.tokens} tokens from {request.client.host}.")

    await _bucket_table[request.client.host].consume(post.tokens)


# =============================================================================
# Mine functions section
# =============================================================================
def main():
    import uvicorn
    uvicorn.run(_app, host="0.0.0.0", port=8000)


# =============================================================================
# Main program section
# =============================================================================
if __name__ == '__main__':
    main()


# End of file 'TestServer.py'