import numpy as np
import cv2
from collections import deque
from tensorflow.keras.models import load_model
from tensorflow.keras import layers
import mediapipe as mp

# ====== Config ======
MODEL_PATH = "action_gru_model.h5"  # thay đường dẫn model của bạn
ACTIONS = ["nocommand", "swipeleft", "swiperight"]

# Load GRU model
model = load_model(MODEL_PATH)
_, TIMESTEPS, FEATURES = model.input_shape

# Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Buffer lưu chuỗi landmark
seq_buffer = deque(maxlen=TIMESTEPS)


def extract_features(results, image_w, image_h):
    """
    Trích xuất feature vector từ kết quả Mediapipe Hands
    -> vector 42 chiều (21 điểm * (x, y))
    """
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        coords = []
        for lm in hand_landmarks.landmark:
            coords.extend([lm.x * image_w, lm.y * image_h])
        return np.array(coords, dtype=np.float32)
    else:
        # không có tay => padding zeros
        return np.zeros(FEATURES, dtype=np.float32)


def predict(frame):
    """
    Nhận 1 frame (BGR), xử lý landmark, chạy model predict
    Trả về dict {"label": str, "prob": float}
    """
    global seq_buffer

    h, w, _ = frame.shape
    # Mediapipe yêu cầu RGB
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    feat = extract_features(results, w, h)
    seq_buffer.append(feat)

    pred_label, pred_prob = None, 0.0
    if len(seq_buffer) == TIMESTEPS:
        x = np.expand_dims(np.asarray(seq_buffer, dtype=np.float32), axis=0)
        pred = model.predict(x, verbose=0)[0]
        pred_idx = int(np.argmax(pred))
        pred_label = ACTIONS[pred_idx]
        pred_prob = float(np.max(pred))

    return {
        "label": pred_label,
        "prob": pred_prob
    }
