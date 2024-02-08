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
# 2024-02-08 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * asyncio_playground.py: created.
#
# =============================================================================


# =============================================================================
#
# TODO:
# * Define a clas that will be used to store data representing client's tasks
#   for the server resources (i.e. access to the server's API). The class should
#   have the following attributes:
#   - user_id: a unique identifier of the service user
#   - priority: a priority of the task
#   - target_url: a target URL of the task
#   - target_model: a target AI model of the task
#   - total_request: an estimate of the total number of requests that will be
#     made by the task
#   - total_tokens: an estimate of the total number of tokens that will be
#     consumed by the request (i.e. the number of tokens that will be consumed
#     by the task and the number of tokens that will be consumed by the
#     response)
#   - task_tokens: an exact number of tokens that will be consumed by the task
#
#   
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
import asyncio
from time import sleep
from starlette import status
from pydantic import BaseModel, Field
from fastapi import FastAPI


# =============================================================================
# User-defined Classes Section
# =============================================================================
class Task(BaseModel):
    user_id: str        = Field(min_length=1, max_length=20)
    priority: int       = Field(ge=1, le=100)
    target_url: str     = Field(pattern=r"^https?://")
    target_model: str   = Field(min_length=1, max_length=20)
    total_requests: int = Field(ge=1)
    total_tokens: int   = Field(ge=1)
    task_tokens: int    = Field(ge=1)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "XXXXXX",
                "priority": 10,
                "target_url": "https://example.com",
                "target_model": "model_1",
                "total_requests": 100,
                "total_tokens": 1000,
                "task_tokens": 100
            }
        }

class TaskResult(BaseModel):
    status: int = Field(ge=200, le=299)
    result: str = Field(min_length=1, max_length=20)

    class Config:
        validate_assignment = True
        extra = "forbid"
        schema_extra = {
            "example": {
                "task_id": "XXXXXX",
                "status": 202,
                "result": "ACCEPTED"
            }
        }


# =============================================================================
# Web API Section
# =============================================================================

# Create FastAPI application object -------------------------------------------
_app = FastAPI()

# API entry point for adding a new task to the queue --------------------------
@_app.post("/post_task")
async def post_task(task: Task) -> TaskResult:
    await asyncio.sleep(5)
    return TaskResult(status=status.HTTP_202_ACCEPTED, result="ACCEPTED")


# =============================================================================
# Application Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(_app, host="127.0.0.1", port=8000)