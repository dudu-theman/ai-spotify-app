from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from helper_functions.song_maker import make_song
import boto3
from io import BytesIO
import requests
from werkzeug.utils import secure_filename

load_dotenv()

# ----------------- AWS SETUP -----------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ----------------- FLASK + DB SETUP -----------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class AISong(db.Model):
    __tablename__ = "ai_song"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    audio_url = db.Column(db.String(300))

# Create tables (DO NOT drop_on_restart)
with app.app_context():
    db.create_all()

# -----------------------------------------------------
# ROUTE 1 — React frontend health check
# -----------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "backend running"}), 200


@app.route("/generate", methods=["POST"])
def generate_song():
    make_song()
    return jsonify({"message": "Generation started"}), 200


@app.route("/callback", methods=["POST"])
def callback():
    data = request.json or {}
    print("Received callback:", data)

    songs_data = data.get("data", {}).get("data", [])

    if data.get("code") == 200:
        for i, song in enumerate(songs_data):

            title = song.get("title", f"Song_{i}")
            audio_url = song.get("audio_url")

            if not audio_url:
                print("Skipping missing audio_url for song:", title)
                continue

            # download MP3 and upload to S3
            response = requests.get(audio_url)
            file_name = secure_filename(f"{title}.mp3")
            s3.upload_fileobj(
                BytesIO(response.content),
                AWS_BUCKET_NAME,
                f"{i}{file_name}",
                ExtraArgs={"ContentType": "audio/mpeg"}
            )

            # construct S3 URL and save in DB
            s3_url = (
                f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{i}{file_name}"
            )
            new_song = AISong(title=title, audio_url=s3_url)
            db.session.add(new_song)

        db.session.commit()

    return "Callback processed", 200


# -----------------------------------------------------
# ROUTE 4 — React fetches all songs from here
# -----------------------------------------------------
@app.route("/api/songs", methods=["GET"])
def api_songs():
    songs = AISong.query.all()

    return jsonify([
        {
            "id": s.id,
            "title": s.title,
            "audio_url": s.audio_url
        }
        for s in songs
    ]), 200


# -----------------------------------------------------
# RUN SERVER
# -----------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
