"""Tests for flatten."""
from pathlib import Path
import importlib.util
import ast


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_flatten(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.flatten([[1, 2], [3, 4], [5, 6]]) == [1, 2, 3, 4, 5, 6]


def test_uneven_rows(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.flatten([[1], [2, 3, 4], [5]]) == [1, 2, 3, 4, 5]


def test_empty_outer(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.flatten([]) == []


def test_empty_inner(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.flatten([[]]) == []
    assert mod.flatten([[], [1, 2], []]) == [1, 2]


def test_single_row(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.flatten([[10, 20, 30]]) == [10, 20, 30]


def test_uses_comprehension(solution_path: Path) -> None:
    """Check that the solution uses a list comprehension, not append."""
    source = solution_path.read_text()
    tree = ast.parse(source)

    has_comprehension = any(
        isinstance(node, ast.ListComp)
        for node in ast.walk(tree)
    )
    assert has_comprehension, \
        "Solution must use a list comprehension (not a for loop with append)"

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "append":
            raise AssertionError(
                "Do not use .append() — use a list comprehension"
            )


TEST_CASES = [
    ("Basic 2×3 matrix", test_basic_flatten),
    ("Uneven row lengths", test_uneven_rows),
    ("Empty outer list", test_empty_outer),
    ("Empty inner list(s)", test_empty_inner),
    ("Single row", test_single_row),
    ("Uses list comprehension (no append)", test_uses_comprehension),
]
