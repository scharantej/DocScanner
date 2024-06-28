### Flask Application Design

#### HTML Files

- **upload.html**:
    - Form to upload a PDF transcript
    - Button to trigger the upload

- **transcripts.html**:
    - List of uploaded transcripts and their statuses
    - Link to view the detail of each transcript

- **transcript_detail.html**:
    - Viewer for the uploaded PDF transcript
    - Fields for viewing and editing the extracted credits
    - Buttons to approve, reject, or request additional information

#### Routes

- **main_page** (**@app.route("/")**):
    - Endpoint to display the upload form (`upload.html`)

- **upload_transcript** (**@app.route("/upload-transcript", methods=["POST"])**):
    - Endpoint to handle the transcript upload process
    - Saves the transcript to Google Cloud Storage and adds an entry to BigQuery

- **transcripts** (**@app.route("/transcripts")**):
    - Endpoint to fetch the list of uploaded transcripts

- **transcript_detail** (**@app.route("/transcript-detail/<transcript_id>")**):
    - Endpoint to display the details of a specific transcript
    - Shows the PDF viewer, fields, and buttons for editing

- **update_transcript** (**@app.route("/update-transcript/<transcript_id>", methods=["POST"])**):
    - Endpoint to handle the transcript detail update process
    - Updates the extracted credits in the database and the transcript in Google Cloud Storage (if needed)