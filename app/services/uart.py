import serial
import threading
import asyncio

# ===================== CONFIG =====================
UART_PORT = "COM3"
UART_BAUDRATE = 115200
UART_TIMEOUT = 1  # giây

# ===================== GLOBALS =====================
ser = None
uart_rx_queue = asyncio.Queue()  # queue chứa dữ liệu nhận từ UART
_read_thread = None
_stop_thread = False

# ===================== INIT UART =====================
def init_uart(port=UART_PORT, baudrate=UART_BAUDRATE, timeout=UART_TIMEOUT):
    global ser
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"[UART] Kết nối thành công {port}@{baudrate}")
    except serial.SerialException as e:
        ser = None
        print(f"[UART] Không thể mở cổng: {e}")

# ===================== CHECK CONNECT =====================
def is_serial_connected():
    return ser is not None and ser.is_open

# ===================== SEND COMMAND =====================
def send_command(command: str):
    if not is_serial_connected():
        print("[UART] Chưa kết nối UART!")
        return
    msg = (command + "\n").encode()
    ser.write(msg)

async def send_command_async(command: str):
    # Gửi UART trên thread để không block async worker
    await asyncio.to_thread(send_command, command)

# ===================== READ THREAD =====================
def _uart_read_loop():
    """Đọc dữ liệu từ UART liên tục trong một thread"""
    global event_loop
    global _stop_thread
    while not _stop_thread and is_serial_connected():
        try:
            data = ser.readline() 
            if data and event_loop is not None:
                # Đẩy dữ liệu vào async queue
                asyncio.run_coroutine_threadsafe(uart_rx_queue.put(data), event_loop)
        except Exception as e:
            print(f"[UART] Read error: {e}")
            break

def start_read_thread():
    """Khởi tạo thread đọc UART liên tục"""
    global _read_thread, _stop_thread
    if _read_thread is None or not _read_thread.is_alive():
        _stop_thread = False
        _read_thread = threading.Thread(target=_uart_read_loop, daemon=True)
        _read_thread.start()
        print("[UART] Read thread started")

def stop_read_thread():
    """Dừng thread đọc UART"""
    global _stop_thread, _read_thread
    _stop_thread = True
    if _read_thread:
        _read_thread.join()
        _read_thread = None
        print("[UART] Read thread stopped")

# ===================== DATA PROCESSING =====================
def data_received(data: bytes):
    """Xử lý dữ liệu nhận từ UART"""
    text = data.decode(errors='ignore').strip()
    if text:
        print(f"[UART] Received: {text}")

# CONCLUSION : CODE HAVE A PROBLEM , CANT READ DATA FROM UART (route.py)