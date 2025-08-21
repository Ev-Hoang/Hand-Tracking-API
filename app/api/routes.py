import cv2
import numpy as np
import asyncio
from fastapi import APIRouter, WebSocket
from app.services import ai_model, uart



router = APIRouter()

# Queue chỉ giữ 1 feature mới nhất
queue = asyncio.Queue(maxsize=1)

# Worker chạy predict liên tục
async def worker():
    while True:
        feat = await queue.get()
        try:
            label, prob = ai_model.predict_action(feat)  # sync predict
            print(f"predicted: {label}, prob: {prob:.2f}")
            uart.send_command(label)
        except Exception as e:
            print("Predict error:", e)
        finally:
            queue.task_done()

# Tạo task worker khi server start
@router.on_event("startup")
async def startup_event():
    asyncio.create_task(worker())


@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")
    try:
        while True:
            msg = await websocket.receive()
            if "bytes" in msg:
                feat = np.frombuffer(msg["bytes"], dtype=np.float32)

                # Nếu queue đầy, bỏ frame cũ đi
                if queue.full():
                    try:
                        _ = queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        pass

                await queue.put(feat)

    except Exception as e:
        print("Client disconnected:", e)

