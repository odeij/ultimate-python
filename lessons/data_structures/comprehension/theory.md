## List Comprehensions vs for Loops

A list comprehension is an **expression** that produces a list. It is syntactic
sugar for a specific pattern of for loop + append:

```python
# Explicit loop
squares = []
for x in range(10):
    squares.append(x ** 2)

# Equivalent list comprehension — one expression, no mutation
squares = [x ** 2 for x in range(10)]
```

With a filter condition:

```python
# Explicit loop
evens = []
for x in range(20):
    if x % 2 == 0:
        evens.append(x)

# Comprehension
evens = [x for x in range(20) if x % 2 == 0]
```

**When to use a comprehension**: when the body of the loop is a single expression
and the result is a collection. If the loop body is multi-statement or has side
effects, a regular loop is clearer.

**C mental model**: comprehensions are a high-level notation for the malloc +
loop + assign pattern. `[f(x) for x in arr]` is equivalent to:
```c
result = malloc(len * sizeof(*result));
for (int i = 0; i < len; i++) result[i] = f(arr[i]);
```

## Dict and Set Comprehensions

The same syntax works for dicts (with a key:value pair) and sets (with curly braces):

```python
words = ["hello", "world", "python"]

# Dict comprehension: word → length
lengths = {word: len(word) for word in words}
# {"hello": 5, "world": 5, "python": 6}

# Set comprehension: unique lengths
unique_lengths = {len(word) for word in words}
# {5, 6}

# With filter
long_words = {w for w in words if len(w) > 4}
# {"hello", "world", "python"}
```

Inverted dict (swapping keys and values):

```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}
```

## Generator Expressions

Swapping `[]` for `()` turns a list comprehension into a **generator expression**:

```python
# List: computes all values now, stores them in memory
squares_list = [x**2 for x in range(1_000_000)]  # allocates 1M-element list

# Generator: computes values lazily, one at a time
squares_gen = (x**2 for x in range(1_000_000))   # allocates almost nothing
```

Generators are **iterators**: you call `next()` on them or consume them in a loop.
They yield one value at a time and cannot be indexed or re-iterated.

```python
gen = (x**2 for x in range(5))
next(gen)  # 0
next(gen)  # 1
next(gen)  # 4
# ...

# sum() and max() consume generators without materialising a list
total = sum(x**2 for x in range(1000))    # no [] allocation
maximum = max(len(line) for line in open("file.txt"))
```

**Rule**: if you pass a comprehension to a function that only iterates once
(`sum`, `max`, `min`, `any`, `all`, `sorted`), use a generator expression —
it's faster and uses less memory.

## Nested Comprehensions

Comprehensions can nest to iterate over 2D structures:

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Flatten — outer loop first, then inner
flat = [elem for row in matrix for elem in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Equivalent loop:
flat = []
for row in matrix:
    for elem in row:
        flat.append(elem)
```

Reading rule: **outer loop is written first** in the comprehension, just as in
the nested loop version.

2D transformation (transpose):

```python
# Transpose a 3×3 matrix
transposed = [[row[i] for row in matrix] for i in range(3)]
```

**Warning**: deeply nested comprehensions (3+ levels) become hard to read. If
you find yourself writing three nested loops as a comprehension, a regular loop
is almost always clearer.

## Practical Guidelines

| Expression type | Syntax | Use when |
|---|---|---|
| List comprehension | `[expr for x in it]` | You need a list with all values now |
| Dict comprehension | `{k: v for x in it}` | Building a mapping |
| Set comprehension | `{expr for x in it}` | Unique values, order doesn't matter |
| Generator expression | `(expr for x in it)` | Single-pass consumption, large data |
| Regular for loop | `for x in it: ...` | Multi-statement body, side effects |
