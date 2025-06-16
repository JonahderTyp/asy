# __main__.py
import json
import os
import sys

import cv2
import pygame
from dotenv import load_dotenv
from pygame.locals import FULLSCREEN, KEYDOWN, QUIT, K_q

from .datastructures import Playfield
from .geometry import Point2Da
from .mqtt_handler import MqttHandler
from .renderer import ScreenRenderer

load_dotenv()


# initialize pygame
# pygame.init()
# info = pygame.display.Info()
# screen = pygame.display.set_mode((800, 600), FULLSCREEN)
# pygame.display.set_caption("MQTT Display")
# clock = pygame.time.Clock()

# init MQTT & renderer
mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                   int(os.getenv("MQTT_PORT")),
                   os.getenv("MQTT_TOPIC"),
                   os.getenv("MQTT_USER"),
                   os.getenv("MQTT_PASSWORD"))
# renderer = ScreenRenderer(screen)


running = True

# Create a named window with fullscreen property
cv2.namedWindow("Fullscreen", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(
    "Fullscreen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


while running:
    # try:
    ppf = Playfield.from_json(mqtt.last_message)
    # except json.JSONDecodeError:
    #     print("Invalid JSON received from MQTT, skipping...")

    if ppf:
        cv2.imshow("Fullscreen", ppf.render(offset=Point2Da(0, 0)))

    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
        break

# clean up
mqtt.disconnect()
cv2.destroyAllWindows()
# pygame.quit()
sys.exit()
