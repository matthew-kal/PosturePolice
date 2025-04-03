from fastapi import FastAPI, WebSocket
import cv2
import mediapipe as mp
import numpy as np
import base64
import time
from io import BytesIO
from PIL import Image

app = FastAPI()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Default slouch tracking variables
slouch_start_time = None
slouching_detected = False

def calculate_distance(a, b):
    """Calculate the Euclidean distance between two points."""
    return np.linalg.norm(np.array(a) - np.array(b))

def detect_slouching(image: np.ndarray) -> bool:
    """Detect slouching using nose-to-shoulder distance."""
    results = pose.process(image)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                landmarks[mp_pose.PoseLandmark.NOSE.value].y]
        shoulders = [(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x +
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) / 2,
                     (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2]
        return calculate_distance(nose, shoulders) < 0.225
    return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global slouch_start_time, slouching_detected

    await websocket.accept()
    print("Client connected")

    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            try:
                _, encoded = data.split(",", 1)  # Ensure proper Base64 format
                img_bytes = base64.b64decode(encoded)
                image = Image.open(BytesIO(img_bytes)).convert("RGB")  # Ensure it's RGB
                image = np.array(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = cv2.flip(image, 1)  # Flip for correct perspective

                # Detect slouching
                slouching = detect_slouching(image)
                print(f"Slouching: {slouching}")  # ✅ Always print True/False in the terminal


                if slouching:
                    if not slouching_detected:
                        slouch_start_time = time.time()  # Start timer
                        slouching_detected = True
                    else:
                        elapsed_time = time.time() - slouch_start_time
                        if elapsed_time > 5:  # Trigger warning after 5 seconds
                            print("⚠️ Sending alert: play_sound")  # ✅ Print when sending alert
                            await websocket.send_json({"alert": "play_sound"})
                else:
                    slouching_detected = False  # Reset timer

                await websocket.send_json({"slouching": slouching})

            except Exception as e:
                print(f"Error decoding image: {e}")
                await websocket.send_json({"error": "Invalid image received"})

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Client disconnected")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)