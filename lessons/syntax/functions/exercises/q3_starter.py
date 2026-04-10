"""Exercise: Fix the mutable default argument in build_history

The broken version below uses a mutable default.
Your job: re-implement it correctly.

Requirements
------------
1. Each call WITHOUT an explicit `history` argument must start with a fresh list.
2. If a caller DOES pass their own list, append to that list (not a new one).
3. Always return the history list after appending the event.

Examples
--------
build_history("login")          # ["login"]
build_history("click")          # ["click"]  ← fresh list, NOT ["login", "click"]

my_log = []
build_history("start", my_log)  # ["start"]  — appended to the caller's list
build_history("stop",  my_log)  # ["start", "stop"]
"""
from typing import Optional


# BROKEN version — here for reference only, do NOT use this implementation
def _build_history_broken(event: str, history: list = []) -> list:  # noqa: B006
    history.append(event)
    return history


# YOUR IMPLEMENTATION BELOW
# Replace `pass` with the correct implementation.
def build_history(event: str, history: Optional[list] = None) -> list:
    """Append event to history and return it.

    Creates a new list if history is not provided.
    """
    # YOUR CODE HERE
    pass
