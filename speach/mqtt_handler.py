# mqtt_handler.py
import json
from time import sleep
from typing import Any, Dict, List

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage


class MqttHandler:
    def __init__(self, broker: str, port: int, topic: str, username, password):
        self.topic = topic
        self._connected = False

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._last_message = ""

        print(f"Connecting... to MQTT broker {broker}:{port}...")
        self.client.connect(broker, port, keepalive=60)
        self.client.loop_start()

        while not self._connected:
            pass

    def _on_message(self, client: mqtt.Client, userdata: Any, message: MQTTMessage):
        message_data = message.payload.decode('utf-8')
        print(f"Received message on topic {message.topic}: {message_data}")
        self._last_message = message_data

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected")
            self._connected = True
            client.subscribe("asy/voice")
        else:
            print(f"MQTT connect failed (code {rc})")

    def get_message(self) -> str:
        msg = self._last_message
        self._last_message = ""
        return msg

    def send(self, payload: str):
        self.client.publish(self.topic, payload)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
