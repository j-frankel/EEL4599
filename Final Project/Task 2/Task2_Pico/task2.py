from machine import UART, Pin, I2C
import time

# === MPU6050 Configuration ===
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
ACCEL_SCALE = 16384.0
GYRO_SCALE = 131.0
G_TO_MS2 = 9.80665

# Bias values (from calibration)
ACCEL_BIAS = (0.49945, -0.00703, 0.03125)
GYRO_BIAS = (-3.60553, 1.16218, 2.40221)

# I2C setup (MPU6050)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)
i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, b'\x00')  # Wake up MPU6050

def read_raw_data(register):
    high = i2c.readfrom_mem(MPU_ADDR, register, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, register + 1, 1)[0]
    value = (high << 8) | low
    if value >= 0x8000:
        value = -((65536 - value))
    return value

def read_mpu6050():
    ax = (read_raw_data(ACCEL_XOUT_H) / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[0]
    ay = (read_raw_data(ACCEL_XOUT_H + 2) / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[1]
    az = (read_raw_data(ACCEL_XOUT_H + 4) / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[2]

    gx = (read_raw_data(GYRO_XOUT_H) / GYRO_SCALE) - GYRO_BIAS[0]
    gy = (read_raw_data(GYRO_XOUT_H + 2) / GYRO_SCALE) - GYRO_BIAS[1]
    gz = (read_raw_data(GYRO_XOUT_H + 4) / GYRO_SCALE) - GYRO_BIAS[2]

    return ax, ay, az, gx, gy, gz

# === UART + XBee Setup ===
uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
DEST_ADDR_64 = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Replace with real address

def send_api_frame(payload: str, dest_addr: bytes):
    frame_type = 0x10
    frame_id = 0x01
    dest16 = b'\xFF\xFE'
    broadcast_radius = 0x00
    options = 0x00
    rf_data = payload.encode('utf-8')

    frame_data = (
        bytes([frame_type, frame_id]) +
        dest_addr +
        dest16 +
        bytes([broadcast_radius, options]) +
        rf_data
    )

    length = len(frame_data)
    length_bytes = length.to_bytes(2, 'big')
    checksum = 0xFF - (sum(frame_data) & 0xFF)

    full_frame = b'\x7E' + length_bytes + frame_data + bytes([checksum])
    uart.write(full_frame)

# === Main Loop ===
while True:
    ax, ay, az, gx, gy, gz = read_mpu6050()

    # Format into string, [AX, AY, AZ, GX, GY, GZ]
    msg = f"PICO,{ax:.2f},{ay:.2f},{az:.2f},{gx:.2f},{gy:.2f},{gz:.2f}"
    
    # Print message for debugging
    print("Sending:", msg)
    
    # Send via API frame
    send_api_frame(msg, DEST_ADDR_64)

    time.sleep(0.5)
