import numpy as np
from collections import deque
from tensorflow.keras.models import load_model

# Load model
MODEL_PATH = "action_gru_model.h5"
ACTIONS = ["ACT","nocommand", "SW_L", "SW_R"]

model = load_model(MODEL_PATH)
_, TIMESTEPS, FEATURES = model.input_shape
seq_buffer = deque(maxlen=TIMESTEPS)

def predict_action(feat):
    """
    Predict action from feature sequence
    Input:
        feat : np.ndarray (42,)
        model: keras model
    Output:
        label: str hoặc None
        prob : float
    """
    seq_buffer.append(feat)

    if len(seq_buffer) == TIMESTEPS:
        x = np.expand_dims(np.asarray(seq_buffer, dtype=np.float32), axis=0)  # (1, T, 42)
        pred = model.predict(x, verbose=0)[0]  # (num_classes,)
        pred_idx = int(np.argmax(pred))
        pred_label = ACTIONS[pred_idx]
        pred_prob = float(np.max(pred))
        return pred_label, pred_prob
    else:
        return None, 0.0

