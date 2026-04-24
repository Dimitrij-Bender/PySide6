from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Burster7281Config:
    port: str
    baudrate: int = 9600
    timeout_s: float = 0.3

class Burster7281:
    def __init__(self, config: Burster7281Config) -> None:
        self.config = config
        self.ser = None
    def connect(self) -> None:
        if self.ser is not None:
            return
        import serial  # type: ignore
        self.ser = serial.Serial(self.config.port, self.config.baudrate, timeout=self.config.timeout_s)
    def enable_measurement_mode(self) -> None:
        self.connect()
        self.ser.write(b"M\r\n")
    def read_value(self) -> str:
        self.connect()
        self.ser.write(b"?\r\n")
        return self.ser.readline().decode("ascii", errors="replace").strip()
