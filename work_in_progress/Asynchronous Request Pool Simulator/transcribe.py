import os
from dotenv import load_dotenv
load_dotenv('.env')

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import json
import os
import requests

import tiktoken
import threading




from utils import *

import openai
from dotenv import load_dotenv
load_dotenv('/srv/users/jovan/.env')
openai.api_key = os.getenv('OPENAI_KEY')
openai.organization = os.getenv('OPENAI_ORGANIZATION')
graphs_location = os.getenv('GRAPHS_LOCATION')
broker_api = os.getenv('BROKER_API')
transcribe_api_base = os.getenv('TRANSCRIBE_API_BASE')


import warnings
warnings.filterwarnings(action="ignore", category=DeprecationWarning)


tokenizer = tiktoken.encoding_for_model("gpt-4")
EMBEDDING_MODEL = "text-embedding-ada-002"


router = APIRouter()
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
    


    
# @router.post("/api/youtube")
# def get_audio(user_input: Transcript):
#     from pytube import YouTube
#     yt=YouTube(user_input.file_id)
#     t=yt.streams.filter(only_audio=True)
#     audio_filename = t[0].default_filename
#     if audio_filename not in os.listdir('./audio/'):
#         t[0].download(f'./audio/')
#     else:
#         print('File already exists.')
    
#     return {'file': file_id}

#@router.post("/api/transcribe_raw", 
#             summary='Generates raw transcripts only', 
#             description='This route only generates raw, untidy transcript as one paragraph, without spell-checking and speakers')
#def transcribe_raw(user_input: Transcript):
#    base_filename = user_input.file_id
#    audio_filepath = f'/srv/users/jovan/diplo_apps/apis/transcribe_api/audio/{user_input.file_id}.mp4'
#    result = generate_raw_transcript(audio_filepath)
#    
#    with open(f'./transcripts/{base_filename}_raw.json', 'w') as f:
#        json.dump(result, f)
#    return {'user_id': user_input.user_id, 'status': 'READY', 'result': result}


@router.get("/api/transcripts",
         summary="Get transcript information",
         description="Return information on each transcript found in the user's folder")
def get_transcripts():
    try:
        transcript_info = get_status()
        if not transcript_info:
            raise HTTPException(status_code=404, detail="No transcripts found")
        
        return {"transcripts": transcript_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@router.post("/api/test_api_for_broker",
         summary="If you dont know what this is, its not for you")
def get_transcripts2(user_input: Transcript):
    try:
        print(f'Poceo na apiju za generisanje za  {user_input.user_id}')
        time.sleep(10)
        print(f'Gotovo za {user_input.user_id}')
        return {'answer': f'Evo ti info za {user_input.user_id}'}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/transcripts",
            summary='Generates tidy transcripts', 
            description='This route generates transcripts, along with speaker detection, spell correction, paragraph formation.')
def transcribe(user_input: Transcript):
    
    response = user_input.dict()
    event_folder_path = f'./transcripts'

    response['transcript_status'] = 'IN PROGRESS'
    
    with open(f'{event_folder_path}/{user_input.file_id}_neat.json', 'w') as f:
        json.dump(response, f)
    
    update_status_table(response)
    try:
        broker_url = broker_api
        api_url = f"{transcribe_api_base}/transcripts_"
        api_type = "POST"
        
        broker_response = requests.post(broker_url, params= {"api_url": api_url, "api_type": api_type},json=response).json()
        
        
        return {'user_id': user_input.user_id, 'event_id': user_input.event_id, 'title': user_input.title,'file_id': user_input.file_id, 'transcript_status': f'QUEUED AS {broker_response["queue_number"]}'}

    except Exception as e:
        response['transcript_status'] = 'FAILED'
        
        with open(f'{event_folder_path}/{user_input.file_id}_neat.json', 'w') as f:
            json.dump(response, f)
        update_status_table(response)
        raise HTTPException(status_code = 500 , detail= str(e))
            

    



#---------------------------------------------
@router.post("/api/transcripts_",
            summary='Generates tidy transcripts', 
            description='This route generates transcripts, along with speaker detection, spell correction, paragraph formation.')
def transcribe_(user_input: Transcript):
    import warnings
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

    response = user_input.dict()
    event_folder_path = f'./transcripts'
    print(f'Raw transcript: Starting')
    filepath = f"/srv/users/jovan/diplo_apps/apps/transcripts_1/public/media/{user_input.file_id}.{user_input.file_type}"
    audio_filepath = media_preprocess(filepath)
    print("\n************************\n", audio_filepath, "\n************************\n")
    result = generate_raw_transcript(audio_filepath)
    with open(f'{event_folder_path}/{user_input.file_id}_raw.json', 'w') as f:
        json.dump(result, f)
    print(f'\rRaw transcript: DONE     \n------------------\n')
    transcript = result['text']

    #time.sleep(5)
    #print(f'Tidy transcript: Starting')
    #corrected_transcript = tidy_transcript(transcript, user_input.moderator, user_input.speakers)
    #with open(f'{user_folder_path}/{user_input.file_id}.txt', 'w') as f:
    #    f.write(corrected_transcript)
    
    #final_result = map_corrected_transcript(corrected_transcript, result)
    # print(f'\rTidy transcript: DONE     \n------------------\n')
    # response['transcript'] = final_result
    # response['status'] = 'GENERATED'
    # response['speakers'].extend([segment['speaker'] for segment in final_result['segments']])
    # response['speakers'] = list(set(response['speakers']))
    result_segments = []
    for i in range(len(result['segments'])):
        result_segments.append({'text': result['segments'][i]['text'], 'id': i, 'start': result['segments'][i]['start'], 'end': result['segments'][i]['end']})
        
    #result['segments'] = [r[['id','start', 'end','text']] for r in result['segments']]
    for i in range(len(result['segments'])):
        result_segments[i]['speaker'] = 'UNKNOWN'
        result_segments[i]['paragraph_number'] = 1
    response['transcript'] = {}
    response['transcript']['segments'] = result_segments
    response['transcript']['text'] = transcript
    response['transcript_status'] = 'GENERATED'
    response['speakers'] =['UNKNOWN']
    
    with open(f'{event_folder_path}/{user_input.file_id}_neat.json', 'w') as f:
        json.dump(response, f)
    update_status_table(response)
    return {'user_id': user_input.user_id, 'event_id': user_input.event_id, 'title': user_input.title,'file_id': user_input.file_id, 'transcript_status': 'GENERATED'}

    
    
#---------------------------------------------



@router.get("/api/transcripts/{file_id}",
             summary='Return single transcript', 
             description='Return single transcript for file_id')
def get_transcripts(file_id: str):
    try:
        with open(f'./transcripts/{file_id}_neat.json', 'r') as f:
            transcript = json.load(f)
        # status = get_status()
        # status_report_status = [s for s in status if s['file_id'] == file_id][0]['report_status']
        # status_transcript_status = [s for s in status if s['file_id'] == file_id][0]['transcript_status']
        # transcript['report_status'] = status_report_status
        # transcript['transcript_status'] = status_transcript_status
    
        return transcript
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
    
@router.post("/api/transcripts/{file_id}",
          summary="Update transcript",
          description="Accept corrected transcript and overwrite existing file")
def update_transcripts(file_id: str, corrected_transcript: Transcript):
    try:
        
        # Open the existing file and overwrite it with the corrected transcript
        with open(f'./transcripts/{file_id}_neat.json', 'w') as f:
            json.dump(corrected_transcript.dict(), f)
        
        update_status_table(corrected_transcript.dict())
        return {"message": "Transcript updated successfully"}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
    

@router.delete("/api/transcripts/delete/{file_id}",
             summary='Delete single transcript', 
             description='Delete single transcript for file_id')
def del_transcripts(file_id: str):
    try:
        # delete file file_id from event_id folder
        os.remove(f'./transcripts/{file_id}_raw.json')
        os.remove(f'./transcripts/{file_id}_neat.json')
        delete_from_status_table(file_id)
        return {"message": "File deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
