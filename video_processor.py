import os
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

def create_video(avatar_url: str, audio_path: str, text: str) -> str:
    """Create video with avatar animation and audio"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/video_{timestamp}.mp4"

        # Get audio duration using ffprobe
        try:
            probe_cmd = [
                'ffprobe', 
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            duration = float(subprocess.check_output(probe_cmd).decode().strip())
            logger.debug(f"Audio duration: {duration} seconds")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error probing audio file: {str(e)}")
            duration = 10  # Fallback duration

        # Construct FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            # Input 1: Create black background
            '-f', 'lavfi',
            '-i', f'color=c=black:s=1280x720:d={duration}',
            # Input 2: Avatar image
            '-i', avatar_url,
            # Input 3: Audio file
            '-i', audio_path,
            # Video filters
            '-filter_complex',
            '[1:v]scale=720:-1[avatar];[avatar]pad=1280:720:(ow-iw)/2:(oh-ih)/2[scaled];[0:v][scaled]overlay=0:0',
            # Output options
            '-c:a', 'aac',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-y',  # Overwrite output file if exists
            output_file
        ]

        # Execute FFmpeg command
        logger.debug(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if process.returncode != 0:
            logger.error(f"FFmpeg error: {process.stderr}")
            raise Exception(f"FFmpeg processing failed: {process.stderr}")

        if os.path.exists(output_file):
            logger.info(f"Successfully created video: {output_file}")
            return output_file
        else:
            raise Exception("Output file was not created")

    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise Exception(f"Failed to create video: {str(e)}")