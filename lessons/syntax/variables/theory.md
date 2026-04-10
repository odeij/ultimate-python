# Variables & References: Names, Not Boxes

## Names Are References, Not Boxes

In C, a variable is a named memory location:

```c
int x = 5;
// x IS a 4-byte box at some address.  The box contains 5.
```

In Python, a variable is a **name** bound to an **object**:

```python
x = 5
# x is a label that points to an int object containing 5.
```

This one shift in mental model explains almost every Python "gotcha".

**C model** — variable IS the storage:
```
x: [ 5 ]
```

**Python model** — variable is a tag pointing to an object:
```
x ──► [int object: value=5, refcount=1]
```

When you write `y = x` in C you get an independent copy:
```
x: [ 5 ]
y: [ 5 ]   ← separate box, independent value
```

When you write `y = x` in Python you get a second name for the same object:
```
x ──► [list: [1, 2, 3]] ◄── y
```

Both names point to the **same object**. No list was copied.

---

## Mutable vs Immutable: The Core Distinction

The reference model bites you hardest with **mutable** objects (lists, dicts, sets).

```python
a = [1, 2, 3]
b = a          # b holds a copy of the REFERENCE, not the list
b.append(4)    # mutates the object both names point to

print(a)       # [1, 2, 3, 4]  ← "a changed too!"
```

This is not a bug.  In C terms: `b` is a pointer to the same heap-allocated
array as `a`.  Calling `b.append(4)` is like `b->push_back(4)` in C++.

**Immutable** objects (int, str, tuple, float, bool) cannot be mutated.
Rebinding a name to an immutable always creates a new object:

```python
x = 42
y = x
y = y + 1      # int + int → NEW int object; rebinds y to it

print(x)       # 42 — x still points to the original object
print(y)       # 43 — y now points to a different object
```

**The rule**: mutation changes the object.  Reassignment changes where the name points.

| Operation | What happens |
|-----------|-------------|
| `a = [1,2,3]` | Creates a list object; binds `a` to it |
| `b = a` | Binds `b` to the same object as `a` |
| `b.append(4)` | Mutates the shared object — both `a` and `b` see it |
| `b = b + [4]` | Creates a NEW list; rebinds `b` — `a` unchanged |

---

## Identity vs Equality

Python has two distinct comparison operators:

| Operator | Checks | C equivalent |
|----------|--------|-------------|
| `a == b` | Equal values (`__eq__`) | `*a == *b` |
| `a is b` | Same object (`id(a) == id(b)`) | `a == b` (pointer comparison) |

```python
a = [1, 2, 3]
b = [1, 2, 3]   # separate list with equal contents
c = a

print(a == b)   # True  — equal values
print(a is b)   # False — different objects in memory
print(a is c)   # True  — same object
print(id(a) == id(c))  # True — same address
```

`id()` gives you the CPython memory address.  It is the Python equivalent of
casting a pointer to `uintptr_t` in C.

**Rule**: always use `==` for value comparison.  Only use `is` to check for
`None` (`if x is None`) or to explicitly test identity.

---

## Practical Patterns

**Copying a list**:
```python
original = [1, 2, 3]

shallow = original.copy()     # or list(original) or original[:]
deep    = import copy; copy.deepcopy(original)  # for nested structures
```

**The mutable default argument gotcha** (preview of the functions lesson):
```python
# BROKEN: the default list is created ONCE when the function is defined
def append_to(item, lst=[]):
    lst.append(item)
    return lst

append_to(1)   # [1]
append_to(2)   # [1, 2]  ← same list!

# CORRECT: use None as sentinel
def append_to(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

**Quick reference**:
```python
import sys

x = "hello"
y = x

# All of these are True
assert x is y                # same object
assert id(x) == id(y)       # same address
assert sys.getrefcount(x) >= 2  # at least two references exist
```
