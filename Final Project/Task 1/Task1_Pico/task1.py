from machine import UART, Pin
import time

# Initialize UART0 on GPIO 16 (TX) and 17 (RX)
uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))

# Transmit to this XBee's 64-bit address (replace with your target)
DEST_ADDR_64 = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # example address

# === Transparent Mode ===
def send_transparent(message: str):
    print("Sending transparent")
    uart.write(message + '\r\n')  # Append \r\n for readability in XCTU

# === API Mode (Transmit Request Frame) ===
def send_api_frame(payload: str, dest_addr: bytes):
    print("Sending API frame")
    frame_type = 0x10
    frame_id = 0x01
    dest16 = b'\xFF\xFE'
    broadcast_radius = 0x00
    options = 0x00
    rf_data = payload.encode('utf-8')

    # Compose frame data (not including 7E and length)
    frame_data = (
        bytes([frame_type, frame_id]) +
        dest_addr +
        dest16 +
        bytes([broadcast_radius, options]) +
        rf_data
    )

    # Compute frame length and checksum
    length = len(frame_data)
    length_bytes = length.to_bytes(2, 'big')
    checksum = 0xFF - (sum(frame_data) & 0xFF)

    # Full API frame
    full_frame = b'\x7E' + length_bytes + frame_data + bytes([checksum])
    
    #print(full_frame)
    
    uart.write(full_frame)

# === Main loop ===
while True:
    # Choose ONE:
    #send_transparent("Hello World")  # for transparent mode
    send_api_frame("Hello World", DEST_ADDR_64)  # for API mode

    time.sleep(1)
