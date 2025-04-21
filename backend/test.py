import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import time

# MediaPipe Pose and Face Mesh Setup
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
pose_detector = mp_pose.Pose()
face_tracker = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
draw_utils = mp.solutions.drawing_utils

# Sensitivity constants
SENSITIVITY_CHIN = 0.125 * 1.25
SENSITIVITY_TURN = 0.03 * 1.25
FRAME_BUFFER_SIZE = 25  # Number of frames to keep track of
ALERT_THRESHOLD = 12    # Minimum slouching frames required to trigger alert
FPS = 5  # Desired frames per second

# Initialize a deque to keep track of the last 25 frames
slouch_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

# Function to check slouch based on chin position
def check_slouch(img):
    pose_res = pose_detector.process(img)
    face_res = face_tracker.process(img)

    if not pose_res.pose_landmarks or not face_res.multi_face_landmarks:
        return False

    chin = np.array([
        face_res.multi_face_landmarks[0].landmark[152].x,
        face_res.multi_face_landmarks[0].landmark[152].y
    ])

    pose_landmarks = pose_res.pose_landmarks.landmark
    left_shoulder = np.array([pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                              pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])

    right_shoulder = np.array([pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])

    mid_shoulder = (left_shoulder + right_shoulder) / 2
    mid_shoulder[1] -= SENSITIVITY_CHIN

    return chin[1] > mid_shoulder[1]

# Function to check head turn based on facial landmark deviation
def check_head_turn(img):
    face_data = face_tracker.process(img)

    if not face_data.multi_face_landmarks:
        return False

    nose_x = face_data.multi_face_landmarks[0].landmark[1].x
    left_eye_x = face_data.multi_face_landmarks[0].landmark[33].x
    right_eye_x = face_data.multi_face_landmarks[0].landmark[263].x

    eye_center_x = (left_eye_x + right_eye_x) / 2
    deviation = abs(nose_x - eye_center_x)

    return deviation > SENSITIVITY_TURN

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Set the desired frame rate
frame_interval = 1 / FPS  # Interval between frames in seconds

try:
    while cap.isOpened():
        start_time = time.time()

        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Check slouching and head turn conditions
        slouching_chin = check_slouch(img_rgb)
        slouching_turn = check_head_turn(img_rgb)

        # Record whether the current frame indicates slouching
        slouching = slouching_chin or slouching_turn
        slouch_buffer.append(slouching)

        # Count how many of the last 25 frames indicate slouching
        slouch_count = sum(slouch_buffer)
        play_sound = slouch_count >= ALERT_THRESHOLD

        # Display result on frame
        label = "Slouching Detected" if play_sound else "Good Posture"
        color = (0, 0, 255) if play_sound else (0, 255, 0)
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # Show the webcam feed
        cv2.imshow("Posture Detection", frame)

        # Maintain the desired frame rate
        elapsed_time = time.time() - start_time
        if elapsed_time < frame_interval:
            time.sleep(frame_interval - elapsed_time)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()