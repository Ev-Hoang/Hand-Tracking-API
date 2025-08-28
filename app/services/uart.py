import serial
import threading
import asyncio

# ===================== CONFIG =====================
UART_PORT = "COM4"
UART_BAUDRATE = 115200
UART_TIMEOUT = 1  

# ===================== GLOBALS =====================
ser = None
uart_rx_queue = asyncio.Queue()  
_read_thread = None
_stop_thread = False

# ===================== INIT UART =====================
def init_uart(port=UART_PORT, baudrate=UART_BAUDRATE, timeout=UART_TIMEOUT):
    """
    Initialize UART connection
    Input:
        port    : str
        baudrate: int
        timeout : int (seconds)
    Output:
        None
    """
    global ser
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"[UART] Connection Successful {port}@{baudrate}")
    except serial.SerialException as e:
        ser = None
        print(f"[UART] Connection Failed: {e}")

# ===================== CHECK CONNECT =====================
def is_serial_connected():
    """
        Check if UART is connected
    """
    return ser is not None and ser.is_open

# ===================== SEND COMMAND =====================
def send_command(command: str):
    """
    Send command via UART
    Input:
        command: str
    Output:
        None
    """
    if not is_serial_connected():
        print("[UART] Cannot Send! (Havent connect to COM port)")
        return
    msg = (command + "\n").encode()
    ser.write(msg)

async def send_command_async(command: str):
    await asyncio.to_thread(send_command, command)

# ===================== READ THREAD =====================
def _uart_read_loop():
    """
    Thread loop read UART simultaneously
    Input:
        None
    Output:
        None
    """
    global event_loop
    global _stop_thread
    while not _stop_thread and is_serial_connected():
        try:
            data = ser.readline() 
            if data and event_loop is not None:
                asyncio.run_coroutine_threadsafe(uart_rx_queue.put(data), event_loop)
        except Exception as e:
            print(f"[UART] Read error: {e}")
            break

def start_read_thread():
    """
    Start thread to read UART
    Input:
        None
    Output:
        None
    """
    global _read_thread, _stop_thread
    if _read_thread is None or not _read_thread.is_alive():
        _stop_thread = False
        _read_thread = threading.Thread(target=_uart_read_loop, daemon=True)
        _read_thread.start()
        print("[UART] Read thread started")

def stop_read_thread():
    """
    Stop thread reading UART
    Input:
        None
    Output:
        None
    """
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