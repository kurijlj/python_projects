# !/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2023 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
#  This file is part of Redis Broker.
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
# 2024-02-12 Ljubomir Kurij <ljubomi_kurij@protonmail.com>
#
# * redis_broker.py: created.
#
# =============================================================================


# =============================================================================
# Modules import section
# =============================================================================
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# =============================================================================
# API Definition Section
# =============================================================================
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_root():
    return """<html>
    <head>
        <title>Hello Redis Broker</title>
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
        <h1>Hello Redis Broker!</h1>
    </body>
</html>"""


# =============================================================================
# App Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8546)


# End of file 'redis_broker.py'