import serial

PORT = 'COM3'       # Update as needed
BAUD_RATE = 9600

def main():
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        print(f"[INFO] Listening on {PORT} (Transparent Mode)...\n")

        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"[RECV] {line}")
            except KeyboardInterrupt:
                print("\n[INFO] Stopped by user.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == '__main__':
    main()
