## The Problem Generators Solve

A regular function computes all its results upfront and returns them at once:

```python
def squares_list(n):
    return [x**2 for x in range(n)]   # allocates full list

squares_list(1_000_000)   # 8MB+ of memory, just to iterate once
```

A generator computes values **lazily** — one at a time, only when asked:

```python
def squares_gen(n):
    for x in range(n):
        yield x**2        # suspends here and returns x**2

gen = squares_gen(1_000_000)   # almost no memory — no values computed yet
next(gen)   # 0
next(gen)   # 1
next(gen)   # 4
```

**C mental model**: a generator is a coroutine — a function that can pause
execution at a specific point (`yield`) and resume from that exact point later.
It's similar to `setjmp/longjmp` for execution state, but clean and safe.

## How yield Works

When Python encounters `yield value` inside a function:
1. The function's local state (variables, instruction pointer) is **frozen**
2. `value` is returned to whoever called `next()` on the generator
3. The function stays paused until the next `next()` call resumes it
4. When the function returns (or falls off the end), `StopIteration` is raised

```python
def countdown(n):
    print("Starting")
    while n >= 0:
        yield n
        n -= 1
    print("Done")

gen = countdown(3)
# Nothing printed yet — body hasn't run

next(gen)   # prints "Starting", yields 3
# 3
next(gen)   # yields 2
# 2
next(gen)   # yields 1
# 1
next(gen)   # yields 0
# 0
next(gen)   # prints "Done", raises StopIteration
```

## Generators as Iterators

A generator object implements the iterator protocol: it has both `__iter__`
(returns self) and `__next__` (returns the next value). This means generators
work everywhere iterables are expected:

```python
for x in countdown(5):   # for loop calls iter(), then next() repeatedly
    print(x)

sum(x**2 for x in range(100))   # generator expression, consumed by sum

list(countdown(3))   # [3, 2, 1, 0]
```

A generator can only be consumed **once**. After StopIteration, it's exhausted:

```python
gen = countdown(2)
list(gen)   # [2, 1, 0]
list(gen)   # [] — already exhausted
```

## yield from — Delegating to Sub-generators

`yield from` delegates to another iterable, forwarding all its values:

```python
def chain(*iterables):
    for it in iterables:
        yield from it   # yields every item from it in sequence

list(chain([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]
```

This is cleaner than `for item in it: yield item` and also correctly propagates
`send()` and `throw()` calls through the delegation chain.

## Practical Generator Patterns

```python
# Infinite sequences (can't make a list of these)
def naturals():
    n = 0
    while True:
        yield n
        n += 1

import itertools
first_10 = list(itertools.islice(naturals(), 10))

# Pipeline: generators compose without intermediate storage
def read_lines(path):
    with open(path) as f:
        yield from f

def filter_empty(lines):
    for line in lines:
        if line.strip():
            yield line.rstrip()

def parse_ints(lines):
    for line in lines:
        yield int(line)

# Compose the pipeline — no intermediate lists allocated
total = sum(parse_ints(filter_empty(read_lines("numbers.txt"))))
```

In ML code, generators appear as data pipelines: PyTorch's `DataLoader`
uses Python generators internally. When you write a custom `Dataset.__iter__`
method, you're implementing the same protocol.
