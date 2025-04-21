from machine import I2C, Pin
import time
import math

# MPU6050 I2C address
MPU_ADDR = 0x68

# MPU6050 Registers
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Sensitivity scale factors
ACCEL_SCALE = 16384.0  # LSB/g
GYRO_SCALE = 131.0     # LSB/(°/s)
G_TO_MS2 = 9.80665     # 1g in m/s²

# Bias values from calibration
ACCEL_BIAS = (0.49945, -0.00703, 0.03125)  # ax, ay, az in m/s²
GYRO_BIAS = (-3.60553, 1.16218, 2.40221)   # gx, gy, gz in °/s

# Initialize I2C (I2C0 on GP0=SDA, GP1=SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

# Wake up MPU6050
i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, bytes([0]))

def read_raw_data(register):
    high = i2c.readfrom_mem(MPU_ADDR, register, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, register + 1, 1)[0]
    value = (high << 8) | low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def read_mpu6050():
    # Raw accelerometer data
    ax_raw = read_raw_data(ACCEL_XOUT_H)
    ay_raw = read_raw_data(ACCEL_XOUT_H + 2)
    az_raw = read_raw_data(ACCEL_XOUT_H + 4)

    # Raw gyroscope data
    gx_raw = read_raw_data(GYRO_XOUT_H)
    gy_raw = read_raw_data(GYRO_XOUT_H + 2)
    gz_raw = read_raw_data(GYRO_XOUT_H + 4)

    # Convert to physical units and apply bias compensation
    ax = (ax_raw / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[0]
    ay = (ay_raw / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[1]
    az = (az_raw / ACCEL_SCALE) * G_TO_MS2 - ACCEL_BIAS[2]

    gx = (gx_raw / GYRO_SCALE) - GYRO_BIAS[0]
    gy = (gy_raw / GYRO_SCALE) - GYRO_BIAS[1]
    gz = (gz_raw / GYRO_SCALE) - GYRO_BIAS[2]

    return {
        "accel": (ax, ay, az),  # m/s²
        "gyro": (gx, gy, gz)    # °/s
    }

# Example loop
while True:
    data = read_mpu6050()
    ax, ay, az = data["accel"]
    gx, gy, gz = data["gyro"]

    print(f"Accel (m/s^2): X={ax:.2f}, Y={ay:.2f}, Z={az:.2f}")
    print(f"Gyro  (deg/s): X={gx:.2f}, Y={gy:.2f}, Z={gz:.2f}")
    print("-" * 50)
    time.sleep(0.5)
