import cv2

def verify_face_biometric():
    """Captures webcam frame and verifies face presence using OpenCV Haar Cascades."""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return False

        found_face = False
        for _ in range(30):  # Test for ~3 seconds
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                found_face = True
                break

        cap.release()
        cv2.destroyAllWindows()
        return found_face
    except Exception as e:
        print(f"Biometric Error: {e}")
        return False

verify_face = verify_face_biometric
