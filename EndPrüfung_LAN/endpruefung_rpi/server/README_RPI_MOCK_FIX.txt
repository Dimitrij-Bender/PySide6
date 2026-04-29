# Fix für ModuleNotFoundError: No module named 'RPi'

Diese Backend-Dateien laufen:
- auf dem Raspberry Pi mit echten GPIOs
- auf Mac/Windows/Linux automatisch im Mock-Modus

Kopiere die Dateien nach:
endpruefung_rpi/server/

Dann starte:
python3 ui/gui_pyside6.py

Auf dem Raspberry Pi:
pip install RPi.GPIO
optional für ADS1115:
pip install adafruit-circuitpython-ads1x15
