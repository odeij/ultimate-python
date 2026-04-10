"""Implement Rectangle and Square using inheritance.

Square must call super().__init__ — do NOT redefine area() or perimeter().
"""
from __future__ import annotations


class Rectangle:
    """A rectangle with width and height.

    Examples:
        r = Rectangle(4, 3)
        r.area()       # 12
        r.perimeter()  # 14
        repr(r)        # "Rectangle(width=4, height=3)"
    """

    def __init__(self, width, height):
        pass  # TODO

    def area(self):
        pass  # TODO

    def perimeter(self):
        pass  # TODO

    def __repr__(self):
        pass  # TODO  — "Rectangle(width=W, height=H)"


class Square(Rectangle):
    """A square — a rectangle where width == height.

    Examples:
        s = Square(5)
        s.area()       # 25  (inherited from Rectangle)
        s.perimeter()  # 20  (inherited from Rectangle)
        repr(s)        # "Square(side=5)"
        isinstance(s, Rectangle)  # True
    """

    def __init__(self, side):
        pass  # TODO — one line: call super().__init__

    def __repr__(self):
        pass  # TODO  — "Square(side=S)"
