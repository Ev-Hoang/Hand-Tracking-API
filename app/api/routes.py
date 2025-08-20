import cv2
import numpy as np
import asyncio
from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")

    try:
        while True:
            data = await websocket.receive_bytes()

            # decode frame
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # 👉 xử lý AI nên để vào thread pool, tránh chặn loop
                # prediction = await predict_async(frame)

                # thay vì imshow, trả về JSON cho client
                await websocket.send_json({"status": "ok", "shape": frame.shape})

            # nghỉ 1 tí để nhường CPU cho event loop
            await asyncio.sleep(0)

    except Exception as e:
        print("Client disconnected:", e)
