"""Exercise: Implement is_same_object(a, b)

Your task
---------
Return True if `a` and `b` refer to the same object in memory.
Return False if they are different objects (even if their values are equal).

C mental model
--------------
This is equivalent to comparing two pointers for address equality:
    (void*)a == (void*)b
NOT comparing the values stored at those addresses:
    *a == *b   ← that would be `a == b` in Python

Constraint
----------
Do NOT use the `==` operator. Use Python's identity operator.
"""


def is_same_object(a, b) -> bool:
    """Return True if a and b refer to the same object in memory."""
    # YOUR CODE HERE
    pass
