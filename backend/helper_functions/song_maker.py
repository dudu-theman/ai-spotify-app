# import requests
from dotenv import load_dotenv
import os
import requests
from anthropic import Anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

api_key = os.getenv("SUNO_API_KEY")
url = "https://api.sunoapi.org/api/v1/generate"
# payload = {
#     "prompt": "Slow, peaceful lofi beats",
#     "title": "Lofi beat", 
#     "customMode": True,
#     "instrumental": True,
#     "model": "V5",
#     "callBackUrl": "https://lofi-app-dc75.onrender.com/callback"
# }

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

#def make_song_params():
#    return {"url": url, 
#           "payload": payload, 
#            "headers": headers}

def make_song(query):
    title = make_title_name(query)
    payload = {
        "prompt": f"{query}",
        "title": f"{title}", 
        "customMode": True,
        "instrumental": True,
        "model": "V4",
        "callBackUrl": "https://lofi-app-dc75.onrender.com/callback"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

def make_title_name(query):
    prompt = (f"I am generating a song with the following prompt: <prompt>{query}</prompt>. " 
            "Come up with a short title name for the song. Only give me the title of the song, "
            "and nothing else. For example:\n"
            "prompt: 'Upbeat instrumental beat with great vibes' response: 'Energy Overload'")
    response = client.messages.create(
        model="claude-3-haiku-20240307",
	    max_tokens=50,
	    messages = [
	        {"role": "user", "content":  f"{prompt}"}
        ],
        temperature = 1
    )
    return response.content[0].text 
    
print(make_title_name("Calm lofi beat with rain and wind sounds in the background."))

# train model title
