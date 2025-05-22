
from typing import Dict, List

import numpy as np
from numpy import float64
from numpy.typing import NDArray

Point2D = NDArray[float64]


class Point2Da(np.ndarray):
    """A 2-element ndarray with .x and .y properties."""
    def __new__(cls, x: float, y: float, dtype=np.float64):
        # build a 1×2 array, then view it as our subclass
        arr = np.array([x, y], dtype=dtype)
        return arr.view(cls)

    @property
    def x(self) -> float:
        return float(self[0])

    @x.setter
    def x(self, value: float):
        # assign into the underlying array
        self[0] = value

    @property
    def y(self) -> float:
        return float(self[1])

    @y.setter
    def y(self, value: float):
        self[1] = value

    def __repr__(self):
        return f"Point2D(x={self.x}, y={self.y})"


class Messages:

    def __init__(self):
        self.messages: Dict[str, Dict] = {}

    def add_message(self, message, id):
        self.messages[id] = message

    def get_message(self, id):
        return self.messages.get(id)

    def delete_message(self, id):
        if id in self.messages:
            del self.messages[id]
        else:
            raise KeyError(f"Message with id {id} not found.")

    def get_all_messages(self) -> List[Dict]:
        return self.messages.values()


class Form:
    def __init__(self, color):
        self.color = (255, 255, 255)
        if color:
            self.color = color


class Circle(Form):
    def __init__(self, color, center: Point2D, radius: float = 0, fill: bool = False):
        super().__init__(color)
        self.center = center
        self.radius = radius
        self.fill = fill


class Polygon(Form):
    def __init__(self, color, points: List[Point2D]):
        super().__init__(color)
        self.points = points

    @property
    def num_points(self):
        return len(self.points)


class Text(Form):
    def __init__(self, color, position: Point2D, text: str, size: int = 36):
        super().__init__(color)
        self.position = position
        self.text = text
        self.size = size


class Playfield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._forms = {}

    def clear(self):
        for id in self._forms:
            self._forms[id] = None

    def put_form(self, id: int, form: Form):
        self._forms[id] = form

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
