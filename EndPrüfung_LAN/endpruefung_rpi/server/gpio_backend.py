from __future__ import annotations

"""
GPIO-Backend für Raspberry Pi + Mock-Modus.

Warum?
- Auf dem Raspberry Pi wird automatisch RPi.GPIO benutzt.
- Auf Mac/Windows/Linux ohne Raspberry Pi läuft automatisch ein Mock,
  damit die PySide6-GUI testbar bleibt.
"""

try:
    import RPi.GPIO as GPIO  # type: ignore
    GPIO_AVAILABLE = True
except ModuleNotFoundError:
    GPIO_AVAILABLE = False


# ===== INPUTS BCM =====
PIN_ENDSCHALTER_OBEN = 17
PIN_ENDSCHALTER_UNTEN = 26
PIN_NOTAUS = 27
PIN_KRAFT = 22
PIN_TASTER_AUF = 5
PIN_TASTER_AB = 6
PIN_SCHNELL = 13

# ===== OUTPUTS BCM =====
PIN_MOTOR_UP_FAST = 23
PIN_MOTOR_DOWN_FAST = 24
PIN_MOTOR_UP_SLOW = 16
PIN_MOTOR_DOWN_SLOW = 20
PIN_WARNLAMPE = 25


class MockGPIO:
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"

    def __init__(self):
        self.outputs = {}
        self.inputs = {
            PIN_ENDSCHALTER_OBEN: 1,
            PIN_ENDSCHALTER_UNTEN: 1,
            PIN_NOTAUS: 1,
            PIN_KRAFT: 1,
            PIN_TASTER_AUF: 1,
            PIN_TASTER_AB: 1,
            PIN_SCHNELL: 1,
        }

    def setmode(self, mode):
        print(f"[MOCK GPIO] setmode({mode})")

    def setup(self, pin, mode, pull_up_down=None):
        print(f"[MOCK GPIO] setup(pin={pin}, mode={mode})")
        if mode == self.OUT:
            self.outputs[pin] = 0

    def input(self, pin):
        return self.inputs.get(pin, 1)

    def output(self, pin, value):
        self.outputs[pin] = int(bool(value))
        print(f"[MOCK GPIO] output(pin={pin}, value={value})")

    def cleanup(self):
        print("[MOCK GPIO] cleanup()")


if not GPIO_AVAILABLE:
    GPIO = MockGPIO()  # type: ignore
    print("WARNUNG: RPi.GPIO nicht gefunden. Backend läuft im MOCK-Modus.")
else:
    print("RPi.GPIO gefunden. Backend läuft mit echten Raspberry-Pi-GPIOs.")


GPIO.setmode(GPIO.BCM)

# Inputs: active low, also aktiv wenn GPIO == 0
for pin in [
    PIN_ENDSCHALTER_OBEN,
    PIN_ENDSCHALTER_UNTEN,
    PIN_NOTAUS,
    PIN_KRAFT,
    PIN_TASTER_AUF,
    PIN_TASTER_AB,
    PIN_SCHNELL,
]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in [
    PIN_MOTOR_UP_FAST,
    PIN_MOTOR_DOWN_FAST,
    PIN_MOTOR_UP_SLOW,
    PIN_MOTOR_DOWN_SLOW,
    PIN_WARNLAMPE,
]:
    GPIO.setup(pin, GPIO.OUT)


def read_inputs():
    return {
        "limit_top": GPIO.input(PIN_ENDSCHALTER_OBEN) == 0,
        "limit_bottom": GPIO.input(PIN_ENDSCHALTER_UNTEN) == 0,
        "notaus": GPIO.input(PIN_NOTAUS) == 0,
        "kraft": GPIO.input(PIN_KRAFT) == 0,
        "button_up": GPIO.input(PIN_TASTER_AUF) == 0,
        "button_down": GPIO.input(PIN_TASTER_AB) == 0,
        "speed_fast": GPIO.input(PIN_SCHNELL) == 0,

        # alte Namen für Kompatibilität
        "endschalter": GPIO.input(PIN_ENDSCHALTER_OBEN) == 0,
    }


def all_outputs_off():
    GPIO.output(PIN_MOTOR_UP_FAST, False)
    GPIO.output(PIN_MOTOR_DOWN_FAST, False)
    GPIO.output(PIN_MOTOR_UP_SLOW, False)
    GPIO.output(PIN_MOTOR_DOWN_SLOW, False)
    GPIO.output(PIN_WARNLAMPE, False)


def motor_up_fast():
    all_outputs_off()
    GPIO.output(PIN_MOTOR_UP_FAST, True)


def motor_down_fast():
    all_outputs_off()
    GPIO.output(PIN_MOTOR_DOWN_FAST, True)


def motor_up_slow():
    all_outputs_off()
    GPIO.output(PIN_MOTOR_UP_SLOW, True)


def motor_down_slow():
    all_outputs_off()
    GPIO.output(PIN_MOTOR_DOWN_SLOW, True)


def motor_stop():
    all_outputs_off()


def warn_on():
    GPIO.output(PIN_WARNLAMPE, True)


def warn_off():
    GPIO.output(PIN_WARNLAMPE, False)
