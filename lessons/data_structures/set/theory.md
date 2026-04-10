## Sets Are Dicts Without Values

Python's `set` is essentially a `dict` where only keys are stored and there are
no associated values. The implementation is identical: a hash table with open
addressing. Everything that makes dicts fast also makes sets fast.

```python
s = {1, 2, 3, 4, 5}
print(type(s))    # <class 'set'>

# Empty set — CANNOT use {} (that makes an empty dict)
empty = set()     # correct
wrong = {}        # this is an empty dict, not a set

# Build from any iterable
from_list = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3} — duplicates removed
```

**Properties of sets**:
- Elements must be hashable (same rule as dict keys)
- Elements are unique — adding a duplicate is a no-op
- Sets are unordered — no indexing, no slicing
- Mutable (add/remove elements). Frozen equivalent: `frozenset`

## O(1) Membership Testing

The most important use of sets: replacing a slow O(n) list scan with an O(1)
hash lookup.

```python
# Bad — O(n) per check
allowed = ["admin", "editor", "viewer"]
if "editor" in allowed:    # scans the whole list each time
    ...

# Good — O(1) per check
allowed = {"admin", "editor", "viewer"}
if "editor" in allowed:    # hash lookup, constant time
    ...
```

In C terms: the list scan is a linear walk through an array; the set lookup is
a hash table probe that finds the right bucket in one step.

```python
# When this matters: deduplication and repeated lookups
names = ["alice", "bob", "alice", "carol", "bob", "alice"]
unique_names = set(names)       # {"alice", "bob", "carol"} in O(n)

seen = set()
results = []
for name in names:
    if name not in seen:        # O(1) each time
        seen.add(name)
        results.append(name)
# results = ["alice", "bob", "carol"] — first-seen order preserved
```

## Set Operations

Python sets implement the full algebra of mathematical sets:

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Union — all elements from either set
a | b           # {1, 2, 3, 4, 5, 6}
a.union(b)      # same

# Intersection — only elements in both
a & b           # {3, 4}
a.intersection(b)

# Difference — elements in a but not in b
a - b           # {1, 2}
a.difference(b)

# Symmetric difference — elements in exactly one set
a ^ b           # {1, 2, 5, 6}
a.symmetric_difference(b)

# Subset / superset
{1, 2} <= a     # True — {1,2} is a subset of a
a >= {1, 2}     # True — a is a superset of {1,2}
```

These are all implemented in C and run in **O(min(len(a), len(b)))** or
**O(len(a) + len(b))** time.

## Mutation Methods

```python
s = {1, 2, 3}

s.add(4)         # add one element — O(1)
s.remove(2)      # remove — KeyError if absent
s.discard(99)    # remove — no error if absent (prefer this)
s.pop()          # remove and return an arbitrary element

# In-place set operations:
s.update({5, 6})           # union in place  (like |=)
s.intersection_update({1, 5, 6})  # intersect in place (like &=)
```

## When to Use Sets vs Lists vs Dicts

| Need | Use |
|---|---|
| Ordered sequence with duplicates | `list` |
| Fast membership test, no duplicates | `set` |
| Key-value mapping | `dict` |
| Immutable set (as dict key, frozen) | `frozenset` |
| Remove duplicates from a list | `list(set(lst))` (order not preserved) or seen-set pattern |

**Rule of thumb**: whenever you find yourself doing `if x in my_list` inside a
loop, ask whether a set would be faster. If the list is built once and queried
many times, converting it to a set upfront is almost always the right call.
