## Lists Are Dynamic Arrays

In C you'd write `int arr[5]` to get five contiguous integers on the stack, or
`malloc(5 * sizeof(int))` for the heap. The size is fixed at allocation time.

Python's `list` is a **dynamic array** — like `std::vector` in C++. Under the hood
CPython keeps three things:

```
ob_item  →  pointer to a heap-allocated array of object pointers
ob_size  →  number of elements currently stored
allocated →  capacity of the backing array (>= ob_size)
```

When `ob_size == allocated` and you call `append()`, CPython does a `realloc`
that roughly doubles the capacity. The amortised cost of append is **O(1)**
because the expensive copy happens rarely.

```python
import sys

lst = []
for i in range(8):
    lst.append(i)
    print(f"len={len(lst)}  sys.getsizeof={sys.getsizeof(lst)}")

# Capacity jumps at 0 → 4 → 8 → 16 ... (powers of ~1.125× growth factor in CPython)
```

**Key consequence**: a list of N elements uses O(N) extra memory for the backing
array, plus O(N) for the pointers themselves. Unlike a C array, the elements are
**not** stored inline — the list stores pointers to objects.

## Aliasing vs Copying

Python assignment copies the reference, not the object:

```python
a = [1, 2, 3]
b = a           # b points at the same list
b.append(4)
print(a)        # [1, 2, 3, 4] — you mutated a through b
```

To get an independent copy:

```python
b = a[:]        # shallow copy via full slice — like memcpy of the pointer array
b = list(a)     # equivalent, explicit
b = a.copy()    # same, method form
```

All three are **shallow copies**: if the list contains mutable objects (other lists,
dicts), the inner objects are still shared. For a deep copy: `import copy; copy.deepcopy(a)`.

**C mental model**: `b = a` is `int **b = a` (copy the pointer, not the array).
`b = a[:]` is `memcpy(b, a, n * sizeof(ptr))`.

## Indexing, Slicing, Negative Indices

```python
lst = [10, 20, 30, 40, 50]

lst[0]      # 10   — first element
lst[-1]     # 50   — last element  (C: lst[len(lst)-1])
lst[1:3]    # [20, 30] — elements at index 1 and 2 (end is exclusive)
lst[::2]    # [10, 30, 50] — every other element
lst[::-1]   # [50, 40, 30, 20, 10] — reversed
```

Slicing creates a **new list** (shallow copy of the selected range). It is O(k)
where k is the number of elements selected.

Negative indices wrap around: `lst[-i]` is equivalent to `lst[len(lst) - i]`.

## Essential List Operations and Their Complexity

| Operation | Syntax | Time |
|---|---|---|
| Access by index | `lst[i]` | O(1) |
| Append | `lst.append(x)` | O(1) amortized |
| Insert at position | `lst.insert(i, x)` | O(n) — shifts elements |
| Remove by value | `lst.remove(x)` | O(n) — linear scan |
| Pop from end | `lst.pop()` | O(1) |
| Pop from index | `lst.pop(i)` | O(n) |
| Slice | `lst[a:b]` | O(b-a) |
| Sort | `lst.sort()` | O(n log n) |
| Length | `len(lst)` | O(1) |

```python
lst = [3, 1, 4, 1, 5, 9, 2, 6]

lst.sort()                 # in-place, modifies lst
sorted_copy = sorted(lst)  # returns new list, lst unchanged

lst.reverse()              # in-place
lst[::-1]                  # new reversed list

# Checking membership
5 in lst       # O(n) linear scan — use a set if you do this repeatedly
```

## Patterns: enumerate, zip, unpacking

```python
fruits = ["apple", "banana", "cherry"]

# enumerate gives index + value — avoids manual counter
for i, fruit in enumerate(fruits):
    print(i, fruit)

# zip pairs two sequences together
prices = [1.2, 0.5, 2.0]
for fruit, price in zip(fruits, prices):
    print(f"{fruit}: ${price}")

# Unpacking
first, *rest = fruits       # first="apple", rest=["banana", "cherry"]
*head, last  = fruits       # head=["apple", "banana"], last="cherry"
a, b, c      = fruits       # exact match — ValueError if lengths differ
```
