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
import uuid

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class AISong(db.Model):
    __tablename__ = "ai_song"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    audio_url = db.Column(db.String(300))
    song_id = db.Column(db.String(300))

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)


with app.app_context():
    db.drop_all()
    db.create_all()


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "backend running"}), 200


@app.route("/generate", methods=["POST"])
def generate_song():
    query = request.args.get("q")
    make_song(query)
    return jsonify({"message": "Generation started"}), 200


@app.route("/callback", methods=["POST"])
def callback():
    data = request.json or {}
    print("Received callback:", data)

    songs_data = data.get("data", {}).get("data", [])

    if data.get("code") == 200:
        song = songs_data[0]

        title = song.get("title","Song is missing title")
        audio_url = song.get("audio_url")
        if not audio_url:
            print("Skipping missing audio_url for song:", title)

        song_id = song.get("id")
        existing = AISong.query.filter_by(song_id=song_id).first()
        if existing:
            print("Callback already processed for this song:", song_id)
            return "Already processed", 200


        # download MP3 and upload to S3
        response = requests.get(audio_url)
        unique_id = str(uuid.uuid4())
        file_name = secure_filename(f"{unique_id}_{title}.mp3")
        s3.upload_fileobj(
            BytesIO(response.content),
            AWS_BUCKET_NAME,
            f"{file_name}",
            ExtraArgs={"ContentType": "audio/mpeg"}
        )

        # construct S3 URL and save in DB
        s3_url = (
            f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        )
        new_song = AISong(title=title, audio_url=s3_url, song_id=song_id)
        db.session.add(new_song)

        db.session.commit()

    return "Callback processed", 200

@app.route("/login", methods=["GET","POST"])
def verify_identity():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Missing fields"}, 400
    
    existing = Users.query.filter_by(username=username).first()
    if not existing:
        return {"message": "Username doesn't exist"}, 400

    if existing.password != password:
        return {"message": "Incorrect password"}, 400

    else:
        return {"login successful"}, 200

@app.route("/signup", methods=["GET","POST"])
def create_account():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Missing fields"}, 400


    existing = Users.query.filter_by(username=username).first()
    if existing:
        return {"message": "Username already exists"}, 400

    new_user = Users(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    print("SUCCESFUL")
    return {"message": "User created successfully"}, 200



@app.route("/api/songs", methods=["GET"])
def api_songs():
    songs = AISong.query.all()

    result = []
    for s in songs:
        result.append({
            "id": s.id,
            "title": s.title,
            "audio_url": s.audio_url
        })

    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# Firebase, Clerk for authentication