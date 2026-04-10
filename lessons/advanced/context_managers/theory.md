## The with Statement and RAII

In C, resource management is manual: you allocate, use, then free — and if you
forget to free (or an error occurs between alloc and free), you leak. C++ solved
this with RAII (Resource Acquisition Is Initialization): destructors run
automatically when objects go out of scope.

Python's `with` statement is the runtime equivalent of RAII:

```python
# File handling without with — easy to forget f.close()
f = open("data.txt")
data = f.read()
f.close()   # What if read() raises? close() is skipped.

# With with — close() is GUARANTEED, even on exception
with open("data.txt") as f:
    data = f.read()
# f is closed here whether or not an exception occurred
```

The `with` block guarantees that cleanup code runs. This is why all resource
management in Python (files, network connections, locks, database transactions)
uses context managers.

## The Protocol: __enter__ and __exit__

Any object that implements two methods can be used with `with`:

```python
class ManagedResource:
    def __enter__(self):
        # Setup: acquire resource, record state, etc.
        print("Entering")
        return self   # value bound to the `as` target

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown: always runs
        print("Exiting")
        # Return True to suppress exceptions, False/None to propagate
        return False

with ManagedResource() as r:
    print("Inside block")
    # r is whatever __enter__ returned (self in this case)
```

The three arguments to `__exit__`:
- `exc_type`: the exception class, or `None` if no exception
- `exc_val`: the exception instance, or `None`
- `exc_tb`: the traceback object, or `None`

If `__exit__` returns a truthy value, the exception is **suppressed**. Almost
always you want to return `False` (or just `return`) so exceptions propagate
normally.

## The contextlib Approach

For simple cases, writing a full class is overkill. `contextlib.contextmanager`
lets you write a generator instead:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    # --- __enter__ phase ---
    print("Setup")
    resource = acquire_resource()
    try:
        yield resource          # <-- the `as` target; with-block runs here
    finally:
        # --- __exit__ phase ---
        release_resource(resource)
        print("Teardown")

with managed_resource() as r:
    use(r)
```

The `try/finally` ensures cleanup runs even if the `with` block raises. This
is the most common pattern for one-off context managers in application code.

## Common Built-in Context Managers

```python
# Files
with open("file.txt", "r") as f:
    content = f.read()

# Locks (thread safety)
import threading
lock = threading.Lock()
with lock:
    shared_state += 1     # lock acquired; released automatically

# Temporary directory
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    # tmpdir is a Path string; directory deleted on exit
    pass

# Suppress specific exceptions
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("might_not_exist.txt")
```

In PyTorch, `torch.no_grad()` is a context manager that disables gradient
computation:

```python
with torch.no_grad():
    output = model(input)   # no autograd graph built — saves memory
```

`torch.autocast` is another — enables mixed-precision computation for the block.
Understanding context managers means you can write your own when PyTorch's
built-ins don't cover your use case.

## Nesting and Multiple Context Managers

```python
# Nest multiple with statements in one line
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())

# Equivalent to nested with statements:
with open("in.txt") as src:
    with open("out.txt", "w") as dst:
        dst.write(src.read())
```
