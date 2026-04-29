# GPIO- und 9250-Integration

## Eingetragene GPIO-Pins (BCM)

### Eingänge

| Funktion | BCM | Hinweis |
|---|---:|---|
| Endschalter oben | 5 | aktiv LOW, gegen GND schalten |
| Endschalter unten | 6 | aktiv LOW, gegen GND schalten |
| Not-Aus | 13 | nur potentialfreier/angepasster Kontakt |
| Taster Auf | 16 | aktiv LOW |
| Taster Ab | 20 | aktiv LOW |
| Schalter schnell/langsam | 21 | aktiv LOW = schnell |
| Kraftnebenschluss | 26 | nur über Optokoppler/Pegelwandler |

### Ausgänge

| Funktion | BCM | Hinweis |
|---|---:|---|
| Motor aufwärts schnell | 17 | Relais/MOSFET, nicht direkt Motor |
| Motor abwärts schnell | 27 | Relais/MOSFET, nicht direkt Motor |
| Motor aufwärts langsam | 22 | Relais/MOSFET, 5-V-Steuerkreis |
| Motor abwärts langsam | 23 | Relais/MOSFET, 5-V-Steuerkreis |
| Signalleuchte Kraftnebenschluss | 24 | Relais/MOSFET/Treiber |

## 24-V-Signale

Raspberry-Pi-GPIOs sind 3,3-V-Eingänge. 24 V aus der Anlage dürfen nicht direkt angeschlossen werden. Benötigt wird galvanische Trennung oder Pegelanpassung, z. B. Optokoppler.

## 9250 reale Anbindung

Standard in `config/default_config.json`:

```json
"position_source": "burster_9250_usb_ascii",
"burster_9250": {
  "mode": "usb_ascii",
  "port": "/dev/ttyACM0",
  "baudrate": 115200,
  "poll_command": "",
  "scale": 1.0,
  "offset": 0.0
}
```

Das funktioniert, wenn der 9250 über USB/COM Messwerte als ASCII-Zeilen liefert. Beispiele wie `12.345 mm` oder `POS=12,345` werden geparst.

Falls dein 9250 nur per DigiVision konfiguriert wird und keine Messwerte streamt, muss der Analogausgang des 9250 über ADC eingelesen werden, z. B. 0..10 V mit Spannungsteiler oder 4..20 mA mit Shunt.
