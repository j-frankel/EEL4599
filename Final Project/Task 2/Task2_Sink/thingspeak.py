from digi.xbee.devices import XBeeDevice
import serial
import requests
import time
from dotenv import load_dotenv
import os

PORT = 'COM3'
BAUD_RATE = 9600
load_dotenv()
API_KEY = os.getenv("THINGSPEAK_API_KEY")
THINGSPEAK_URL = 'https://api.thingspeak.com/update'

imu_data = {'ax': None, 'ay': None, 'az': None, 'gx': None, 'gy': None, 'gz': None}
ultrasonic = None

def send_to_thingspeak():
    payload = {
        'api_key': API_KEY,
        'field1': imu_data['ax'],
        'field2': imu_data['ay'],
        'field3': imu_data['az'],
        'field4': imu_data['gx'],
        'field5': imu_data['gy'],
        'field6': imu_data['gz'],
        'field7': ultrasonic
    }
    try:
        r = requests.post(THINGSPEAK_URL, params=payload)
        print(f"[SEND] {payload} -> Status {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed to send to ThingSpeak: {e}")

def main():
    global ultrasonic
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        print(f"[INFO] Listening on {PORT} (Transparent Mode)...\n")

        last_post_time = 0
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue

                print(f"[RECV] {line}")
                parts = line.split(',')

                if parts[0] == 'ESP' and len(parts) == 7:
                    imu_data['ax'] = parts[1]
                    imu_data['ay'] = parts[2]
                    imu_data['az'] = parts[3]
                    imu_data['gx'] = parts[4]
                    imu_data['gy'] = parts[5]
                    imu_data['gz'] = parts[6]

                elif parts[0] == 'PICO' and len(parts) == 2:
                    ultrasonic = parts[1]

                # send to ThingSpeak every 15 seconds
                if time.time() - last_post_time > 15:
                    send_to_thingspeak()
                    last_post_time = time.time()

            except KeyboardInterrupt:
                print("\n[INFO] Stopped by user.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == '__main__':
    main()
