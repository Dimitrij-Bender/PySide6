from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

from amplifier_9250 import MockPositionReader, Burster9250USBReader, PositionReading
from gpio_interface import GPIOBackend, GPIOPins
from measurement_7281 import Burster7281, Burster7281Config


@dataclass
class PlantState:
    mode: str = "manual"
    motion: str = "stop"
    current_position: float = 0.0
    target_position: Optional[float] = None
    position_source: str = "mock"
    error_active: bool = False
    error_reason: str = ""
    estop: bool = False
    limit_top: bool = False
    limit_bottom: bool = False
    force_shunt: bool = False
    last_7281_value: str = ""


class EndpruefungController:
    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path)
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        gpio_cfg = self.config["gpio"]
        self.gpio = GPIOBackend(
            GPIOPins(
                inputs=gpio_cfg["inputs"],
                outputs=gpio_cfg["outputs"],
                active_low_inputs=gpio_cfg.get("active_low_inputs", True),
            ),
            allow_mock=gpio_cfg.get("use_mock_when_unavailable", True),
        )
        self.state = PlantState()
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self.positions: Dict[str, float] = self.config["positions"]
        sensors_cfg = self.config["sensors"]
        source = sensors_cfg.get("position_source", "mock")
        if source == "mock":
            self.position_reader = MockPositionReader(
                start=float(sensors_cfg.get("position_mock_start", 0.0)),
                step=float(sensors_cfg.get("position_mock_step", 0.5)),
            )
        else:
            usb_cfg = sensors_cfg["burster_9250"]
            self.position_reader = Burster9250USBReader(
                port=usb_cfg["port"], baudrate=int(usb_cfg.get("baudrate", 9600))
            )
        self.reader_7281: Burster7281 | None = None
        if sensors_cfg.get("burster_7281", {}).get("enabled", False):
            cfg7281 = sensors_cfg["burster_7281"]
            self.reader_7281 = Burster7281(
                Burster7281Config(
                    port=cfg7281["port"],
                    baudrate=int(cfg7281.get("baudrate", 9600)),
                    timeout_s=float(cfg7281.get("timeout_s", 0.3)),
                )
            )
        self.poll_interval = float(self.config["motion"].get("poll_interval_s", 0.05))
        self.slow_stop_tolerance = float(self.config["motion"].get("slow_stop_tolerance", 1.0))
        self.auto_timeout_s = float(self.config["motion"].get("auto_timeout_s", 60))
        self.worker = threading.Thread(target=self._loop, daemon=True)

    def start(self) -> None:
        self.worker.start()

    def stop(self) -> None:
        self._stop_event.set()
        self.gpio.all_outputs_off()

    def get_state(self) -> PlantState:
        with self._lock:
            return PlantState(**asdict(self.state))

    def connect_7281(self) -> None:
        if self.reader_7281:
            self.reader_7281.connect()
            self.reader_7281.enable_measurement_mode()

    def read_7281(self) -> str:
        if not self.reader_7281:
            raise RuntimeError("7281 ist nicht aktiviert")
        value = self.reader_7281.read_value()
        with self._lock:
            self.state.last_7281_value = value
        return value

    def set_mode(self, mode: str) -> None:
        with self._lock:
            if mode not in {"manual", "auto"}:
                raise ValueError("Ungültiger Modus")
            self.state.mode = mode
            self.state.motion = "stop"
            self.state.target_position = None
            self.gpio.all_outputs_off()

    def manual_move(self, command: str) -> None:
        with self._lock:
            self.state.mode = "manual"
            self.state.target_position = None
            self.state.motion = command

    def stop_motion(self) -> None:
        with self._lock:
            self.state.motion = "stop"
            self.state.target_position = None
            self.gpio.all_outputs_off()

    def auto_move_to(self, name: str) -> None:
        if name not in self.positions:
            raise KeyError(f"Position {name} ist nicht definiert")
        with self._lock:
            self.state.mode = "auto"
            self.state.target_position = float(self.positions[name])
            self.state.motion = "auto"

    def save_current_position(self, name: str) -> None:
        with self._lock:
            self.positions[name] = self.state.current_position
            self.config["positions"] = self.positions
            self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")

    def _read_inputs(self) -> None:
        with self._lock:
            self.state.limit_top = self.gpio.read_input("limit_top")
            self.state.limit_bottom = self.gpio.read_input("limit_bottom")
            self.state.estop = self.gpio.read_input("estop")
            self.state.force_shunt = self.gpio.read_input("force_shunt")
            if self.state.estop:
                self.state.error_active = True
                self.state.error_reason = "Not-Aus aktiv"
            elif self.state.force_shunt:
                self.state.error_active = True
                self.state.error_reason = "Kraftnebenschluss aktiv"
            else:
                self.state.error_active = False
                self.state.error_reason = ""

    def _read_position(self) -> PositionReading:
        reading = self.position_reader.read()
        with self._lock:
            self.state.current_position = reading.value
            self.state.position_source = reading.source
        return reading

    def _apply_outputs(self, up_fast=False, down_fast=False, up_slow=False, down_slow=False, lamp=False) -> None:
        self.gpio.write_output("motor_up_fast", up_fast)
        self.gpio.write_output("motor_down_fast", down_fast)
        self.gpio.write_output("motor_up_slow", up_slow)
        self.gpio.write_output("motor_down_slow", down_slow)
        self.gpio.write_output("warning_lamp", lamp)

    def _manual_logic(self) -> None:
        motion = self.state.motion
        if self.state.error_active:
            self._apply_outputs(lamp=True)
            return
        if motion == "up_fast" and not self.state.limit_top:
            self._apply_outputs(up_fast=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(+1)
        elif motion == "down_fast" and not self.state.limit_bottom:
            self._apply_outputs(down_fast=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(-1)
        elif motion == "up_slow" and not self.state.limit_top:
            self._apply_outputs(up_slow=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(+1)
        elif motion == "down_slow" and not self.state.limit_bottom:
            self._apply_outputs(down_slow=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(-1)
        else:
            self._apply_outputs()

    def _auto_logic(self) -> None:
        if self.state.error_active:
            self._apply_outputs(lamp=True)
            self.state.motion = "stop"
            return
        target = self.state.target_position
        if target is None:
            self._apply_outputs()
            return
        diff = target - self.state.current_position
        if abs(diff) <= self.slow_stop_tolerance:
            self._apply_outputs()
            self.state.motion = "stop"
            return
        if diff > 0 and not self.state.limit_top:
            self._apply_outputs(up_slow=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(+1)
        elif diff < 0 and not self.state.limit_bottom:
            self._apply_outputs(down_slow=True)
            if isinstance(self.position_reader, MockPositionReader):
                self.position_reader.nudge(-1)
        else:
            self._apply_outputs()
            self.state.motion = "stop"

    def _loop(self) -> None:
        auto_started_at = time.monotonic()
        while not self._stop_event.is_set():
            self._read_inputs()
            self._read_position()
            with self._lock:
                self.gpio.write_output("warning_lamp", self.state.error_active)
                if self.state.mode == "auto" and self.state.motion == "auto":
                    if time.monotonic() - auto_started_at > self.auto_timeout_s:
                        self.state.error_active = True
                        self.state.error_reason = "Automatik-Timeout"
                        self._apply_outputs(lamp=True)
                    else:
                        self._auto_logic()
                else:
                    auto_started_at = time.monotonic()
                    self._manual_logic()
            time.sleep(self.poll_interval)
