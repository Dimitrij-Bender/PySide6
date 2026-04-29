#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
import random

sys.path.append(str(Path(__file__).resolve().parents[1] / "server"))
from controller import EndpruefungController  # noqa: E402

CONFIG = str(Path(__file__).resolve().parents[1] / "config" / "default_config.json")
LOGO = Path(__file__).resolve().parent / "burster_logo.png"

x = random.randint(-1000, 1000)


class App(tk.Tk):
    """GUI Endprüfung."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Endprüfung")
        self.geometry("980x680")
        self.configure(bg="#FFFFFF")

        self.color_bg = "#FFFFFF"
        self.color_panel = "#FFFFFF"
        self.color_btn = "#0277BD"
        self.color_text = "#000000"
        self.color_warn = "#F44336"
        self.color_ok = "#558B2F"
        self.color_burster = "#009681"

        self.controller = EndpruefungController(CONFIG)
        self.controller.start()

        self.var_mode = tk.StringVar(value="Manuell")
        self.var_position = tk.StringVar(value="0.0 mm")
        self.var_source = tk.StringVar(value="mock")
        self.var_status = tk.StringVar(value="Bereit")
        self.var_error = tk.StringVar(value="-")
        self.var_7281 = tk.StringVar(value="-")

        self.logo_img: tk.PhotoImage | None = None
        self.position_buttons_frame: tk.LabelFrame
        self._build()
        self.after(200, self.refresh)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def label(self, parent: tk.Widget, text: str, **kw) -> tk.Label:
        return tk.Label(parent, text=text, fg=self.color_text, bg=kw.pop("bg", self.color_bg), **kw)

    def value_label(self, parent: tk.Widget, var: tk.StringVar) -> tk.Label:
        return tk.Label(parent, textvariable=var, fg=self.color_text, bg=self.color_panel,
                        width=30, anchor="center", relief="sunken")

    def button(self, parent: tk.Widget, text: str, command, width: int = 14, bg: str | None = None) -> tk.Button:
        return tk.Button(parent, text=text, width=width, command=command,
                         fg=self.color_text, bg=bg or self.color_btn, relief="ridge")

    def _build(self) -> None:
        # Wichtig: Im Hauptfenster wird nur pack() verwendet.
        # grid() wird nur innerhalb von Frames benutzt. Dadurch entsteht kein Tkinter-Fehler.
        top = tk.Frame(self, bg=self.color_bg, padx=18, pady=12, height=135)
        top.pack(fill="x")
        top.pack_propagate(False)

        if LOGO.exists():
            self.logo_img = tk.PhotoImage(file=str(LOGO))
            tk.Label(top, image=self.logo_img, bg=self.color_bg).place(x=0, y=0)

        self.label(top, "Endprüfung", font=("Arial", 36, "bold")).pack(anchor="w", padx=(145, 0))
        self.label(top, "Endprüfung – LAN/VNC Bedienoberfläche", font=("Arial", 14)).pack(anchor="w", padx=(145, 0), pady=(4, 0))

        status = tk.LabelFrame(self, text="Status", fg=self.color_text, bg=self.color_bg, padx=10, pady=10)
        status.pack(fill="x", padx=18, pady=8)
        status.grid_columnconfigure(1, weight=1)
        status.grid_columnconfigure(3, weight=1)

        fields = [
            ("Modus", self.var_mode),
            ("Aktuelle Position", self.var_position),
            ("Quelle", self.var_source),
            ("Status", self.var_status),
            ("Fehler", self.var_error),
            ("7281", self.var_7281),
        ]
        for i, (name, var) in enumerate(fields):
            r = i // 2
            c = (i % 2) * 2
            self.label(status, name + ":").grid(row=r, column=c, sticky="w", padx=4, pady=3)
            self.value_label(status, var).grid(row=r, column=c + 1, sticky="we", padx=4, pady=3)

        main = tk.Frame(self, bg=self.color_bg)
        main.pack(fill="x", padx=18, pady=8)

        manual = tk.LabelFrame(main, text="Manuelle Steuerung", fg=self.color_text, bg=self.color_bg, padx=10, pady=10)
        manual.pack(side="left", fill="y", padx=(0, 10), pady=0)

        manual_buttons = [
            ("Auf schnell", lambda: self.move("up_fast")),
            ("Ab schnell", lambda: self.move("down_fast")),
            ("Auf langsam", lambda: self.move("up_slow")),
            ("Ab langsam", lambda: self.move("down_slow")),
            ("STOP", self.stop_motion),
        ]
        for text, cmd in manual_buttons:
            self.button(manual, text, cmd, width=18, bg=self.color_warn if text == "STOP" else None).pack(padx=6, pady=6, fill="x")

        auto = tk.LabelFrame(main, text="Automatik / Kalibrierbetrieb", fg=self.color_text, bg=self.color_bg, padx=10, pady=10)
        auto.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=0)
        auto.grid_columnconfigure(0, weight=1)
        auto.grid_columnconfigure(1, weight=0)
        auto.grid_columnconfigure(2, weight=0)

        self.position_buttons_frame = auto
        self.rebuild_positions()

        self.button(auto, "Aktuelle Position speichern", self.save_position_dialog, width=28, bg=self.color_burster).grid(row=99, column=0, pady=10, padx=(6, 6), sticky="w")
        self.button(auto, "Aktuelle Position löschen", self.delete_position_dialog, width=26, bg=self.color_warn).grid(row=99, column=1, pady=10, padx=(6, 6), sticky="w")

        opt = tk.LabelFrame(self, text="Messgeräte", fg=self.color_text, bg=self.color_bg, padx=10, pady=10)
        opt.pack(fill="x", padx=18, pady=8)
        self.button(opt, "7281 verbinden", self.connect_7281, width=18).grid(row=0, column=0, padx=6, pady=5)
        self.button(opt, "7281 Messwert holen", self.read_7281, width=20).grid(row=0, column=1, padx=6, pady=5)

        hint = tk.LabelFrame(self, text="VNC/LAN-Hinweis", fg=self.color_text, bg=self.color_bg, padx=10, pady=10)
        hint.pack(fill="both", expand=True, padx=18, pady=8)
        msg = (
            "1. Raspberry Pi 4/5 per LAN-Kabel mit Laptop/PC oder Netzwerk verbinden.\n"
            "2. VNC Viewer auf dem Laptop/PC öffnen.\n"
            "3. LAN-IP-Adresse oder Hostname des Raspberry Pi eintragen.\n"
            "4. Mit dem Raspberry-Pi-Desktop verbinden.\n"
            "5. Diese Oberfläche heißt bewusst \"Adeept RaspClaws\", nutzt aber das burster-Logo."
        )
        self.label(hint, msg, justify="left", anchor="nw").pack(anchor="w")

    def rebuild_positions(self) -> None:
        for widget in self.position_buttons_frame.grid_slaves():
            if int(widget.grid_info().get("row", 0)) < 99:
                widget.destroy()

        positions = self.controller.positions
        for idx, (name, value) in enumerate(positions.items()):
            self.button(self.position_buttons_frame, f"{name} anfahren", lambda n=name: self.auto_move(n), width=22).grid(row=idx, column=0, padx=6, pady=4, sticky="w")
            tk.Label(self.position_buttons_frame, text=f"{value:.3f} mm", fg=self.color_text, bg=self.color_panel, width=16, anchor="center", relief="sunken").grid(row=idx, column=1, padx=6, pady=4, sticky="w")

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

    def delete_position_dialog(self) -> None:
        positions = list(self.controller.positions.keys())
        if not positions:
            messagebox.showinfo("Position löschen", "Es gibt keine gespeicherten Positionen.")
            return

        name = simpledialog.askstring(
            "Position löschen",
            "Name der Position eingeben:\n\n" + ", ".join(positions),
            parent=self,
        )
        if not name:
            return
        if name not in self.controller.positions:
            messagebox.showerror("Position löschen", f"Position '{name}' existiert nicht.")
            return
        if messagebox.askyesno("Position löschen", f"Position '{name}' wirklich löschen?"):
            self.controller.delete_position(name)
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
        mode = getattr(state, "mode", "manual")
        self.var_mode.set("Manuell" if mode == "manual" else "Automatik")
        self.var_position.set(f"{x} mm")
        self.var_source.set(state.position_source)
        self.var_status.set(state.motion)
        self.var_error.set(state.error_reason or "-")
        self.after(200, self.refresh)

    def on_close(self) -> None:
        self.controller.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
