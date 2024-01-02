# !/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# This file is part of Request Priority Que.
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
# * Implement a POST request handler for adding requests to the queue.
#
# * Implement request pool. Requests are added to the pool when they are
#   received alongside with the IP address of the client. Each client can have
#   certian number of requests per second. Requests are removed from the pool
#   when they are processed. If max number of requests per minute is reached,
#   further requests are rejected until the time window is over.
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
# * For developing threaded applications with threading, see:
#   <https://docs.python.org/3/library/threading.html>.
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
#   This class represents a request pool object that holds requests from a
#   signle client IP address.
#
# Attributes:
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
#   This class represents a timer queue object.
#
# Attributes:
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

    def add(self, request: RequestPool):
        """Add a request to the queue."""
        self._queue.append({'request': request, 'start': perf_counter()})

    def check_elapsed(self):
        """Reset the pool for the top most request pool if time limit is reached."""
        if self._queue:
            if perf_counter() - self._queue[0]['start'] > self._time_limit:
                rp = self._queue.pop(0)['request']
                rp.reset_pool()
                self._queue.append({'request': rp, 'start': perf_counter()})


# =============================================================================
# User data models section
# =============================================================================

# -----------------------------------------------------------------------------
# Class: Request

class Request(BaseModel):
    """Request data model."""
    ip: str = Field(min_length=7, max_length=15)
    tokens: int = Field(gt=1)

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
# Function: pool_timers_loop
# -----------------------------------------------------------------------------
def pool_timers_loop():
    """Check for elapsed timers."""
    print('Timer queue loop started')
    while True:
        _pool.check_elapsed()
        sleep(1)

# =============================================================================
# Global constants
# =============================================================================
TPM = 5


# =============================================================================
# Global variables
# =============================================================================
# _pool = []
_pool = TimerQueue(60)


# =============================================================================
# Web app initialization
# =============================================================================

# Create FastAPI application object -------------------------------------------
app = FastAPI()

# Create the API entry for retrieving the list of requests --------------------
# @app.get('/pool', status_code=status.HTTP_200_OK)
@app.get('/pool', response_class=HTMLResponse)
async def pool_status():
    result = '<html><head><title>Request Pool Status</title></head><body>'
    for item in _pool:
        result += f'<p>{item["request"].ip}: {item["request"].tokens}</p>'
    result += '</body></html>'

    return result
        

# Create the API entry for adding requests to the pool ------------------------
@app.post('/request', status_code=status.HTTP_201_CREATED)
async def make_a_request(request: Request):
    """Add a request to the pool."""
    # Create a new request object
    request_pool = RequestPool(**request.model_dump())

    if _pool:
        for item in _pool:
            if item['request'].ip == request_pool.ip:
                if item['request'].tokens + request_pool.tokens > TPM:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail='RPM exceeded')
                else:
                    item['request'].tokens += request_pool.tokens
                    return
    
    _pool.add(request_pool)


# =============================================================================
# Main program
# =============================================================================
if __name__ == '__main__':
    # Start the web app -------------------------------------------------------
    import uvicorn

    # Start the timer queue loop ----------------------------------------------
    
    # Create a thread for the timer queue loop
    import threading
    timer_queue_thread = threading.Thread(target=pool_timers_loop, daemon=True)
    timer_queue_thread.start()

    # Run the web app ---------------------------------------------------------
    uvicorn.run(app, host='0.0.0.0', port=8000)