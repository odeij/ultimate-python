"""Implement a Timer context manager.

__enter__ records start time and returns self.
__exit__ stores elapsed time in self.elapsed.
Use time.perf_counter() for precision.
"""
from __future__ import annotations
import time


class Timer:
    """Context manager that measures elapsed wall-clock time.

    Usage:
        with Timer() as t:
            do_work()
        print(t.elapsed)   # seconds as a float
    """

    def __enter__(self):
        pass  # TODO

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # TODO
