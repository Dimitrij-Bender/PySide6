from motor_control import safe_move
from sensor_reader import read_position
from gpio_backend import read_inputs

class EndpruefungController:

    def __init__(self, config):
        self.mode = "manual"
        self.positions = {}

    def start(self):
        print("Controller gestartet")

    def manual_move(self, motion):
        if motion == "up_fast" or motion == "up_slow":
            return safe_move("up")
        elif motion == "down_fast" or motion == "down_slow":
            return safe_move("down")

    def stop_motion(self):
        safe_move("stop")

    def get_state(self):
        class State:
            pass

        s = State()
        s.mode = self.mode
        s.current_position = read_position()
        s.position_source = "Seilzugsensor"
        s.motion = "läuft"
        s.error_reason = None

        inputs = read_inputs()
        if inputs["notaus"]:
            s.error_reason = "NOT-AUS"
        elif inputs["kraft"]:
            s.error_reason = "Kraftnebenschluss"

        return s

    def save_current_position(self, name):
        self.positions[name] = read_position()

    def auto_move_to(self, name):
        print(f"Fahre zu {name}")
