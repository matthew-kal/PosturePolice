from fastapi import FastAPI, WebSocket
import cv2
import mediapipe as mp
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def calculate_distance(a, b):
    """Calculate the Euclidean distance between two points."""
    a = np.array(a)
    b = np.array(b)
    distance = np.linalg.norm(a - b)
    return distance

def detect_slouching(image: np.ndarray) -> bool:
    """
    Function to process the frame and detect slouching.
    Returns True if slouching is detected, False otherwise.
    """
    results = pose.process(image)
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                landmarks[mp_pose.PoseLandmark.NOSE.value].y]
        shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        shoulder_midpoint = [(shoulder_left[0] + shoulder_right[0]) / 2,
                             (shoulder_left[1] + shoulder_right[1]) / 2]

        distance = calculate_distance(nose, shoulder_midpoint)

        slouch_threshold = 0.225
        
        if distance < slouch_threshold:
            return True
    return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    try:
        while True:
            # Receive the frame from the frontend
            data = await websocket.receive_text()

            # Decode Base64 image data
            header, encoded = data.split(",", 1)  # Remove Base64 header
            img_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(img_data))
            image = np.array(image)

            # Flip the image and convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = cv2.flip(image, 1)

            # Call the detect_slouching function to check if slouching is detected
            slouching = detect_slouching(image)

            # Send the result back to the frontend
            print(slouching)
            await websocket.send_text(f"Slouching: {slouching}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Client disconnected")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#python mockserver.py to start