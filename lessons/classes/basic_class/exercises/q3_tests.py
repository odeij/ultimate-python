"""Tests for Vector2D."""
from pathlib import Path
import importlib.util


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_construction_and_repr(solution_path: Path) -> None:
    mod = _load(solution_path)
    v = mod.Vector2D(1, 2)
    assert v.x == 1 and v.y == 2, "x and y attributes must be set"
    assert repr(v) == "Vector2D(1, 2)", f"repr should be 'Vector2D(1, 2)', got {repr(v)!r}"


def test_addition(solution_path: Path) -> None:
    mod = _load(solution_path)
    a = mod.Vector2D(1, 2)
    b = mod.Vector2D(3, 4)
    result = a + b
    assert result.x == 4 and result.y == 6, \
        f"(1,2) + (3,4) should be (4,6), got ({result.x},{result.y})"


def test_addition_returns_new_vector(solution_path: Path) -> None:
    mod = _load(solution_path)
    a = mod.Vector2D(1, 2)
    b = mod.Vector2D(3, 4)
    result = a + b
    assert isinstance(result, mod.Vector2D), "__add__ must return a Vector2D"
    assert a.x == 1 and a.y == 2, "__add__ must not mutate the original"


def test_scalar_multiplication(solution_path: Path) -> None:
    mod = _load(solution_path)
    a = mod.Vector2D(2, 3)
    result = a * 4
    assert result.x == 8 and result.y == 12, \
        f"(2,3) * 4 should be (8,12), got ({result.x},{result.y})"
    assert isinstance(result, mod.Vector2D), "__mul__ must return a Vector2D"


def test_equality(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.Vector2D(1, 2) == mod.Vector2D(1, 2), "Equal vectors should be equal"
    assert mod.Vector2D(1, 2) != mod.Vector2D(1, 3), "Different vectors should not be equal"


def test_repr_format(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert repr(mod.Vector2D(0, 0)) == "Vector2D(0, 0)"
    assert repr(mod.Vector2D(-1, 5)) == "Vector2D(-1, 5)"


TEST_CASES = [
    ("Construction and repr", test_construction_and_repr),
    ("Vector addition result", test_addition),
    ("Addition returns new Vector2D", test_addition_returns_new_vector),
    ("Scalar multiplication", test_scalar_multiplication),
    ("Equality operator", test_equality),
    ("repr format matches exactly", test_repr_format),
]
