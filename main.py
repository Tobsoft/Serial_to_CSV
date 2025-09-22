"""
Project: Serial_to_CSV
File: main.py
Created: 22.09.2025 13:57
"""

from serial_handler import SerialHandler
from serial_gui import CSVLoggerTrainer

def main():
    serial_port = "COM3"  # Change to your ESP32 port
    serial_handler = SerialHandler(port=serial_port, baudrate=115200)
    serial_handler.start()

    app = CSVLoggerTrainer(serial_handler)
    app.mainloop()

    serial_handler.stop()

if __name__ == "__main__":
    main()
