import os
import logging
from datetime import datetime
import ffmpeg
from typing import Optional

logger = logging.getLogger(__name__)

def create_video(avatar_url: str, audio_path: str, text: str) -> str:
    """Create video with avatar animation and audio"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/video_{timestamp}.mp4"

        # Get audio duration using ffprobe
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])

        # Create video with ffmpeg
        stream = (
            ffmpeg
            .input('color=c=black:s=1280x720:d=' + str(duration), f='lavfi')
            .overlay(
                ffmpeg.input(avatar_url)
                .filter('scale', 720, -1)  # Scale avatar while maintaining aspect ratio
                .filter('pad', 1280, 720, '(ow-iw)/2', '(oh-ih)/2')  # Center avatar
            )
        )

        # Add audio
        stream = ffmpeg.input(audio_path).output(
            stream,
            output_file,
            acodec='aac',
            vcodec='h264',
            pix_fmt='yuv420p',
            shortest=None  # End when shortest input ends
        )

        # Run ffmpeg
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        logger.info(f"Successfully created video: {output_file}")
        return output_file

    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise Exception("Failed to create video - FFmpeg error")
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise Exception("Failed to create video")