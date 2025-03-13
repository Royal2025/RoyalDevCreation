import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from tts_engine import generate_speech
from avatars import get_random_avatars
from video_processor import create_video
from utils import cleanup_old_files

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import models after db initialization to avoid circular imports
from models import VideoGeneration

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

@app.route('/')
def index():
    try:
        avatars = get_random_avatars(20)
        # Get recent generations
        recent_generations = VideoGeneration.query.order_by(
            VideoGeneration.created_at.desc()
        ).limit(5).all()
        return render_template('index.html', 
                             avatars=avatars,
                             recent_generations=recent_generations)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('index.html', error="Failed to load avatars")

@app.route('/preview-voice', methods=['POST'])
def preview_voice():
    try:
        data = request.json
        text = data.get('text')
        voice = data.get('voice', 'en-US-AriaNeural')

        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400

        # Generate preview audio
        audio_path = generate_speech(text, voice)

        # Return audio file URL
        return jsonify({
            'status': 'success',
            'audio_url': f'/download/{os.path.basename(audio_path)}'
        })
    except Exception as e:
        logger.error(f"Error previewing voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text')
        avatar_url = data.get('avatar')
        voice = data.get('voice', 'en-US-AriaNeural')

        if not all([text, avatar_url]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Create database entry
        generation = VideoGeneration(
            text=text,
            avatar_url=avatar_url,
            voice=voice,
            status='processing'
        )
        db.session.add(generation)
        db.session.commit()

        try:
            # Generate speech
            audio_path = generate_speech(text, voice)

            # Create video with animation
            video_path = create_video(avatar_url, audio_path, text)

            # Update database entry
            generation.video_path = video_path
            generation.status = 'completed'
            db.session.commit()

            # Cleanup old files
            cleanup_old_files()

            return jsonify({
                'status': 'success',
                'video_path': video_path,
                'generation': generation.to_dict()
            })
        except Exception as e:
            generation.status = 'failed'
            db.session.commit()
            raise e

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

# Create database tables
with app.app_context():
    db.create_all()