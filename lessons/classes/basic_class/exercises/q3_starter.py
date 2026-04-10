"""Implement a Vector2D class with arithmetic operator support."""
from __future__ import annotations


class Vector2D:
    """A 2D vector supporting addition, scalar multiplication, and equality.

    Examples:
        a = Vector2D(1, 2)
        b = Vector2D(3, 4)
        a + b           # Vector2D(4, 6)
        a * 3           # Vector2D(3, 6)
        a == Vector2D(1, 2)  # True
        repr(a)         # "Vector2D(1, 2)"
    """

    def __init__(self, x, y):
        pass  # TODO

    def __repr__(self):
        pass  # TODO  — must return "Vector2D(x, y)"

    def __add__(self, other):
        pass  # TODO  — vector addition

    def __mul__(self, scalar):
        pass  # TODO  — scalar multiplication

    def __eq__(self, other):
        pass  # TODO  — equality check
