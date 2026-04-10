"""
Python Memory Model — understanding the runtime the way you understand C.

C programmer's mental model shift:
  C: you allocate memory, you own it, you free it
  Python: the interpreter manages a heap; you hold references, not memory addresses

Key concepts:
  1. Everything is an object (even int, bool, None)
  2. Variables are references (not boxes), like pointers that auto-dereference
  3. Reference counting + cyclic garbage collector
  4. Identity (id / `is`) vs equality (== / __eq__)
  5. Mutable vs immutable — the source of most "why did Python do that?" bugs
  6. Small integer cache and string interning

Reading this module will answer:
  - Why `a = b; a.append(1)` modifies b   (they both point to the same list)
  - Why `a = b; a += 1`      does NOT modify b   (int is immutable, new object created)
  - Why `x is y` can be True for small integers but not large ones
"""

import sys
import ctypes


# ---------------------------------------------------------------------------
# 1. Variables are references
# ---------------------------------------------------------------------------

def demo_reference_semantics() -> None:
    """Show that assignment binds a name to an object, not a value.

    In C:  int a = 5; int b = a;  — b gets a COPY of the value
    In Python: a = [1,2,3]; b = a  — b gets a COPY of the REFERENCE (pointer)
    """
    # Mutable object: both names point to the same list
    a = [1, 2, 3]
    b = a                   # b = copy of reference, not copy of list
    b.append(4)
    assert a == [1, 2, 3, 4]   # a sees the change — SAME object

    # Immutable object: reassignment creates a new object
    x = 42
    y = x
    y = y + 1               # creates a new int object; rebinds y
    assert x == 42           # x unchanged — not the same as y now

    # Verify with identity check
    a2 = [1, 2]
    b2 = a2
    assert a2 is b2          # same object in memory

    a2 = a2 + [3]            # list + creates a NEW list
    assert a2 is not b2      # different objects now


# ---------------------------------------------------------------------------
# 2. id() and is — Python's equivalent of pointers
# ---------------------------------------------------------------------------

def demo_identity() -> None:
    """id() returns the memory address of the object (in CPython).

    `is` checks if two references point to the SAME object (same address).
    `==` checks if two objects have equal value (__eq__).
    """
    a = [1, 2, 3]
    b = [1, 2, 3]
    assert a == b            # equal values
    assert a is not b        # different objects

    c = a
    assert a is c            # same object
    assert id(a) == id(c)    # same memory address


# ---------------------------------------------------------------------------
# 3. Small integer cache (CPython implementation detail)
# CPython pre-allocates integers -5 to 256.
# This is WHY `x is y` works for small ints but not large ones.
# ---------------------------------------------------------------------------

def demo_integer_cache() -> None:
    """Demonstrate CPython's integer caching.

    IMPORTANT: this is a CPython implementation detail, not a language guarantee.
    Never use `is` to compare integer values in real code — use `==`.
    """
    # Small integers are cached — same object
    a = 100
    b = 100
    assert a is b    # True in CPython (cached)

    # Large integers are NOT cached — different objects each time
    x = 1000
    y = 1000
    # x is y might be False (depends on context/compiler optimization)
    assert x == y    # always use == for value comparison


# ---------------------------------------------------------------------------
# 4. Reference counting
# ---------------------------------------------------------------------------

def demo_reference_counting() -> None:
    """Show how Python tracks references.

    sys.getrefcount() returns the ref count.
    Note: the call to getrefcount itself adds 1 (passing the arg creates a ref).
    """
    obj = [1, 2, 3]
    base_count = sys.getrefcount(obj)   # at least 2 (obj + getrefcount's arg)

    ref2 = obj
    assert sys.getrefcount(obj) == base_count + 1

    del ref2
    assert sys.getrefcount(obj) == base_count   # back to original


# ---------------------------------------------------------------------------
# 5. Mutable default argument — the classic Python gotcha
# In C: static local variable — initialized once, persists across calls
# ---------------------------------------------------------------------------

def broken_append(item: int, lst: list[int] = []) -> list[int]:
    """BROKEN: the default list is created ONCE at function definition time.

    Every call that uses the default shares THE SAME list object.
    This is like a static variable in C — it persists across calls.
    """
    lst.append(item)
    return lst


def correct_append(item: int, lst: list[int] | None = None) -> list[int]:
    """CORRECT: use None sentinel and create a new list each call."""
    if lst is None:
        lst = []
    lst.append(item)
    return lst


def demo_mutable_default() -> None:
    """Show the mutable default argument gotcha."""
    r1 = broken_append(1)
    r2 = broken_append(2)
    # r1 and r2 are THE SAME list object!
    assert r1 is r2
    assert r1 == [1, 2]   # 2 was appended to the same list

    c1 = correct_append(1)
    c2 = correct_append(2)
    assert c1 is not c2
    assert c1 == [1]
    assert c2 == [2]


# ---------------------------------------------------------------------------
# 6. Copy semantics — shallow vs deep copy
# ---------------------------------------------------------------------------

def demo_copy_semantics() -> None:
    """Demonstrate shallow copy vs deep copy.

    Shallow copy: new outer container, same inner objects
    Deep copy:    new outer container AND new inner objects (fully independent)
    """
    import copy

    original = [[1, 2], [3, 4]]

    # Shallow copy
    shallow = copy.copy(original)
    assert shallow is not original          # different list objects
    assert shallow[0] is original[0]        # SAME inner lists

    shallow[0].append(99)
    assert original[0] == [1, 2, 99]       # original is affected!

    # Deep copy
    original2 = [[1, 2], [3, 4]]
    deep = copy.deepcopy(original2)
    assert deep[0] is not original2[0]     # different inner lists

    deep[0].append(99)
    assert original2[0] == [1, 2]          # original NOT affected


# ---------------------------------------------------------------------------
# 7. Memory layout insight: __slots__
# Reduces memory per instance by replacing the instance __dict__ with
# a fixed-size array (like a C struct).
# ---------------------------------------------------------------------------

class NormalPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    # Each instance has a __dict__: {"x": ..., "y": ...}
    # For 1M points this is ~200 bytes/instance = 200MB overhead


class SlottedPoint:
    __slots__ = ("x", "y")   # pre-declare attributes, no __dict__

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    # Each instance: ~56 bytes vs ~232 bytes for NormalPoint
    # Critical for large-scale ML data pipelines


def demo_slots() -> None:
    """Show that __slots__ prevents adding arbitrary attributes."""
    p = SlottedPoint(1.0, 2.0)
    assert p.x == 1.0

    slot_error = False
    try:
        p.z = 3.0   # type: ignore[attr-defined]
    except AttributeError:
        slot_error = True
    assert slot_error


def main() -> None:
    demo_reference_semantics()
    demo_identity()
    demo_integer_cache()
    demo_reference_counting()
    demo_mutable_default()
    demo_copy_semantics()
    demo_slots()


if __name__ == "__main__":
    main()
