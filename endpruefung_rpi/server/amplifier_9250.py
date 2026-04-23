from __future__ import annotations

"""
Schnittstelle für den Messverstärker 9250.

Wichtig:
- Laut bereitgestelltem Datenblatt dient die Micro-USB-Schnittstelle sicher der
  Konfiguration via DigiVision.
- In den Unterlagen liegt jedoch KEINE belastbare Protokollbeschreibung vor,
  wie Messwerte direkt per Python über USB ausgelesen werden können.

Deshalb wird hier bewusst eine austauschbare Abstraktion bereitgestellt.
"""

from dataclasses import dataclass


@dataclass
class PositionReading:
    value: float
    unit: str = "mm"
    source: str = "mock"


class MockPositionReader:
    def __init__(self, start: float = 0.0, step: float = 0.5) -> None:
        self.value = start
        self.step = step

    def read(self) -> PositionReading:
        return PositionReading(value=self.value, unit="mm", source="mock")

    def nudge(self, direction: int) -> None:
        self.value += self.step * direction


class Burster9250USBReader:
    def __init__(self, port: str, baudrate: int = 9600) -> None:
        self.port = port
        self.baudrate = baudrate

    def read(self) -> PositionReading:
        raise NotImplementedError(
            "Für den 9250 fehlt in den bereitgestellten Unterlagen die konkrete USB-"
            "Messwertschnittstelle. Diese Klasse ist als Integrationspunkt vorbereitet."
        )
