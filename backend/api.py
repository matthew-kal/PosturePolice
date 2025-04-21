from fastapi import FastAPI, WebSocket
import base64
import numpy as np
import cv2
import mediapipe as mp
from collections import deque
import json
import time
from contextlib import contextmanager

app = FastAPI()

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

SENSITIVITY_CHIN = 0.125 
SENSITIVITY_TURN = 0.03
FRAME_BUFFER_SIZE = 25
ALERT_THRESHOLD = 17
MAX_FRAME_SIZE = 1_000_000  
MIN_FRAME_INTERVAL = 0.05  

@contextmanager
def mediapipe_context():
    pose = mp_pose.Pose()
    face = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
    try:
        yield pose, face
    finally:
        pose.close()
        face.close()

def check_slouch(img, intensity, pose_detector, face_tracker):
    pose_res = pose_detector.process(img)
    face_res = face_tracker.process(img)

    if not pose_res.pose_landmarks or not face_res.multi_face_landmarks:
        return False

    chin = np.array([
        face_res.multi_face_landmarks[0].landmark[152].x,
        face_res.multi_face_landmarks[0].landmark[152].y
    ])

    landmarks = pose_res.pose_landmarks.landmark
    left_shoulder = np.array([
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
    ])
    right_shoulder = np.array([
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
    ])

    mid_shoulder = (left_shoulder + right_shoulder) / 2
    mid_shoulder[1] -= SENSITIVITY_CHIN * intensity

    return chin[1] > mid_shoulder[1]

def check_head_turn(img, intensity, face_tracker):
    face_data = face_tracker.process(img)
    if not face_data.multi_face_landmarks:
        return False

    nose_x = face_data.multi_face_landmarks[0].landmark[1].x
    left_eye_x = face_data.multi_face_landmarks[0].landmark[33].x
    right_eye_x = face_data.multi_face_landmarks[0].landmark[263].x

    eye_center_x = (left_eye_x + right_eye_x) / 2
    deviation = abs(nose_x - eye_center_x)

    return deviation > SENSITIVITY_TURN * intensity

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    slouch_buffer = deque(maxlen=FRAME_BUFFER_SIZE)
    last_frame_time = 0

    try:
        with mediapipe_context() as (pose_detector, face_tracker):
            while True:
                raw_data = await websocket.receive_text()

                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                    continue

                frame_str = data.get("data")
                if not frame_str:
                    await websocket.send_text(json.dumps({"error": "Missing frame data"}))
                    continue

                try:
                    header, encoded = frame_str.split(",", 1)

                    # ✅ Frame size limiter
                    if len(encoded) > MAX_FRAME_SIZE:
                        await websocket.send_text(json.dumps({"error": "Frame too large"}))
                        continue

                    # ✅ Frame rate limiter
                    now = time.time()
                    if now - last_frame_time < MIN_FRAME_INTERVAL:
                        continue
                    last_frame_time = now

                    img_bytes = base64.b64decode(encoded)
                    np_arr = np.frombuffer(img_bytes, np.uint8)
                    img_rgb = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                    if img_rgb is None:
                        raise ValueError("Decoded image is None")
                except Exception as e:
                    await websocket.send_text(json.dumps({"error": f"Image decode failed: {str(e)}"}))
                    continue

                try:
                    intensity = float(data.get("sensitivity", 1.0))
                except ValueError:
                    intensity = 1.0

                try:
                    head_tilt = bool(data.get("HeadTilt", True))
                except ValueError: 
                    head_tilt = True 


                slouch_chin = check_slouch(img_rgb, intensity, pose_detector, face_tracker)
                slouch_turn = check_head_turn(img_rgb, intensity, face_tracker)
                slouching = (slouch_chin or slouch_turn) if head_tilt else slouch_chin

                slouch_buffer.append(slouching)
                play_sound = sum(slouch_buffer) >= ALERT_THRESHOLD

                await websocket.send_text(json.dumps({"play_sound": bool(play_sound)}))

    except Exception as e:
        print("WebSocket error:", e)
    finally:
        print("Client disconnected")
        await websocket.close()

# uvicorn api:app --host 0.0.0.0 --port 8000