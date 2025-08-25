import cv2
import numpy as np
import asyncio
from fastapi import APIRouter, WebSocket
from app.services import ai_model, uart



router = APIRouter()

# Queue chỉ giữ 1 feature mới nhất
queue = asyncio.Queue(maxsize=1)


uart.init_uart()
uart.start_read_thread()

# Async worker đọc dữ liệu từ UART
async def uart_worker():
    print("UART worker started")
    while True:
        data = await uart.uart_rx_queue.get()
        uart.data_received(data)
        uart.uart_rx_queue.task_done()

# Worker chạy predict liên tục
async def ai_worker():
    print("AI worker started")
    while True:
        feat = await queue.get()
        try:
            label, prob = ai_model.predict_action(feat)  # sync predict
            # print(f"predicted: {label}, prob: {prob:.2f}")
            if uart.is_serial_connected() and label is not None:
                asyncio.create_task(uart.send_command_async(label))
        except Exception as e:
            print("Predict error:", e)
        finally:
            queue.task_done()

# Tạo task worker khi server start
workers_started = False
@router.on_event("startup")
async def startup_event():
    global workers_started
    if not workers_started:
        uart.event_loop = asyncio.get_running_loop() 
        asyncio.create_task(ai_worker())
        asyncio.create_task(uart_worker())
        workers_started = True



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

# CONCLUSOIN : CODE HAVE A PROBLEM , CANT READ DATA FROM UART (uart.py)
