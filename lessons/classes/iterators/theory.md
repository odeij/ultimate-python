## The Iterator Protocol

Every `for` loop in Python runs on top of two simple protocols:

1. **Iterable**: has `__iter__()` which returns an iterator
2. **Iterator**: has `__next__()` which returns the next value or raises
   `StopIteration`

```python
# What Python does internally for every for loop:
it = iter(my_collection)      # calls my_collection.__iter__()
while True:
    try:
        item = next(it)        # calls it.__next__()
        # ... loop body ...
    except StopIteration:
        break
```

**C mental model**: an iterator is a cursor struct. The iterable creates the
cursor (`__iter__`); `__next__` advances it and returns the current element.
When the cursor is exhausted, it signals done with `StopIteration`.

## Iterables vs Iterators

| Type | `__iter__` | `__next__` | Multiple passes? |
|------|-----------|------------|-----------------|
| Iterable (list, tuple, str) | ✓ returns fresh iterator | ✗ | Yes |
| Iterator (file, generator) | ✓ returns self | ✓ | No — exhausted after one pass |

```python
lst = [1, 2, 3]        # iterable — not an iterator
it  = iter(lst)        # iterator — wraps the list

next(it)   # 1
next(it)   # 2
next(it)   # 3
next(it)   # StopIteration

# Iterables can produce fresh iterators each time
iter(lst) is iter(lst)   # False — two different iterator objects

# Iterators are their own iterators
iter(it) is it           # True
```

## Implementing a Custom Iterator

```python
class EvenNumbers:
    """Yields 0, 2, 4, ... up to limit."""

    def __init__(self, limit):
        self.limit   = limit
        self.current = 0

    def __iter__(self):
        return self      # the object is its own iterator

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        value = self.current
        self.current += 2
        return value

for n in EvenNumbers(8):
    print(n)
# 0, 2, 4, 6, 8

list(EvenNumbers(6))   # [0, 2, 4, 6]
```

The object is **both** an iterable and an iterator because `__iter__` returns
`self`. This means it can be used in a `for` loop directly, but it cannot be
iterated multiple times (once exhausted, it stays exhausted).

## Separating Iterable from Iterator

For collections that should support multiple passes, separate the iterable from
the iterator:

```python
class NumberRange:
    """An iterable that produces a fresh iterator each time."""

    def __init__(self, start, stop):
        self.start = start
        self.stop  = stop

    def __iter__(self):
        return NumberRangeIterator(self.start, self.stop)


class NumberRangeIterator:
    """The actual iterator — one-shot."""

    def __init__(self, current, stop):
        self.current = current
        self.stop    = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

rng = NumberRange(1, 4)
list(rng)   # [1, 2, 3]
list(rng)   # [1, 2, 3]  — fresh iterator, works again
```

Python's built-in `range` follows this pattern — `iter(range(5))` creates a
new iterator object each time.

## Generator Functions as the Easy Path

Writing a full iterator class is verbose. A generator function produces an
equivalent iterator with far less code:

```python
def even_numbers(limit):
    current = 0
    while current <= limit:
        yield current
        current += 2

# Identical behaviour to EvenNumbers class above
list(even_numbers(8))   # [0, 2, 4, 6, 8]
```

**Rule of thumb**:
- Use a generator function when you just need a sequence of values once.
- Use a class-based iterator when you need to support multiple passes, or when
  the iterator needs to expose additional methods or state.

## Useful Iterator Tools

```python
import itertools

# Chain multiple iterables
list(itertools.chain([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]

# Take the first N elements from any iterator
list(itertools.islice(even_numbers(1000), 5))
# [0, 2, 4, 6, 8]

# Enumerate with a starting index
for i, val in enumerate(["a", "b", "c"], start=1):
    print(i, val)

# zip stops at the shortest
for a, b in zip([1, 2, 3], ["x", "y"]):
    print(a, b)
# 1 x
# 2 y
```
