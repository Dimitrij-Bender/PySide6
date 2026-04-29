from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import time
import threading

from motor_control import safe_move
from sensor_reader import read_position, position_source
from gpio_backend import read_inputs, all_outputs_off


@dataclass
class PlantState:
    mode: str = "manual"
    motion: str = "stop"
    current_position: float = 0.0
    target_position: Optional[float] = None
    position_source: str = "mock"
    error_active: bool = False
    error_reason: str = ""
    last_7281_value: str = "-"


class EndpruefungController:
    def __init__(self, config=None):
        self.mode = "manual"
        self.positions: Dict[str, float] = {
            "GS_1": 0.0,
            "GS_2": 50.0,
            "GS_3": 100.0,
        }
        self.state = PlantState()
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self.worker = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        if not self.worker.is_alive():
            self.worker.start()

    def stop(self):
        self._stop_event.set()
        all_outputs_off()

    def manual_move(self, motion: str):
        with self._lock:
            self.state.mode = "manual"
            self.state.motion = motion

        if motion == "up_fast":
            return safe_move("up_fast")
        if motion == "up_slow":
            return safe_move("up_slow")
        if motion == "down_fast":
            return safe_move("down_fast")
        if motion == "down_slow":
            return safe_move("down_slow")
        return safe_move("stop")

    def stop_motion(self):
        with self._lock:
            self.state.motion = "stop"
            self.state.target_position = None
        return safe_move("stop")

    def auto_move_to(self, name: str):
        if name not in self.positions:
            raise KeyError(f"Position {name} ist nicht definiert")

        with self._lock:
            self.state.mode = "auto"
            self.state.target_position = float(self.positions[name])
            self.state.motion = "auto"

    def save_current_position(self, name: str):
        with self._lock:
            self.positions[name] = float(self.state.current_position)

    def delete_position(self, name: str):
        with self._lock:
            if name not in self.positions:
                raise KeyError(f"Position {name} ist nicht definiert")
            del self.positions[name]

    def connect_7281(self):
        with self._lock:
            self.state.last_7281_value = "7281 Mock verbunden"

    def read_7281(self):
        with self._lock:
            self.state.last_7281_value = "0.000 N"
            return self.state.last_7281_value

    def get_state(self) -> PlantState:
        with self._lock:
            self.state.current_position = float(read_position())
            self.state.position_source = position_source()

            inputs = read_inputs()
            self.state.error_active = False
            self.state.error_reason = ""

            if inputs.get("notaus"):
                self.state.error_active = True
                self.state.error_reason = "NOT-AUS"
            elif inputs.get("kraft"):
                self.state.error_active = True
                self.state.error_reason = "Kraftnebenschluss"
            elif inputs.get("limit_top") and self.state.motion in {"up_fast", "up_slow"}:
                self.state.error_reason = "Endschalter oben"
            elif inputs.get("limit_bottom") and self.state.motion in {"down_fast", "down_slow"}:
                self.state.error_reason = "Endschalter unten"

            return PlantState(**self.state.__dict__)

    def _loop(self):
        while not self._stop_event.is_set():
            state = self.get_state()

            if state.error_active:
                self.stop_motion()

            if state.motion == "auto" and state.target_position is not None:
                delta = state.target_position - state.current_position

                if abs(delta) < 1.0:
                    self.stop_motion()
                elif delta > 0:
                    safe_move("up_slow" if abs(delta) < 5.0 else "up_fast")
                else:
                    safe_move("down_slow" if abs(delta) < 5.0 else "down_fast")

            time.sleep(0.1)
