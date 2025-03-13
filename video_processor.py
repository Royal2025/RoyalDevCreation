import os
import logging
from datetime import datetime
import ffmpeg

logger = logging.getLogger(__name__)

def create_video(avatar_url: str, audio_path: str, text: str) -> str:
    """Create video with avatar animation and audio"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/video_{timestamp}.mp4"

        # Create video with ffmpeg
        (
            ffmpeg
            .input('color=c=black:s=1280x720:d=10', f='lavfi')
            .overlay(ffmpeg.input(avatar_url))
            .output(audio_path, output_file,
                   acodec='aac',
                   vcodec='h264',
                   pix_fmt='yuv420p')
            .overwrite_output()
            .run()
        )
        return output_file
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise Exception("Failed to create video")