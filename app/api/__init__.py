import asyncio
from fastapi import APIRouter
from app.services import uart
from app.workers.ai_worker import ai_worker
from app.workers.uart_worker import uart_worker
from app.api import routes

router = APIRouter()
router.include_router(routes.router)

uart.init_uart()
uart.start_read_thread()

workers_started = False
@router.on_event("startup")
async def startup_event():
    """
    Start background workers on startup
    Input: 
        None
    Output: 
        None
    """
    global workers_started
    if not workers_started:
        uart.event_loop = asyncio.get_running_loop() 
        asyncio.create_task(ai_worker())
        asyncio.create_task(uart_worker())
        workers_started = True
