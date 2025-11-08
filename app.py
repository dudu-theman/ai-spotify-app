from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])
def index():
    print("hi")
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)