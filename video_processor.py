import os
import logging
from datetime import datetime
import ffmpeg

logger = logging.getLogger(__name__)

def create_video(avatar_url: str, audio_path: str, text: str) -> str:
    """Create video with avatar animation and audio"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/video_{timestamp}.mp4"

        # Get audio duration
        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['streams'][0]['duration'])
            logger.debug(f"Audio duration: {duration} seconds")
        except Exception as e:
            logger.error(f"Error probing audio file: {str(e)}")
            duration = 10  # Fallback duration

        try:
            # Create black background
            background = ffmpeg.input(
                f'color=c=black:s=1280x720:d={duration}',
                f='lavfi'
            )

            # Input avatar and scale it
            avatar = (
                ffmpeg.input(avatar_url)
                .filter('scale', 720, -1)  # Scale avatar maintaining aspect ratio
                .filter('pad', 1280, 720, '(ow-iw)/2', '(oh-ih)/2')  # Center avatar
            )

            # Input audio
            audio = ffmpeg.input(audio_path)

            # Combine video and audio streams
            out = ffmpeg.output(
                background.overlay(avatar),
                audio,
                output_file,
                acodec='aac',
                vcodec='h264',
                pix_fmt='yuv420p',
                preset='medium',  # Balance between speed and quality
                movflags='+faststart',  # Enable fast start for web playback
                **{'b:v': '2M'}  # Set video bitrate
            ).overwrite_output()

            # Run FFmpeg command
            logger.debug("Running FFmpeg command...")
            ffmpeg.run(out, capture_stdout=True, capture_stderr=True)

            if os.path.exists(output_file):
                logger.info(f"Successfully created video: {output_file}")
                return output_file
            else:
                raise Exception("Output file was not created")

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg error: {error_message}")
            raise Exception(f"FFmpeg processing failed: {error_message}")

    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise Exception(f"Failed to create video: {str(e)}")