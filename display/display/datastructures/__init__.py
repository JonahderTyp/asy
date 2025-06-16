
from __future__ import annotations

import json
from pprint import pprint
from typing import Dict, List

import cv2
import numpy as np

from ..geometry import Point2Da
from ..transformer import HomographyTransformer


class Form:
    def __init__(self, color):
        self.color = (255, 255, 255)
        if color:
            self.color = color

    def to_json(self) -> str:
        """Convert the Form to a JSON string."""
        return json.dumps({
            "type": self.__class__.__name__,
            "color": self.color
        })

    @staticmethod
    def from_json(cls, json_str: str) -> 'Form':
        raise NotImplementedError(
            "Subclasses must implement from_json method.")


class Circle(Form):
    def __init__(self, color, center: Point2Da, radius: float = 0, fill: bool = False):
        super().__init__(color)
        self.center = center
        self.radius = radius
        self.fill = fill

    def to_json(self):
        """Convert the Circle to a JSON string."""
        return json.dumps({
            "type": "Circle",
            "color": self.color,
            "center": {"x": self.center.x, "y": self.center.y},
            "radius": self.radius,
            "fill": self.fill
        })

    @staticmethod
    def from_dict(data: Dict) -> 'Circle':
        center = Point2Da(data["center"]["x"], data["center"]["y"])
        return Circle(color=data["color"], center=center, radius=data["radius"], fill=data.get("fill", False))

    @staticmethod
    def from_json(json_str: str) -> 'Circle':
        """Create a Circle from a JSON string."""
        print("Circle.from_json", json_str)
        data = json.loads(json_str)
        return Circle.from_dict(data)

    def __str__(self):
        return f"Circle(center=({self.center[0]}, {self.center[1]}), radius={self.radius}, color={self.color}, fill={self.fill})"

    def __repr__(self):
        return self.__str__()


class Polygon(Form):
    def __init__(self, color, points: List[Point2Da]):
        super().__init__(color)
        self.points = points

    @property
    def num_points(self):
        return len(self.points)

    def to_json(self):
        """Convert the Polygon to a JSON string."""
        return json.dumps({
            "type": "Polygon",
            "color": self.color,
            "points": [{"x": p[0], "y": p[1]} for p in self.points]
        })

    @staticmethod
    def from_dict(data: Dict) -> 'Polygon':
        points = [Point2Da(p["x"], p["y"]) for p in data["points"]]
        return Polygon(color=data["color"], points=points)

    @staticmethod
    def from_json(json_str: str) -> 'Polygon':
        """Create a Polygon from a JSON string."""
        data = json.loads(json_str)
        return Polygon.from_dict(data)


class Text(Form):
    def __init__(self, color, position: Point2Da, text: str, size: int = 36):
        super().__init__(color)
        self.position: Point2Da = position
        self.text = text
        self.size = size

    def to_json(self):
        return json.dumps({
            "type": "Text",
            "color": self.color,
            "position": self.position.to_json(),
            "text": self.text,
            "size": self.size
        })

    @staticmethod
    def from_dict(data: Dict) -> 'Text':
        position = Point2Da.from_json(data["position"])
        return Text(color=data["color"], position=position, text=data["text"], size=data.get("size", 36))

    @staticmethod
    def from_json(json_str: str) -> 'Text':
        """Create a Text from a JSON string."""
        data = json.loads(json_str)
        return Text.from_dict(data)


class Playfield:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)
        self._forms: Dict[int, Form | None] = {}

    def clear(self):
        for id in self._forms:
            self._forms[id] = None

    def put_form(self, id: int, form: Form):
        self._forms[int(id)] = form

    def add_form(self, id: int, form: Form):
        if id in self._forms:
            raise KeyError(f"Form with id {id} already exists.")
        self.put_form(id, form)

    def update_form(self, id: int, form: Form):
        if id not in self._forms:
            raise KeyError(f"Form with id {id} not found.")
        self._forms[id] = form

    def delete_form(self, id):
        if id in self._forms:
            self._forms[id] = None
        else:
            raise KeyError(f"Form with id {id} not found.")

    def get_form(self, id):
        return self._forms.get(id)

    def get_forms(self):
        return self._forms

    def __repr__(self):
        return f"playfield({self.width}, {self.height})"

    def to_json(self) -> str:
        """Convert the Playfield to a JSON string."""
        forms_json = {id: form.to_json()
                      for id, form in self._forms.items()}
        return json.dumps({
            "width": self.width,
            "height": self.height,
            "forms": forms_json
        })

    @staticmethod
    def from_json(json_str: str) -> 'Playfield':
        """Create a Playfield from a JSON string."""
        try:
            data = json.loads(json_str)
        except Exception as e:
            print("Error decoding JSON:", e)
            pprint(json_str)
            return None

        playfield = Playfield(data["width"], data["height"])

        print(
            f"Decoded Playfield: {data['width']}x{data['height']}, {len(data['forms'])} forms")

        for id, form_json in data["forms"].items():
            form_json = json.loads(str(form_json)) if isinstance(
                form_json, str) else form_json

            # print(form_json)
            # print(type(form_json))

            # print(form_json["type"])

            if form_json["type"] == "Circle":
                form = Circle.from_dict(form_json)
            elif form_json["type"] == "Polygon":
                form = Polygon.from_dict(form_json)
            elif form_json["type"] == "Text":
                form = Text.from_dict(form_json)
            else:
                raise ValueError(f"Unknown form type: {form_json['type']}")
            playfield.put_form(int(id), form)
        return playfield

    def render(self, offset: Point2Da = Point2Da(100, 100)) -> np.ndarray:
        """
        Render the playfield to an image with all forms drawn.
        """
        # Create a blank image (black background)

        image = np.full((self.height + int(offset.x * 2),
                         self.width + int(offset.y * 2),
                         3), fill_value=127,
                        dtype=np.uint8)

        image[int(offset.y):int(offset.y + self.height),
              int(offset.x):int(offset.x + self.width)] = (0, 0, 0)

        for form in self._forms.values():
            if form is None:
                continue

            if isinstance(form, Circle):
                center = (int(form.center[0] + offset.x),
                          int(form.center[1] + offset.y))
                radius = int(form.radius)
                color = tuple(map(int, form.color))
                thickness = -1 if form.fill else 2
                cv2.circle(image, center, radius, color, thickness)

            elif isinstance(form, Polygon):
                pts = np.array([
                    [int(p[0] + offset.x), int(p[1] + offset.y)]
                    for p in form.points
                ], dtype=np.int32)
                pts = pts.reshape((-1, 1, 2))
                color = tuple(map(int, form.color))
                cv2.polylines(image, [pts], isClosed=True,
                              color=color, thickness=2)

            elif isinstance(form, Text):
                position = (
                    int(form.position[0] + offset.x), int(form.position[1] + offset.y))
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = form.size / 36
                color = tuple(map(int, form.color))
                thickness = 1
                cv2.putText(image, form.text, position, font,
                            font_scale, color, thickness, lineType=cv2.LINE_AA)

            else:
                raise ValueError(
                    f"Unknown form type during rendering: {type(form)}")

        return image

    def transform(self, transformer: HomographyTransformer, dest_pf: Playfield) -> Playfield:
        """
        Apply a transformation to all forms in the playfield.
        """

        for id, form in self._forms.items():
            if form is None:
                continue
            elif isinstance(form, Circle):
                center = transformer.map_point(form.center)
                dest_pf.put_form(id, Circle(
                    color=form.color,
                    center=Point2Da(center[0], center[1]),
                    radius=form.radius,
                    fill=form.fill
                ))
            elif isinstance(form, Polygon):
                dest_pf.put_form(id, Polygon(
                    color=form.color,
                    points=[transformer.map_point(p) for p in form.points]
                ))
            elif isinstance(form, Text):
                dest_pf.put_form(id, Text(
                    color=form.color,
                    position=transformer.map_point(form.position),
                    text=form.text,
                    size=form.size
                ))
            else:
                raise ValueError(f"Unknown form type: {type(form)}")
            # Other forms can be added here as needed

        return dest_pf
