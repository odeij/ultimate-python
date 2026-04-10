## Functions Are Objects

In C, a function is a block of code at a fixed address. You can store that address
in a function pointer, but the function itself is not a first-class value — you
can't pass it around like an int or store it in a struct easily.

In Python, **every function is a first-class object**. You can assign it to a
variable, store it in a list, pass it as an argument, or return it from another
function:

```python
def greet(name):
    return f"Hello, {name}"

say_hi = greet          # another name for the same object
say_hi("Ada")           # "Hello, Ada"

funcs = [greet, str.upper, len]   # store functions in a list
funcs[0]("Ada")                   # "Hello, Ada"
```

**C mental model**: every Python function is like a `void *` that points to a
callable struct. Python hides the pointer arithmetic; you just write the name.

## What a Decorator Is

A decorator is a function that takes a function and returns a (usually modified)
function. The `@` syntax is pure syntactic sugar:

```python
@my_decorator
def func():
    ...

# Exactly equivalent to:
def func():
    ...
func = my_decorator(func)
```

The decorator runs at **definition time**, not call time. By the time the first
caller invokes `func`, the name already points to `my_decorator`'s return value.

The most common pattern is wrapping — add behaviour before/after the original:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done {func.__name__}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(1, 2)
# Calling add
# Done add
# 3
```

## Preserving Metadata with functools.wraps

Without `functools.wraps`, the wrapper hides the original function's identity:

```python
add.__name__   # "wrapper"  ← wrong
add.__doc__    # None       ← lost
```

Fix: apply `@wraps(func)` to the wrapper:

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

Now `add.__name__ == "add"` and `add.__wrapped__` gives access to the original.
Always use `@wraps` in production decorators.

## Decorators with Arguments

Sometimes you want a decorator that itself takes configuration:

```python
def repeat(n):
    """Returns a decorator that calls func n times."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def hello():
    print("Hello!")

hello()
# Hello!
# Hello!
# Hello!
```

`@repeat(3)` calls `repeat(3)` first (returns a decorator), then applies that
decorator to `hello`. Two levels of wrapping.

## Real-World Patterns

```python
from functools import wraps, lru_cache
import time

# Memoization (caching)
@lru_cache(maxsize=None)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# Timing decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

# Retry decorator
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper
    return decorator
```

In ML code you'll see decorators everywhere: `@torch.no_grad()`,
`@staticmethod`, `@property`, `@dataclass`. Understanding how they work
de-mystifies the entire framework.
