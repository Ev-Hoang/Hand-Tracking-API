import serial

# cấu hình UART
try:
    ser = serial.Serial("COM5", 115200, timeout=1)
except serial.SerialException as e:
    ser = None
    print(f"[UART] Không thể mở cổng: {e}")

def send_command(command: str):
    msg = (command + "\n").encode()
    ser.write(msg)

def is_serial_connected() -> bool:
    global ser
    return ser is not None and ser.is_open