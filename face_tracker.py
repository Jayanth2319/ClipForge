import cv2

def get_face_center_x(video_path, start_time=0):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_time * fps))
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return 0.5
        h, w = frame.shape[:2]
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            x, y, fw, fh = faces[0]
            return (x + fw / 2) / w
        return 0.5
    except Exception as e:
        print(f"Error in face_tracker: {e}")
        return 0.5
