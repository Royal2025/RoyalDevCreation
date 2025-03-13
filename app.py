import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from tts_engine import generate_speech
from avatars import get_random_avatars
from video_processor import create_video
from utils import cleanup_old_files

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

@app.route('/')
def index():
    try:
        avatars = get_random_avatars(20)
        return render_template('index.html', avatars=avatars)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('index.html', error="Failed to load avatars")

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text')
        avatar_url = data.get('avatar')
        voice = data.get('voice', 'en-US-AriaNeural')

        if not all([text, avatar_url]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Generate speech
        audio_path = generate_speech(text, voice)
        
        # Create video with animation
        video_path = create_video(avatar_url, audio_path, text)
        
        # Cleanup old files
        cleanup_old_files()
        
        return jsonify({
            'status': 'success',
            'video_path': video_path
        })
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download(filename):
    try:
        return send_file(
            f'output/{filename}',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'File not found'}), 404
