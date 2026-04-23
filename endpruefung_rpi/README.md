# Endprüfung auf Raspberry Pi (LAN + VNC)

Dieses Projekt ist eine **auf die Endprüfung angepasste Kopie der Steuerungslogik** von Adeept RaspClaws – aber **ohne WLAN/AP-Modus** und **ohne Roboter-Fokus**.

Ziel ist eine Raspberry-Pi-basierte Steuerung für die Endprüfstufe von Kraftsensoren mit:

- Bedienung **lokal auf dem Raspberry Pi**
- Fernbedienung **über LAN + VNC Viewer**
- optionaler Fernbedienung **über SSH-CLI**
- manueller und automatischer Motorsteuerung
- Einlesen von Endschaltern, Not-Aus und Kraftnebenschluss
- Positionsanzeige über Seilzugsensor / Messverstärker 9250
- optionalem Auslesen eines burster 7281

## Wichtiger Hinweis

Die Logik für den **burster 7281** ist bereits als Python-Protokoll umgesetzt.

Für den **burster 9250 per USB** ist in den vorliegenden Unterlagen keine belastbare USB-Protokollbeschreibung enthalten. Deshalb ist in diesem Projekt die 9250-Anbindung als **klar markierte Schnittstelle / Platzhalter** umgesetzt. Sie kann sofort durch eine echte Treiberschicht ersetzt werden, sobald das tatsächliche Datenformat bzw. die Zugriffsmethode bekannt ist.

## Architektur

- `server/controller.py` – zentrale Anlagenlogik
- `server/gpio_interface.py` – GPIO-Zugriff für Raspberry Pi oder Mock-Betrieb
- `server/measurement_7281.py` – serielle Kommunikation mit burster 7281
- `server/amplifier_9250.py` – Platzhalter für Positionswert vom 9250
- `ui/gui.py` – lokale GUI für den Raspberry Pi Desktop
- `cli/remote_cli.py` – SSH-kompatible Befehlssteuerung
- `config/default_config.json` – Pins, Geschwindigkeiten, Zielpositionen

## Bedienkonzept

### LAN + VNC

1. Raspberry Pi per **LAN-Kabel** mit Netzwerk oder direkt mit Laptop/PC verbinden.
2. Raspberry Pi Desktop starten.
3. Auf dem Laptop/PC **VNC Viewer** öffnen.
4. IP-Adresse oder Hostname des Raspberry Pi eintragen.
5. Verbinden.
6. Auf dem Raspberry Pi die GUI `ui/gui.py` starten.

### SSH

Beispiele:

```bash
python3 cli/remote_cli.py status
python3 cli/remote_cli.py move up_fast
python3 cli/remote_cli.py move stop
python3 cli/remote_cli.py auto GS_1
```

## Installation

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-tk
pip3 install -r requirements.txt
```

## Start

```bash
python3 ui/gui.py
```

## Nächste Schritte für die reale Inbetriebnahme

1. GPIO-Pins in `config/default_config.json` auf die echte Verdrahtung anpassen.
2. 9250-Zugriff ergänzen:
   - entweder echte USB-Protokollanbindung,
   - oder alternativen Messpfad definieren.
3. Zielpositionen der Gewichtssätze im Kalibrierbetrieb einlernen.
4. Optional 7281 aktivieren.
5. systemd-Service aktivieren.
