from typing import List


class point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class form:
    def __init__(self, color):
        self.color = (255, 255, 255)
        if color:
            self.color = color


class circle(form):
    def __init__(self, color, center: point, radius: float = 0, fill: bool = False):
        super().__init__(color)
        self.center = center
        self.radius = radius
        self.fill = fill


class polygon(form):
    def __init__(self, color, points: List[point]):
        super().__init__(color)
        self.points = points

    @property
    def num_points(self):
        return len(self.points)


class Text(form):
    def __init__(self, color, position: point, text: str, size: int = 36):
        super().__init__(color)
        self.position = position
        self.text = text
        self.size = size


class Playfield:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self._forms = {}

    def clear(self):
        for id in self._forms:
            self._forms[id] = None

    def put_form(self, id: int, form: form):
        self._forms[id] = form

    def add_form(self, id: int, form: form):
        if id in self._forms:
            raise KeyError(f"Form with id {id} already exists.")
        self.put_form(id, form)

    def update_form(self, id: int, form: form):
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
