from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from helper_functions.song_maker import make_song
import boto3
from io import BytesIO
import requests
from werkzeug.utils import secure_filename

load_dotenv()

AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION=os.getenv("AWS_REGION")
AWS_BUCKET_NAME=os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

app = Flask(__name__)

# DATABASE SETUP (postgre)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# an AISong is:
# id song_title song_url 
# task_id is kind of useless right now since it is just suno's thing
class AISong(db.Model):
    __tablename__ = "ai_song"  # explicitly define table name to avoid mismatch
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    audio_url = db.Column(db.String(300))  # this column must exist in the DB
  #  task_id = db.Column(db.String(100))

# drop and recreate the table
with app.app_context():
    db.drop_all()
    db.create_all()

# ----------------- ROUTES -----------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/playlist", methods=["POST","GET"])
def handle_callback():
    if request.method == "GET":
         # trigger Suno song generation
        make_song()
        return render_template("playlist.html")
    data = request.json or {}
    print("Received callback:", data)
  
  #  task_id = callback_data.get("task_id")

    # callback_data is a dictionary with:
    # callbackType: either "complete" or "error"
    # task_id
    # data: listof songs, each song is represented by a dict
    callback_data = data.get("data",{})
    # get the list of songs
    music_data = callback_data.get("data", [])
    code = data.get("code")
    if code == 200: # code 200 means music generation succeeded
        for i, song in enumerate(music_data):
            title = song.get("title", f"Song_{i}")
            audio_url = song.get("audio_url")

            # download MP3 song file from audio url
            response = requests.get(audio_url)

            # upload the song to S3 bucket
            file_name = secure_filename(f"{title}.mp3")
            s3.upload_fileobj(
                BytesIO(response.content),
                AWS_BUCKET_NAME,
                f"{i}{file_name}",
                ExtraArgs={"ContentType": "audio/mpeg"}
            )

            # construct the S3 URL
            s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{i}{file_name}"

            # Save URL in the database
            new_song = AISong(title=title, audio_url=s3_url)
            db.session.add(new_song)

        db.session.commit()   
        print(f"Uploaded {len(music_data)} songs to S3 and saved to database.")

    return "Callback processed"

@app.route("/displaysongurls", methods=["GET"])
def disp_songs():
    songs = AISong.query.all()
    return render_template("displaysongurls.html", songurls=songs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
