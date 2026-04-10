"""
NumPy Internals — understanding the engine underneath your ML code.

Why this matters:
  Every tensor operation in PyTorch/TensorFlow ultimately calls into
  something equivalent to what NumPy does. Understanding NumPy's memory
  model makes you a dramatically better ML engineer.

Key concepts:
  1. ndarray memory layout — C-order vs F-order (row-major vs column-major)
  2. Strides — how NumPy navigates memory to implement slices/transposes
  3. Views vs copies — the source of most NumPy bugs
  4. Broadcasting — the rules that make arr + arr[None, :] work
  5. Vectorization — replace Python loops with C-level array ops
  6. Universal functions (ufuncs) — the kernel abstraction

C programmer's translation:
  A C 2D array: float data[M][N]  — contiguous block, row-major
  A NumPy array: same, but with a shape tuple and a strides tuple
  that describe HOW to walk the flat memory block.

  strides = (bytes_per_row, bytes_per_element)
  data[i][j] = *(float*)(ptr + i*strides[0] + j*strides[1])
"""

import numpy as np


# ---------------------------------------------------------------------------
# 1. Memory layout: C-order (row-major) vs F-order (column-major)
# ---------------------------------------------------------------------------

def demo_memory_layout() -> None:
    """Show how data is laid out in memory.

    C-order (default): rows are contiguous.  arr[0, :] is one contiguous block.
    F-order (Fortran):  columns are contiguous.  arr[:, 0] is one contiguous block.

    Why it matters: iterating along the contiguous axis is ~10x faster
    due to CPU cache lines.
    """
    arr_c = np.array([[1, 2, 3], [4, 5, 6]], order='C', dtype=np.float64)
    arr_f = np.array([[1, 2, 3], [4, 5, 6]], order='F', dtype=np.float64)

    # C-order: (24, 8) = (3 elements * 8 bytes, 1 element * 8 bytes)
    # Means: moving 1 row = skip 24 bytes, moving 1 column = skip 8 bytes
    assert arr_c.strides == (24, 8)

    # F-order: (8, 16) — columns are contiguous
    assert arr_f.strides == (8, 16)

    assert arr_c.flags['C_CONTIGUOUS'] is True
    assert arr_f.flags['F_CONTIGUOUS'] is True


# ---------------------------------------------------------------------------
# 2. Strides and views — the most important NumPy concept
# ---------------------------------------------------------------------------

def demo_strides_and_views() -> None:
    """Demonstrate that slices create views, not copies.

    A VIEW shares the same underlying memory with a different shape/stride.
    Modifying a view modifies the original — same as pointer arithmetic in C.
    """
    original = np.arange(12).reshape(3, 4)   # [[0,1,2,3], [4,5,6,7], [8,9,10,11]]

    # Slice = view (no data copied)
    row = original[1, :]        # [4, 5, 6, 7]
    # np.shares_memory is the correct check: row.base may be original's base, not original
    # itself when original was produced by reshape (reshape can return a view too)
    assert np.shares_memory(row, original)

    row[0] = 99
    assert original[1, 0] == 99  # original was modified through the view!

    # Transpose = view with swapped strides
    t = original.T
    assert np.shares_memory(t, original)  # transpose shares memory with original
    assert t.strides == (original.strides[1], original.strides[0])

    # Force a copy with .copy()
    copy = original[1, :].copy()
    assert copy.base is None     # no base — independent data
    copy[0] = 0
    assert original[1, 0] == 99  # original unchanged


# ---------------------------------------------------------------------------
# 3. Broadcasting — the rules
# ---------------------------------------------------------------------------

def demo_broadcasting() -> None:
    """Show NumPy broadcasting rules.

    Rules (applied right-to-left on dimensions):
      1. If arrays have different number of dims, prepend 1s to the smaller shape
      2. Dimensions must be equal OR one of them must be 1
      3. Dimension of size 1 gets stretched to match the other

    This is how matrix + bias vector works in neural networks.
    """
    # Add scalar to array: scalar broadcast to all elements
    arr = np.array([1, 2, 3])
    result = arr + 10
    assert np.array_equal(result, [11, 12, 13])

    # Add row vector to matrix: row broadcast to all rows
    matrix = np.ones((3, 4))    # shape (3, 4)
    row_vec = np.array([1, 2, 3, 4])   # shape (4,) -> broadcast to (3, 4)
    result = matrix + row_vec
    assert result.shape == (3, 4)
    assert np.array_equal(result[0], result[1])   # all rows identical

    # Add column vector to matrix: column broadcast to all columns
    col_vec = np.array([[10], [20], [30]])   # shape (3, 1) -> broadcast to (3, 4)
    result = matrix + col_vec
    assert result.shape == (3, 4)
    assert np.all(result[0] == 11.0)
    assert np.all(result[1] == 21.0)
    assert np.all(result[2] == 31.0)

    # Outer product via broadcasting
    a = np.array([1, 2, 3])[:, None]   # shape (3, 1)
    b = np.array([10, 20, 30])[None, :]  # shape (1, 3)
    outer = a * b                        # shape (3, 3)
    assert np.array_equal(outer, np.outer([1, 2, 3], [10, 20, 30]))


# ---------------------------------------------------------------------------
# 4. Vectorization — replace loops with array operations
# ---------------------------------------------------------------------------

def slow_pairwise_distance(X: np.ndarray) -> np.ndarray:
    """Compute pairwise Euclidean distances — naive Python loop (DO NOT USE)."""
    n = X.shape[0]
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i, j] = np.sqrt(np.sum((X[i] - X[j]) ** 2))
    return dist


def fast_pairwise_distance(X: np.ndarray) -> np.ndarray:
    """Compute pairwise distances vectorized.

    ||x - y||^2 = ||x||^2 + ||y||^2 - 2 * x.T @ y

    This is the standard trick used in k-NN and attention mechanisms.
    """
    sq_norms = np.sum(X ** 2, axis=1)   # shape (n,)
    # Broadcasting: sq_norms[:, None] = column, sq_norms[None, :] = row
    sq_dists = sq_norms[:, None] + sq_norms[None, :] - 2 * X @ X.T
    # Numerical precision: small negatives can appear due to floating point
    sq_dists = np.maximum(sq_dists, 0)
    return np.sqrt(sq_dists)


# ---------------------------------------------------------------------------
# 5. Einsum — the Swiss Army knife of tensor contractions
# Used heavily in attention mechanisms and custom layer implementations.
# ---------------------------------------------------------------------------

def demo_einsum() -> None:
    """Demonstrate numpy.einsum for various tensor operations.

    einsum notation: 'ij,jk->ik' means sum over j (matrix multiply)
    Each letter is a dimension. Repeated letters that don't appear in output
    are summed over.

    This is the same notation used in papers and in PyTorch's torch.einsum.
    """
    A = np.random.randn(3, 4)
    B = np.random.randn(4, 5)

    # Matrix multiply
    C_einsum = np.einsum('ij,jk->ik', A, B)
    C_matmul = A @ B
    assert np.allclose(C_einsum, C_matmul)

    # Batch matrix multiply (used in attention)
    batch_A = np.random.randn(8, 3, 4)   # batch of 8 matrices
    batch_B = np.random.randn(8, 4, 5)
    result = np.einsum('bij,bjk->bik', batch_A, batch_B)
    assert result.shape == (8, 3, 5)

    # Dot product of each row with itself (batch squared norms)
    X = np.random.randn(10, 4)
    sq_norms_einsum = np.einsum('ij,ij->i', X, X)
    sq_norms_direct = np.sum(X ** 2, axis=1)
    assert np.allclose(sq_norms_einsum, sq_norms_direct)

    # Outer product
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    outer_einsum = np.einsum('i,j->ij', a, b)
    outer_direct = np.outer(a, b)
    assert np.allclose(outer_einsum, outer_direct)


# ---------------------------------------------------------------------------
# 6. Memory efficiency: in-place operations
# ---------------------------------------------------------------------------

def demo_inplace_operations() -> None:
    """Show how in-place ops avoid allocating new arrays.

    Critical in training loops where tensors are large.
    """
    a = np.array([1.0, 2.0, 3.0])
    original_id = id(a)

    # Out-of-place: creates a new array
    b = a + 1.0
    assert id(b) != original_id

    # In-place: modifies a, no new allocation
    a += 1.0
    assert id(a) == original_id   # same object
    assert np.array_equal(a, [2.0, 3.0, 4.0])

    # Explicit out-of parameter
    c = np.zeros(3)
    np.add(a, 10.0, out=c)   # write result into c, no new allocation
    assert np.array_equal(c, [12.0, 13.0, 14.0])
    assert np.array_equal(a, [2.0, 3.0, 4.0])  # a unchanged


def main() -> None:
    demo_memory_layout()
    demo_strides_and_views()
    demo_broadcasting()

    # Pairwise distance
    X = np.random.randn(10, 3)
    dist_slow = slow_pairwise_distance(X)
    dist_fast = fast_pairwise_distance(X)
    assert np.allclose(dist_slow, dist_fast, atol=1e-6)
    # Diagonal should be zero (distance from point to itself)
    # Use atol due to floating-point residuals after sqrt
    assert np.allclose(np.diag(dist_fast), 0.0, atol=1e-6)

    demo_einsum()
    demo_inplace_operations()


if __name__ == "__main__":
    main()
