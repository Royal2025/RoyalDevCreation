import numpy as np
import librosa
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LipSync:
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.frame_length = 2048

    def analyze_audio(self, audio_path: str) -> List[Dict[str, float]]:
        """Analyze audio file and generate lip sync data"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Calculate amplitude envelope
            amplitude_envelope = self._get_amplitude_envelope(y)
            
            # Convert to lip movements
            lip_movements = self._amplitude_to_lip_movement(amplitude_envelope)
            
            return lip_movements
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            return []

    def _get_amplitude_envelope(self, y: np.ndarray) -> np.ndarray:
        """Calculate amplitude envelope of the audio signal"""
        try:
            # Calculate RMS energy for each frame
            rms = librosa.feature.rms(
                y=y,
                frame_length=self.frame_length,
                hop_length=self.hop_length
            )[0]
            
            # Normalize
            rms = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
            
            return rms
        except Exception as e:
            logger.error(f"Error calculating amplitude envelope: {str(e)}")
            return np.zeros(1)

    def _amplitude_to_lip_movement(self, amplitude: np.ndarray) -> List[Dict[str, float]]:
        """Convert amplitude data to lip movement keyframes"""
        try:
            movements = []
            
            for i, amp in enumerate(amplitude):
                # Calculate time in seconds
                time = (i * self.hop_length) / self.sample_rate
                
                # Map amplitude to mouth opening
                mouth_open = amp * 0.8  # Scale factor for mouth movement
                
                # Generate keyframe
                keyframe = {
                    'timestamp': time,
                    'mouth_open': float(mouth_open),
                    'mouth_shape': {
                        'width': 1.0 + float(mouth_open * 0.2),  # Slight width variation
                        'height': float(mouth_open)
                    }
                }
                
                movements.append(keyframe)
            
            return movements
        except Exception as e:
            logger.error(f"Error converting amplitude to lip movement: {str(e)}")
            return []

    def get_frame_data(self, lip_movements: List[Dict[str, float]], timestamp: float) -> Dict[str, float]:
        """Get interpolated lip shape data for a specific timestamp"""
        try:
            if not lip_movements:
                return {
                    'mouth_open': 0.0,
                    'mouth_shape': {'width': 1.0, 'height': 0.0}
                }

            # Find surrounding keyframes
            prev_frame = None
            next_frame = None
            
            for frame in lip_movements:
                if frame['timestamp'] <= timestamp:
                    prev_frame = frame
                if frame['timestamp'] > timestamp and next_frame is None:
                    next_frame = frame
                    break

            if prev_frame is None:
                return lip_movements[0]
            if next_frame is None:
                return prev_frame

            # Interpolate between frames
            t_diff = next_frame['timestamp'] - prev_frame['timestamp']
            if t_diff == 0:
                return prev_frame

            alpha = (timestamp - prev_frame['timestamp']) / t_diff
            
            return {
                'mouth_open': self._lerp(prev_frame['mouth_open'], 
                                       next_frame['mouth_open'], 
                                       alpha),
                'mouth_shape': {
                    'width': self._lerp(prev_frame['mouth_shape']['width'],
                                      next_frame['mouth_shape']['width'],
                                      alpha),
                    'height': self._lerp(prev_frame['mouth_shape']['height'],
                                       next_frame['mouth_shape']['height'],
                                       alpha)
                }
            }
        except Exception as e:
            logger.error(f"Error getting frame data: {str(e)}")
            return {
                'mouth_open': 0.0,
                'mouth_shape': {'width': 1.0, 'height': 0.0}
            }

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between two values"""
        return a + (b - a) * t
