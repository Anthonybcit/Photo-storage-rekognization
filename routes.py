import boto3
import uuid
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from pymongo import MongoClient
import logging
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig




mongo = MongoClient(Config.MONGO_URI)

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
        labellist.append({"name": label["Name"].lower(), "confidence": label["Confidence"]})
    return labellist

maindb = mongo 
db = maindb["Project"]
labeldb = db["labels"]
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
            
            labelz = {
                "name" : new_filename,
                "labels":labels
            }


            labeldb.insert_one(labelz)
        return redirect(url_for("index"))
        
    return render_template("index.html")
@app.route("/search")
def search():
    q = request.args.get("q", "").lower()

    print("SEARCH:", q)

    if q:
        results = list(labeldb.find({"labels.name": q}))
    else:
        results = []

    print("RESULTS:", results)

    s3 = boto3.client(
        "s3",
        region_name=region,
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"}
        ),
    )

    for photo in results:
        photo["url"] = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": Config.bucket_name,
                "Key": photo["name"]
            },
            ExpiresIn=3600
        )

    return render_template("results.html", results=results)

@app.route("/photos", methods=["GET", "POST"])
def photos():
    photos =  list(labeldb.find())
    s3 = boto3.client(
        "s3",
        region_name=region,
        config=BotoConfig(signature_version="s3v4", s3={"addressing_style": "virtual"}),
    )
    for photo in photos:
        photo["url"] = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": Config.bucket_name,
                "Key": photo["name"]
            },
            ExpiresIn=3600
        )

    return render_template("photos.html", photos=photos)

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    s3 = boto3.client("s3", region_name=region)
    s3.delete_object(
        Bucket=Config.bucket_name,
        Key=name
    )
    labeldb.delete_one({"name": name})

    return redirect(url_for("photos"))