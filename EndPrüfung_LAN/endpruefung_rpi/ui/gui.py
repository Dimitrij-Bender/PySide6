#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

sys.path.append(str(Path(__file__).resolve().parents[1] / "server"))
from controller import EndpruefungController  # noqa: E402

CONFIG = str(Path(__file__).resolve().parents[1] / "config" / "default_config.json")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Endprüfung – LAN/VNC Bedienoberfläche")
        self.geometry("980x620")
        self.controller = EndpruefungController(CONFIG)
        self.controller.start()

        self.var_mode = tk.StringVar(value="manual")
        self.var_position = tk.StringVar(value="0.0 mm")
        self.var_source = tk.StringVar(value="mock")
        self.var_status = tk.StringVar(value="Bereit")
        self.var_error = tk.StringVar(value="-")
        self.var_7281 = tk.StringVar(value="-")

        self._build()
        self.after(200, self.refresh)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build(self) -> None:
        top = tk.Frame(self, padx=12, pady=12)
        top.pack(fill="x")
        tk.Label(top, text="Bedienung lokal auf Raspberry Pi, Fernzugriff über VNC Viewer via LAN", font=("Arial", 13, "bold")).pack(anchor="w")

        info = tk.LabelFrame(self, text="Status", padx=10, pady=10)
        info.pack(fill="x", padx=12, pady=8)
        for i, (name, var) in enumerate([
            ("Modus", self.var_mode),
            ("Aktuelle Position", self.var_position),
            ("Quelle", self.var_source),
            ("Status", self.var_status),
            ("Fehler", self.var_error),
            ("7281", self.var_7281),
        ]):
            tk.Label(info, text=name + ":", width=18, anchor="w").grid(row=i // 2, column=(i % 2) * 2, sticky="w")
            tk.Label(info, textvariable=var, width=26, anchor="w", relief="sunken").grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="we", padx=4, pady=2)

        manual = tk.LabelFrame(self, text="Manuell", padx=10, pady=10)
        manual.pack(fill="x", padx=12, pady=8)
        buttons = [
            ("Auf schnell", lambda: self.move("up_fast")),
            ("Ab schnell", lambda: self.move("down_fast")),
            ("Auf langsam", lambda: self.move("up_slow")),
            ("Ab langsam", lambda: self.move("down_slow")),
            ("Stop", self.stop_motion),
        ]
        for idx, (text, cmd) in enumerate(buttons):
            tk.Button(manual, text=text, width=16, command=cmd).grid(row=0, column=idx, padx=4, pady=4)

        auto = tk.LabelFrame(self, text="Automatik / Kalibrierbetrieb", padx=10, pady=10)
        auto.pack(fill="x", padx=12, pady=8)
        self.position_buttons_frame = auto
        self.rebuild_positions()
        tk.Button(auto, text="Aktuelle Position speichern", command=self.save_position_dialog).grid(row=99, column=0, columnspan=2, pady=8, sticky="w")

        opt = tk.LabelFrame(self, text="Optional", padx=10, pady=10)
        opt.pack(fill="x", padx=12, pady=8)
        tk.Button(opt, text="7281 verbinden", command=self.connect_7281).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(opt, text="7281 Messwert holen", command=self.read_7281).grid(row=0, column=1, padx=4, pady=4)

        hint = tk.LabelFrame(self, text="VNC/LAN-Hinweis", padx=10, pady=10)
        hint.pack(fill="both", expand=True, padx=12, pady=8)
        msg = (
            "1. Raspberry Pi per LAN verbinden.\n"
            "2. VNC Viewer auf Laptop/PC öffnen.\n"
            "3. IP oder Hostname des Raspberry Pi eintragen.\n"
            "4. Mit dem Desktop verbinden.\n"
            "5. Diese GUI auf dem Raspberry Pi bedienen."
        )
        tk.Label(hint, text=msg, justify="left", anchor="nw").pack(anchor="w")

    def rebuild_positions(self) -> None:
        for widget in self.position_buttons_frame.grid_slaves():
            if int(widget.grid_info().get("row", 0)) < 99:
                widget.destroy()
        positions = self.controller.positions
        for idx, (name, value) in enumerate(positions.items()):
            tk.Button(self.position_buttons_frame, text=f"{name} anfahren", width=18,
                      command=lambda n=name: self.auto_move(n)).grid(row=idx, column=0, padx=4, pady=4, sticky="w")
            tk.Label(self.position_buttons_frame, text=f"{value:.3f} mm", width=14, anchor="w").grid(row=idx, column=1, padx=4, pady=4, sticky="w")

    def move(self, motion: str) -> None:
        self.controller.manual_move(motion)

    def stop_motion(self) -> None:
        self.controller.stop_motion()

    def auto_move(self, name: str) -> None:
        self.controller.auto_move_to(name)

    def save_position_dialog(self) -> None:
        name = simpledialog.askstring("Position speichern", "Name der Position, z. B. GS_5:", parent=self)
        if not name:
            return
        self.controller.save_current_position(name)
        self.rebuild_positions()

    def connect_7281(self) -> None:
        try:
            self.controller.connect_7281()
            self.var_status.set("7281 verbunden")
        except Exception as exc:
            messagebox.showerror("7281", str(exc))

    def read_7281(self) -> None:
        try:
            self.var_7281.set(self.controller.read_7281())
        except Exception as exc:
            messagebox.showerror("7281", str(exc))

    def refresh(self) -> None:
        state = self.controller.get_state()
        self.var_mode.set(state.mode)
        self.var_position.set(f"{state.current_position:.3f} mm")
        self.var_source.set(state.position_source)
        self.var_status.set(state.motion)
        self.var_error.set(state.error_reason or "-")
        self.after(200, self.refresh)

    def on_close(self) -> None:
        self.controller.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
