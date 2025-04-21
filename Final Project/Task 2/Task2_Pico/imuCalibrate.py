from machine import I2C, Pin
import time

# MPU6050 I2C Address and Registers
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Conversion Factors
ACCEL_SCALE = 16384.0  # LSB/g
GYRO_SCALE = 131.0     # LSB/(°/s)
G_TO_MS2 = 9.80665     # 1g = 9.80665 m/s²

# Initialize I2C (default I2C0: SDA=GP0, SCL=GP1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

# Wake up MPU6050
i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, bytes([0]))

def read_raw_data(register):
    high = i2c.readfrom_mem(MPU_ADDR, register, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, register + 1, 1)[0]
    value = (high << 8) | low
    if value >= 0x8000:
        value = -((65536 - value))
    return value

def read_accel_gyro():
    ax = read_raw_data(ACCEL_XOUT_H)
    ay = read_raw_data(ACCEL_XOUT_H + 2)
    az = read_raw_data(ACCEL_XOUT_H + 4)
    gx = read_raw_data(GYRO_XOUT_H)
    gy = read_raw_data(GYRO_XOUT_H + 2)
    gz = read_raw_data(GYRO_XOUT_H + 4)

    ax_ms2 = (ax / ACCEL_SCALE) * G_TO_MS2
    ay_ms2 = (ay / ACCEL_SCALE) * G_TO_MS2
    az_ms2 = (az / ACCEL_SCALE) * G_TO_MS2
    gx_dps = gx / GYRO_SCALE
    gy_dps = gy / GYRO_SCALE
    gz_dps = gz / GYRO_SCALE

    return (ax_ms2, ay_ms2, az_ms2, gx_dps, gy_dps, gz_dps)

def calibrate_mpu6050(samples=500, delay=0.005):
    print("Starting calibration... Keep the sensor flat and still.")

    sum_ax = sum_ay = sum_az = 0
    sum_gx = sum_gy = sum_gz = 0

    for _ in range(samples):
        ax, ay, az, gx, gy, gz = read_accel_gyro()
        sum_ax += ax
        sum_ay += ay
        sum_az += az
        sum_gx += gx
        sum_gy += gy
        sum_gz += gz
        time.sleep(delay)

    avg_ax = sum_ax / samples
    avg_ay = sum_ay / samples
    avg_az = sum_az / samples
    avg_gx = sum_gx / samples
    avg_gy = sum_gy / samples
    avg_gz = sum_gz / samples

    # Expect az ≈ 9.81, ax ≈ 0, ay ≈ 0 when flat
    accel_bias = (avg_ax, avg_ay, avg_az - G_TO_MS2)
    gyro_bias = (avg_gx, avg_gy, avg_gz)

    print("\nCalibration complete.")
    print("Accelerometer bias (m/s^2):")
    print("  ax_bias = {:.5f}, ay_bias = {:.5f}, az_bias = {:.5f}".format(*accel_bias))
    print("Gyroscope bias (deg/s):")
    print("  gx_bias = {:.5f}, gy_bias = {:.5f}, gz_bias = {:.5f}".format(*gyro_bias))

    return accel_bias, gyro_bias

# Run if executed directly
if __name__ == "__main__":
    calibrate_mpu6050()
