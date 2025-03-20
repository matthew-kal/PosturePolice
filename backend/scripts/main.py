import cv2
import mediapipe as mp
import numpy as np
import pygame

pygame.mixer.init()
alert_sound = pygame.mixer.Sound("warn.mp3")

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
pose_detector = mp_pose.Pose()
face_tracker = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
draw_utils = mp.solutions.drawing_utils

SENSITIVITY_CHIN = 0.125
SENSITIVITY_TURN = 0.01

def check_slouch(img, frame):
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

def check_head_turn(img, frame):
    face_data = face_tracker.process(img)

    if not face_data.multi_face_landmarks:
        return False

    nose_x = face_data.multi_face_landmarks[0].landmark[1].x
    left_eye_x = face_data.multi_face_landmarks[0].landmark[33].x
    right_eye_x = face_data.multi_face_landmarks[0].landmark[263].x

    eye_center_x = (left_eye_x + right_eye_x) / 2
    deviation = abs(nose_x - eye_center_x)

    return deviation > SENSITIVITY_TURN


camera = cv2.VideoCapture(0)

while camera.isOpened():
    ret, frame = camera.read()
    if not ret:
        break

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    slouching_chin = check_slouch(img_rgb, frame)
    slouching_turn = check_head_turn(img_rgb, frame)

    if slouching_chin or slouching_turn:
        alert_sound.play()
        cv2.putText(frame, "Slouching!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Good Posture", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Posture Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()