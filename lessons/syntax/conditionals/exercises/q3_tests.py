"""Tests for the safe_divide exercise."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("_solution", solution_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _test_normal_division(path: Path) -> None:
    sol = _load(path)
    result = sol.safe_divide(10, 2)
    assert result == 5.0, f"safe_divide(10, 2) should be 5.0, got {result!r}"


def _test_zero_denominator(path: Path) -> None:
    sol = _load(path)
    result = sol.safe_divide(7, 0)
    assert result == 0.0, f"safe_divide(7, 0) should be 0.0, got {result!r}"


def _test_zero_numerator(path: Path) -> None:
    sol = _load(path)
    result = sol.safe_divide(0, 5)
    assert result == 0.0, f"safe_divide(0, 5) should be 0.0, got {result!r}"


def _test_negative(path: Path) -> None:
    sol = _load(path)
    result = sol.safe_divide(-6, 2)
    assert result == -3.0, f"safe_divide(-6, 2) should be -3.0, got {result!r}"


def _test_returns_float(path: Path) -> None:
    sol = _load(path)
    result = sol.safe_divide(7, 0)
    assert isinstance(result, float), (
        f"Return type must be float, got {type(result).__name__!r}.\n"
        "  Hint: use `0.0` (not `0`) as the fallback."
    )


def _test_no_if_statement(path: Path) -> None:
    """Check that the solution uses a single expression, not an if block."""
    import ast
    source = path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            # IfExp is the ternary `x if cond else y` — that is allowed
            if isinstance(node, ast.If):
                raise AssertionError(
                    "The function should not use an `if` block — "
                    "use short-circuit `and`/`or` or a ternary expression."
                )


TEST_CASES = [
    ("Normal division: 10 / 2 → 5.0",     _test_normal_division),
    ("Zero denominator: 7 / 0 → 0.0",     _test_zero_denominator),
    ("Zero numerator: 0 / 5 → 0.0",       _test_zero_numerator),
    ("Negative: -6 / 2 → -3.0",           _test_negative),
    ("Return type is float",               _test_returns_float),
    ("No `if` block (use short-circuit)",  _test_no_if_statement),
]
