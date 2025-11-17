# import requests
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("SUNO_API_KEY")
url = "https://api.sunoapi.org/api/v1/generate"
payload = {
    "prompt": "Slow, peaceful lofi beats",
    "title": "Lofi beat", 
    "customMode": True,
    "instrumental": True,
    "model": "V5",
    "callBackUrl": "https://lofi-app-dc75.onrender.com/callback"
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def make_song_params():
    return {"url": url, 
            "payload": payload, 
            "headers": headers}

def make_song():
    response = requests.post(url, json=payload, headers=headers)
    return response
            
