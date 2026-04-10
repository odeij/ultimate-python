# Conditionals: Truthiness & Short-Circuit Evaluation

## Truthiness: Everything Has a Boolean Value

In C, conditionals work on integers: `0` is false, everything else is true.
Python generalises this: **every object** has a boolean value determined by
`__bool__` (or `__len__` as a fallback).

**Falsy values** — everything else is truthy:
```python
# All of these are falsy:
False
None
0      # int zero
0.0    # float zero
0j     # complex zero
""     # empty string
[]     # empty list
{}     # empty dict
()     # empty tuple
set()  # empty set
```

```python
# All of these are truthy:
True
1
-1
"false"      # non-empty string — truthy regardless of content!
[0]          # list with one element — non-empty
{"a": None}  # dict with one key
```

**Why it matters**:
```python
# C style (verbose, redundant):
if len(my_list) != 0:
    ...

# Pythonic (idiomatic):
if my_list:
    ...
```

Both are equivalent.  The second form is preferred because Python's truthiness
rules make `bool(my_list)` equivalent to `len(my_list) != 0` for lists.

---

## Short-Circuit Evaluation

`and` and `or` in Python do **not** return booleans — they return one of
their operands.  They also short-circuit (stop evaluating as soon as the
result is determined), just like `&&` and `||` in C.

**`or`** — returns the first truthy operand, or the last operand:
```python
0 or 42           # 42   (0 is falsy, so evaluate and return right side)
"hi" or "bye"     # "hi"  (first truthy — short-circuits, never evaluates "bye")
None or []        # []   (both falsy — returns last)
```

**`and`** — returns the first falsy operand, or the last operand:
```python
0 and 42          # 0    (0 is falsy — short-circuits immediately)
"hi" and "bye"    # "bye"  (both truthy — returns last)
None and 1/0      # None  (short-circuits — division never evaluated!)
```

**C programmer's translation**:

| Python | C equivalent |
|--------|-------------|
| `x = a or default` | `x = a ? a : default` |
| `x = condition and value` | `x = condition ? value : 0` |
| `if a and b:` | `if (a && b)` but evaluates to the actual value of b |

---

## Conditional Expressions (Ternary)

Python has a ternary operator, but the syntax is different from C:

```c
// C
int x = condition ? true_val : false_val;
```

```python
# Python — condition in the MIDDLE
x = true_val if condition else false_val
```

Examples:
```python
sign = "positive" if n > 0 else "non-positive"
abs_val = n if n >= 0 else -n
capped = value if value < MAX else MAX
```

These are expressions — they can appear anywhere a value is expected, including
in list comprehensions and function arguments.

---

## Common Idioms

**Default values**:
```python
name = user_input or "Anonymous"     # use default if input is falsy
config = provided_config or {}       # empty dict if None provided
```

**Guard clauses** (early return pattern):
```python
def process(data):
    if not data:          # equivalent to: if data is None or data == []
        return None
    # ... rest of function
```

**Chained comparisons** (Python only, no C equivalent):
```python
# C: if (0 < x && x < 100)
# Python:
if 0 < x < 100:     # chained — evaluated as (0 < x) and (x < 100)
    ...
```

**`in` operator**:
```python
# C: if (strcmp(s, "a") == 0 || strcmp(s, "b") == 0 || ...)
# Python:
if command in ("quit", "exit", "q"):
    ...
```
