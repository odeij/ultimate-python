"""
Generators — Python's lazy evaluation mechanism, deeply tied to iterators.

C programmer's translation guide:
  C has no built-in lazy sequences. The closest analog:
    - A callback/function pointer called repeatedly  ->  generator with yield
    - Coroutine with setjmp/longjmp                 ->  generator with send()
    - Producer/consumer thread pair                  ->  generator pipeline

Why this matters for AI research:
  - Data loaders in PyTorch use generators under the hood
  - Infinite sequence generation (tokens, training batches) is natural with yield
  - Memory efficiency: process 1M training examples without loading all into RAM
  - Async I/O for fetching batches from disk/network uses the same protocol

Generator protocol:
  Any object with __iter__() and __next__() is an iterator.
  yield makes a function into a generator function — returns a generator object.
  Generators are iterators that can also receive values (via .send()).

Topics covered:
  1. Basic generator function (yield)
  2. Generator expression (lazy version of list comprehension)
  3. Sending values into a generator (coroutine-style)
  4. yield from — delegation to sub-generators
  5. Infinite sequence generators
  6. Memory comparison: list vs generator
"""

import sys
from typing import Generator, Iterator


# ---------------------------------------------------------------------------
# 1. Basic generator function
# ---------------------------------------------------------------------------

def countdown(n: int) -> Generator[int, None, None]:
    """Generate integers from n down to 1.

    The function body does NOT run when called. It returns a generator object.
    The body runs lazily, one yield at a time, when next() is called.
    """
    while n > 0:
        yield n
        n -= 1


def fibonacci_gen() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence.

    This would be impossible with a list. With a generator, it's natural.
    In C you would write a stateful struct + function pair.
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ---------------------------------------------------------------------------
# 2. Generator expressions — lazy list comprehensions
# ---------------------------------------------------------------------------

def demo_generator_expression() -> None:
    """Generator expression: (expr for x in iterable if cond)
    Same syntax as list comprehension but with () — produces values lazily.
    """
    # List comprehension: computes ALL values immediately
    squares_list = [x ** 2 for x in range(1000)]    # 1000 values in memory
    assert sys.getsizeof(squares_list) > 0

    # Generator expression: computes values one at a time
    squares_gen = (x ** 2 for x in range(1000))     # no values computed yet
    # Generator object is a fixed small size regardless of N; list grows with N
    assert sys.getsizeof(squares_gen) < sys.getsizeof(squares_list)

    # Both produce the same results
    assert list(squares_gen) == squares_list
    assert len(squares_list) == 1000


# ---------------------------------------------------------------------------
# 3. Sending values into a generator
# This is the basis for Python coroutines (async/await is built on this)
# ---------------------------------------------------------------------------

def running_average() -> Generator[float, float, None]:
    """Coroutine that maintains a running average.

    Protocol:
      gen = running_average()
      next(gen)              — prime the generator (advance to first yield)
      result = gen.send(value)   — send a value in, receive result back
    """
    total = 0.0
    count = 0
    average = 0.0
    while True:
        value = yield average   # yield sends out average, receives next value
        if value is None:
            break
        total += value
        count += 1
        average = total / count


def demo_send() -> None:
    """Show the send() protocol."""
    gen = running_average()
    next(gen)             # prime: advance to first yield

    assert gen.send(10) == 10.0
    assert gen.send(20) == 15.0
    assert gen.send(30) == 20.0


# ---------------------------------------------------------------------------
# 4. yield from — delegation
# Equivalent to calling the sub-generator in a loop and yielding each value.
# This is how Python's async machinery chains coroutines.
# ---------------------------------------------------------------------------

def chain(*iterables):
    """Concatenate multiple iterables, lazily.

    `yield from iterable` is equivalent to:
      for item in iterable:
          yield item
    But it's more efficient (C-level delegation, no Python loop overhead).
    """
    for it in iterables:
        yield from it


def flatten(nested) -> Generator:
    """Recursively flatten a nested list using yield from."""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


# ---------------------------------------------------------------------------
# 5. Practical: lazy file reader (memory efficient)
# ---------------------------------------------------------------------------

def read_lines_lazy(filepath: str) -> Generator[str, None, None]:
    """Read a file line by line without loading it all into memory.

    For a 10GB training corpus: list = OOM, generator = fine.
    """
    with open(filepath) as f:
        yield from f


def read_chunks(filepath: str, chunk_size: int = 1024) -> Generator[bytes, None, None]:
    """Read a binary file in chunks — same pattern used in data loaders."""
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):   # walrus operator: assign + test
            yield chunk


# ---------------------------------------------------------------------------
# 6. Custom iterator class — the explicit form of what a generator does
# ---------------------------------------------------------------------------

class Range:
    """Reimplementation of range() to show the iterator protocol explicitly.

    A generator function creates this machinery automatically.
    Understanding this lets you write custom data loaders.
    """

    def __init__(self, start: int, stop: int, step: int = 1):
        self.current = start
        self.stop = stop
        self.step = step

    def __iter__(self) -> "Range":
        """Return the iterator object itself."""
        return self

    def __next__(self) -> int:
        """Return next value or raise StopIteration."""
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


# ---------------------------------------------------------------------------
# 7. Generator pipeline — the functional streaming pattern
# ---------------------------------------------------------------------------

def data_pipeline_demo() -> list[int]:
    """Chain generators to build a lazy processing pipeline.

    This is how PyTorch DataLoader works at a conceptual level:
      raw_data -> filter -> transform -> batch -> model

    Nothing executes until list() forces evaluation at the end.
    """
    raw = range(100)                                   # source
    filtered = (x for x in raw if x % 2 == 0)         # keep evens
    squared = (x ** 2 for x in filtered)              # square
    bounded = (x for x in squared if x < 1000)        # cap at 1000

    return list(bounded)


def main() -> None:
    # Countdown
    result = list(countdown(5))
    assert result == [5, 4, 3, 2, 1]

    # Fibonacci
    fib = fibonacci_gen()
    first_ten = [next(fib) for _ in range(10)]
    assert first_ten == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # Generator expression
    demo_generator_expression()

    # Send
    demo_send()

    # yield from chain
    assert list(chain([1, 2], [3, 4], [5])) == [1, 2, 3, 4, 5]

    # flatten
    assert list(flatten([1, [2, [3, 4]], [5]])) == [1, 2, 3, 4, 5]

    # Custom Range
    assert list(Range(0, 5)) == [0, 1, 2, 3, 4]
    assert list(Range(0, 10, 2)) == [0, 2, 4, 6, 8]

    # Pipeline
    pipeline_result = data_pipeline_demo()
    assert pipeline_result == [0, 4, 16, 36, 64, 100, 144, 196, 256, 324,
                                400, 484, 576, 676, 784, 900]


if __name__ == "__main__":
    main()
