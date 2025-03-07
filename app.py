import os
import time
import uuid
import json
import threading
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Import from your existing transcriber
import whisper
from language_utils import SUPPORTED_LANGUAGES, is_language_supported, get_language_name
from transcriber import transcribe_audio, save_transcription

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'ogg'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Store job status
jobs = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_file(job_id, file_path, model_size, language):
    """Process a single file and update job status"""
    try:
        # Update job status
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 0
        
        # Create a custom progress callback
        def progress_callback(stage, progress):
            jobs[job_id]['stage'] = stage
            jobs[job_id]['progress'] = progress
        
        # Transcribe the audio
        result = transcribe_audio_for_web(file_path, model_size, language, progress_callback)
        
        # Save the transcription
        output_file = os.path.join(app.config['RESULT_FOLDER'], f"{job_id}.txt")
        save_transcription(result, output_file)
        
        # Update job status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['result_file'] = output_file
        
        # Add language info if auto-detection was used
        if language == "auto" and "language" in result:
            detected_code = result["language"]
            detected_name = get_language_name(detected_code)
            jobs[job_id]['detected_language'] = {
                'code': detected_code,
                'name': detected_name
            }
        
    except Exception as e:
        # Update job status with error
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)

def transcribe_audio_for_web(file_path, model_size="base", language=None, progress_callback=None):
    """Modified version of transcribe_audio for web use with progress callbacks"""
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Load the Whisper model
    if progress_callback:
        progress_callback("loading_model", 0)
    
    model = whisper.load_model(model_size)
    
    if progress_callback:
        progress_callback("loading_model", 100)
    
    # Prepare transcription options
    transcribe_options = {}
    
    # Handle language option
    if language and language != "auto":
        transcribe_options["language"] = language
    
    # Transcribe the audio
    if progress_callback:
        progress_callback("transcribing", 0)
    
    # Run transcription
    result = model.transcribe(file_path, **transcribe_options)
    
    if progress_callback:
        progress_callback("transcribing", 100)
    
    return result

@app.route('/')
def index():
    # Get sorted list of languages for the dropdown
    languages = sorted(SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
    return render_template('index.html', languages=languages)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Get form parameters
    model_size = request.form.get('model', 'base')
    language = request.form.get('language', None)
    
    # Validate model size
    if model_size not in ["tiny", "base", "small", "medium", "large"]:
        return jsonify({'error': 'Invalid model size'}), 400
    
    # Validate language if provided
    if language and not is_language_supported(language):
        return jsonify({'error': 'Unsupported language code'}), 400
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    file.save(file_path)
    
    # Create job entry
    jobs[job_id] = {
        'id': job_id,
        'filename': filename,
        'file_path': file_path,
        'model': model_size,
        'language': language,
        'status': 'queued',
        'created_at': time.time()
    }
    
    # Start processing in a background thread
    threading.Thread(
        target=process_file,
        args=(job_id, file_path, model_size, language)
    ).start()
    
    # Return job ID to client
    return jsonify({
        'job_id': job_id,
        'status': 'queued'
    })

@app.route('/status/<job_id>')
def job_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])

@app.route('/download/<job_id>')
def download_result(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Transcription not completed'}), 400
    
    return send_file(
        job['result_file'],
        as_attachment=True,
        download_name=f"{os.path.splitext(job['filename'])[0]}_transcript.txt"
    )

@app.route('/languages')
def get_languages():
    # Return the list of supported languages
    return jsonify({
        'languages': SUPPORTED_LANGUAGES,
        'sorted': sorted(SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
    })

# Clean up old jobs and files periodically (would be implemented with a scheduler in production)
def cleanup_old_jobs():
    current_time = time.time()
    for job_id in list(jobs.keys()):
        # Remove jobs older than 24 hours
        if current_time - jobs[job_id]['created_at'] > 86400:
            # Delete files
            try:
                if os.path.exists(jobs[job_id]['file_path']):
                    os.remove(jobs[job_id]['file_path'])
                
                if 'result_file' in jobs[job_id] and os.path.exists(jobs[job_id]['result_file']):
                    os.remove(jobs[job_id]['result_file'])
            except:
                pass
            
            # Remove job from dictionary
            del jobs[job_id]

if __name__ == '__main__':
    app.run(debug=True)

