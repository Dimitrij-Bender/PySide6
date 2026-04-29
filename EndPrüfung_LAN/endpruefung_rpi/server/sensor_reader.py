from __future__ import annotations

import random

try:
    import board  # type: ignore
    import busio  # type: ignore
    import adafruit_ads1x15.ads1115 as ADS  # type: ignore
    from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore
    ADS_AVAILABLE = True
except ModuleNotFoundError:
    ADS_AVAILABLE = False


class PositionReader:
    def __init__(self):
        self.mock_position = 0.0

        if ADS_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.ads = ADS.ADS1115(i2c)
                self.chan = AnalogIn(self.ads, ADS.P0)
                self.source = "ADS1115"
            except Exception as exc:
                print(f"WARNUNG: ADS1115 nicht verfügbar, Mock aktiv: {exc}")
                self.chan = None
                self.source = "mock"
        else:
            print("WARNUNG: ADS1115 Bibliotheken nicht gefunden. Positionssensor läuft im MOCK-Modus.")
            self.chan = None
            self.source = "mock"

    def read_position(self) -> float:
        if self.chan is None:
            self.mock_position += random.uniform(-0.3, 0.3)
            return round(self.mock_position, 3)

        voltage = float(self.chan.voltage)

        # Beispiel: 0-10 V entspricht 0-500 mm.
        # ACHTUNG: ADS1115 darf nicht direkt 10 V bekommen!
        # Nur über Spannungsteiler/Signalwandler.
        return round((voltage / 10.0) * 500.0, 3)


_reader = PositionReader()


def read_position() -> float:
    return _reader.read_position()


def position_source() -> str:
    return _reader.source
