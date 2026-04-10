# Functions: First-Class Objects & the Mutable Default Trap

## Functions Are First-Class Objects

In C, a function is code at a fixed address.  You can pass function pointers,
but a function is not a first-class value — you cannot store it in a struct
field without a typedef.

In Python, **a function is an object** like any other:

```python
def greet(name):
    return f"Hello, {name}"

# Functions can be stored in variables
say_hi = greet
print(say_hi("Odei"))   # Hello, Odei

# Functions can be stored in data structures
actions = [greet, str.upper, len]

# Functions can be passed as arguments
def apply(func, value):
    return func(value)

apply(greet, "world")   # "Hello, world"
apply(len, "world")     # 5
```

**C translation**: a Python function is like a first-class function pointer
whose type is `PyObject *`, so it can be passed to any parameter that accepts
an object.

Inspect any function:
```python
print(greet.__name__)   # "greet"
print(greet.__doc__)    # the docstring
import inspect
print(inspect.signature(greet))  # (name)
```

---

## Argument Passing: References All the Way Down

Python passes **references** to objects — not copies of values, not pointers
to stack variables.  This has two consequences:

**Immutable arguments**: rebinding inside the function does not affect the caller:
```python
def double(x):
    x = x * 2    # rebinds local name x to a new int — caller unchanged
    return x

n = 5
double(n)
print(n)   # still 5
```

**Mutable arguments**: mutating (not rebinding) inside the function IS visible:
```python
def append_one(lst):
    lst.append(1)   # mutates the shared object

data = [0]
append_one(data)
print(data)   # [0, 1]  ← mutation is visible to caller
```

**C translation**: Python argument passing is like passing a `void *` to a
function.  You can mutate what it points to, but you cannot make the caller's
variable point somewhere else.

---

## The Mutable Default Argument Trap

This is the most common Python gotcha for beginners and C programmers alike:

```python
# BROKEN
def append_to(item, collection=[]):
    collection.append(item)
    return collection

r1 = append_to(1)   # [1]
r2 = append_to(2)   # [1, 2]  ← WRONG! Same list!
assert r1 is r2     # True — they ARE the same object
```

**Why?**  Default argument values are evaluated **once at function definition
time** and stored in `append_to.__defaults__`.  The same list object is reused
on every call that uses the default.

**C mental model**: it is exactly like:
```c
// C — static variable persists across calls
void append_to(int item) {
    static int collection[100];  // initialised once
    // ...
}
```

**The fix** — use `None` as a sentinel:
```python
# CORRECT
def append_to(item, collection=None):
    if collection is None:
        collection = []          # fresh list on every call
    collection.append(item)
    return collection

r1 = append_to(1)   # [1]
r2 = append_to(2)   # [2]  ← independent fresh list
assert r1 is not r2
```

---

## *args and **kwargs

Python functions can accept variable numbers of arguments:

```python
def variadic(*args, **kwargs):
    # args is a tuple of positional arguments
    # kwargs is a dict of keyword arguments
    print(args)   # (1, 2, 3)
    print(kwargs) # {"name": "Odei", "role": "researcher"}

variadic(1, 2, 3, name="Odei", role="researcher")
```

**Positional-only and keyword-only** (Python 3.8+):
```python
def strict(pos_only, /, normal, *, kw_only):
    ...

# pos_only can only be passed positionally
# kw_only can only be passed as a keyword argument
```

**Unpacking at call sites**:
```python
args   = (1, 2, 3)
kwargs = {"sep": "-"}

# These are equivalent:
print(*args, **kwargs)
print(1, 2, 3, sep="-")
```

---

## Closures: Functions That Remember Their Scope

```python
def make_counter(start=0):
    count = start

    def increment():
        nonlocal count   # bind to the enclosing scope's variable
        count += 1
        return count

    return increment

counter = make_counter(10)
print(counter())   # 11
print(counter())   # 12
```

**C translation**: a closure is like a function pointer bundled with a pointer
to the surrounding stack frame that has been promoted to the heap.

Closures are the basis for decorators, which you'll cover in the advanced track.
