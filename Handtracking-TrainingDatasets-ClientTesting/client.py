### SPAGHETTI CODE ###
# This code captures video from the webcam, extracts hand landmarks using Mediapipe,
# and sends the processed 42D feature vectors to a WebSocket server asynchronously.
# It uses threading to separate video capture and feature extraction from network communication.
# The feature vectors are normalized based on the wrist position and scale.
# The client continuously sends the latest feature vector to the server and prints any responses received.

# Note: Ensure that the WebSocket server is running and accessible at SERVER_URL before executing this client code.
# Press 'q' to quit the video window.

# JUST A TEST CLIENT CODE, NOT PRODUCTION READY

import cv2
import numpy as np
import mediapipe as mp
import asyncio
import websockets
import threading
import queue
import time

SERVER_URL = "ws://localhost:8000/api/ws/video"

# ================= Mediapipe setup =================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

feature_queue = queue.Queue(maxsize=1)

def extract_features(frame):
    """Trích xuất vector 42D từ frame với chuẩn hóa wrist + scale"""
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0]
        
        coords = np.array([[p.x, p.y] for p in lm.landmark], dtype=np.float32)

        wrist = coords[0]
        coords -= wrist

        max_dist = np.linalg.norm(coords, axis=1).max()
        if max_dist > 0:
            coords /= max_dist

        return coords.flatten()
    else:
        return np.zeros(42, dtype=np.float32)  

# ================= Thread A: Capture & Feature Extraction =================
def camera_thread():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        feat = extract_features(frame)

        if not feature_queue.empty():
            try:
                feature_queue.get_nowait()  
            except queue.Empty:
                pass
        feature_queue.put_nowait(feat.tolist())

        cv2.imshow("Client", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# ================= Thread B: Async WebSocket =================
async def send_features():
    async with websockets.connect(SERVER_URL) as ws:
        while True:
            try:
                feat = feature_queue.get_nowait()  
            except queue.Empty:
                await asyncio.sleep(0.005)  
                continue

            arr = np.array(feat, dtype=np.float32)
            await ws.send(arr.tobytes())
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=0.01)
                print("Server:", response)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.033)

# ================= Main =================
if __name__ == "__main__":
    t = threading.Thread(target=camera_thread, daemon=True)
    t.start()
    asyncio.run(send_features())
