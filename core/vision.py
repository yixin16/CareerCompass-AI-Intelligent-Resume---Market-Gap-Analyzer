# core/vision.py
import cv2
import numpy as np
from deepface import DeepFace
import threading
import queue

class VideoAnalyzer:
    def __init__(self):
        # We use a queue to store emotions to avoid blocking the main thread
        self.emotion_queue = queue.Queue()
        self.emotion_history = []
        self.is_running = False
        
    def analyze_frame(self, frame_rgb):
        """
        Runs emotion analysis on a single frame.
        Note: DeepFace can be slow, so usually we run this every 5th or 10th frame.
        """
        try:
            # DeepFace expects BGR usually if passing path, but numpy array is flexible.
            # Enforce detection to ensure a face exists
            analysis = DeepFace.analyze(
                img_path=frame_rgb, 
                actions=['emotion'], 
                enforce_detection=False,
                detector_backend='opencv', # 'opencv' is fastest, 'mtcnn' is more accurate
                silent=True
            )
            
            # DeepFace returns a list of dicts (one for each face)
            if analysis and isinstance(analysis, list):
                dominant_emotion = analysis[0]['dominant_emotion']
                confidence = analysis[0]['face_confidence'] if 'face_confidence' in analysis[0] else 1.0
                
                return {
                    "emotion": dominant_emotion,
                    "all_scores": analysis[0]['emotion'],
                    "confidence": confidence
                }
        except Exception as e:
            # Face not found or error
            return None
        return None

    def aggregate_emotions(self):
        """
        Summarizes the session for the final report.
        """
        if not self.emotion_history:
            return "No video data available."

        from collections import Counter
        emotions = [e['emotion'] for e in self.emotion_history]
        counts = Counter(emotions)
        total = len(emotions)
        
        summary = {k: f"{(v/total)*100:.1f}%" for k, v in counts.items()}
        return summary
