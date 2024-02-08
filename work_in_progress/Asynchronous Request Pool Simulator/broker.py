import uvicorn
from fastapi import FastAPI, Query
import httpx
import asyncio

from pydantic import BaseModel

from typing import Optional
class Transcript(BaseModel):
    user_id: str
    file_id: str
    file_type: str
    event_name: str
    event_day: str
    event_id: str
    tags: list
    wp_id: str
    upload_date: str
    title: str
    moderator: str
    speakers: list
    description: str
    transcript_status: str
    transcript: dict
    report_status: str
    report: dict
    report_url: Optional[str] = None
    

app = FastAPI()
request_queue = asyncio.Queue()

async def process_queue(api_url: str, api_type: str):
    while True:
        transcript, api_url, api_type = await request_queue.get()
        try:
            timeout = httpx.Timeout(10.0, read=600.0)  # 10 seconds for connecting, 30 seconds for reading
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"x-token": "zini-da-ti-kazem"}
    
                if api_type == "GET":
                    response = await client.get(api_url, params=transcript.dict(), headers=headers)
                elif api_type == "POST":
                    response = await client.post(api_url, json=transcript.dict(), headers=headers)
                else:
                    print(f"Invalid API type: {api_type}")
                    continue
                if response.status_code == 200:
                    print(f"Successfully processed transcript: {transcript.user_id}, {transcript.file_id}: API {api_type} {api_url},\nResponse: {response.json()}")
                    await asyncio.sleep(30)
                else:
                    print(f"Failed to process transcript: {transcript.user_id}, {transcript.file_id}: API {api_type} {api_url}, Status Code: {response.status_code}")
        except httpx.RequestError as e:
            print(f"An error occurred while processing transcript: {transcript.user_id}, {transcript.file_id}: API {api_type} {api_url}. Error: {e}")
        request_queue.task_done()

@app.on_event("startup")
async def startup_event():
    api_url = "https://nimani.diplomacy.edu:8550/api/test_api_for_broker"
    api_type = "POST"
    asyncio.create_task(process_queue(api_url, api_type))

@app.post("/enqueue")
async def enqueue_request(transcript: Transcript, api_url: str = "https://nimani.diplomacy.edu:8550/api/test_api_for_broker", api_type: str = "POST"):
    await request_queue.put((transcript, api_url, api_type))
    queue_size = request_queue.qsize()
    return {"queue_number": queue_size}


@app.get("/queue")
async def get_queue():
    queue_size = request_queue.qsize()
    jobs = []
    for i, item in enumerate(request_queue._queue):
        transcript = item[0]
        job = {
            "queue_number": i + 1,
            "user_id": transcript.user_id,
            "file_id": transcript.file_id,
            "event_id": transcript.event_id,
        }
        jobs.append(job)
    return {"queue_size": queue_size, "jobs": jobs}


if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=8546, log_level="info",workers=4)
    server = uvicorn.Server(config)
    server.run()