import os
import ffmpeg
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_video(avatar_url: str, audio_path: str, text: str) -> str:
    """Create video with avatar animation and audio"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/video_{timestamp}.mp4"
        
        # Create video with ffmpeg
        stream = ffmpeg.input('color=c=black:s=1280x720:d=10', f='lavfi')
        stream = ffmpeg.overlay(stream, ffmpeg.input(avatar_url))
        stream = ffmpeg.input(audio_path)
        
        stream = ffmpeg.output(stream, output_file,
                             acodec='aac',
                             vcodec='h264',
                             pix_fmt='yuv420p')
        
        ffmpeg.run(stream, overwrite_output=True)
        return output_file
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise Exception("Failed to create video")
