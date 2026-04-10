"""Implement running_average as a generator function.

Must use yield — not return [...].
Yields a float after each element consumed.
"""
from __future__ import annotations


def running_average(numbers):
    """Yield the running average after each element in numbers.

    Examples:
        list(running_average([10, 20, 30]))    == [10.0, 15.0, 20.0]
        list(running_average([4, 2, 6, 8]))    == [4.0, 3.0, 4.0, 5.0]
        list(running_average([]))              == []
    """
    pass
