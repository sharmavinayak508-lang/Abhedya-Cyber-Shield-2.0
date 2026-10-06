import cv2
import os

def verify_face_biometric():
    """ Opens live camera stream for face detection """
    try:
        # Load pre-trained Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)

        # Open default webcam (0)
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return False

        detected = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(100, 100)
            )

            # Draw green box around detected face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected - Press 'Q' or Wait", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if len(faces) > 0:
                detected = True

            # Display live camera window
            cv2.imshow("CyberShield - Biometric Face Scan (Press Q to exit)", frame)

            # Break loop if 'q' is pressed or after detecting face
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # If face detected, show for 1 second then complete verification
            if detected:
                cv2.waitKey(1000)
                break

        cap.release()
        cv2.destroyAllWindows()
        return detected

    except Exception as e:
        print(f"Biometric Verification Error: {e}")
        return False
