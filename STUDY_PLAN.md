# Python Mastery Study Plan
### Target: Research-grade Python + Interview-ready algorithms — 6 months

**Profile**: C programmer, ICRA 2026 published researcher, MIT Linear Algebra in progress,
uses Python for ML libraries (NumPy/PyTorch/sklearn), no competitive programming background.

**Goal**: Own Python the way you own C, plus crack algorithm interviews at research labs
(Google DeepMind, Meta FAIR, Microsoft Research, OpenAI) and PhD programs.

---

## Structure

Three parallel tracks that interleave throughout:

| Track | What | Why |
|---|---|---|
| **A — Python Internals** | How Python works under the hood | Own the language, not just use it |
| **B — Algorithms** | LeetCode patterns, interview problems | Research lab & PhD interviews |
| **C — Research Python** | NumPy/PyTorch internals, paper implementation | Become dangerous as an AI researcher |

**Daily rhythm** (adapt to your schedule):
- 1–2 hours: algorithms (a problem or two + pattern study)
- 1 hour: the month's core module (internals or research)
- Rest: reading, reviewing, running the files in this repo

---

## Month 1 — Python as a Language (Not a Library)
**Theme**: Stop using Python like a scripted C. Learn the idioms.

### Week 1 — Syntax you already "know" but don't own

**Study** (this repo):
- `ultimatepython/syntax/variable.py` — names are references, not boxes
- `ultimatepython/syntax/conditional.py` — truthiness, short-circuit evaluation
- `ultimatepython/syntax/loop.py` — `enumerate`, `zip`, `for/else`
- `ultimatepython/syntax/function.py` — `*args`, `**kwargs`, default argument gotcha
- `ultimatepython/syntax/expression.py` — comprehensions are expressions
- `ultimatepython/mastery/internals/memory_model.py` — **START HERE for the C-to-Python unlock**

**C-to-Python mental models to build this week**:
- `int *p = &x` → `p = x` (but you can't increment p, because ints are immutable)
- `malloc/free` → reference counting (watch `sys.getrefcount`)
- `struct` → class (but fields are stored in `__dict__`, not a fixed memory block)
- `void *` → Python object (everything is an object — `id()` gives you the address)

**Algorithm track — Easy, Arrays**:
- Read: `ultimatepython/mastery/algorithms/arrays_and_hashing.py` (understand every line)
- Solve on LeetCode (in this order):
  1. Two Sum (1)
  2. Valid Anagram (242)
  3. Contains Duplicate (217)
  4. Concatenation of Array (1929)
  5. Replace Elements with Greatest Element on Right Side (1299)
- **Do not look at solutions.** Write brute force first, then optimize.
- After each problem: ask "what is the C equivalent? What does Python hide from me here?"

---

### Week 2 — Data Structures: Python's built-ins vs what you built in C

**Study** (this repo):
- `ultimatepython/data_structures/list.py`
- `ultimatepython/data_structures/dict.py`
- `ultimatepython/data_structures/set.py`
- `ultimatepython/data_structures/comprehension.py`
- `ultimatepython/data_structures/defaultdict.py`

**Key insight**: Python's `list` is a dynamic array (like `std::vector`). Python's `dict` is a
hash table with open addressing — similar to what you'd write in C but with collision handling
and automatic resizing. `set` is a dict without values.

**Algorithm track**:
- Read: `ultimatepython/mastery/algorithms/sliding_window.py`
- Solve:
  1. Best Time to Buy and Sell Stock (121)
  2. Longest Substring Without Repeating Characters (3)
  3. Maximum Average Subarray I (643)
  4. Maximum Number of Vowels in a Substring (1456)
  5. Max Consecutive Ones III (1004)

---

### Week 3 — Functions as First-Class Citizens

**Study** (this repo):
- `ultimatepython/syntax/arg_enforcement.py`
- `ultimatepython/advanced/decorator.py`
- `ultimatepython/advanced/context_manager.py`
- `ultimatepython/mastery/internals/generators_deep.py`

**C-to-Python translation**:
- Function pointer in C → callable object in Python (anything with `__call__`)
- Decorator = higher-order function = takes a function, returns a modified function
- `with` statement = RAII (but runtime, not compile-time)
- Generator = coroutine (Python has native coroutines since 3.5)

**Algorithm track**:
- Stack problems (use `list` as stack in Python):
  1. Valid Parentheses (20)
  2. Min Stack (155)
  3. Evaluate Reverse Polish Notation (150)
  4. Daily Temperatures (739)
  5. Car Fleet (853)

---

### Week 4 — Object Model and Classes

**Study** (this repo):
- `ultimatepython/classes/basic_class.py`
- `ultimatepython/classes/inheritance.py`
- `ultimatepython/classes/abstract_class.py`
- `ultimatepython/classes/iterator_class.py`
- `ultimatepython/advanced/mro.py`

**Deep dive**: Run `type(int)`, `type(type)`, `isinstance(int, object)` in the REPL.
Python's object hierarchy is simpler than C++'s vtable — once you see it, everything makes sense.

**Algorithm track**:
- Binary search (understand: the invariant, not the boundary conditions by memory):
  1. Binary Search (704)
  2. Search a 2D Matrix (74)
  3. Koko Eating Bananas (875)
  4. Find Minimum in Rotated Sorted Array (153)
  5. Search in Rotated Sorted Array (33)

**Month 1 checkpoint**: Run `python runner.py` from the repo root. All syntax, data_structures, and classes modules should pass. If any fail, read the error and fix your understanding.

---

## Month 2 — Python Internals (The C Programmer's Unlock)
**Theme**: Understand what the interpreter is doing. Stop guessing.

### Week 5 — The Descriptor Protocol

**Study**:
- `ultimatepython/mastery/internals/descriptors.py` — **read every line, understand every assert**
- Then read: how `@property` actually works in CPython source (`Objects/descrobject.c`)
- `ultimatepython/advanced/meta_class.py` — metaclasses are the descriptor protocol for classes

**Exercise**: Implement `@cached_property` from scratch (it's already in the file — close it
and try before reading). Then compare your implementation to `functools.cached_property` in
the Python standard library source.

**Algorithm track — Two Pointers**:
1. Valid Palindrome (125)
2. Two Sum II - Input Array Is Sorted (167)
3. 3Sum (15)
4. Container With Most Water (11)
5. Trapping Rain Water (42) — **hard, do this one**

---

### Week 6 — Memory Model Deep Dive

**Study**:
- `ultimatepython/mastery/internals/memory_model.py` — second pass, understand `__slots__`
- `ultimatepython/advanced/weak_ref.py` — weak references for cache implementation
- Python Data Model docs: `__hash__`, `__eq__`, `__lt__` (comparable objects)

**Practical experiment**:
```python
import tracemalloc
tracemalloc.start()
# ... create 1M objects both with and without __slots__ ...
snapshot = tracemalloc.take_snapshot()
```
Measure the actual memory difference. This is the kind of experiment that makes ML
practitioners dangerous — you can estimate memory cost before running a training job.

**Algorithm track — Linked Lists** (implement from scratch in Python):
1. Reverse Linked List (206)
2. Merge Two Sorted Lists (21)
3. Reorder List (143)
4. Remove Nth Node From End of List (19)
5. Linked List Cycle (141)
6. Find The Duplicate Number (287)

---

### Week 7 — Concurrency and the GIL

**Study** (this repo):
- `ultimatepython/advanced/thread.py`
- `ultimatepython/advanced/async.py`
- `ultimatepython/advanced/subinterpreters.py`

**The key insight for ML**: The GIL means Python threads do NOT parallelize CPU-bound work.
This is why PyTorch uses C++ threads for computation and Python threads only for I/O
(data loading, checkpointing). Understanding this explains:
- Why `torch.DataLoader(num_workers=4)` uses multiprocessing, not threads
- Why your GPU training doesn't speed up with more Python threads
- When to use `asyncio` vs `multiprocessing` vs `concurrent.futures`

**Algorithm track — Trees (start)**:
- Read `ultimatepython/mastery/algorithms/trees.py`
- Solve:
  1. Invert Binary Tree (226)
  2. Maximum Depth of Binary Tree (104)
  3. Diameter of Binary Tree (543)
  4. Balanced Binary Tree (110)
  5. Same Tree (100)
  6. Subtree of Another Tree (572)

---

### Week 8 — Advanced Patterns

**Study** (this repo):
- `ultimatepython/advanced/mixin.py` — composition over inheritance
- `ultimatepython/data_structures/heap.py`
- `ultimatepython/data_structures/deque.py`
- `ultimatepython/data_structures/itertools.py`

**Focus on `itertools`**: This is your competitive programming toolkit in Python.
`product`, `combinations`, `permutations`, `chain`, `islice`, `groupby` — know them all.

**Algorithm track — Trees (finish) + Heap**:
1. Level Order Traversal (102)
2. Right Side View (199)
3. Count Good Nodes in Binary Tree (1448)
4. Validate BST (98)
5. Kth Largest Element in a Stream (703) — heap
6. Last Stone Weight (1046) — heap
7. K Closest Points to Origin (973) — heap

**Month 2 checkpoint**:
- Can you explain Python's descriptor protocol to someone else?
- Can you predict `sys.getrefcount` for a given code snippet?
- Have you solved at least 30 LeetCode problems?

---

## Month 3 — Algorithms Intensive
**Theme**: Build algorithmic fluency. Shift from "can I solve it?" to "I see the pattern."

### Week 9 — Graphs

**Study**: `ultimatepython/mastery/algorithms/graphs.py`

**Theory to review** (essential for research):
- BFS/DFS complexity analysis (V + E, and why)
- Why topological sort = reverse postorder DFS
- Union-Find: path compression + union by rank proof that it's near-O(1)
- Why these matter: GNN message passing = BFS, autograd = topological sort

**Solve**:
1. Number of Islands (200)
2. Clone Graph (133)
3. Max Area of Island (695)
4. Pacific Atlantic Water Flow (417)
5. Surrounded Regions (130)
6. Rotting Oranges (994)
7. Course Schedule (207)
8. Course Schedule II (210)
9. Redundant Connection (684)
10. Word Ladder (127) — **hard**

---

### Week 10 — Dynamic Programming I

**Study**: `ultimatepython/mastery/algorithms/dynamic_programming.py`

**Framework to master** (apply to every DP problem):
1. What is the state? `dp[i] means "..."`
2. What is the recurrence?
3. What are the base cases?
4. What order do I fill the table?
5. Can I reduce space (rolling array, etc.)?

**Solve**:
1. Climbing Stairs (70)
2. Min Cost Climbing Stairs (746)
3. House Robber (198)
4. House Robber II (213)
5. Longest Palindromic Substring (5)
6. Palindromic Substrings (647)
7. Decode Ways (91)
8. Coin Change (322)
9. Maximum Product Subarray (152)
10. Word Break (139)

---

### Week 11 — Dynamic Programming II (2D)

**Focus**: 2D DP — the basis of sequence-to-sequence model objectives.

**Solve**:
1. Unique Paths (62)
2. Longest Common Subsequence (1143) — **do this, it's the core of edit distance + BLEU**
3. Edit Distance (72) — **critical: used in NLP evaluation, tokenizer debugging**
4. Interleaving String (97)
5. Distinct Subsequences (115)
6. Longest Increasing Subsequence (300) — also do the O(n log n) version
7. Maximum Profit in Job Scheduling (1235)

After solving LCS, read the Wikipedia page on the Smith-Waterman algorithm.
You now understand biological sequence alignment. Same DP, different scoring.

---

### Week 12 — Intervals + Advanced Patterns

**Solve**:
1. Meeting Rooms (252)
2. Meeting Rooms II (253) — heap-based
3. Merge Intervals (56)
4. Non-overlapping Intervals (435)
5. Minimum Interval to Include Each Query (2402) — hard
6. Jump Game (55)
7. Jump Game II (45)
8. Gas Station (134)

**Month 3 checkpoint**:
- Solve 3 random Medium problems in under 25 minutes each
- You should be able to identify the pattern (sliding window / BFS / DP) within 2 minutes
- Target: 75+ total problems solved

---

## Month 4 — NumPy Internals + Hard Algorithms
**Theme**: Research-grade array thinking + the harder interview problems.

### Week 13 — NumPy Internals

**Study**: `ultimatepython/mastery/research/numpy_internals.py`

**Deep dives**:
1. **Strides**: After reading the file, open IPython and run:
   ```python
   import numpy as np
   a = np.arange(16).reshape(4, 4)
   print(a.strides)        # (32, 8) — 4 floats per row * 8 bytes per float
   print(a.T.strides)      # (8, 32) — transposed = strides swapped
   print(a[::2].strides)   # (64, 8) — skip every other row
   ```
   Every one of these is zero-copy. No data moved. Only the stride changed.

2. **Broadcasting rules**: Write them down from memory. Test yourself by predicting the
   output shape before running.

3. **Vectorization exercise**: Take any loop in your existing research code and
   vectorize it. Measure the speedup with `%timeit`.

**Algorithm track — Backtracking**:
1. Subsets (78)
2. Combination Sum (39)
3. Permutations (46)
4. Subsets II (90) — with duplicates
5. Combination Sum II (40)
6. Letter Combinations of a Phone Number (17)
7. N-Queens (51) — **hard, do this**
8. Sudoku Solver (37) — **hard**

---

### Week 14 — PyTorch Module Protocol

**Study**: `ultimatepython/mastery/research/custom_autograd.py`

**After understanding the autograd engine**:
1. Open PyTorch and read `torch.autograd.Function` documentation
2. Implement a custom ReLU using `torch.autograd.Function`:
   ```python
   class MyReLU(torch.autograd.Function):
       @staticmethod
       def forward(ctx, x):
           ctx.save_for_backward(x)
           return x.clamp(min=0)
       @staticmethod
       def backward(ctx, grad_output):
           x, = ctx.saved_tensors
           return grad_output * (x > 0).float()
   ```
3. Verify your gradients with `torch.autograd.gradcheck`

**Why this matters**: Every novel architecture you will ever publish requires a custom
backward pass. If you can't write one, you can't implement your ideas.

**Algorithm track — Advanced Trees**:
1. Construct BST from Preorder (1008)
2. Binary Tree Maximum Path Sum (124) — **hard**
3. Serialize and Deserialize Binary Tree (297)
4. Word Search II (212) — Trie + backtracking
5. Design Add and Search Words (211) — Trie

---

### Week 15 — Profiling and Optimization

**Tools to learn**:
```bash
python -m cProfile -s cumulative your_script.py   # CPU profiling
python -m memory_profiler your_script.py           # memory profiling
# In PyTorch:
with torch.profiler.profile() as prof:
    model(x)
print(prof.key_averages().table())
```

**Study topics**:
- `cProfile` + `pstats`: find your actual bottleneck, not the one you assume
- `line_profiler` (`@profile` decorator): line-by-line timing
- `tracemalloc`: find memory leaks in training loops
- `torch.profiler`: GPU kernel timeline, memory allocation events

**Exercise**: Profile your own research code. Find one place where vectorization
or memory layout change yields >2x speedup.

**Algorithm track — Advanced Graph**:
1. Alien Dictionary (269) — topological sort
2. Cheapest Flights Within K Stops (787) — Bellman-Ford
3. Network Delay Time (743) — Dijkstra
4. Swim in Rising Water (778) — Dijkstra variant
5. Reconstruct Itinerary (332) — Euler path

**Month 4 checkpoint**:
- Can you write a custom autograd function in PyTorch?
- Can you explain why NumPy transpose is O(1)?
- Solve a Hard DP problem from scratch in under 35 minutes

---

## Month 5 — Implement a Paper
**Theme**: Apply everything. Take a paper and build it from scratch in clean Python.

### Week 17–18 — Paper Choice and Setup

Choose ONE paper from this list (ordered by implementation difficulty):
1. **[Easiest]** Neural Turing Machine (Graves 2014) — LSTMs + external memory
2. **[Medium]** Attention Is All You Need (Vaswani 2017) — implement Transformer from scratch
3. **[Medium-Hard]** Deep Deterministic Policy Gradient (DDPG) — RL, connects to robotics
4. **[Hard]** MAML: Model-Agnostic Meta-Learning (Finn 2017) — connects to your ICRA work

**Implementation rules** (this is what makes it a learning exercise):
- No Hugging Face, no high-level wrappers
- Pure PyTorch `nn.Module` only
- Must pass a sanity check (loss decreases, shapes are correct)
- Write one test per component (you learned this from this repo's style)

**Structure your implementation as**:
```
my_paper/
  model.py         — the architecture (nn.Module subclasses)
  train.py         — training loop
  data.py          — dataset + dataloader
  tests/
    test_shapes.py — assert output shapes are correct
    test_grads.py  — gradcheck on custom layers
```

---

### Week 19 — Code Quality for Research

**Study**:
- Type hints in Python: `typing` module, `mypy` usage (already in `pyproject.toml`)
- `dataclasses` for config management:
  ```python
  from dataclasses import dataclass
  @dataclass
  class TrainConfig:
      lr: float = 1e-4
      batch_size: int = 32
      max_epochs: int = 100
  ```
- Reproducibility: `torch.manual_seed`, `np.random.seed`, `random.seed`
- Logging: `logging` module (not `print`), TensorBoard integration

**Algorithm track — Tries**:
1. Implement Trie (208)
2. Design Add and Search Words Data Structure (211)
3. Word Search II (212)

---

### Week 20 — Advanced Python Patterns for ML

**Study**:
- `ultimatepython/advanced/benchmark.py` — measuring performance
- `ultimatepython/advanced/regex.py` — for text preprocessing pipelines
- `ultimatepython/data_structures/namedtuple.py` — lightweight data containers

**Advanced topics**:
- `__init_subclass__` — metaclass-free class registration (PyTorch uses this for optimizers)
- `Protocol` from `typing` — structural subtyping (like C++ concepts)
- `functools.partial` — pre-filling function arguments (common in training scripts)
- `contextlib.contextmanager` — write context managers as generators

**Month 5 checkpoint**:
- Your paper implementation runs end-to-end
- Loss decreases over training
- Code is readable by someone else (type-annotated, no magic numbers)

---

## Month 6 — Integration + Interview Prep
**Theme**: Polish everything, close gaps, simulate real interviews.

### Week 21 — Mock Interviews

**Protocol** (simulate lab interviews):
1. Pick a problem you haven't seen
2. Set a 35-minute timer
3. Talk through your approach out loud (record yourself if possible)
4. Write correct, clean code — not "I'll clean it up later"
5. Analyze time and space complexity
6. Test with edge cases (empty input, single element, all same)

**Problem set for research lab interviews** (medium-hard):
1. LRU Cache (146) — design + linked list
2. Time Based Key-Value Store (981) — binary search on sorted list
3. Design Twitter (355) — heap + OOP design
4. Median of Two Sorted Arrays (4) — hard binary search
5. Largest Rectangle in Histogram (84) — monotonic stack
6. Longest Valid Parentheses (32)
7. Regular Expression Matching (10) — 2D DP

---

### Week 22 — System Design for ML

This is asked in research engineering roles (not pure research). Know:
- **Data pipeline**: how would you serve 10M training examples efficiently?
  Answer involves: file formats (HDF5, Parquet, TFRecord), sharding, prefetching
- **Model serving**: batch inference, latency vs throughput tradeoff
- **Distributed training**: data parallel vs model parallel, gradient synchronization
- **Experiment tracking**: MLflow, W&B — understand what they actually store

**Python specifics**:
- `multiprocessing.Queue` for producer-consumer data pipelines
- `torch.nn.parallel.DistributedDataParallel` internals
- Memory-mapped arrays (`np.memmap`) for large datasets that don't fit in RAM

---

### Week 23 — Research Portfolio Polish

**Algorithmic thinking for papers**:
- Can you describe your ICRA paper's algorithm in terms of data structures and complexity?
  Reviewers and interviewers appreciate researchers who think algorithmically.
- Practice: describe any ML algorithm as if it were a graph problem.
  Attention = weighted sum = dense graph message passing.
  Backprop = topological sort + chain rule.

**Open source contribution**:
- Find one issue in PyTorch, NumPy, or a robotics ML library
- Fix it, write a test, submit a PR
- This demonstrates all three tracks simultaneously

---

### Week 24 — Final Review and Gaps

**Run the full test suite**:
```bash
cd /path/to/ultimate_python
python runner.py
```
Every module in `ultimatepython/mastery/` should pass.

**Self-assessment questions**:
1. Can you explain Python's GIL and why it matters for ML?
2. Can you implement BFS, DFS, topological sort, and Dijkstra from memory?
3. Can you write a custom PyTorch `autograd.Function` with a correct backward pass?
4. Can you explain what a numpy stride is and why `arr.T` is O(1)?
5. Can you solve any LeetCode Medium in 20 minutes?
6. Can you implement a Transformer attention head from scratch?

If the answer to any of these is no — that is your last week's focus.

---

## Quick Reference: Problem Patterns

| Pattern | Trigger words | Template |
|---|---|---|
| Sliding Window | "subarray", "substring", "contiguous", "at most k" | Two pointers, expand right, shrink left |
| Two Pointers | "sorted array", "pair sum", "palindrome" | left=0, right=n-1, move toward center |
| BFS | "shortest path", "minimum steps", "level order" | deque, visited set, process by level |
| DFS/Backtracking | "all combinations", "all paths", "permutations" | recurse, choose, unchoose |
| DP | "count ways", "minimum cost", "max profit", "can you" | define state, write recurrence |
| Heap | "kth largest/smallest", "top k", "merge k sorted" | heapq, negate for max-heap |
| Topological Sort | "prerequisite", "dependency", "DAG ordering" | Kahn's BFS with in-degree array |
| Union-Find | "connected components", "redundant edge", "group" | path compression + union by rank |
| Binary Search | "sorted + find", "minimize maximum", "feasibility" | invariant-based, not memorized bounds |
| Monotonic Stack | "next greater", "span", "histogram rectangle" | stack of indices, maintain monotone order |

---

## Resources (by track)

### Track A — Internals
- CPython source: `github.com/python/cpython` (read `Objects/` directory)
- *Fluent Python* by Luciano Ramalho — the bible for Python internals
- David Beazley's talks on generators and coroutines (PyCon 2009, 2014)
- *CPython Internals* by Anthony Shaw — explains the interpreter loop

### Track B — Algorithms
- NeetCode.io — organized by pattern, same structure as this plan
- *Introduction to Algorithms* (CLRS) — for the theory when you need it
- For hard graph problems: competitive programming resources (Codeforces editorial)

### Track C — Research Python
- Andrej Karpathy's micrograd (the inspiration for `custom_autograd.py` in this repo)
- Stanford CS231n Python/NumPy tutorial
- PyTorch internals blog post by Edward Yang
- *High Performance Python* by Micha Gorelick — profiling, optimization

---

## Tracking Your Progress

Each module in `ultimatepython/mastery/` has a `main()` function that runs assertions.
Use these as your checkpoints:

```bash
# Run all mastery modules
python -c "
from ultimatepython.mastery.algorithms import arrays_and_hashing, sliding_window, trees, graphs, dynamic_programming
from ultimatepython.mastery.internals import memory_model, generators_deep, descriptors
from ultimatepython.mastery.research import numpy_internals, custom_autograd
for mod in [arrays_and_hashing, sliding_window, trees, graphs, dynamic_programming,
            memory_model, generators_deep, descriptors, numpy_internals, custom_autograd]:
    mod.main()
    print(f'PASS: {mod.__name__}')
"
```

When all 10 pass without error, you own the material.
