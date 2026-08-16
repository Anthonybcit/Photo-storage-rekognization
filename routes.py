import boto3
import uuid
from flask import Flask, render_template, request
from config import Config

region = Config.region
client=boto3.client('rekognition', region_name=region)
Allowed_Extensions = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_Extensions:
        return True
    return False


def detect_labels(photo, bucket):
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
            MaxLabels=10, MinConfidence=60)
    labellist = []
    for label in response["Labels"]:
        labellist.append({"name": label["Name"], "confidence": label["Confidence"]})
    return labellist


app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        s3 = boto3.resource("s3", region_name=region)
        bucket_name = Config.bucket_name
        uploaded_files = request.files.getlist("file-to-save")
        for uploaded_file in uploaded_files:
            if uploaded_file.filename == '':
                continue
            if not allowed_file(uploaded_file.filename):
                return "INVALID FILE"
     
            new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()
            s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)
            labels = detect_labels(new_filename, bucket_name)
            return "Upload successful"
    return render_template("index.html")

@app.route("/photos", methods=["GET", "POST"])
def photos():
    return render_template("photos.html")