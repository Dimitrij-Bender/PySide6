#!/usr/bin/env python3
"""
Endprüfung LAN/VNC - fertige PySide6-GUI

Start:
    pip install PySide6
    python endpruefung_gui_fertig.py

Hinweis:
- Wenn dein echtes Projektmodul `server/controller.py` vorhanden ist, wird automatisch
  `EndpruefungController` daraus verwendet.
- Wenn nicht, startet die GUI mit einem eingebauten Mock-Controller, damit du die
  Oberfläche sofort testen kannst.
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG = str(BASE_DIR / "config" / "default_config.json")
LOGO = BASE_DIR / "burster_logo.png"


@dataclass
class ControllerState:
    mode: str = "manual"
    current_position: float = 0.0
    position_source: str = "mock"
    motion: str = "Bereit"
    error_reason: Optional[str] = None


class MockEndpruefungController:
    """Ersatz-Controller zum Testen der GUI ohne Hardware/Server-Modul."""

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.positions: dict[str, float] = {
            "Grundstellung": 0.0,
            "GS_5": 5.0,
            "GS_10": 10.0,
        }
        self.state = ControllerState()
        self._running = False
        self._connected_7281 = False

    def start(self) -> None:
        self._running = True
        self.state.motion = "Bereit"

    def stop(self) -> None:
        self._running = False
        self.stop_motion()

    def manual_move(self, motion: str) -> None:
        steps = {
            "up_fast": 0.25,
            "down_fast": -0.25,
            "up_slow": 0.05,
            "down_slow": -0.05,
        }
        if motion not in steps:
            raise ValueError(f"Unbekannte Bewegung: {motion}")

        self.state.mode = "manual"
        self.state.motion = motion
        self.state.current_position += steps[motion]
        self.state.error_reason = None

    def stop_motion(self) -> None:
        self.state.motion = "STOP"

    def auto_move_to(self, name: str) -> None:
        if name not in self.positions:
            raise ValueError(f"Position '{name}' ist nicht gespeichert.")

        self.state.mode = "auto"
        self.state.motion = f"Fahre {name} an"
        self.state.current_position = float(self.positions[name])
        self.state.error_reason = None

    def save_current_position(self, name: str) -> None:
        self.positions[name] = float(self.state.current_position)

    def delete_position(self, name: str) -> None:
        if name not in self.positions:
            raise ValueError(f"Position '{name}' existiert nicht.")
        del self.positions[name]

    def connect_7281(self) -> None:
        self._connected_7281 = True
        self.state.motion = "7281 verbunden"

    def read_7281(self) -> str:
        if not self._connected_7281:
            raise RuntimeError("Bitte zuerst 7281 verbinden.")
        return f"{random.uniform(0.0, 100.0):.3f}"

    def get_state(self) -> ControllerState:
        return self.state


def load_controller_class():
    """Lädt den echten Controller, falls er vorhanden ist. Sonst Mock verwenden."""
    possible_server_dirs = [
        BASE_DIR / "server",
        BASE_DIR.parent / "server",
    ]

    for server_dir in possible_server_dirs:
        if server_dir.exists():
            sys.path.insert(0, str(server_dir))
            try:
                from controller import EndpruefungController  # type: ignore

                return EndpruefungController
            except Exception:
                pass

    return MockEndpruefungController


EndpruefungController = load_controller_class()


class StatusValue(QLabel):
    def __init__(self, text: str = "-") -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(28)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet(
            """
            QLabel {
                background: #ffffff;
                color: #000000;
                border: 1px solid #bbbbbb;
                padding: 4px;
                font-size: 14px;
            }
            """
        )


class EndpruefungWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Endprüfung LAN/VNC")
        self.resize(1100, 720)

        self.color_burster = "#009681"
        self.color_warn = "#F44336"

        self.controller = EndpruefungController(CONFIG)
        self.controller.start()

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(200)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(18, 14, 18, 14)
        main.setSpacing(10)

        main.addWidget(self._header())
        main.addWidget(self._status_box())

        middle = QHBoxLayout()
        middle.setSpacing(12)
        middle.addWidget(self._manual_box(), 0)
        middle.addWidget(self._auto_box(), 1)
        main.addLayout(middle)

        main.addWidget(self._device_box())
        main.addWidget(self._hint_box(), 1)

        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #ffffff;
                color: #000000;
                font-family: Arial;
            }

            QGroupBox {
                border: 2px solid #dddddd;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                font-size: 15px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                background: #ffffff;
            }

            QPushButton {
                background: #0277BD;
                color: #000000;
                border: 1px solid #01579B;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 28px;
            }

            QPushButton:hover {
                background: #039BE5;
            }

            QPushButton:pressed {
                background: #01579B;
            }
            """
        )

    def _header(self) -> QWidget:
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        logo.setFixedSize(120, 90)
        logo.setAlignment(Qt.AlignCenter)

        if LOGO.exists():
            pixmap = QPixmap(str(LOGO))
            logo.setPixmap(pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("burster")
            logo.setStyleSheet(
                f"background: {self.color_burster}; color: white; "
                "font-size: 24px; font-weight: bold;"
            )

        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(12, 0, 0, 0)

        title = QLabel("Endprüfung – LAN/VNC Bedienoberfläche")
        title.setStyleSheet("font-size: 34px; font-weight: bold;")
        subtitle = QLabel("Raspberry Pi 4/5 per LAN verbinden → VNC Viewer öffnen → IP-Adresse eingeben")
        subtitle.setStyleSheet("font-size: 14px; color: #333333;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()

        layout.addWidget(logo)
        layout.addWidget(title_box, 1)
        return header

    def _status_box(self) -> QGroupBox:
        box = QGroupBox("Status")
        grid = QGridLayout(box)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)

        self.lbl_mode = StatusValue("Manuell")
        self.lbl_position = StatusValue("0.000 mm")
        self.lbl_source = StatusValue("mock")
        self.lbl_status = StatusValue("Bereit")
        self.lbl_error = StatusValue("-")
        self.lbl_7281 = StatusValue("-")

        fields = [
            ("Modus", self.lbl_mode),
            ("Aktuelle Position", self.lbl_position),
            ("Quelle", self.lbl_source),
            ("Status", self.lbl_status),
            ("Fehler", self.lbl_error),
            ("7281", self.lbl_7281),
        ]

        for i, (name, widget) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            name_label = QLabel(name + ":")
            name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            name_label.setStyleSheet("font-size: 14px;")
            grid.addWidget(name_label, row, col)
            grid.addWidget(widget, row, col + 1)

        return box

    def _manual_box(self) -> QGroupBox:
        box = QGroupBox("Manuelle Steuerung")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        buttons = [
            ("Auf schnell", lambda: self.move("up_fast"), None),
            ("Ab schnell", lambda: self.move("down_fast"), None),
            ("Auf langsam", lambda: self.move("up_slow"), None),
            ("Ab langsam", lambda: self.move("down_slow"), None),
            ("STOP", self.stop_motion, self.color_warn),
        ]

        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setMinimumWidth(180)
            if color:
                btn.setStyleSheet(f"background: {color}; color: #000000; font-weight: bold;")
            layout.addWidget(btn)

        layout.addStretch()
        return box

    def _auto_box(self) -> QGroupBox:
        box = QGroupBox("Automatik / Kalibrierbetrieb")
        layout = QVBoxLayout(box)

        self.position_list = QListWidget()
        self.position_list.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.position_list, 1)

        row_buttons = QHBoxLayout()

        btn_drive = QPushButton("Ausgewählte Position anfahren")
        btn_drive.clicked.connect(self.drive_selected_position)

        btn_save = QPushButton("Aktuelle Position speichern")
        btn_save.setStyleSheet(f"background: {self.color_burster}; color: #000000; font-weight: bold;")
        btn_save.clicked.connect(self.save_position_dialog)

        btn_delete = QPushButton("Aktuelle Position löschen")
        btn_delete.setStyleSheet("background: #ffb300; color: #000000; font-weight: bold;")
        btn_delete.clicked.connect(self.delete_position_dialog)

        row_buttons.addWidget(btn_drive)
        row_buttons.addWidget(btn_save)
        row_buttons.addWidget(btn_delete)

        layout.addLayout(row_buttons)
        self.rebuild_positions()
        return box

    def _device_box(self) -> QGroupBox:
        box = QGroupBox("Messgeräte")
        layout = QHBoxLayout(box)

        btn_connect = QPushButton("7281 verbinden")
        btn_connect.clicked.connect(self.connect_7281)

        btn_read = QPushButton("7281 Messwert holen")
        btn_read.clicked.connect(self.read_7281)

        layout.addWidget(btn_connect)
        layout.addWidget(btn_read)
        layout.addStretch()
        return box

    def _hint_box(self) -> QGroupBox:
        box = QGroupBox("VNC/LAN-Hinweis")
        layout = QVBoxLayout(box)

        text = QLabel(
            "1. Raspberry Pi 4/5 per LAN-Kabel mit Laptop/PC oder Netzwerk verbinden.\n"
            "2. VNC Viewer auf dem Laptop/PC öffnen.\n"
            "3. LAN-IP-Adresse oder Hostname des Raspberry Pi eintragen.\n"
            "4. Mit dem Raspberry-Pi-Desktop verbinden.\n\n"
            "Sicherheit: 24 V, Endschalter, Not-Aus und Motor dürfen nicht direkt an GPIO. "
            "Nur über Optokoppler, Relaiskarte oder Motortreiber anbinden."
        )
        text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        text.setStyleSheet("font-size: 14px; line-height: 1.3;")
        layout.addWidget(text)
        return box

    def move(self, motion: str) -> None:
        try:
            self.controller.manual_move(motion)
        except Exception as exc:
            QMessageBox.critical(self, "Motorsteuerung", str(exc))

    def stop_motion(self) -> None:
        try:
            self.controller.stop_motion()
        except Exception as exc:
            QMessageBox.critical(self, "STOP", str(exc))

    def rebuild_positions(self) -> None:
        self.position_list.clear()
        for name, value in self.controller.positions.items():
            item = QListWidgetItem(f"{name}    {float(value):.3f} mm")
            item.setData(Qt.UserRole, name)
            self.position_list.addItem(item)

    def selected_position_name(self) -> Optional[str]:
        item = self.position_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)

    def drive_selected_position(self) -> None:
        name = self.selected_position_name()
        if not name:
            QMessageBox.information(self, "Position", "Bitte zuerst eine Position auswählen.")
            return
        try:
            self.controller.auto_move_to(name)
        except Exception as exc:
            QMessageBox.critical(self, "Automatik", str(exc))

    def save_position_dialog(self) -> None:
        name, ok = QInputDialog.getText(self, "Position speichern", "Name der Position, z. B. GS_5:")
        if not ok or not name.strip():
            return
        try:
            self.controller.save_current_position(name.strip())
            self.rebuild_positions()
        except Exception as exc:
            QMessageBox.critical(self, "Position speichern", str(exc))

    def delete_position_dialog(self) -> None:
        name = self.selected_position_name()
        if not name:
            QMessageBox.information(self, "Position löschen", "Bitte zuerst eine Position auswählen.")
            return

        answer = QMessageBox.question(
            self,
            "Position löschen",
            f"Soll die Position „{name}“ wirklich gelöscht werden?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            self.controller.delete_position(name)
            self.rebuild_positions()
        except Exception as exc:
            QMessageBox.critical(self, "Position löschen", str(exc))

    def connect_7281(self) -> None:
        try:
            self.controller.connect_7281()
            self.lbl_status.setText("7281 verbunden")
        except Exception as exc:
            QMessageBox.critical(self, "7281", str(exc))

    def read_7281(self) -> None:
        try:
            self.lbl_7281.setText(str(self.controller.read_7281()))
        except Exception as exc:
            QMessageBox.critical(self, "7281", str(exc))

    def refresh(self) -> None:
        try:
            state = self.controller.get_state()
            mode_text = "Manuell" if state.mode == "manual" else "Automatik"
            self.lbl_mode.setText(mode_text)
            self.lbl_position.setText(f"{float(state.current_position):.3f} mm")
            self.lbl_source.setText(str(state.position_source))
            self.lbl_status.setText(str(state.motion))
            self.lbl_error.setText(str(state.error_reason or "-"))

            if state.error_reason:
                self.lbl_error.setStyleSheet(
                    "background: #F44336; color: #000000; border: 1px solid #bbbbbb; "
                    "padding: 4px; font-weight: bold;"
                )
            else:
                self.lbl_error.setStyleSheet(
                    "background: #ffffff; color: #000000; border: 1px solid #bbbbbb; padding: 4px;"
                )
        except Exception as exc:
            self.lbl_error.setText(str(exc))

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt-Methodenname
        try:
            self.controller.stop()
        finally:
            event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    window = EndpruefungWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
