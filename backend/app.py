from flask import Flask, request, jsonify, g, session
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
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://lofi-app-dc75.onrender.com", "https://ai-spotify-app.vercel.app"])
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
db = SQLAlchemy(app)

class AISong(db.Model):
    __tablename__ = "ai_song"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    audio_url = db.Column(db.String(300))
    song_id = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=True)
    owner = db.relationship("Users", backref="songs")

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
  
class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending | complete | error


with app.app_context():
    db.drop_all()
    db.create_all()


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "backend running"}), 200

@app.before_request
def load_current_user():
    user_id = session.get('user_id')
    if user_id:
        g.current_user = Users.query.get(user_id)
    else:
        g.current_user = None


@app.route("/generate", methods=["POST"])
def generate_song():
    query = request.args.get("q")
    if not g.current_user:
        return jsonify({"message": "Please log in"}), 401
    
    response = make_song(query)
    if response.get("code") != 200:
        return jsonify({"message": "Suno API error"}), 500
    
    task_id = response["data"]["taskId"]
    print(f"GENERATED TASK ID IS {task_id}",flush=True)

    new_task = Task(task_id=task_id, user_id=g.current_user.id, status="pending")
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Generation started",
        "task_id": task_id,
        "status": new_task.status
    }), 200


@app.route("/callback", methods=["POST"])
def callback():
    data = request.json or {}
    songs_data = data.get("data", {}).get("data", [])
    task_id = data.get("data",{}).get("task_id")
    print(f"DATA IS {data}", flush=True)
    print(f"TASK ID FOR CALLBACK IS {task_id}", flush=True)

    callback_type = data.get("data", {}).get("callbackType")
    if callback_type != "complete":
        return "Waiting for final callback", 200
    
    task = Task.query.get(task_id)
    if not task:
        print("Unknown task_id:", task_id)
        return "Unknown task", 400
    
    if data.get("code") != 200:
        task.status = "error"
        db.session.commit()
        return "Callback returned error", 200

    if data.get("code") == 200:
        song = songs_data[0]
        title = song.get("title","Song is missing title")
        audio_url = song.get("audio_url")

        if not audio_url:
            print("Skipping missing audio_url for song:", title)
            return "No audio to download yet", 200

        song_id = song.get("id")
        existing = AISong.query.filter_by(song_id=song_id).first()
        if existing:
            print("Callback already processed for this song:", song_id)
            return "Already processed", 200


        # download MP3 and upload to S3  
        print(f"{audio_url}", flush=True)
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

        new_song = AISong(title=title, audio_url=s3_url, song_id=song_id, user_id=task.user_id)
        db.session.add(new_song)
        task.status = "complete"
        db.session.commit()
        

    return "Callback processed", 200

@app.route("/task_status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Unknown task"}), 404
    return jsonify({"task_id": task.task_id, "status": task.status}), 200


@app.route("/login", methods=["GET","POST"])
def verify_identity():
    data = request.get_json()
    if not data:
        return jsonify({"message": "invalid JSON"}), 500
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing fields"}), 400
    
    existing = Users.query.filter_by(username=username).first()
    if not existing:
        return jsonify({"message": "Username doesn't exist"}), 400

    if existing.password != password:
        return jsonify({"message": "Incorrect password"}), 400

    else:
        session['user_id'] = existing.id
        return jsonify({"message": "login successful"}), 200

@app.route("/signup", methods=["GET","POST"])
def create_account():
    data = request.get_json()
    print(data)

    if not data:
        return jsonify({"message": "invalid JSON"}), 500
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing fields"}), 400


    existing = Users.query.filter_by(username=username).first()
    if existing:
        return jsonify({"message": "Username already exists"}), 400

    new_user = Users(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 200



@app.route("/api/songs/private", methods=["GET"])
def api_songs():
    if g.current_user:
        private_songs = AISong.query.filter_by(user_id=g.current_user.id).all()
    else:
        return jsonify({"message": "Please log in"}), 401

    result = []
    for s in private_songs:
        result.append({
            "id": s.id,
            "title": s.title,
            "audio_url": s.audio_url
        })

    return jsonify(result), 200

@app.route("/api/songs/public", methods=["GET"])
def public_songs():
    songs = AISong.query.filter_by(user_id=None).all()
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

# IMPLEMENT OVER BREAK
# 1. disable song creation while one is already in process
# 2. create aleart for when song is generating
# 3. add libarary of public songs