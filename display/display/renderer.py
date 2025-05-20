# renderer.py
from typing import Any, Dict, List

import pygame


class ScreenRenderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def render(self, commands: List[Dict[str, Any]]):
        # print(f"Rendering {len(commands)} commands")

        for cmd in commands:
            try:
                if not cmd.get("type"):
                    continue
                t = cmd["type"]
                color = tuple(cmd.get("color", [255, 255, 255]))
                if t == "rect":
                    r = pygame.Rect(cmd["x"], cmd["y"], cmd["w"], cmd["h"])
                    pygame.draw.rect(self.screen, color, r)
                elif t == "circle":
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (cmd["x"], cmd["y"]),
                        cmd["radius"]
                    )
                elif t == "text":
                    size = cmd.get("size", 48)
                    font = pygame.font.SysFont(None, size)
                    surf = font.render(cmd["text"], True, color)
                    self.screen.blit(surf, (cmd["x"], cmd["y"]))
                elif t == "poly":
                    points = cmd.get("points", [])
                    if len(points) < 3:
                        print("Not enough points for polygon")
                        continue
                    pygame.draw.polygon(self.screen, color, points)
                # …and so on for other shapes
            except Exception as e:
                print(f"Error rendering command {cmd}: {e}")
