import numpy as np
import json
from collections import deque
from tensorflow.keras.models import load_model
from fastapi import APIRouter, WebSocket

router = APIRouter()

# Load model
MODEL_PATH = "action_gru_model.h5"
ACTIONS = ["nocommand", "swipeleft", "swiperight"]

model = load_model(MODEL_PATH)
_, TIMESTEPS, FEATURES = model.input_shape
seq_buffer = deque(maxlen=TIMESTEPS)

@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")

    try:
        while True:
            msg = await websocket.receive_text()
            feat = np.array(json.loads(msg), dtype=np.float32)

            seq_buffer.append(feat)

            pred_label, pred_prob = None, 0.0
            if len(seq_buffer) == TIMESTEPS:
                x = np.expand_dims(np.asarray(seq_buffer, dtype=np.float32), axis=0)
                pred = model.predict(x, verbose=0)[0]
                pred_idx = int(np.argmax(pred))
                pred_label = ACTIONS[pred_idx]
                pred_prob = float(np.max(pred))

            await websocket.send_text(json.dumps({
                "label": pred_label,
                "prob": pred_prob
            }))

    except Exception as e:
        print("Connection closed:", e)
