# __main__.py
import os
import sys

import pygame
from dotenv import load_dotenv
from mqtt_handler import MqttHandler
from pygame.locals import FULLSCREEN, KEYDOWN, QUIT, K_q
from renderer import ScreenRenderer

load_dotenv()


# initialize pygame
pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("MQTT Display")
clock = pygame.time.Clock()

# init MQTT & renderer
mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                   int(os.getenv("MQTT_PORT")),
                   os.getenv("MQTT_TOPIC"),
                   os.getenv("MQTT_USER"),
                   os.getenv("MQTT_PASSWORD"))
renderer = ScreenRenderer(screen)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_q):
            running = False

    screen.fill((0, 0, 0))
    # print(f"commands: {mqtt.draw_commands}")
    renderer.render(mqtt.messages.get_all_messages())
    pygame.display.flip()
    clock.tick(30)

# clean up
mqtt.disconnect()
pygame.quit()
sys.exit()
