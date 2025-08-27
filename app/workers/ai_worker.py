import asyncio
from app.services import ai_model, uart

queue = asyncio.Queue(maxsize=1)

async def ai_worker():
    """
    Worker dự đoán hành động và gửi command qua UART
    """
    print("AI worker started")
    previous_label = "nocommand"
    while True:
        feat = await queue.get()
        try:
            label, prob = ai_model.predict_action(feat)
            if uart.is_serial_connected() and label is not None:
                if(previous_label != label and prob > 0.8 ):
                    previous_label = label
                    if(label != "nocommand"):
                        asyncio.create_task(uart.send_command_async(label))
        except Exception as e:
            print("Predict error:", e)
        finally:
            queue.task_done()