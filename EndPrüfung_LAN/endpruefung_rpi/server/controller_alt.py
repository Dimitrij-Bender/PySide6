from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

from amplifier_9250 import MockPositionReader, build_9250_reader, PositionReading
from gpio_interface import GPIOBackend, GPIOPins
from measurement_7281 import Burster7281, Burster7281Config

@dataclass
class PlantState:
    mode: str = "manual"
    motion: str = "stop"
    current_position: float = 0.0
    target_position: Optional[float] = None
    position_source: str = "init"
    error_active: bool = False
    error_reason: str = ""
    estop: bool = False
    limit_top: bool = False
    limit_bottom: bool = False
    force_shunt: bool = False
    button_up: bool = False
    button_down: bool = False
    speed_fast: bool = False
    last_7281_value: str = ""

class EndpruefungController:
    def __init__(self, config_path: str) -> None:
        self.config_path = Path(config_path)
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        gpio_cfg = self.config["gpio"]
        self.gpio = GPIOBackend(
            GPIOPins(gpio_cfg["inputs"], gpio_cfg["outputs"], gpio_cfg.get("active_low_inputs", True)),
            allow_mock=gpio_cfg.get("use_mock_when_unavailable", True),
        )
        self.state = PlantState()
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self.positions: Dict[str, float] = self.config["positions"]
        sensors_cfg = self.config["sensors"]
        self._fallback_reader = MockPositionReader(
            start=float(sensors_cfg.get("burster_9250", {}).get("mock_start", 0.0)),
            step=float(sensors_cfg.get("burster_9250", {}).get("mock_step", 0.25)),
        )
        self._fallback_to_mock = bool(sensors_cfg.get("burster_9250", {}).get("fallback_to_mock", True))
        if sensors_cfg.get("position_source") == "mock":
            self.position_reader = self._fallback_reader
        else:
            self.position_reader = build_9250_reader(sensors_cfg["burster_9250"])
        self.reader_7281: Burster7281 | None = None
        if sensors_cfg.get("burster_7281", {}).get("enabled", False):
            cfg7281 = sensors_cfg["burster_7281"]
            self.reader_7281 = Burster7281(Burster7281Config(cfg7281["port"], int(cfg7281.get("baudrate", 9600)), float(cfg7281.get("timeout_s", 0.3))))
        self.poll_interval = float(self.config["motion"].get("poll_interval_s", 0.05))
        self.slow_stop_tolerance = float(self.config["motion"].get("slow_stop_tolerance", 1.0))
        self.auto_timeout_s = float(self.config["motion"].get("auto_timeout_s", 60))
        self.hardware_button_hold = bool(self.config["motion"].get("hardware_button_hold_to_move", True))
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

    def delete_position(self, name: str) -> None:
        with self._lock:
            if name not in self.positions:
                raise KeyError(f"Position {name} ist nicht definiert")
            del self.positions[name]
            self.config["positions"] = self.positions
            self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")

    def _read_inputs(self) -> None:
        with self._lock:
            for name in ["limit_top", "limit_bottom", "estop", "force_shunt", "button_up", "button_down", "speed_fast"]:
                setattr(self.state, name, self.gpio.read_input(name))
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
        try:
            reading = self.position_reader.read()
        except Exception as exc:
            if not self._fallback_to_mock:
                raise
            reading = self._fallback_reader.read()
            reading.source = "mock-fallback-9250-fehlt"
            reading.raw = str(exc)
        with self._lock:
            self.state.current_position = reading.value
            self.state.position_source = reading.source
        return reading

    def _apply_outputs(self, up_fast=False, down_fast=False, up_slow=False, down_slow=False, lamp=False) -> None:
        self.gpio.write_output("motor_up_fast", up_fast)
        self.gpio.write_output("motor_down_fast", down_fast)
        self.gpio.write_output("motor_up_slow", up_slow)
        self.gpio.write_output("motor_down_slow", down_slow)
        self.gpio.write_output("force_shunt_lamp", lamp)

    def _safe_motion(self, motion: str) -> str:
        if self.state.error_active:
            return "stop"
        if self.state.limit_top and motion in {"up_fast", "up_slow"}:
            return "stop"
        if self.state.limit_bottom and motion in {"down_fast", "down_slow"}:
            return "stop"
        return motion

    def _hardware_buttons_to_motion(self) -> Optional[str]:
        if not self.hardware_button_hold or self.state.mode != "manual":
            return None
        if self.state.button_up and not self.state.button_down:
            return "up_fast" if self.state.speed_fast else "up_slow"
        if self.state.button_down and not self.state.button_up:
            return "down_fast" if self.state.speed_fast else "down_slow"
        return None

    def _loop(self) -> None:
        auto_started = None
        while not self._stop_event.is_set():
            self._read_inputs()
            self._read_position()
            with self._lock:
                if self.state.error_active:
                    self.state.motion = "stop"
                    self.state.target_position = None
                hw_motion = self._hardware_buttons_to_motion()
                motion = hw_motion if hw_motion is not None else self.state.motion
                if self.state.mode == "auto" and self.state.target_position is not None and motion == "auto":
                    if auto_started is None:
                        auto_started = time.time()
                    delta = self.state.target_position - self.state.current_position
                    if abs(delta) <= self.slow_stop_tolerance:
                        motion = "stop"
                        self.state.motion = "stop"
                        self.state.target_position = None
                        auto_started = None
                    elif time.time() - auto_started > self.auto_timeout_s:
                        motion = "stop"
                        self.state.motion = "stop"
                        self.state.target_position = None
                        self.state.error_active = True
                        self.state.error_reason = "Automatik-Timeout"
                    elif delta > 0:
                        motion = "up_slow" if abs(delta) < 5 * self.slow_stop_tolerance else "up_fast"
                    else:
                        motion = "down_slow" if abs(delta) < 5 * self.slow_stop_tolerance else "down_fast"
                else:
                    auto_started = None
                motion = self._safe_motion(motion)
                lamp = self.state.force_shunt or self.state.error_active
            self._apply_outputs(
                up_fast=motion == "up_fast",
                down_fast=motion == "down_fast",
                up_slow=motion == "up_slow",
                down_slow=motion == "down_slow",
                lamp=lamp,
            )
            time.sleep(self.poll_interval)
