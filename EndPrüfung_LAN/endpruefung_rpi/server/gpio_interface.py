from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

@dataclass
class GPIOPins:
    inputs: Dict[str, int]
    outputs: Dict[str, int]
    active_low_inputs: bool = True

class GPIOBackend:
    """GPIO-Backend mit echter BCM-Belegung und Mock-Fallback."""
    def __init__(self, pins: GPIOPins, allow_mock: bool = True) -> None:
        self.pins = pins
        self.mock = False
        self._mock_inputs = {name: False for name in pins.inputs}
        self._mock_outputs = {name: False for name in pins.outputs}
        try:
            import RPi.GPIO as GPIO  # type: ignore
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            pud = GPIO.PUD_UP if pins.active_low_inputs else GPIO.PUD_DOWN
            for pin in pins.inputs.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=pud)
            for pin in pins.outputs.values():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        except Exception:
            if not allow_mock:
                raise
            self.mock = True
            self.GPIO = None

    def read_input(self, name: str) -> bool:
        if self.mock:
            return self._mock_inputs.get(name, False)
        raw = bool(self.GPIO.input(self.pins.inputs[name]))
        return (not raw) if self.pins.active_low_inputs else raw

    def write_output(self, name: str, value: bool) -> None:
        if self.mock:
            self._mock_outputs[name] = bool(value)
            return
        self.GPIO.output(self.pins.outputs[name], self.GPIO.HIGH if value else self.GPIO.LOW)

    def all_outputs_off(self) -> None:
        for name in self.pins.outputs:
            self.write_output(name, False)
