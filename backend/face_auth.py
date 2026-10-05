import cv2

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

def verify_face_biometric(timeout_frames=100) -> bool:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False

    detected = False
    frame_count = 0

    while frame_count < timeout_frames:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            detected = True
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    return detected

