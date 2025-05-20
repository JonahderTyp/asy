# mqtt_handler.py
import json
from typing import Any, Dict, List

import paho.mqtt.client as mqtt
from message import Messages
from paho.mqtt.client import MQTTMessage


class MqttHandler:
    def __init__(self, broker: str, port: int, topic: str, username, password):
        self.topic = topic
        self.messages = Messages()

        self.client = mqtt.Client()
        self.client.tls_set()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # self.messages.add_message(
        #     {"type": "text", "x": 10, "y": 10, "text": "Connecting", "size": 24, "color": [255, 0, 0]}, 1)

        print(f"Connecting to MQTT broker {broker}:{port}...")
        self.client.connect(broker, port, keepalive=60)
        print("Connected to MQTT broker... Starting loop...")
        self.client.loop_start()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected — subscribing to {self.topic}")
            client.subscribe(self.topic)
            # self.messages.add_message(
            #     {"type": "text", "x": 10, "y": 10, "text": "Connected", "size": 24, "color": [0, 255, 0]}, 1)
        else:
            print(f"MQTT connect failed (code {rc})")

    def _on_message(self, client, userdata, msg: MQTTMessage):
        """
        Expects JSON dicts like:
          {"type":"rect","x":10,"y":20,"w":100,"h":50,"color":[255,0,0]}
          {"type":"circle","x":400,"y":300,"radius":75,"color":[0,0,255]}
          {"type":"text","x":200,"y":50,"text":"hey","size":36,"color":[255,255,255]}
        """
        try:
            cmd = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            print("Invalid JSON:", msg.payload)
            return

        # print(f"Received command: {cmd}")

        if "id" in cmd:
            self.messages.add_message(cmd, cmd["id"])
        else:
            print("Ignored command (no id):", cmd)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
