# Asynchronous Request Pool Simulator

## Project Overview:
The Asynchronous Request Pool Simulator is a Python-based application designed to emulate a server-client interaction with a focus on managing requests within a specified time frame. The project employs key libraries such as Uvicorn for implementing a simple ASGI web server, FastAPI for creating an OpenAPI web interface, and threading to facilitate the development of a multithreading application.

## Key Features:
### Request Pool Management:
- The server simulates a request pool where incoming requests, along with
  client IP addresses, are added for processing.
- Each client is assigned a specific quota of requests per minute.
- Requests are systematically removed from the pool upon processing completion.
- To prevent overloading, the server rejects further requests when the maximum
  number of requests per minute is reached until the designated
  time window elapses.

### Client Simulation:
The project includes a client module that generates and sends requests to the server.
The client implements a priority request queue, ensuring certain requests take precedence.
Request processing on the client side continues until the server's request pool limit is reached.
Subsequent request processing is paused until the time window resets, preventing unnecessary strain on the server.
Libraries Used:

Uvicorn: Employed for implementing the ASGI web server.
FastAPI: Utilized to create an OpenAPI web interface, enhancing the project's accessibility and usability.
Threading: Implemented for developing a multithreading application, allowing for concurrent processing of requests.
Technical Specifications:

Server-Side: Handles incoming requests, manages the request pool, and enforces request quotas per client.
Client-Side: Simulates a client environment, generating requests with prioritization.
Development Stack:

Programming Languages: Python
Libraries: Uvicorn, FastAPI, Threading
Usage Scenario:

This project serves as a valuable tool for testing server resilience and assessing the efficiency of handling concurrent requests, providing insights into potential bottlenecks and areas for optimization.
Conclusion:
The Asynchronous Request Pool Simulator is an innovative Python project that combines the power of Uvicorn, FastAPI, and threading to mimic a dynamic server-client interaction. By simulating request management, the application offers a practical platform for evaluating the robustness and performance of systems under varying loads.