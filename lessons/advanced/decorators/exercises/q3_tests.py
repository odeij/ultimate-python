"""Tests for memoize decorator."""
from pathlib import Path
import importlib.util


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_caching(solution_path: Path) -> None:
    mod = _load(solution_path)
    call_count = {"n": 0}

    @mod.memoize
    def double(x):
        call_count["n"] += 1
        return x * 2

    assert double(5) == 10
    assert double(5) == 10      # second call — should be cached
    assert call_count["n"] == 1, \
        "Function body should only run once for the same arguments"


def test_different_args_not_cached(solution_path: Path) -> None:
    mod = _load(solution_path)

    @mod.memoize
    def square(x):
        return x * x

    assert square(3) == 9
    assert square(4) == 16
    assert square(3) == 9   # from cache


def test_fibonacci_performance(solution_path: Path) -> None:
    mod = _load(solution_path)

    @mod.memoize
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    assert fib(10) == 55
    assert fib(30) == 832040   # would be very slow without memoization


def test_preserves_metadata(solution_path: Path) -> None:
    mod = _load(solution_path)

    @mod.memoize
    def my_func():
        """My docstring."""
        pass

    assert my_func.__name__ == "my_func", \
        "functools.wraps must preserve __name__"
    assert my_func.__doc__ == "My docstring.", \
        "functools.wraps must preserve __doc__"


def test_cache_attribute_exposed(solution_path: Path) -> None:
    mod = _load(solution_path)

    @mod.memoize
    def add(a, b):
        return a + b

    add(1, 2)
    add(3, 4)

    assert hasattr(add, "cache"), "Wrapped function must have a .cache attribute"
    assert isinstance(add.cache, dict), ".cache must be a dict"
    assert (1, 2) in add.cache, "(1, 2) should be a key in add.cache"
    assert add.cache[(1, 2)] == 3


TEST_CASES = [
    ("Caches result on repeated call", test_basic_caching),
    ("Different args computed independently", test_different_args_not_cached),
    ("fib(30) is fast with memoization", test_fibonacci_performance),
    ("functools.wraps preserves __name__ and __doc__", test_preserves_metadata),
    (".cache dict exposed on wrapper", test_cache_attribute_exposed),
]
