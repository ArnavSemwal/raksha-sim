import serial
import json
import time

class ESP32Reader:
    def __init__(self, port="/dev/ttyACM0", baud_rate=115200, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        print(f"Connecting to ESP32 on {self.port}...")
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Wait for ESP32 to reset after connection
            self.ser.reset_input_buffer()
            print("Connected successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to ESP32: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Disconnected from ESP32.")

    def ping(self):
        if not self.ser:
            return False
        self.ser.write(b"PING\n")
        start = time.time()
        while time.time() - start < 5:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line == "PONG":
                return True
        return False

    def send_raw_command(self, command: str):
        """
        Sends an arbitrary newline-terminated command to the ESP32 over Serial.
        Does NOT wait for any response — used for fire-and-forget commands like
        VOICE_KW:<csv> where the ESP32 simply stores the value internally.
        """
        if not self.ser:
            print(f"[WARN] send_raw_command: not connected, dropping command '{command}'")
            return
        print(f"Sending raw command: {command}")
        self.ser.write(f"{command}\n".encode('utf-8'))

    def read_sensor(self, command: str, wait_timeout: int = 75) -> dict:
        if not self.ser:
            return {"error": "Not connected"}
        
        print(f"Requesting: {command}")
        self.ser.write(f"{command}\n".encode('utf-8'))
        
        start_time = time.time()
        while True:
            if time.time() - start_time > wait_timeout:
                return {"error": f"Request {command} timed out."}
                
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) == 3:
                sensor_code, json_payload, _ = parts
                if sensor_code == "ERR":
                    return {"error": json_payload}
                else:
                    try:
                        return json.loads(json_payload)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON response"}

