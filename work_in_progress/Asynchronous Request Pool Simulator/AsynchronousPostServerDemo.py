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
# * AsynchronousPostServerDemo.py: created.
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
from time import perf_counter, strftime
import asyncio


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
            print("{} Time counter initialized to {}"\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._last_refresh_time
                        )
                )

        # Reset the token bucket if time limit has passed --------------------
        current_time = perf_counter()
        # current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - self._last_refresh_time
        print("{} Elapsed time: {}"\
                .format(
                    strftime("%Y-%m-%d %H:%M:%S"),
                    elapsed_time
                    )
            )
        if elapsed_time > self._time_limit:
            print("{} Token bucket reset."\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S")
                        )
                )
            self._status = self._max_tpm
            self._last_refresh_time = current_time
            elapsed_time = 0

        if 0 > self._status - tokens:
            # Raise an exception if not enough tokens available
            print("{} Token limit exceeded: Not enough tokens available {}."\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        self._status - tokens
                        )
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token limit exceeded: Not enough tokens available."
                )

        else:
            # Consume tokens
            print("{} Consuming {} tokens."\
                    .format(
                        strftime("%Y-%m-%d %H:%M:%S"),
                        tokens
                        )
                )

            self._status -= tokens

            # if 0 > self._status:
            #     self._status = 0
    
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
    """Request data model."""
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
    print("{} Consuming {} tokens from {}."\
            .format(
                strftime("%Y-%m-%d %H:%M:%S"),
                post.tokens,
                request.client.host
                )
        )
    # try:
    #     await _bucket_table[request.client.host].consume(post.tokens)
    
    # finally:
    #     return {
    #         "ip": request.client.host,
    #         "tokens": post.tokens
    #     }
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


# End of file 'AsynchronousPostServerDemo.py'