from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/photos")
def photos():
    return render_template("photos.html")