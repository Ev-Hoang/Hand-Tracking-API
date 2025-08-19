import serial

# cấu hình UART
ser = serial.Serial("COM3", 115200, timeout=1)  # Windows
# ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)  # Linux

def send_command(command: str):
    msg = (command + "\n").encode()
    ser.write(msg)