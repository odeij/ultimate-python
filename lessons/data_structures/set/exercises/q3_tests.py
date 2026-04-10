"""Tests for find_duplicates."""
from pathlib import Path
import importlib.util


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_duplicates(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.find_duplicates([1, 2, 3, 2, 4, 3]) == [2, 3], \
        "Expected [2, 3]"


def test_no_duplicates(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.find_duplicates([1, 2, 3]) == [], \
        "No duplicates → empty list"


def test_empty_list(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.find_duplicates([]) == [], \
        "Empty input → empty output"


def test_all_same(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.find_duplicates([5, 5, 5]) == [5], \
        "All same → [5]"


def test_sorted_output(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = mod.find_duplicates([4, 1, 3, 1, 2, 4, 3])
    assert result == sorted(result), \
        f"Output must be sorted; got {result}"


def test_each_duplicate_once(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = mod.find_duplicates([1, 1, 1, 2, 2, 2])
    assert result == [1, 2], \
        f"Each duplicate must appear once; got {result}"


TEST_CASES = [
    ("Basic duplicates", test_basic_duplicates),
    ("No duplicates", test_no_duplicates),
    ("Empty list", test_empty_list),
    ("All same element", test_all_same),
    ("Output is sorted", test_sorted_output),
    ("Each duplicate appears once", test_each_duplicate_once),
]
