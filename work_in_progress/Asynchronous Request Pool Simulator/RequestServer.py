# !/usr/bin/env python3
"""Request Priority Queue server.

This module contains the server implementation of the Request Priority Queue
application. The server is implemented using FastAPI, Uvicorn, and Starlette
libraries. The server is a REST API that accepts requests from the client
application and adds them to the request pool. The server also provides a
status page that displays the current state of the request pool.

Attributes:
    TPM (int): the maximum number of tokens per minute.
    _pool (TimerQueue): the request pool.
    _app (FastAPI): the FastAPI application.

Classes:
    RequestPool: the request pool object.
    TimerQueue: the timer queue object.
    IncomingRequest: the request object data model.

The module is intended to be run as a standalone application. The module
contains a main program that starts the server and the timer queue loop.
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
# 2023-12-28 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * RequestServer.py: created.
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
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from starlette import status
from time import perf_counter, sleep


# =============================================================================
# User classes section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: RequestPool
# -----------------------------------------------------------------------------
#
# Description:
#   This class represents a request pool object that tracks the number of
#   spent tokens for a given IP address, and if the number of tokens spent
#   in the given time frame exceeds the preset limit. If the limit is
#   reached, the request pool is reset. When the time frame is reached, the
#   request pool is reset.
#
# Attributes:
#   - ip:     the IP address of the request pool.
#   - tokens: the number of tokens spent in the request pool.
#
# Methods:
#   - __init__:    initialize the RequestPool object.
#   - __str__:     return a string representation of the RequestPool object.
#   - reset_pool:  reset the request pool.
#
# -----------------------------------------------------------------------------
class RequestPool:
    """RequestPool class."""
    ip: str
    tokens: int

    def __init__(self, ip: str, tokens: int):
        """Initialize the Request object."""
        self.ip = ip
        self.tokens = tokens
    
    def __str__(self):
        """Return a string representation of the Request object."""
        return f'Request(ip={self.ip}, tokens={self.tokens})'
    
    def reset_pool(self):
        """Reset the request pool."""
        self.tokens = 0

# -----------------------------------------------------------------------------
# Class: TimerQueue
# -----------------------------------------------------------------------------
#
# Description:
#   This class represents a timer queue object. The timer queue is a list of
#   request pools that are added to the queue when a request is made. The
#   timer queue is checked periodically for elapsed timers. If a timer is
#   elapsed, the request pool is reset.
#
# Attributes:
#   - _queue:      the list of dictionaries containing the request pool and the
#                  start time.
#   - _time_limit: the time limit for the request pool.
#
# Methods:
#   - __init__:      initialize the TimerQueue object.
#   - __iter__:      return the iterator for the TimerQueue object.
#   - __str__:       return a string representation of the TimerQueue object.
#   - add:           add a request to the queue.
#   - check_elapsed: reset the pool for the top most request pool if time
#                    limit is reached.
#
# -----------------------------------------------------------------------------
class TimerQueue:
    """TimerQueue class."""
    _queue: list

    def __init__(self, time_limit: float):
        """Initialize the TimerQueue object."""
        self._queue = []
        self._time_limit = time_limit
    
    def __iter__(self):
        """Return the iterator for the TimerQueue object."""
        return iter(self._queue)

    def __str__(self):
        """Return a string representation of the TimerQueue object."""
        return f'TimerQueue(queue={self._queue})'

    def add(self, pool: RequestPool):
        """Add a request to the queue."""
        self._queue.append({'pool': pool, 'start': perf_counter()})

    def check_elapsed(self):
        """Reset the pool for the top most request pool if time limit is
        reached."""
        if self._queue:
            if perf_counter() - self._queue[0]['start'] > self._time_limit:
                rp = self._queue.pop(0)['pool']
                rp.reset_pool()
                self._queue.append({'pool': rp, 'start': perf_counter()})


# =============================================================================
# User data models section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: IncomingRequest
# -----------------------------------------------------------------------------
#
# Description:
#   This class represents a request data model. The IncomingRequest data model
#   is used to validate the request data.
#
# Attributes:
#   - ip:     the IP address of the request.
#   - tokens: the number of tokens spent in the request.
#
# Methods:
#   - __init__:    initialize the Request object.
#   - __str__:     return a string representation of the Request object.
#   - model_dump:  return a dictionary representation of the Request object.
#
# -----------------------------------------------------------------------------
class IncomingRequest(BaseModel):
    """Request data model."""
    ip: str = Field(min_length=7, max_length=15)
    tokens: int = Field(gt=0)

    class Config:
        json_schema_extra = {
            'example': {
                'ip': '192.168.0.1',
                'tokens': 5
            }
        }


# =============================================================================
# User functions section
# =============================================================================

# -----------------------------------------------------------------------------
# Function: timers_check_loop
# -----------------------------------------------------------------------------
#
# Description:
#   This function is the timers check loop. The timers check loop checks for
#   elapsed timers. If a timer is elapsed, the request pool is reset.
#   The timer queue loop runs in a separate thread.
#
# Arguments:
#   - None
#
# Returns:
#   - None
#
# -----------------------------------------------------------------------------
def timers_check_loop():
    """Check for elapsed timers."""
    while True:
        _queue.check_elapsed()
        sleep(1)


# =============================================================================
# Global constants
# =============================================================================
TPM = 5


# =============================================================================
# Global variables
# =============================================================================

# Create the timer queue object with a time limit of 60 seconds ----------------
_queue = TimerQueue(60)


# =============================================================================
# Web app initialization
# =============================================================================

# Create FastAPI application object -------------------------------------------
_app = FastAPI()

# Create the API entry for retrieving the list of requests --------------------
@_app.get('/queue', response_class=HTMLResponse)
async def queue_status():
    result = """<html>
                    <head>
                        <title>Request Queue Status</title>
                        <style>
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
                    `   <h1>Request Queue Status</h1>
                        <table>
                            <tr>
                                <th>IP</th>
                                <th>Tokens</th>
                            </tr>"""
    for item in _queue:
        result += f"""<tr>
                          <td>{item['pool'].ip}</td>
                          <td>{item['pool'].tokens}</td>
                      </tr>"""
    result += """           </table>
                        </body>
                    </html>"""

    return result
        
# Create the API entry for adding requests to the pool ------------------------
@_app.post('/request', status_code=status.HTTP_201_CREATED)
async def make_a_request(request: IncomingRequest):
    """Add a request to the queue."""
    # Create a new request object
    rp = RequestPool(**request.model_dump())

    if _queue:
        for item in _queue:
            if item['pool'].ip == rp.ip:
                if item['pool'].tokens + rp.tokens > TPM:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail='RPM exceeded')
                else:
                    item['pool'].tokens += rp.tokens
                    return
    
    _queue.add(rp)


# =============================================================================
# Main program
# =============================================================================
if __name__ == '__main__':
    # Start the web app -------------------------------------------------------
    import uvicorn

    # Start the timer queue loop ----------------------------------------------
    
    # Create a thread for the timer queue loop
    import threading
    check_loop_thread = threading.Thread(target=timers_check_loop, daemon=True)
    check_loop_thread.start()

    # Run the web app ---------------------------------------------------------
    uvicorn.run(_app, host='0.0.0.0', port=8000)


# End of file 'RequestServer.py'