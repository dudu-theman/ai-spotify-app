# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# import os
# import requests
# import boto3
# from helper_functions.song_maker import make_song

# from dotenv import load_dotenv
# load_dotenv()

# app = Flask(__name__)

# # ----------------- DATABASE SETUP -----------------
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # Cloud Postgres URI
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)

# class AISong(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150))
#     s3_url = db.Column(db.String(300))
#     task_id = db.Column(db.String(100))

# with app.app_context():
#     db.create_all()

# # ----------------- S3 SETUP -----------------
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#     region_name=os.getenv("AWS_REGION")
# )
# bucket_name = os.getenv("AWS_BUCKET_NAME")

# def upload_to_s3(file_url, filename):
#     """
#     Downloads file from file_url and uploads it to S3, returns S3 URL
#     """
#     response = requests.get(file_url)
#     response.raise_for_status()

#     s3_client.put_object(
#         Bucket=bucket_name,
#         Key=filename,
#         Body=response.content,
#         ACL='public-read'  # optional: makes the file publicly accessible
#     )

#     s3_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"
#     return s3_url

# # ----------------- ROUTES -----------------
# @app.route("/", methods=["GET"])
# def index():
#     return render_template("index.html")

# @app.route("/playlist", methods=["GET", "POST"])
# def call_suno():
#     if request.method == "GET":
#         # Trigger Suno song generation
#         make_song()
#         return render_template("playlist.html")
    
#     elif request.method == "POST":
#         # Suno callback
#         data = request.json
#         print("Received callback:", data)

#         code = data.get('code')
#         callback_data = data.get('data', {})
#         task_id = callback_data.get('task_id')
#         music_data = callback_data.get('data', [])

#         if code == 200:
#             for i, song in enumerate(music_data):
#                 audio_url = song['audio_url']
#                 title = song.get('title', f"Song_{i}")

#                 # Create unique filename for S3
#                 filename = f"{task_id}_{i}.mp3"

#                 try:
#                     s3_url = upload_to_s3(audio_url, filename)
#                     # Save metadata in DB
#                     new_song = AISong(title=title, s3_url=s3_url, task_id=task_id)
#                     db.session.add(new_song)
#                     db.session.commit()
#                     print(f"Uploaded {title} to S3: {s3_url}")
#                 except Exception as e:
#                     print(f"Error uploading song: {e}")

#         return "Callback processed"

# @app.route("/displaysongurls", methods=["GET"])
# def disp_songs():
#     songurls = AISong.query.all()
#     return render_template("displaysongurls.html", songurls=songurls)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=False)


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

# ----------------- DATABASE SETUP -----------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # e.g. postgresql://user:pass@host:port/dbname
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class AISong(db.Model):
    __tablename__ = "ai_song"  # explicitly define table name to avoid mismatch
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    audio_url = db.Column(db.String(300))  # this column must exist in the DB
    task_id = db.Column(db.String(100))

# Drop and recreate the table to fix column mismatch
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
         # Trigger Suno song generation
        make_song()
        return render_template("playlist.html")
    data = request.json or {}
    print("Received callback:", data)

    code = data.get("code")
    callback_data = data.get("data", {})
    task_id = callback_data.get("task_id")
    music_data = callback_data.get("data", [])

    if code == 200:
        for i, song in enumerate(music_data):
            title = song.get("title", f"Song_{i}")
            audio_url = song.get("audio_url")

            if not audio_url:
                print(f"Skipping {title}: no audio_url")
                continue

            # 1️⃣ Download MP3 from Suno
            response = requests.get(audio_url)
            if response.status_code != 200:
                print(f"Failed to download {title}")
                continue

            # 2️⃣ Upload to your S3 bucket
            file_name = secure_filename(f"{title}.mp3")
            s3.upload_fileobj(
                BytesIO(response.content),
                AWS_BUCKET_NAME,
                file_name,
                ExtraArgs={"ContentType": "audio/mpeg"}
            )

            # 3️⃣ Construct the S3 URL
            s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"

            # 4️⃣ Save that URL in the database
            new_song = AISong(title=title, audio_url=s3_url, task_id=task_id)
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
