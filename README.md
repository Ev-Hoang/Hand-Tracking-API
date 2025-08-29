# Hand-Tracking API
An API model to predict hand movement, and can send to STM32 through COM-Serial.

## Overview
This project provides:
- Hand action recognition using **MediaPipe** and **TensorFlow/Keras**.
- Image processing with **OpenCV**.
- Backend server built with **FastAPI** and **WebSocket** for real-time communication.
- UART communication support via **pyserial**.

## Requirements
- Python 3.11
- Conda (Anaconda or Miniconda recommended)
- GPU (optional, for TensorFlow acceleration)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Hand-Tracking-API.git
cd Hand-Tracking-API

conda env create -f environment.yml

conda activate handtracking-env

python -m ipykernel install --user --name=handtracking-env --display-name "Python (handtracking-env)"
```
 or you can just run the .bat file, will automatically run the bash for you :)

## Setup

### 1. Run the API server
```bash
uvicorn app.main:app --reload
```

2. Access the API
```bash
REST API endpoint: http://127.0.0.1:8000
WebSocket endpoint: ws://127.0.0.1:8000/ws
```

4. Model path
The trained model is stored under:

```bash
HandTracking-TrainingDataset-TestingClient/action_gru_model.h5
```

You can load it in your code with:

```python
MODEL_PATH = "HandTracking-TrainingDataset-TestingClient/action_gru_model.h5"
```

## Development Notes
Use conda to manage dependencies and isolate environments.
Use pip for packages not available in Conda (e.g., mediapipe).

- If you want use your own data set, with own command, follow the .ipynb file in HandTracking-TrainingDatasets-ClientTesting/ or import your datasets and modily the numpy reading function to train.
- You can create another method to send hand features through API, using the same websocket endpoint!
- Instead of COM-Serial to STM32, u can connect another device with COM-Serial Endpoint and modily the command code, or modify inside API-CODE to send whatever you prefer.

Keep the model file (.h5) inside the HandTracking-TrainingDataset-TestingClient/ directory for consistency.
