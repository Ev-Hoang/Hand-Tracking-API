from fastapi import APIRouter, UploadFile, File
from app.services import ai_model, uart
from app.schemas.predict import PredictionResponse
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import numpy as np

router = APIRouter()

@router.post("/upload_frame/")
async def upload_frame(file: UploadFile = File(...)):
    # Đọc dữ liệu ảnh
    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes))

    # Convert sang numpy (giống như OpenCV dùng)
    frame = np.array(image)

    # 👉 Ở đây bạn xử lý AI hoặc gửi UART sang STM32
    # ví dụ:
    # command = ai_model.predict(frame)
    # send_uart(command)

    return JSONResponse({"status": "ok", "shape": frame.shape})
