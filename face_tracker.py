import cv2
import mediapipe as mp

def get_face_center_x(video_path, start_time, num_frames=5):
    """
    Reads frames starting at `start_time`, detects faces using MediaPipe,
    and returns the average x-center of the detected face as a ratio (0.0 to 1.0).
    Returns 0.5 if no face is detected.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Failed to open video in face_tracker.")
            return 0.5

        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame_idx = int(start_time * fps)
        
        # Space out the frames over 1 second to get a stable average
        stride = max(1, int(fps / num_frames))
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
        
        centers = []
        for i in range(num_frames):
            frame_idx = start_frame_idx + (i * stride)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert BGR to RGB for mediapipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image_rgb)
            
            if results.detections:
                # We simply use the first detected face (assuming mainly 1 speaker)
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                # Face center x relative ratio
                center_x = bbox.xmin + (bbox.width / 2.0)
                
                # Keep it within [0, 1] bounds
                center_x = max(0.0, min(1.0, center_x))
                centers.append(center_x)

        cap.release()
        face_detection.close()
        
        if centers:
            return sum(centers) / len(centers)
        else:
            return 0.5

    except Exception as e:
        print(f"Error in face_tracker: {e}")
        return 0.5
