# PySide6 GUI für Endprüfung

## Installation auf Raspberry Pi

```bash
python3 -m pip install PySide6
```

## Start

```bash
cd endpruefung_rpi/ui
python3 gui_pyside6.py
```

## Hinweise

- Die GUI ersetzt die tkinter-Datei.
- Der vorhandene Backend-Controller wird weiter benutzt.
- Datei gehört in den Ordner `endpruefung_rpi/ui/`.
- Das Logo `burster_logo.png` muss ebenfalls im Ordner `ui/` liegen.
- 24-V-Signale niemals direkt an Raspberry-Pi-GPIO anschließen.
