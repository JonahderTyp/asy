
from __future__ import annotations

import json
from typing import Dict, List

import cv2
import numpy as np
from numpy import float64
from numpy.typing import NDArray


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

    def to_json(self) -> str:
        """Convert the Point2D to a JSON string."""
        return json.dumps({"x": self.x, "y": self.y})

    @staticmethod
    def from_json(json_str: str) -> 'Point2Da':
        """Create a Point2D from a JSON string."""
        data = json.loads(json_str)
        return Point2Da(data["x"], data["y"])
