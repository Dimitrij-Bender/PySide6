# LAN + VNC Inbetriebnahme

## Zielbild

Die Endprüfung läuft auf dem Raspberry Pi 4/5.
Vor Ort gibt es **kein WLAN**, sondern nur **LAN**.
Die Bedienung erfolgt deshalb über einen **Laptop/PC mit VNC Viewer**.

## Ablauf

1. Raspberry Pi per Ethernet anschließen.
2. Raspberry Pi booten.
3. IP-Adresse ermitteln:
   - Router / DHCP-Liste
   - `hostname -I`
   - alternativ feste IP konfigurieren
4. Auf dem Laptop/PC `VNC Viewer` öffnen.
5. IP-Adresse des Raspberry Pi eintragen.
6. Verbinden.
7. Auf dem Pi-Desktop die GUI `python3 ui/gui.py` starten.

## Empfehlung

Für die Anlage ist eine **statische IP-Adresse** sinnvoll, damit der VNC-Zugriff immer gleich bleibt.
