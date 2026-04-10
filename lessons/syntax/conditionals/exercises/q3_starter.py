"""Exercise: Implement safe_divide(a, b)

Your task
---------
Return a / b if b is non-zero, otherwise return 0.0.
Your function body must be a single return statement — no if blocks.

C mental model
--------------
Python's `or` and `and` return values, not just True/False.
This lets you write:
    b and (a / b) or 0.0
which short-circuits: if b is falsy (zero), the division is never evaluated.

Examples
--------
safe_divide(10, 2)  → 5.0
safe_divide(7, 0)   → 0.0
safe_divide(0, 5)   → 0.0
safe_divide(-6, 2)  → -3.0
"""


def safe_divide(a: float, b: float) -> float:
    """Return a / b, or 0.0 if b is zero.

    Implement using short-circuit logic — one return statement, no if blocks.
    """
    # YOUR CODE HERE
    pass
