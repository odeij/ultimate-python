"""Tests for Rectangle and Square."""
from pathlib import Path
import importlib.util
import ast


def _load(solution_path: Path):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rectangle_area(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.Rectangle(4, 3).area() == 12


def test_rectangle_perimeter(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.Rectangle(4, 3).perimeter() == 14


def test_rectangle_repr(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert repr(mod.Rectangle(4, 3)) == "Rectangle(width=4, height=3)"


def test_square_area(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.Square(5).area() == 25


def test_square_perimeter(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert mod.Square(5).perimeter() == 20


def test_square_repr(solution_path: Path) -> None:
    mod = _load(solution_path)
    assert repr(mod.Square(5)) == "Square(side=5)"


def test_square_is_rectangle(solution_path: Path) -> None:
    mod = _load(solution_path)
    s = mod.Square(3)
    assert isinstance(s, mod.Rectangle), "Square must inherit from Rectangle"


def test_square_uses_super(solution_path: Path) -> None:
    """Square.__init__ must contain a super().__init__ call."""
    source = solution_path.read_text()
    tree = ast.parse(source)

    # Find Square class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Square":
            for item in ast.walk(node):
                if isinstance(item, ast.Call):
                    func = item.func
                    if (isinstance(func, ast.Attribute) and
                            func.attr == "__init__" and
                            isinstance(func.value, ast.Call) and
                            isinstance(func.value.func, ast.Name) and
                            func.value.func.id == "super"):
                        return  # found super().__init__
    raise AssertionError("Square.__init__ must call super().__init__(side, side)")


TEST_CASES = [
    ("Rectangle area", test_rectangle_area),
    ("Rectangle perimeter", test_rectangle_perimeter),
    ("Rectangle repr", test_rectangle_repr),
    ("Square area (inherited)", test_square_area),
    ("Square perimeter (inherited)", test_square_perimeter),
    ("Square repr", test_square_repr),
    ("Square is instance of Rectangle", test_square_is_rectangle),
    ("Square uses super().__init__", test_square_uses_super),
]
