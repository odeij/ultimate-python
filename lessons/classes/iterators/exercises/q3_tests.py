"""Tests for Countdown iterator."""
from pathlib import Path
import importlib.util


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_countdown(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert list(mod.Countdown(3)) == [3, 2, 1, 0]


def test_countdown_from_zero(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert list(mod.Countdown(0)) == [0]


def test_countdown_from_five(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert list(mod.Countdown(5)) == [5, 4, 3, 2, 1, 0]


def test_iter_returns_self(solution_path: Path) -> None:
    mod = _load(solution_path)
    c = mod.Countdown(3)
    assert iter(c) is c, "__iter__ must return self"


def test_stops_after_zero(solution_path: Path) -> None:
    mod = _load(solution_path)
    c = mod.Countdown(1)
    assert next(c) == 1
    assert next(c) == 0
    try:
        next(c)
        assert False, "Expected StopIteration after 0"
    except StopIteration:
        pass


def test_usable_in_for_loop(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = []
    for n in mod.Countdown(3):
        result.append(n)
    assert result == [3, 2, 1, 0]


TEST_CASES = [
    ("Basic countdown from 3", test_basic_countdown),
    ("Countdown from 0 yields [0]", test_countdown_from_zero),
    ("Countdown from 5", test_countdown_from_five),
    ("__iter__ returns self", test_iter_returns_self),
    ("StopIteration raised after 0", test_stops_after_zero),
    ("Works in a for loop", test_usable_in_for_loop),
]
