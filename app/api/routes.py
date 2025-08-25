import numpy as np
import asyncio
from fastapi import APIRouter, WebSocket
from app.workers.ai_worker import queue

router = APIRouter()

@router.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    """
    WebSocket endpoint to receive video frames and extract features
    Input: 
        None
    Output: 
        None
    """
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
