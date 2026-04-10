"""Tests for word_count."""
from pathlib import Path
import importlib.util
import ast


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_sentence(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = mod.word_count("the cat sat on the mat")
    assert result == {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}, \
        f"Got {result}"


def test_empty_string(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.word_count("") == {}, "Empty string should return {}"


def test_single_word(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.word_count("hello") == {"hello": 1}


def test_repeated_word(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.word_count("hello hello hello") == {"hello": 3}


def test_case_sensitive(solution_path: Path) -> None:
    mod = _load(solution_path)
    result = mod.word_count("Hello hello HELLO")
    assert result == {"Hello": 1, "hello": 1, "HELLO": 1}, \
        "word_count must be case-sensitive"


def test_no_counter_import(solution_path: Path) -> None:
    source = solution_path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            assert not any("Counter" in n for n in names), \
                "Do not use Counter — build the dict manually"


TEST_CASES = [
    ("Basic sentence with duplicate word", test_basic_sentence),
    ("Empty string returns {}", test_empty_string),
    ("Single word", test_single_word),
    ("All same word", test_repeated_word),
    ("Case-sensitive counting", test_case_sensitive),
    ("No Counter import", test_no_counter_import),
]
