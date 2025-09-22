"""
Project: Serial_to_CSV
File: serial_handler.py
Created: 22.09.2025 13:58
"""
import serial
import threading
import time

class SerialHandler:
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.data_callback = None  # function to call with new CSV lines

    def start(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
        self.running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

    def _read_loop(self):
        while self.running:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                if line and self.data_callback:
                    self.data_callback(line)
            else:
                time.sleep(0.01)

    def set_callback(self, callback):
        self.data_callback = callback
