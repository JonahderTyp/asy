import json
import os
from time import sleep
from typing import Any, Dict, List

import cv2
import numpy as np

from ..camera import Camera
from ..datastructures import (Circle, Messages, Playfield, Point2Da, Polygon,
                              Text)
from ..keyboard_listener import KeyboardListener


def calibrate_camera(camera: Camera, cal_file: str = "cal_cam.json"):
    """
    Calibrate the system.
    """
    print(cal_file)
    if os.path.exists(cal_file):
        with open(cal_file, "r") as f:
            points_json: dict = json.load(f)
            points: list[Point2Da] = [
                Point2Da(float(p["x"]), float(p["y"]))
                for p in points_json.values()
            ]
            print(f"Loaded {len(points)} source calibration points.")
    else:
        points: List[Point2Da] = [
            Point2Da(camera.width*(1/4), camera.height*(1/4)),
            Point2Da(camera.width*(3/4), camera.height*(1/4)),
            Point2Da(camera.width*(1/4), camera.height*(3/4)),
            Point2Da(camera.width*(3/4), camera.height*(3/4))
        ]
        print(f"Created {len(points)} default calibration points.")

    selected = -1

    print("Press 'q' or ESC to exit.")
    print("Press 'e' to save calibration data.")
    print("Press '1', '2', '3', '4' to select points.")
    print("Press 'w', 'a', 's', 'd' to move points.")
    print("Hold SHIFT to move points slower.")
    print(f"Selected: {selected + 1}")

    listener = KeyboardListener()

    while True:
        frame = camera.get_frame()
        # rawkey = readchar.readkey()
        if listener.key_available():
            rawkey = listener.get_key()
            print()
        else:
            rawkey = ""
        upper = rawkey.isupper()
        key = rawkey.lower()

        if key == 'q':
            print("Exit key pressed. Goodbye!")
            sleep(1)
            break

        if key == 'e':
            print("Saving calibration data...")
            data = {i: {"x": p.x, "y": p.y} for i, p in enumerate(points)}
            with open(cal_file, "w") as f:
                f.write(json.dumps(data, indent=4))
            sleep(1)
            break

        last_selected = selected
        try:
            var_selected = int(key) - 1
            if (var_selected >= 0 and var_selected < len(points)) and last_selected != var_selected:
                selected = var_selected
                print(f"Selected: {selected + 1}")
        except ValueError:
            pass

        step = 1 if upper else 20

        if selected >= 0:
            if key == 'w':
                points[selected].y -= step
            elif key == 's':
                points[selected].y += step
            elif key == 'a':
                points[selected].x -= step
            elif key == 'd':
                points[selected].x += step

        for i, p in enumerate(points):
            if i == selected:
                color = (255, 0, 0)
            else:
                color = (255, 255, 255)

            cv2.circle(frame, (int(p.x), int(p.y)), 5, (0, 255, 0), 1)
            cv2.circle(frame, (int(p.x), int(p.y)), 1, (0, 255, 0), -1)
            pt = p + Point2Da(20, 20)
            cv2.putText(frame, str(i+1), (int(pt.x), int(pt.y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow('Hands', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("\n")
    listener.stop()
    camera.cap.release()
    cv2.destroyAllWindows()
