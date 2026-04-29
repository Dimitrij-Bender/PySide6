# Endprüfung auf Raspberry Pi (LAN + VNC)

Aktualisierte Kopie der RaspClaws-Grundstruktur für die Endprüfstufe.

Jetzt eingetragen:

- echte BCM-GPIO-Belegung in `config/default_config.json`
- Hardware-Taster Auf/Ab und Schnell/Langsam
- Endschalter oben/unten
- Not-Aus
- Kraftnebenschluss mit Signalleuchte
- 9250-Schnittstelle über USB/seriellen ASCII-Datenstrom
- Bedienung lokal auf Raspberry Pi, vom Laptop/PC über LAN + VNC Viewer

## Start

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-tk
pip3 install -r requirements.txt
python3 ui/gui.py
```

## Sicherheit

Motoren, Lampen und 24-V-Signale niemals direkt an GPIO anschließen. Ausgänge brauchen Relais/MOSFET-Treiber, Eingänge brauchen Pegelanpassung oder Optokoppler.
