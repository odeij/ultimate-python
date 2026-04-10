"""Tests for the build_history (mutable default) exercise."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("_solution", solution_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _test_returns_list_with_event(path: Path) -> None:
    sol = _load(path)
    result = sol.build_history("login")
    assert isinstance(result, list), f"Expected list, got {type(result).__name__}"
    assert "login" in result, f"'login' should be in the result, got {result!r}"


def _test_independent_calls(path: Path) -> None:
    sol = _load(path)
    r1 = sol.build_history("first")
    r2 = sol.build_history("second")
    assert r1 is not r2, (
        "Each call without an explicit history arg must return a DIFFERENT list.\n"
        "  r1 and r2 are the same object — you have the mutable default bug."
    )
    assert r1 == ["first"],  f"First call should return ['first'], got {r1!r}"
    assert r2 == ["second"], f"Second call should return ['second'], got {r2!r}"


def _test_explicit_list_is_reused(path: Path) -> None:
    sol = _load(path)
    log: list = []
    sol.build_history("start", log)
    sol.build_history("stop", log)
    assert log == ["start", "stop"], (
        f"When a list is passed explicitly, both events should be appended to it.\n"
        f"Got: {log!r}"
    )


def _test_default_is_none_sentinel(path: Path) -> None:
    """Verify the function uses None as the default, not []."""
    import inspect
    sol = _load(path)
    sig = inspect.signature(sol.build_history)
    param = sig.parameters.get("history")
    assert param is not None, "Function must have a 'history' parameter."
    default = param.default
    assert default is None, (
        f"The default for 'history' should be None, got {default!r}.\n"
        "  Use None as the sentinel: `def build_history(event, history=None):`"
    )


def _test_no_mutable_default(path: Path) -> None:
    """The __defaults__ tuple must not contain a list."""
    sol = _load(path)
    defaults = getattr(sol.build_history, "__defaults__", ()) or ()
    for d in defaults:
        assert not isinstance(d, list), (
            f"Found a list ({d!r}) in __defaults__ — "
            "this is the mutable default bug. Use None instead."
        )


TEST_CASES = [
    ("Returns a list containing the event",       _test_returns_list_with_event),
    ("Two calls without history get fresh lists",  _test_independent_calls),
    ("Explicit list is reused across calls",       _test_explicit_list_is_reused),
    ("Default parameter is None (not [])",         _test_default_is_none_sentinel),
    ("No mutable object in __defaults__",          _test_no_mutable_default),
]
