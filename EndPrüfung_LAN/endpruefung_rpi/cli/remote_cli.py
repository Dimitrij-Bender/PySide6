#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "server"))
from controller import EndpruefungController  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SSH-Steuerung für Endprüfung")
    parser.add_argument("command", choices=["status", "move", "auto", "savepos", "read7281"])
    parser.add_argument("value", nargs="?")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config" / "default_config.json"))
    args = parser.parse_args()

    ctl = EndpruefungController(args.config)
    ctl.start()

    if args.command == "status":
        print(json.dumps(ctl.get_state().__dict__, indent=2, ensure_ascii=False))
        return 0
    if args.command == "move":
        if not args.value:
            raise SystemExit("move braucht einen Wert")
        if args.value == "stop":
            ctl.stop_motion()
        else:
            ctl.manual_move(args.value)
        print(f"OK move {args.value}")
        return 0
    if args.command == "auto":
        if not args.value:
            raise SystemExit("auto braucht einen Positionsnamen")
        ctl.auto_move_to(args.value)
        print(f"OK auto {args.value}")
        return 0
    if args.command == "savepos":
        if not args.value:
            raise SystemExit("savepos braucht einen Positionsnamen")
        ctl.save_current_position(args.value)
        print(f"OK savepos {args.value}")
        return 0
    if args.command == "read7281":
        ctl.connect_7281()
        print(ctl.read_7281())
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
