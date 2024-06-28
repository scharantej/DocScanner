
# main.py

from flask import Flask, render_template, request, redirect, url_for, send_file
import uuid
import os
from google.cloud import storage
from google.cloud import bigquery

app = Flask(__name__)

# Google Cloud Storage and BigQuery setup
storage_client = storage.Client()
bucket_name = "transcript-analyzer"
bucket = storage_client.bucket(bucket_name)
bigquery_client = bigquery.Client()

# Routes
@app.route("/")
def main_page():
    return render_template("upload.html")

@app.route("/upload-transcript", methods=["POST"])
def upload_transcript():
    # Get the uploaded transcript
    transcript = request.files["transcript"]
    # Generate a unique identifier for the transcript
    transcript_id = str(uuid.uuid4())
    # Upload the transcript to Google Cloud Storage
    filename = transcript_id + ".pdf"
    blob = bucket.blob(filename)
    blob.upload_from_file(transcript)
    # Add an entry to the BigQuery table
    dataset_id = "transcripts"
    table_id = "transcript_details"
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    data = [{
        "transcript_id": transcript_id,
        "filename": filename,
        "status": "pending"
    }]
    errors = bigquery_client.insert_rows_json(table_ref, data)
    if errors == []:
        return redirect(url_for("transcripts"))
    else:
        return "Error: Could not add transcript to BigQuery."

@app.route("/transcripts")
def transcripts():
    # Get the list of transcripts from BigQuery
    query = """
        SELECT
            transcript_id,
            filename,
            status
        FROM
            `{}.{}.transcript_details`
    """.format(dataset_id, table_id)
    query_job = bigquery_client.query(query)
    results = query_job.result()
    return render_template("transcripts.html", transcripts=results)

@app.route("/transcript-detail/<transcript_id>")
def transcript_detail(transcript_id):
    # Get the transcript details from BigQuery
    query = """
        SELECT
            transcript_id,
            filename,
            status
        FROM
            `{}.{}.transcript_details`
        WHERE
            transcript_id = '{}'
    """.format(dataset_id, table_id, transcript_id)
    query_job = bigquery_client.query(query)
    results = query_job.result()
    transcript = results[0]
    # Get the transcript PDF from Google Cloud Storage
    filename = transcript["filename"]
    blob = bucket.blob(filename)
    return render_template("transcript_detail.html", transcript=transcript, transcript_pdf=blob)

@app.route("/update-transcript/<transcript_id>", methods=["POST"])
def update_transcript(transcript_id):
    # Get the updated transcript details from the form
    status = request.form["status"]
    # Update the transcript details in BigQuery
    query = """
        UPDATE
            `{}.{}.transcript_details`
        SET
            status = '{}'
        WHERE
            transcript_id = '{}'
    """.format(dataset_id, table_id, status, transcript_id)
    query_job = bigquery_client.query(query)
    query_job.result()
    # Redirect to the transcripts page
    return redirect(url_for("transcripts"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
