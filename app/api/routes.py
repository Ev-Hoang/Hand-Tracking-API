from fastapi import APIRouter, UploadFile, File
from app.services import ai_model, uart
from app.schemas.predict import PredictionResponse

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    # đọc dữ liệu ảnh upload
    img_bytes = await file.read()

    # AI model inference
    label = ai_model.predict_image(img_bytes)

    # gửi lệnh UART xuống STM32
    uart.send_command(label)

    return {"prediction": label, "status": "sent to STM32"}
