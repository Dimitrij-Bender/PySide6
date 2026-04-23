from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


class MockGPIO:
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    HIGH = 1
    LOW = 0

    def __init__(self) -> None:
        self.modes: Dict[int, str] = {}
        self.values: Dict[int, int] = {}

    def setmode(self, mode: str) -> None:
        self.mode = mode

    def setup(self, pin: int, mode: str, pull_up_down: str | None = None) -> None:
        self.modes[pin] = mode
        if mode == self.OUT:
            self.values[pin] = self.LOW
        else:
            self.values.setdefault(pin, self.HIGH)

    def input(self, pin: int) -> int:
        return self.values.get(pin, self.HIGH)

    def output(self, pin: int, value: int) -> None:
        self.values[pin] = value

    def cleanup(self) -> None:
        self.modes.clear()
        self.values.clear()


@dataclass
class GPIOPins:
    inputs: Dict[str, int]
    outputs: Dict[str, int]
    active_low_inputs: bool = True


class GPIOBackend:
    def __init__(self, pins: GPIOPins, allow_mock: bool = True) -> None:
        self.pins = pins
        try:
            import RPi.GPIO as GPIO  # type: ignore
            self.GPIO = GPIO
            self.is_mock = False
        except Exception:
            if not allow_mock:
                raise
            self.GPIO = MockGPIO()
            self.is_mock = True
        self.GPIO.setmode(self.GPIO.BCM)
        for _, pin in self.pins.inputs.items():
            self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        for _, pin in self.pins.outputs.items():
            self.GPIO.setup(pin, self.GPIO.OUT)
            self.GPIO.output(pin, self.GPIO.LOW)

    def read_input(self, name: str) -> bool:
        raw = self.GPIO.input(self.pins.inputs[name])
        if self.pins.active_low_inputs:
            return raw == self.GPIO.LOW
        return raw == self.GPIO.HIGH

    def write_output(self, name: str, enabled: bool) -> None:
        self.GPIO.output(self.pins.outputs[name], self.GPIO.HIGH if enabled else self.GPIO.LOW)

    def all_outputs_off(self) -> None:
        for name in self.pins.outputs:
            self.write_output(name, False)

    def set_mock_input(self, name: str, active: bool) -> None:
        if not self.is_mock:
            return
        pin = self.pins.inputs[name]
        if self.pins.active_low_inputs:
            self.GPIO.values[pin] = self.GPIO.LOW if active else self.GPIO.HIGH
        else:
            self.GPIO.values[pin] = self.GPIO.HIGH if active else self.GPIO.LOW
