from fastapi import FastAPI, WebSocket
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import mediapipe as mp
from collections import deque
import json
# FastAPI app initialization
app = FastAPI()


# MediaPipe Pose and Face Mesh Setup
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
pose_detector = mp_pose.Pose()
face_tracker = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
draw_utils = mp.solutions.drawing_utils

# Sensitivity constants
SENSITIVITY_CHIN = 0.125
SENSITIVITY_TURN = 0.03
FRAME_BUFFER_SIZE = 25  # Number of frames to keep track of
ALERT_THRESHOLD = 10    # Minimum slouching frames required to trigger alert

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

# WebSocket endpoint for real-time posture monitoring
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    try:
        while True:
            # Receive the image data from the client
            data = await websocket.receive_text()
            header, encoded = data.split(",", 1)
            img_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(img_data))

            # Convert the image to a format suitable for processing with OpenCV
            img_rgb = np.array(image)
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            # Check slouching and head turn conditions
            slouching_chin = check_slouch(img_rgb)
            slouching_turn = check_head_turn(img_rgb)

            # Record whether the current frame indicates slouching
            slouching = slouching_chin or slouching_turn
            slouch_buffer.append(slouching)

            # Count how many of the last 25 frames indicate slouching
            slouch_count = sum(slouch_buffer)

            # Send the sound play instruction and frame to the frontend
            play_sound = slouch_count >= ALERT_THRESHOLD
            print(play_sound)
            frame = base64.b64encode(cv2.imencode('.jpg', img_rgb)[1]).decode('utf-8')

            # Send the data as a JSON object
            message = {
                "play_sound": bool(play_sound),
            }
            await websocket.send_text(json.dumps(message))  # Use json.dumps() to convert the message to a string


    except Exception as e:
        print("WebSocket error:", e)
    finally:
        print("Client disconnected")
        await websocket.close()

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
