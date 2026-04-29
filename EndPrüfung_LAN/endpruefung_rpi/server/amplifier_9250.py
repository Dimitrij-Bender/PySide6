from __future__ import annotations

import re
import time
from dataclasses import dataclass

@dataclass
class PositionReading:
    value: float
    source: str
    raw: str = ""

class MockPositionReader:
    def __init__(self, start: float = 0.0, step: float = 0.25) -> None:
        self.value = start
        self.step = step
    def read(self) -> PositionReading:
        self.value += self.step
        return PositionReading(self.value, "mock", f"{self.value:.3f}")

class Burster9250USBASCIIReader:
    """9250 über USB/seriellen COM-Port, wenn Messwerte als ASCII-Zeilen kommen."""
    def __init__(self, port: str, baudrate: int = 115200, timeout_s: float = 0.25,
                 poll_command: str = "", regex: str = r"[-+]?[0-9]+(?:[.,][0-9]+)?",
                 scale: float = 1.0, offset: float = 0.0) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout_s = timeout_s
        self.poll_command = poll_command
        self.regex = re.compile(regex)
        self.scale = scale
        self.offset = offset
        self.ser = None
    def connect(self) -> None:
        if self.ser is not None:
            return
        import serial  # type: ignore
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout_s)
        time.sleep(0.2)
        try:
            self.ser.reset_input_buffer()
        except Exception:
            pass
    def read(self) -> PositionReading:
        self.connect()
        if self.poll_command:
            cmd = self.poll_command
            if not cmd.endswith("\r") and not cmd.endswith("\n"):
                cmd += "\r\n"
            self.ser.write(cmd.encode("ascii", errors="ignore"))
        raw = self.ser.readline().decode("ascii", errors="replace").strip()
        match = self.regex.search(raw)
        if not match:
            raise ValueError(f"9250-Antwort enthält keinen Zahlenwert: {raw!r}")
        number = float(match.group(0).replace(",", "."))
        return PositionReading(number * self.scale + self.offset, "9250-usb-ascii", raw)

def build_9250_reader(cfg: dict):
    return Burster9250USBASCIIReader(
        port=cfg.get("port", "/dev/ttyACM0"),
        baudrate=int(cfg.get("baudrate", 115200)),
        timeout_s=float(cfg.get("timeout_s", 0.25)),
        poll_command=cfg.get("poll_command", ""),
        regex=cfg.get("regex", r"[-+]?[0-9]+(?:[.,][0-9]+)?"),
        scale=float(cfg.get("scale", 1.0)),
        offset=float(cfg.get("offset", 0.0)),
    )
