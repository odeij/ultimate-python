## Inheritance and the Object Hierarchy

Every Python class implicitly inherits from `object`. `object` provides the
default implementations of `__repr__`, `__eq__`, `__hash__`, and many others:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

dog = Dog("Rex")
dog.speak()             # "Rex says Woof!"
isinstance(dog, Dog)    # True
isinstance(dog, Animal) # True — subtype relationship
isinstance(dog, object) # True — everything is an object
```

**C mental model**: Python inheritance is like embedding a base struct as the
first member and having a vtable (function pointer table) for virtual methods.
Python's vtable is the class's `__dict__` plus the MRO chain.

## super() and Cooperative Inheritance

`super()` returns a proxy object that looks up methods starting at the **next
class in the MRO**, not necessarily the direct parent. This enables cooperative
multiple inheritance:

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal.__init__: {name}")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # calls Animal.__init__
        self.breed = breed
        print(f"Dog.__init__: {breed}")

dog = Dog("Rex", "Labrador")
# Animal.__init__: Rex
# Dog.__init__: Labrador
```

Always call `super().__init__(...)` unless you explicitly want to skip parent
initialisation. Skipping it leaves parent attributes unset.

## The Method Resolution Order (MRO)

Python uses the **C3 linearisation algorithm** to compute a consistent method
lookup order for multiple inheritance:

```python
class A:
    def who(self): return "A"

class B(A):
    def who(self): return "B"

class C(A):
    def who(self): return "C"

class D(B, C):
    pass

D.__mro__
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

D().who()   # "B" — B comes before C in D's MRO
```

The MRO guarantees: a class always appears before its parents, and base class
order (left to right in the class definition) is respected.

```python
# Inspect the MRO
for cls in D.__mro__:
    print(cls)
```

## Method Overriding

A subclass overrides a method simply by defining it:

```python
class Shape:
    def area(self):
        raise NotImplementedError(f"{type(self).__name__} must implement area()")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, w, h):
        self.width, self.height = w, h

    def area(self):
        return self.width * self.height

shapes = [Circle(5), Rectangle(4, 3)]
for s in shapes:
    print(s.area())   # polymorphism — correct method called for each type
```

## @property: Computed Attributes

`@property` turns a method into a read-only attribute. It's syntactic sugar for
the descriptor protocol:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
c.radius         # 5    — calls the getter
c.radius = 10   # calls the setter with validation
c.area           # 314.159... — computed, not stored
c.area = 0      # AttributeError — no setter defined
```

`@property` replaces direct attribute access with function calls transparently.
In C terms: it's like replacing a struct field with accessor functions, but the
call syntax stays the same.
