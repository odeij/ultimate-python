"""Tests for running_average generator."""
from pathlib import Path
import importlib.util
import ast
import types


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_average(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = list(mod.running_average([10, 20, 30]))
    assert result == [10.0, 15.0, 20.0], f"Got {result}"


def test_four_elements(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = list(mod.running_average([4, 2, 6, 8]))
    assert result == [4.0, 3.0, 4.0, 5.0], f"Got {result}"


def test_empty_input(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert list(mod.running_average([])) == []


def test_single_element(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert list(mod.running_average([7])) == [7.0]


def test_returns_generator(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = mod.running_average([1, 2, 3])
    assert isinstance(result, types.GeneratorType), \
        "running_average must be a generator function (use yield)"


def test_yields_floats(solution_path: Path) -> None:
    mod = _load(solution_path)
    for val in mod.running_average([1, 2, 3]):
        assert isinstance(val, float), f"Expected float, got {type(val)}"


TEST_CASES = [
    ("Basic three-element average", test_basic_average),
    ("Four-element average", test_four_elements),
    ("Empty input yields nothing", test_empty_input),
    ("Single element yields itself", test_single_element),
    ("Returns a generator object", test_returns_generator),
    ("Yields floats", test_yields_floats),
]
