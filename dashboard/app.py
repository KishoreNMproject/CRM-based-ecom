from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend/backend communication

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
