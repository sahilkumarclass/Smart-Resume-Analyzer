# FLASK APP - Run the app using flask --app app.py run
import os, sys, uuid
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from pypdf import PdfReader 
import json
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))


UPLOAD_PATH = r"__DATA__"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_PATH, exist_ok=True)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB limit


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    try:
        if 'pdf_doc' not in request.files:
            return render_template('index.html', error="No file part in the request."), 400

        doc = request.files['pdf_doc']
        if not doc or doc.filename == '':
            return render_template('index.html', error="Please choose a PDF resume to upload."), 400

        filename = secure_filename(doc.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return render_template('index.html', error="Only PDF files are supported."), 400

        unique_name = f"{uuid.uuid4()}.pdf"
        doc_path = os.path.join(UPLOAD_PATH, unique_name)
        doc.save(doc_path)

        job_description = request.form.get('job_description', '').strip()
        resume_text = _read_file_from_path(doc_path)

        response_json_str = ats_extractor(resume_text, job_description if job_description else None)

        try:
            payload = json.loads(response_json_str)
        except Exception:
            return render_template('index.html', error="The AI response could not be parsed. Please try a simpler resume or try again."), 502

        return render_template('index.html', data=payload)
    except Exception:
        return render_template('index.html', error="Something went wrong while processing your request. Please try again."), 500
 
def _read_file_from_path(path):
    reader = PdfReader(path) 
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no] 
        text = page.extract_text()
        if text:
            data += text

    return data 


if __name__ == "__main__":
    app.run(port=8000, debug=True)
    app.run(host='0.0.0.0', port=port)

