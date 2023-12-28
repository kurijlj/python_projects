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
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from threading import Thread


# =============================================================================
# Global constants
# =============================================================================


# =============================================================================
# Web app initialization
# =============================================================================

# Create FastAPI application object -------------------------------------------
app = FastAPI()

# Create a 'root' path operation decorator ------------------------------------
@app.get('/')

# Define the path operation function ------------------------------------------
def root():
    """Return a greeting message."""
    return {"message": "Hello World!"}

# Define the fastapi app startup function -------------------------------------
def startup():
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)


# =============================================================================
# Main program
# =============================================================================
if __name__ == '__main__':
    # Start the web app in a separate thread ----------------------------------
    fastapi_thread = Thread(target=startup)
    fastapi_thread.start()
    
    # Wait for the fastapi thread to finish -----------------------------------
    fastapi_thread.join()