"""Tests for Timer context manager."""
from pathlib import Path
import importlib.util
import time


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_elapsed_is_float(solution_path: Path) -> None:
    mod = _load(solution_path)
    with mod.Timer() as t:
        pass
    assert hasattr(t, "elapsed"), "Timer must set self.elapsed in __exit__"
    assert isinstance(t.elapsed, float), "elapsed must be a float"


def test_elapsed_is_positive(solution_path: Path) -> None:
    mod = _load(solution_path)
    with mod.Timer() as t:
        pass
    assert t.elapsed >= 0, "elapsed must be non-negative"


def test_enter_returns_self(solution_path: Path) -> None:
    mod = _load(solution_path)
    timer = mod.Timer()
    result = timer.__enter__()
    timer.__exit__(None, None, None)
    assert result is timer, "__enter__ must return self"


def test_measures_sleep(solution_path: Path) -> None:
    mod = _load(solution_path)
    with mod.Timer() as t:
        time.sleep(0.05)
    assert t.elapsed >= 0.04, \
        f"Expected ~0.05s, got {t.elapsed:.4f}s — is perf_counter used?"


def test_does_not_suppress_exceptions(solution_path: Path) -> None:
    mod = _load(solution_path)
    raised = False
    try:
        with mod.Timer():
            raise ValueError("test error")
    except ValueError:
        raised = True
    assert raised, "__exit__ must not suppress exceptions (return falsy)"


TEST_CASES = [
    ("elapsed attribute is a float", test_elapsed_is_float),
    ("elapsed is non-negative", test_elapsed_is_positive),
    ("__enter__ returns self", test_enter_returns_self),
    ("measures ~50ms sleep correctly", test_measures_sleep),
    ("exceptions are not suppressed", test_does_not_suppress_exceptions),
]
