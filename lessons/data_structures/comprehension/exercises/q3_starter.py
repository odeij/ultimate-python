"""Flatten a 2D list using a list comprehension.

Use a list comprehension — NOT a for loop with append.
Do not mutate the input.
"""
from __future__ import annotations


def flatten(matrix: list[list[int]]) -> list[int]:
    """Return a flat list of all elements in matrix, in row-major order.

    Examples:
        flatten([[1, 2], [3, 4], [5, 6]]) == [1, 2, 3, 4, 5, 6]
        flatten([[1], [2, 3, 4], [5]])    == [1, 2, 3, 4, 5]
        flatten([])                        == []
        flatten([[]])                      == []
    """
    pass
