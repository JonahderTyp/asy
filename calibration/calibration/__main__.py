# mqtt_handler.py
import json
import os
from time import sleep
from typing import Any, Dict, List

import readchar
from dotenv import load_dotenv
from mqtt_handler import MqttHandler
from playfield import Playfield, Text, circle, point, polygon

load_dotenv()

mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                   int(os.getenv("MQTT_PORT")),
                   os.getenv("MQTT_TOPIC"),
                   os.getenv("MQTT_USER"),
                   os.getenv("MQTT_PASSWORD"))


pf = Playfield(800, 600)


points = [
    point(0, 0),
    point(0, 100),
    point(100, 0),
    point(100, 100),
]

selected = -1

print("Press any key. Press 'q', Esc, or Ctrl+C to exit.")
print("Calibration Ready")
try:
    while True:
        rawkey = readchar.readkey()
        upper = rawkey.isupper()
        key = rawkey.lower()

        if key == 'q' or key == readchar.key.ESC:
            print("Exit key pressed. Goodbye!")
            pf.clear()
            mqtt.send(pf)
            sleep(1)
            break

        if key == 'e':
            print("Saving calibration data...")
            data = {i: {"x": p.x, "y": p.y} for i, p in enumerate(points)}
            with open("cal.json", "w") as f:
                f.write(json.dumps(data, indent=4))
            pf.clear()
            mqtt.send(pf)
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
            c = circle(color=color, center=p, radius=5)
            pf.put_form(i*10+1, t)
            pf.put_form(i*10, c)

        mqtt.send(pf)


except KeyboardInterrupt:
    print("\nCtrl+C detected. Goodbye!")
