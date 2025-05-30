from fastapi import FastAPI, WebSocket
import base64
import numpy as np
import cv2
import mediapipe as mp
from collections import deque, defaultdict
import json
import uuid
import asyncio
from contextlib import contextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socket

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ safest for VSCode extension calls
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

SENSITIVITY_CHIN = 0.125 
SENSITIVITY_TURN = 0.03
FRAME_BUFFER_SIZE = 25
ALERT_THRESHOLD = 12  
MAX_FRAME_SIZE = 1_000_000  

frame_queue = asyncio.Queue()
user_connections = {}  # user_id: websocket
user_buffers = defaultdict(lambda: deque(maxlen=FRAME_BUFFER_SIZE))

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
    user_id = str(uuid.uuid4())
    user_connections[user_id] = websocket
    print(f"Client {user_id} connected")
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                frame_str = data.get("data")
                if not frame_str or len(frame_str) > MAX_FRAME_SIZE:
                    continue
                sensitivity = float(data.get("sensitivity", 1.0))
                head_tilt = bool(data.get("HeadTilt", True))
                await frame_queue.put((user_id, frame_str, sensitivity, head_tilt))
            except:
                continue
    except:
        print(f"Client {user_id} disconnected")
    finally:
        user_connections.pop(user_id, None)

@app.on_event("startup")
async def start_worker():
    asyncio.create_task(frame_processor())

async def frame_processor():
    with mediapipe_context() as (pose_detector, face_tracker):
        while True:
            user_id, frame_str, intensity, head_tilt = await frame_queue.get()
            try:
                header, encoded = frame_str.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                img_rgb = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img_rgb is None:
                    continue
                slouch_chin = check_slouch(img_rgb, intensity, pose_detector, face_tracker)
                slouch_turn = check_head_turn(img_rgb, intensity, face_tracker)
                slouching = (slouch_chin or slouch_turn) if head_tilt else slouch_chin

                user_buffers[user_id].append(slouching)
                play_sound = sum(user_buffers[user_id]) >= ALERT_THRESHOLD

                if user_id in user_connections:
                    await user_connections[user_id].send_text(json.dumps({"play_sound": bool(play_sound)}))
            except Exception as e:
                print(f"Error processing frame for user {user_id}: {e}")

if __name__ == "__main__":
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    port = find_free_port()
    print(f"PORT:{port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)