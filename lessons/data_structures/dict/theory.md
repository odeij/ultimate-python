## Dicts Are Hash Tables

Python's `dict` is one of the most carefully optimised data structures in the
language. It is a **hash table** with open addressing — exactly what you'd build
in C for a key-value store, but with automatic resizing and collision handling
handled for you.

The CPython layout (simplified):

```
hash_table  →  array of (hash, key_ptr, value_ptr) slots
used        →  number of live key-value pairs
fill        →  used + number of dummy (deleted) slots
```

Lookup steps:
1. Compute `h = hash(key)`
2. Use `h % capacity` to find the initial slot
3. If the slot is occupied by a different key, probe to the next slot
4. Return the value if the key matches, or raise `KeyError`

Average case for get/set/delete is **O(1)**. Worst case (all keys collide) is O(n)
but hash randomisation makes this practically impossible in production code.

```python
d = {"name": "Ada", "year": 1815}
print(id(d))  # memory address of the dict object itself
```

## Keys Must Be Hashable

A key is usable only if it has a stable `__hash__` method — one that returns the
same value for the lifetime of the object:

```python
# Hashable — safe as keys
hash(42)           # integers
hash("hello")      # strings (immutable)
hash((1, 2, 3))    # tuples of hashables
hash(True)         # booleans

# Not hashable — TypeError
hash([1, 2, 3])    # list (mutable)
hash({"a": 1})     # dict (mutable)
hash({1, 2, 3})    # set (mutable)
```

**C mental model**: the key is passed to the hash function. If the key could change
after insertion, the hash would change, and the entry would be unreachable
(wrong bucket). Python enforces this by requiring `__hash__`.

Custom classes are hashable by default (hash based on `id()`). If you define
`__eq__`, Python sets `__hash__ = None` — forcing you to also define `__hash__`
to restore hashability.

## Safe Lookup and Mutation Patterns

```python
config = {"debug": True, "timeout": 30}

# KeyError if key absent:
config["missing"]       # KeyError!

# Safe access with a default:
val = config.get("missing", "default_value")  # "default_value"
val = config.get("debug")                      # True

# Set if absent, return current value:
config.setdefault("retries", 3)  # inserts 3 if "retries" not present
config.setdefault("timeout", 99) # returns 30 — already exists, no change

# Bulk update from another dict:
overrides = {"timeout": 60, "verbose": False}
config.update(overrides)
```

## Iteration Patterns

```python
d = {"a": 1, "b": 2, "c": 3}

# Keys (default iteration):
for key in d:
    print(key)

# Values:
for val in d.values():
    print(val)

# Both:
for key, val in d.items():
    print(key, val)
```

**Insertion order is preserved** in Python 3.7+. The dict iterates in the order
keys were inserted — this is a language guarantee, not an implementation detail.

```python
# Dict comprehension — build a dict from any iterable
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Invert a dict (assumes unique values)
inv = {v: k for k, v in squares.items()}
```

## Useful Patterns From the Standard Library

```python
from collections import defaultdict, Counter

# defaultdict: auto-inserts a default value for missing keys
word_lists = defaultdict(list)
word_lists["fruits"].append("apple")   # no KeyError, creates [] first

# Counter: a dict subclass specialised for counting
from collections import Counter
text = "abracadabra"
c = Counter(text)
# Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
c.most_common(3)   # [('a', 5), ('b', 2), ('r', 2)]
```

These are tools to know about, but learn to build them manually first — your
exercises do not allow importing `Counter` so you understand the underlying logic.
