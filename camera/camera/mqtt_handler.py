# mqtt_handler.py
import json
from typing import Any, Dict, List

import paho.mqtt.client as mqtt
from message import Messages
from paho.mqtt.client import MQTTMessage


class Form():
    pass


class Polygon(Form):
    def __init__(self, points: List[tuple[int, int]]):
        self.points = points

    def set_color(self, color: List[int]):
        self.color = tuple(color)

    def get_color(self) -> List[int]:
        return list(self.color)


class Text(Form):
    def __init__(self, text: str, size: int = 36, color: List[int] = [255, 255, 255]):
        self.text = text
        self.size = size
        self.color = tuple(color)

    def set_color(self, color: List[int]):
        self.color = tuple(color)

    def get_color(self) -> List[int]:
        return list(self.color)


class MqttHandler:
    def __init__(self, broker: str, port: int, topic: str, username, password):
        self.topic = topic
        self._last_messages = Messages()

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect

        print(f"Connecting to MQTT broker {broker}:{port}...")
        self.client.connect(broker, port, keepalive=60)
        print("Connected to MQTT broker... Starting loop...")
        self.client.loop_start()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected — subscribing to {self.topic}")
            client.subscribe(self.topic)
        else:
            print(f"MQTT connect failed (code {rc})")

    def send(self, message: Messages):
        if message.get_all_messages() == self._last_messages.get_all_messages():
            return

        for msg_id, msg in message.get_all_messages().items():
            if isinstance(msg, Polygon):
                payload = {
                    "type": "polygon",
                    "points": msg.points,
                    "color": msg.get_color(),
                }
            elif isinstance(msg, Text):
                payload = {
                    "type": "text",
                    "text": msg.text,
                    "size": msg.size,
                    "color": msg.get_color(),
                }
            else:
                raise ValueError("Unsupported message type")

            self.client.publish(self.topic, json.dumps(payload))
            self._last_messages.add_message(msg, msg_id)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
