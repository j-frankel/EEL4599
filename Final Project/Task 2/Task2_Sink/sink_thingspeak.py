from digi.xbee.devices import XBeeDevice
import requests
import time
import os
from dotenv import load_dotenv

# load API key
load_dotenv()
API_KEY = os.getenv("THINGSPEAK_API_KEY")
if not API_KEY:
    raise RuntimeError("THINGSPEAK_API_KEY not found in .env")

# config
PORT = "COM3"
BAUD_RATE = 9600
THINGSPEAK_URL = "https://api.thingspeak.com/update"
POST_INTERVAL = 15     # seconds

# data storage
imu_data = {'ax': None, 'ay': None, 'az': None, 'gx': None, 'gy': None, 'gz': None}
distance = None

last_post_time = 0

def send_to_thingspeak():
    payload = {
        'api_key': API_KEY,
        'field1': imu_data['ax'],
        'field2': imu_data['ay'],
        'field3': imu_data['az'],
        'field4': imu_data['gx'],
        'field5': imu_data['gy'],
        'field6': imu_data['gz'],
        'field7': distance
    }
    try:
        r = requests.post(THINGSPEAK_URL, params=payload)
        print(f"[SEND] {payload} → Status {r.status_code}")
    except Exception as e:
        print(f"[ERROR] ThingSpeak post failed: {e}")

def handle_payload(payload: str):
    global imu_data, distance, last_post_time

    parts = payload.strip().split(',')
    if len(parts) < 2:
        return

    if parts[0] == 'PICO' and len(parts) == 7:
        imu_data['ax'] = parts[1]
        imu_data['ay'] = parts[2]
        imu_data['az'] = parts[3]
        imu_data['gx'] = parts[4]
        imu_data['gy'] = parts[5]
        imu_data['gz'] = parts[6]
        print(f"[PICO] IMU Data: {imu_data}")

    elif parts[0] == 'ESP' and len(parts) == 2:
        distance = parts[1]
        print(f"[ESP] Distance: {distance}")

    else:
        print(f"[WARN] Unknown format: {payload}")
        return

    # post if time
    if time.time() - last_post_time > POST_INTERVAL:
        send_to_thingspeak()
        last_post_time = time.time()

def main():
    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()
        print(f"[INFO] Listening for Zigbee data on {PORT} (API mode)...\n")

        def on_receive(msg):
            try:
                payload = msg.data.decode("utf-8").strip()
                print(f"[RECV] {payload}")
                handle_payload(payload)
            except UnicodeDecodeError:
                print(f"[WARN] Bad UTF-8 frame: {msg.data.hex()}")

        device.add_data_received_callback(on_receive)
        input("[INFO] Press Enter to stop...\n")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if device and device.is_open():
            device.close()

if __name__ == "__main__":
    main()
