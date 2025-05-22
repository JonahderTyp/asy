import json
import os
from time import sleep
from typing import Any, Dict, List

import numpy as np
import readchar

from ..datastructures import (Circle, Messages, Playfield, Point2D, Point2Da,
                              Polygon, Text)
from ..mqtt_handler import MqttHandler


def calibrate(mqtt: MqttHandler, cal_file: str = "cal_projector.json"):
    """
    Calibrate the system.
    """

    # Load calibration points from file

    ppf = Playfield(int(os.getenv("PROJECTOR_WIDTH")),
                    int(os.getenv("PROJECTOR_HEIGHT")))

    points: List[Point2Da] = [
        Point2Da(ppf.width*(1/4), ppf.height*(1/4)),
        Point2Da(ppf.width*(3/4), ppf.height*(1/4)),
        Point2Da(ppf.width*(1/4), ppf.height*(3/4)),
        Point2Da(ppf.width*(3/4), ppf.height*(3/4))
    ]

    selected = -1

    print("Press 'q' or ESC to exit.")
    print("Press 'e' to save calibration data.")
    print("Press '1', '2', '3', '4' to select points.")
    print("Press 'w', 'a', 's', 'd' to move points.")
    print("Hold SHIFT to move points slower.")
    print(f"Selected: {selected + 1}")

    while True:
        rawkey = readchar.readkey()
        upper = rawkey.isupper()
        key = rawkey.lower()

        if key == 'q' or key == readchar.key.ESC:
            print("Exit key pressed. Goodbye!")
            ppf.clear()
            mqtt.send(ppf)
            sleep(1)
            break

        if key == 'e':
            print("Saving calibration data...")
            data = {i: {"x": p.x, "y": p.y} for i, p in enumerate(points)}
            with open("cal_projector.json", "w") as f:
                f.write(json.dumps(data, indent=4))
            ppf.clear()
            mqtt.send(ppf)
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
            t = Text(color=color, position=p, text=str(i+1), size=20)
            c = Circle(color=color, center=p, radius=5)
            ppf.put_form(i*10+1, t)
            ppf.put_form(i*10, c)

        mqtt.send(ppf)
