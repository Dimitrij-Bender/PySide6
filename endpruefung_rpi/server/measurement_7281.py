from __future__ import annotations

import time
from dataclasses import dataclass

import serial

STX = b"\x02"
ETX = b"\x03"
ENQ = b"\x05"
ACK = b"\x06"
NAK = b"\x15"
LF = b"\x0A"
EOT = b"\x04"


@dataclass
class Burster7281Config:
    port: str
    baudrate: int = 9600
    timeout_s: float = 0.3


class Burster7281:
    def __init__(self, cfg: Burster7281Config) -> None:
        self.cfg = cfg
        self.ser: serial.Serial | None = None

    def connect(self) -> None:
        self.ser = serial.Serial(
            self.cfg.port,
            self.cfg.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.cfg.timeout_s,
            rtscts=False,
        )
        self.ser.rts = True

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _require_open(self) -> serial.Serial:
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("7281 ist nicht verbunden")
        return self.ser

    def send_command(self, command: str) -> str:
        ser = self._require_open()
        ser.reset_input_buffer()
        ser.write(STX + command.encode("ascii") + LF + ETX)
        time.sleep(0.05)
        ack = ser.read(1)
        if ack == NAK:
            raise RuntimeError(f"7281 lehnt Befehl ab: {command}")
        if ack != ACK:
            raise RuntimeError(f"7281 ACK fehlt: {ack!r}")
        ser.write(EOT)
        time.sleep(0.05)
        response = ser.read_until(EOT)
        if response.endswith(EOT):
            response = response[:-1]
        ser.write(ACK)
        return response.decode("ascii", errors="ignore").strip()

    def enable_measurement_mode(self) -> None:
        ser = self._require_open()
        ser.reset_input_buffer()
        ser.write(STX + b"DKDM!" + LF + ETX)
        time.sleep(0.05)
        ack = ser.read(1)
        if ack != ACK:
            raise RuntimeError("7281 DKDM fehlgeschlagen")
        ser.write(EOT)
        time.sleep(0.05)
        ser.write(ACK)
        _ = ser.read(1)

    def read_value(self) -> str:
        return self.send_command("WERT?")
