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

    def send(self, payload: str):
        self.client.publish(self.topic, payload)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
