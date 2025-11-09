from flask import Flask, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from helper_functions.song_maker import make_song, make_song_params
import requests

# uses render for deployment

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class AISong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(100),default="NO SONG MADE")

@app.route ("/playlist", methods=["GET"])
def call_suno():
# if request.method == "GET":
    response = make_song()
    return "HELLO"

@app.route("/playlist", methods=["POST"])
def display_song():
  #  elif request.method == "POST":
    data = request.json
    print("Received callback:", data)

    code = data.get('code')
    callback_data = data.get('data', {})
    task_id = callback_data.get('task_id')
    music_data = callback_data.get('data', [])

    if code == 200:
        print(f"Music generation completed for task {task_id}")
        for i, music in enumerate(music_data):
            title = music.get('title')
            audio_url = music.get('audio_url')
            print(f"Downloading track {i+1}: {title}")
            if audio_url:
                r = requests.get(audio_url)
                filename = f"{title}_{task_id}_{i+1}.mp3"
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f"Saved {filename}")
        return "COOL MAN. IT DID IT"
    else:
        return "NOT COOL DUDE"
        print(f"Task failed: {data.get('msg')}")
    return "DONE"
            

@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        # response = make_song()
        return render_template('playlist.html')
    
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

    