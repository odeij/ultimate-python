"""
Descriptors — the protocol that powers @property, @classmethod, and PyTorch's Parameter.

C programmer's translation:
  In C, struct field access is a simple memory offset read.
  In Python, attribute access goes through a lookup chain that can intercept reads,
  writes, and deletes via the descriptor protocol.

The descriptor protocol:
  An object is a descriptor if it defines any of:
    __get__(self, obj, objtype=None)  -> value
    __set__(self, obj, value)
    __delete__(self, obj)

  Data descriptor:    defines __get__ AND __set__ (or __delete__)
                      — takes priority over instance __dict__
  Non-data descriptor: defines ONLY __get__
                      — instance __dict__ takes priority

Why this matters:
  - @property is a descriptor
  - PyTorch's nn.Parameter is a descriptor (how model.weight returns a tensor)
  - Django/SQLAlchemy fields are descriptors
  - Understanding this = understanding how ML framework attribute access works

Topics covered:
  1. Attribute lookup order (MRO chain)
  2. Building @property from scratch
  3. Data descriptor vs non-data descriptor
  4. Typed attribute descriptor (like dataclasses fields)
  5. Cached property (lazy computation with memoization)
"""

import math


# ---------------------------------------------------------------------------
# 1. Attribute lookup order — the full picture
#
# obj.attr resolution order:
#   1. type(obj).__mro__ for DATA descriptors (have __set__)
#   2. obj.__dict__
#   3. type(obj).__mro__ for NON-DATA descriptors (only __get__)
#   4. AttributeError
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 2. Build @property from scratch
# ---------------------------------------------------------------------------

class Property:
    """A reimplementation of Python's built-in @property.

    @property is syntax sugar for:
        attr = property(fget, fset, fdel, doc)

    Which is equivalent to creating a Property descriptor.
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # accessed on the class, not an instance
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


class Circle:
    """Uses our custom Property descriptor."""

    def __init__(self, radius: float):
        self._radius = radius

    @Property
    def radius(self) -> float:
        """Radius of the circle."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @Property
    def area(self) -> float:
        """Area computed from radius (read-only)."""
        return math.pi * self._radius ** 2


# ---------------------------------------------------------------------------
# 3. Typed attribute descriptor — validation on assignment
# This is the pattern Django and SQLAlchemy use for model fields.
# ---------------------------------------------------------------------------

class TypedField:
    """Descriptor that enforces a type constraint on an attribute.

    The descriptor stores the value in the INSTANCE dict under _name,
    not in its own state (which would be shared across all instances).
    """

    def __set_name__(self, owner, name: str) -> None:
        """Called automatically when the descriptor is assigned to a class attribute.

        Python 3.6+: owner is the class, name is the attribute name.
        This replaces the old pattern of passing the name to __init__.
        """
        self.public_name = name
        self.private_name = f"_{name}"   # store value as _<name> in instance dict

    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.public_name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.private_name, value)


class Vector:
    """A typed vector using TypedField descriptors."""

    x = TypedField(float)
    y = TypedField(float)

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)


# ---------------------------------------------------------------------------
# 4. Cached property — lazy, memoized attribute
# Compute expensive value once, cache it in instance dict.
# Python 3.8+ has functools.cached_property but building it shows how it works.
# ---------------------------------------------------------------------------

class CachedProperty:
    """Non-data descriptor that caches computed value in instance __dict__.

    On first access: __get__ is called, value computed and stored in obj.__dict__[name]
    On subsequent accesses: instance __dict__ takes priority (non-data descriptor),
                            so __get__ is NOT called again.
    """

    def __init__(self, func):
        self.func = func
        self.attr_name = None
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name: str) -> None:
        self.attr_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Store in instance dict — next access bypasses this descriptor
        value = self.func(obj)
        obj.__dict__[self.attr_name] = value
        return value


class ExpensiveModel:
    """Simulates a model with expensive initialization."""

    def __init__(self, data: list[float]):
        self.data = data
        self._computed_count = 0

    @CachedProperty
    def mean(self) -> float:
        """Compute mean — only computed once."""
        self._computed_count += 1
        return sum(self.data) / len(self.data)

    @CachedProperty
    def variance(self) -> float:
        """Compute variance — only computed once."""
        self._computed_count += 1
        m = self.mean
        return sum((x - m) ** 2 for x in self.data) / len(self.data)


def main() -> None:
    # Custom Property
    c = Circle(5.0)
    assert abs(c.radius - 5.0) < 1e-9
    assert abs(c.area - math.pi * 25) < 1e-9

    c.radius = 10.0
    assert c.radius == 10.0

    error_raised = False
    try:
        c.radius = -1.0
    except ValueError:
        error_raised = True
    assert error_raised

    # TypedField descriptor
    v = Vector(3.0, 4.0)
    assert v.magnitude() == 5.0

    type_error = False
    try:
        v.x = "not a float"   # type: ignore[assignment]
    except TypeError:
        type_error = True
    assert type_error

    # CachedProperty
    model = ExpensiveModel([1.0, 2.0, 3.0, 4.0, 5.0])
    assert model._computed_count == 0

    mean1 = model.mean
    assert abs(mean1 - 3.0) < 1e-9
    assert model._computed_count == 1

    # Second access — comes from __dict__, descriptor NOT called again
    mean2 = model.mean
    assert mean2 == mean1
    assert model._computed_count == 1   # count did NOT increase

    var = model.variance
    assert abs(var - 2.0) < 1e-9


if __name__ == "__main__":
    main()
