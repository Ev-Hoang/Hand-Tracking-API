from fastapi import APIRouter, WebSocket
from app.services import ai_model, uart
from app.schemas.predict import PredictionResponse
from fastapi.responses import JSONResponse

import numpy as np
import cv2

router = APIRouter()

@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")

    try:
        while True:
            # Nhận bytes từ client
            data = await websocket.receive_bytes()

            # Chuyển bytes -> numpy array -> ảnh
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # Xử lý AI model ở đây (demo: chỉ hiển thị frame)
                prediction = ai_model.predict(frame)
                
                cv2.imshow("Received", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except Exception as e:
        print("Client disconnected:", e)
    finally:
        cv2.destroyAllWindows()
