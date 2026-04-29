from __future__ import annotations

from gpio_backend import (
    read_inputs,
    motor_up_fast,
    motor_down_fast,
    motor_up_slow,
    motor_down_slow,
    motor_stop,
    warn_on,
    warn_off,
)


def safe_move(direction: str):
    inputs = read_inputs()

    if inputs.get("notaus"):
        motor_stop()
        warn_on()
        return "NOT-AUS aktiv"

    if inputs.get("kraft"):
        motor_stop()
        warn_on()
        return "Kraftnebenschluss aktiv"

    if inputs.get("limit_top") and direction in {"up", "up_fast", "up_slow"}:
        motor_stop()
        return "Endschalter oben erreicht"

    if inputs.get("limit_bottom") and direction in {"down", "down_fast", "down_slow"}:
        motor_stop()
        return "Endschalter unten erreicht"

    warn_off()

    if direction in {"up", "up_fast"}:
        motor_up_fast()
    elif direction == "up_slow":
        motor_up_slow()
    elif direction in {"down", "down_fast"}:
        motor_down_fast()
    elif direction == "down_slow":
        motor_down_slow()
    else:
        motor_stop()

    return "OK"
