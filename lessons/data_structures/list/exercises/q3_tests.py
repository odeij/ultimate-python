"""Tests for rotate_left."""
from pathlib import Path
import importlib.util


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_rotation(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.rotate_left([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2], \
        "rotate_left([1,2,3,4,5], 2) should be [3,4,5,1,2]"


def test_zero_rotation(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.rotate_left([1, 2, 3], 0) == [1, 2, 3], \
        "Rotation by 0 should return the list unchanged"


def test_full_rotation(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.rotate_left([1, 2, 3], 3) == [1, 2, 3], \
        "Rotating by len(lst) should return the original order"


def test_k_larger_than_length(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.rotate_left([1, 2, 3, 4], 6) == [3, 4, 1, 2], \
        "k > len(lst) should use k % len(lst); 6 % 4 == 2"


def test_empty_list(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.rotate_left([], 5) == [], \
        "Rotating an empty list should return []"


def test_does_not_mutate(solution_path: Path) -> None:
    mod = _load(solution_path)
    original = [1, 2, 3, 4, 5]
    copy = original[:]
    mod.rotate_left(original, 2)
    assert original == copy, \
        "rotate_left must not mutate the input list"


TEST_CASES = [
    ("Basic rotation by 2", test_basic_rotation),
    ("Zero rotation", test_zero_rotation),
    ("Full rotation (k == len)", test_full_rotation),
    ("k larger than list length", test_k_larger_than_length),
    ("Empty list", test_empty_list),
    ("Input not mutated", test_does_not_mutate),
]
