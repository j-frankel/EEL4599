from digi.xbee.devices import XBeeDevice

PORT = 'COM3'       # Update as needed
BAUD_RATE = 9600

def main():
    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()
        print(f"[INFO] Listening on {PORT} (API Mode)...\n")

        def data_received_callback(xbee_message):
            payload = xbee_message.data.decode('utf-8').strip()
            print(f"[RECV] {payload}")

        device.add_data_received_callback(data_received_callback)
        input("[INFO] Press Enter to stop...\n")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    main()
