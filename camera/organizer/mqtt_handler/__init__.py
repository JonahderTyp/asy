# mqtt_handler.py
import json
from time import sleep
from typing import Any, Dict, List

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from ..datastructures import Circle, Messages, Playfield, Polygon, Text


class MqttHandler:
    def __init__(self, broker: str, port: int, topic: str, username, password):
        self.topic = topic
        self._last_messages = Messages()
        self._connected = False

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect

        print(f"Connecting... to MQTT broker {broker}:{port}...")
        self.client.connect(broker, port, keepalive=60)
        self.client.loop_start()

        while not self._connected:
            pass

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected")
            self._connected = True
        else:
            print(f"MQTT connect failed (code {rc})")

    def send(self, pf: Playfield):
        for id, form in pf.get_forms().items():
            if isinstance(form, Circle):
                payload = {
                    "id": id,
                    "type": "circle",
                    "x": form.center.x,
                    "y": form.center.y,
                    "radius": form.radius,
                    "color": form.color,
                }
            elif isinstance(form, Polygon):
                payload = {
                    "id": id,
                    "type": "polygon",
                    "points": [{"x": p.x, "y": p.y} for p in form.points],
                    "color": form.color,
                }
            elif isinstance(form, Text):
                payload = {
                    "id": id,
                    "type": "text",
                    "x": form.position.x,
                    "y": form.position.y,
                    "text": form.text,
                    "size": form.size,
                    "color": form.color,
                }
            elif form is None:
                payload = {
                    "id": id,
                }
            else:
                raise ValueError(
                    f"Unsupported form type {type(form)} for id {id}")

            self.client.publish(self.topic, json.dumps(payload))
            self._last_messages.add_message(form, id)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
