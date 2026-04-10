"""Tests for the is_same_object exercise.

Convention used by the exercise runner:
  TEST_CASES: list[tuple[str, Callable[[Path], None]]]

Each function receives the path to the user's solution file and raises
AssertionError on failure.  The display name is the first element of
each tuple.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load(solution_path: Path):
    """Dynamically import the user's solution file."""
    spec = importlib.util.spec_from_file_location("_solution", solution_path)
    assert spec and spec.loader, f"Cannot load solution at {solution_path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _test_same_list(path: Path) -> None:
    sol = _load(path)
    lst = [1, 2, 3]
    ref = lst
    result = sol.is_same_object(lst, ref)
    assert result is True, (
        f"Expected True for two names bound to the same list, got {result!r}.\n"
        "  Hint: `ref = lst` makes both names point to the same object."
    )


def _test_different_lists(path: Path) -> None:
    sol = _load(path)
    a = [1, 2, 3]
    b = [1, 2, 3]
    result = sol.is_same_object(a, b)
    assert result is False, (
        f"Expected False for two different lists with equal values, got {result!r}.\n"
        "  Hint: [1,2,3] creates a NEW list each time — different objects, equal values."
    )


def _test_self_identity(path: Path) -> None:
    sol = _load(path)
    x = object()
    result = sol.is_same_object(x, x)
    assert result is True, (
        f"Expected True when comparing an object to itself, got {result!r}."
    )


def _test_returns_bool(path: Path) -> None:
    sol = _load(path)
    lst = [1, 2, 3]
    result = sol.is_same_object(lst, lst)
    assert isinstance(result, bool), (
        f"Return value must be a bool, got {type(result).__name__!r}.\n"
        "  Hint: `is` already returns a bool — return it directly."
    )


def _test_none_vs_none(path: Path) -> None:
    sol = _load(path)
    # None is a singleton — there is only one None object in Python
    result = sol.is_same_object(None, None)
    assert result is True, (
        f"None is a singleton. is_same_object(None, None) should be True, got {result!r}."
    )


# ---------------------------------------------------------------------------
# TEST_CASES: ordered list consumed by the exercise runner
# ---------------------------------------------------------------------------

TEST_CASES = [
    ("Same list reference → True",           _test_same_list),
    ("Two different lists (equal values) → False", _test_different_lists),
    ("Object compared to itself → True",     _test_self_identity),
    ("Return type is bool",                  _test_returns_bool),
    ("None is a singleton → True",           _test_none_vs_none),
]
