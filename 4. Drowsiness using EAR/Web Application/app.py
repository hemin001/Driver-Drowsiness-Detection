from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import math
import csv
from datetime import datetime
import os
import winsound
from collections import deque
import threading
import time

app = Flask(__name__)

# Global variables
ear_values = deque(maxlen=100)
timestamps = deque(maxlen=100)
plot_frame = 0
frame_counter = 0
status = "READY"
avg_ear = 0.0
alert_active = False
last_alert_time = 0
detection_active = False

# Initialize mediapipe components
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Drawing specification
my_drawing_specs = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)

# EAR parameters and frame count threshold
EAR_THRESHOLD = 0.20
EAR_CONSEC_FRAMES = 50

# Eye landmark indices
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

# CSV logging setup
log_filename = "drowsiness_log.csv"
if not os.path.exists(log_filename):
    with open(log_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "EAR", "Status"])

# For Laptop webcam usage use "0" index
cap = cv2.VideoCapture(0)

def calculate_ear(landmarks, eye_indices, image_w, image_h):
    def get_point(index):
        point = landmarks[index]
        return int(point.x * image_w), int(point.y * image_h)
    
    p1, p2 = get_point(eye_indices[1]), get_point(eye_indices[5])
    p3, p4 = get_point(eye_indices[2]), get_point(eye_indices[4])
    p5, p6 = get_point(eye_indices[0]), get_point(eye_indices[3])

    vertical_1 = math.dist(p1, p2)
    vertical_2 = math.dist(p3, p4)
    horizontal = math.dist(p5, p6)

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear

def process_frame(image):
    global frame_counter, status, avg_ear, alert_active, last_alert_time, plot_frame
    
    # Flip and convert to RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image
    results = face_mesh.process(rgb_image)

    # Draw landmarks only if it's detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # EAR Calculation
            landmarks = face_landmarks.landmark
            image_h, image_w, _ = image.shape

            left_ear = calculate_ear(landmarks, LEFT_EYE_INDICES, image_w, image_h)
            right_ear = calculate_ear(landmarks, RIGHT_EYE_INDICES, image_w, image_h)
            avg_ear = (left_ear + right_ear) / 2.0

            # Update plot data
            plot_frame += 1
            ear_values.append(avg_ear)
            timestamps.append(plot_frame)

            # Drowsiness detection
            if avg_ear < EAR_THRESHOLD:
                frame_counter += 1
                if frame_counter >= EAR_CONSEC_FRAMES:
                    status = "DROWSY"
                    alert_active = True
                    last_alert_time = time.time()
                    
                    # Save image
                    filename = f'drowsy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                    cv2.imwrite(filename, image)

                    # Save logs
                    with open(log_filename, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now(), round(avg_ear, 2), status])
            else:
                frame_counter = 0
                status = "AWAKE"
                if time.time() - last_alert_time > 3:  # Clear alert after 3 seconds
                    alert_active = False

            # Draw landmarks and text
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=my_drawing_specs
            )

            # Draw eye points
            for index in LEFT_EYE_INDICES:
                point = face_landmarks.landmark[index]
                x = int(point.x * image.shape[1])
                y = int(point.y * image.shape[0])
                cv2.circle(image, (x, y), 2, (0, 255, 255), -1)

            for index in RIGHT_EYE_INDICES:
                point = face_landmarks.landmark[index]
                x = int(point.x * image.shape[1])
                y = int(point.y * image.shape[0])
                cv2.circle(image, (x, y), 2, (0, 255, 255), -1)

            # Display EAR and status
            # cv2.putText(image, f'EAR: {avg_ear:.2f}', (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # cv2.putText(image, f'Status: {status}', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if status == "DROWSY" else (0, 255, 0), 2)
            
            # Display alert if active
            # if alert_active:
            #     cv2.putText(image, "DROWSINESS ALERT!", (30, 110), 
            #                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
    else:
        # No face detected
        avg_ear = 0.0
        status = "NO FACE"
        cv2.putText(image, "No face detected", (30, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return image

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            if detection_active:
                processed_frame = process_frame(frame)
            else:
                # Show standby screen
                processed_frame = cv2.flip(frame, 1)
                cv2.putText(processed_frame, "Detection Inactive", (30, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(processed_frame, "Click 'Start Detection' to begin", (30, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def get_data():
    global ear_values, timestamps, status, avg_ear, alert_active, detection_active
    return jsonify({
        'ear_values': list(ear_values),
        'timestamps': list(timestamps),
        'status': status,
        'current_ear': avg_ear,
        'alert_active': alert_active,
        'threshold': EAR_THRESHOLD,
        'detection_active': detection_active
    })

@app.route('/toggle_detection', methods=['POST'])
def toggle_detection():
    global detection_active, status, frame_counter, alert_active, ear_values, timestamps, plot_frame
    
    detection_active = not detection_active
    
    if detection_active:
        # Reset values when detection starts
        status = "STARTING"
        frame_counter = 0
        alert_active = False
        ear_values.clear()
        timestamps.clear()
        plot_frame = 0
        return jsonify({"status": "Detection started", "detection_active": True})
    else:
        status = "READY"
        return jsonify({"status": "Detection stopped", "detection_active": False})

def sound_alert():
    while True:
        if alert_active and detection_active:
            winsound.Beep(1000, 500)
        time.sleep(1)

if __name__ == '__main__':
    # Start sound alert
    threading.Thread(target=sound_alert, daemon=True).start()
    app.run(debug=True, threaded=True)