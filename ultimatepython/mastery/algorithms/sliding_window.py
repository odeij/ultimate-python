"""
Sliding Window — the pattern that turns O(n²) loops into O(n).

C programmer's translation guide:
  Two index variables (left, right) act like two pointers into an array.
  The "window" between them is the region of interest.
  In C: for (r=0; r<n; r++) { while (invalid) l++; update_best(); }
  In Python: same logic, but Python's expressive syntax makes it shorter.

When to use:
  - "subarray / substring" problems with a constraint (sum, count, unique chars)
  - Usually involves growing the right boundary and shrinking the left

Patterns covered:
  1. Max Sum Subarray of size k          — fixed window
  2. Longest Substring Without Repeating — variable window + set
  3. Minimum Window Substring            — variable window + need-map
  4. Longest Subarray with ones after deleting one element
"""

from collections import defaultdict


# ---------------------------------------------------------------------------
# Pattern 1: Fixed-size window — max sum of k consecutive elements
# ---------------------------------------------------------------------------

def max_sum_subarray(nums: list[int], k: int) -> int:
    """Return the maximum sum of any contiguous subarray of length k.

    Time: O(n)
    Space: O(1)

    Trick: instead of recomputing the sum every time, subtract the leftmost
    element and add the new rightmost element — sliding the window by one.
    """
    window_sum = sum(nums[:k])
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]   # slide right by 1
        best = max(best, window_sum)
    return best


# ---------------------------------------------------------------------------
# Pattern 2: Variable window — longest substring without repeating characters
# LeetCode 3
# ---------------------------------------------------------------------------

def length_of_longest_substring(s: str) -> int:
    """Return length of longest substring with all unique characters.

    Time:  O(n)  — each character is added and removed at most once
    Space: O(min(n, alphabet_size))

    The window [left, right] is always valid (no duplicates).
    When a duplicate is found at `right`, shrink from `left` until valid again.
    """
    char_index: dict[str, int] = {}   # last seen index of each character
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            # Jump left past the previous occurrence — O(1) instead of while loop
            left = char_index[ch] + 1
        char_index[ch] = right
        best = max(best, right - left + 1)
    return best


# ---------------------------------------------------------------------------
# Pattern 3: Variable window with frequency map — minimum window substring
# LeetCode 76  (hard, but crucial for research interview prep)
# ---------------------------------------------------------------------------

def min_window_substring(s: str, t: str) -> str:
    """Return the smallest window in s that contains all characters of t.

    Time:  O(|s| + |t|)
    Space: O(|t|)

    Strategy:
      - need  = how many more of each char we still need in the window
      - have  = count of distinct characters satisfied (freq >= required)
      - formed= len(need chars that are satisfied)
    """
    if not t or not s:
        return ""

    need: dict[str, int] = defaultdict(int)
    for ch in t:
        need[ch] += 1

    required = len(need)        # number of distinct chars in t
    have = 0                    # how many distinct chars are currently satisfied
    window_counts: dict[str, int] = defaultdict(int)

    best_len = float("inf")
    best_left = 0
    left = 0

    for right, ch in enumerate(s):
        window_counts[ch] += 1
        if ch in need and window_counts[ch] == need[ch]:
            have += 1

        # Try to contract from left while window is valid
        while have == required:
            # Update best
            window_len = right - left + 1
            if window_len < best_len:
                best_len = window_len
                best_left = left
            # Remove leftmost character
            left_ch = s[left]
            window_counts[left_ch] -= 1
            if left_ch in need and window_counts[left_ch] < need[left_ch]:
                have -= 1
            left += 1

    return s[best_left: best_left + best_len] if best_len != float("inf") else ""


# ---------------------------------------------------------------------------
# Pattern 4: Longest subarray with ones (after deleting one zero)
# LeetCode 1493
# ---------------------------------------------------------------------------

def longest_subarray_of_ones(nums: list[int]) -> int:
    """Return length of longest subarray of 1s after deleting exactly one element.

    Reframe: find longest window with at most one 0, then subtract 1 (deleted).

    Time:  O(n)
    Space: O(1)
    """
    left = 0
    zeros_in_window = 0
    best = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros_in_window += 1
        while zeros_in_window > 1:
            if nums[left] == 0:
                zeros_in_window -= 1
            left += 1
        best = max(best, right - left)  # -1 for the deleted element
    return best


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------
# EASY:
#   1. Best Time to Buy & Sell Stock (121)  — track running minimum
#
# MEDIUM:
#   2. Permutation in String (567)          — fixed window + char count
#   3. Fruit Into Baskets (904)             — at most 2 distinct values
#   4. Longest Repeating Character (424)    — variable window + max_count trick
#
# HARD:
#   5. Sliding Window Maximum (239)         — monotonic deque
# ---------------------------------------------------------------------------


def main() -> None:
    # Fixed window
    assert max_sum_subarray([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_sum_subarray([2, 3, 4, 1, 5], 2) == 7

    # Longest substring no repeat
    assert length_of_longest_substring("abcabcbb") == 3
    assert length_of_longest_substring("bbbbb") == 1
    assert length_of_longest_substring("pwwkew") == 3
    assert length_of_longest_substring("") == 0

    # Minimum window substring
    assert min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window_substring("a", "a") == "a"
    assert min_window_substring("a", "aa") == ""

    # Longest ones subarray after one deletion
    assert longest_subarray_of_ones([1, 1, 0, 1]) == 3
    assert longest_subarray_of_ones([0, 1, 1, 1, 0, 1, 1, 0, 1]) == 5
    assert longest_subarray_of_ones([1, 1, 1]) == 2


if __name__ == "__main__":
    main()
