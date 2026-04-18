import os
import tempfile
import numpy as np
import librosa
from moviepy.editor import VideoFileClip

def get_peak_segments(video_path, num_segments=3, segment_duration=60):
    """
    Extract audio from video, compute RMS energy, and return the top 
    non-overlapping segments with the highest average energy.
    """
    try:
        # Load the video's audio using MoviePy
        print(f"Loading video from {video_path}")
        video = VideoFileClip(video_path)
        audio = video.audio
        
        if audio is None:
            raise ValueError("No audio track found in the video.")

        # Create a temporary file to store the extracted audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
            
        print(f"Extracting temporary audio to {temp_wav_path}")
        audio.write_audiofile(temp_wav_path, logger=None)
        
        # We don't need the video instance anymore
        video.close()

        print("Computing RMS energy using Librosa...")
        # Load audio using librosa. sr=22050 is fine for energy detection
        y, sr = librosa.load(temp_wav_path, sr=22050)
        
        # Compute RMS energy per frame
        # Returns shape (1, t)
        rms = librosa.feature.rms(y=y)[0]
        
        # Calculate frame rate for librosa default hop_length (512)
        frames_per_sec = sr / 512
        frames_per_segment = int(frames_per_sec * segment_duration)
        
        if len(rms) < frames_per_segment:
            # If the video is shorter than the segment_duration, just return its entire length
            duration = len(rms) / frames_per_sec
            return [(0, duration)]

        # Find rolling average of RMS energy over the segment duration
        # Convolve with a window of ones to get sum over window
        window = np.ones(frames_per_segment)
        rolling_sums = np.convolve(rms, window, mode='valid')

        peaks = []
        # Create a boolean array to mask out used regions to ensure non-overlapping
        used_mask = np.zeros_like(rolling_sums, dtype=bool)

        print("Finding peak segments...")
        for _ in range(num_segments):
            # Mask out the used segments so we don't pick them again
            masked_sums = np.where(used_mask, -1, rolling_sums)
            
            # Find the max peak among the available frames
            best_frame_idx = np.argmax(masked_sums)
            if masked_sums[best_frame_idx] == -1:
                # No more segments left to pick
                break
                
            start_time = best_frame_idx / frames_per_sec
            
            # Ensure we don't go past the actual audio length just in case
            video_duration = len(rms) / frames_per_sec
            end_time = min(start_time + segment_duration, video_duration)
            
            peaks.append((start_time, end_time))
            
            # Mark the region as used (we disable the whole region the segment spans)
            # We must disable within [-frames_per_segment, +frames_per_segment]
            # around best_frame_idx so no overlapping 60-second window is selected.
            start_mask = max(0, best_frame_idx - frames_per_segment)
            end_mask = min(len(used_mask), best_frame_idx + frames_per_segment)
            used_mask[start_mask:end_mask] = True

        # Clean up temporary WAV file
        os.remove(temp_wav_path)
        
        # Sort chronologically
        peaks.sort(key=lambda x: x[0])
        return peaks

    except Exception as e:
        print(f"Error in peak_detector: {e}")
        return []
