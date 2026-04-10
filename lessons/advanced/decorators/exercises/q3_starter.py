"""Implement a memoization decorator.

Use functools.wraps to preserve metadata.
Expose the cache dict as wrapper.cache.
"""
from __future__ import annotations
from functools import wraps


def memoize(func):
    """Cache the results of func based on its positional arguments.

    The wrapped function must have a .cache attribute pointing to the
    internal dict so callers can inspect cached entries.

    Example:
        @memoize
        def fib(n):
            if n < 2: return n
            return fib(n-1) + fib(n-2)

        fib(10)          # computed recursively
        fib(10)          # returned from cache
        fib.cache        # {(0,): 0, (1,): 1, (2,): 1, ...}
    """
    pass
