"""Implement a Countdown iterator class.

Must implement __iter__ (returns self) and __next__ (returns current
value and decrements, raises StopIteration when done).
"""
from __future__ import annotations


class Countdown:
    """Iterator that counts down from start to 0 inclusive.

    Examples:
        list(Countdown(3))   # [3, 2, 1, 0]
        list(Countdown(0))   # [0]
        for n in Countdown(2):
            print(n)   # 2, 1, 0
    """

    def __init__(self, start):
        pass  # TODO

    def __iter__(self):
        pass  # TODO — return self

    def __next__(self):
        pass  # TODO — return current value and decrement; raise StopIteration when done
