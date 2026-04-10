## Python Objects vs C Structs

In C, a struct is a named block of memory with fixed-size fields at known offsets.
Access is a pointer dereference plus an offset — fast and predictable.

In Python, a class defines a **type**, and each instance is a heap-allocated object
that carries a reference to its type plus a dictionary of attributes:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
p.__dict__        # {'x': 3, 'y': 4}
type(p)           # <class '__main__.Point'>
isinstance(p, Point)  # True
```

The `__dict__` is a regular Python dict — attributes are dynamic. You can add
attributes after construction, and they'll appear in `__dict__`:

```python
p.z = 5
p.__dict__   # {'x': 3, 'y': 4, 'z': 5}
```

**C mental model**: `self` in Python is the equivalent of the first argument in
C struct methods — the pointer to the instance. `self.x` is `obj->x` in C.

## The __init__ Method

`__init__` is the initialiser (not quite a constructor — the object already
exists when __init__ runs; `__new__` creates it). Its job is to set up the
instance's initial state:

```python
class BankAccount:
    def __init__(self, owner, balance=0.0):
        self.owner   = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance:.2f})"

acc = BankAccount("Ada", 1000.0)
acc.deposit(500)
print(acc)   # BankAccount(owner='Ada', balance=1500.00)
```

## __repr__ and __str__

Two methods control how an object is displayed:

| Method | Called by | Purpose |
|--------|-----------|---------|
| `__repr__` | `repr(obj)`, REPL, debugging | Unambiguous representation — ideally `eval(repr(obj)) == obj` |
| `__str__` | `str(obj)`, `print(obj)` | Human-readable representation |

If only `__repr__` is defined, `str()` falls back to it. Always implement
`__repr__` first.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius})"

    def __str__(self):
        return f"{self.celsius}°C  ({self.celsius * 9/5 + 32:.1f}°F)"

t = Temperature(100)
repr(t)    # "Temperature(100)"
str(t)     # "100°C  (212.0°F)"
print(t)   # 100°C  (212.0°F)
```

## Dunder Methods: Python's Operator Overloading

Python uses **dunder** (double underscore) methods to implement operators and
built-in functions. This is how Python's data model works:

```python
a + b      → a.__add__(b)
a == b     → a.__eq__(b)
len(a)     → a.__len__()
a[i]       → a.__getitem__(i)
for x in a → a.__iter__()
```

Implementing these makes your class integrate naturally with Python syntax:

```python
class Matrix2x2:
    def __init__(self, data):
        self.data = data   # [[a, b], [c, d]]

    def __add__(self, other):
        return Matrix2x2([
            [self.data[r][c] + other.data[r][c]
             for c in range(2)] for r in range(2)
        ])

    def __mul__(self, scalar):
        return Matrix2x2([[v * scalar for v in row] for row in self.data])

    def __eq__(self, other):
        return self.data == other.data

    def __repr__(self):
        return f"Matrix2x2({self.data})"
```

## Class vs Instance Attributes

```python
class Dog:
    species = "Canis lupus"   # class attribute — shared by all instances

    def __init__(self, name):
        self.name = name      # instance attribute — unique per instance

rex = Dog("Rex")
buddy = Dog("Buddy")

rex.species    # "Canis lupus"  (found on class, not instance)
rex.name       # "Rex"          (found on instance __dict__)

Dog.species = "Canis familiaris"
rex.species    # "Canis familiaris"  — change propagates to all instances

rex.species = "Wolf"   # creates a NEW instance attribute on rex
rex.species    # "Wolf"     — found on instance first
Dog.species    # "Canis familiaris"  — class attribute unchanged
```

**Rule**: attribute lookup checks the instance `__dict__` first, then the class,
then parent classes (the MRO). This is why instance attributes shadow class ones.
