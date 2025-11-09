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
    "callbackUrl": "https://lofi-app-dc75.onrender.com/playlist"

    
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# return dictionary containing url, payload, headers
def make_song_params():
    return {"url": url, 
            "payload": payload, 
            "headers": headers}

def make_song():
    response = requests.post(url, json=payload, headers=headers)
    return response
            
#response = requests.post(url, json=payload, headers=headers)

# print(f"JSON MESSAGE {response.json()}")
