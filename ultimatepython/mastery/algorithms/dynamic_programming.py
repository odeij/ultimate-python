"""
Dynamic Programming — the most dreaded interview topic, made systematic.

The two mental models:
  Top-down (memoization): recursion + cache.  Write the recurrence first,
                          add @cache or a dict.  Python makes this trivial.
  Bottom-up (tabulation): fill a table iteratively.  More explicit, sometimes
                          faster (no recursion overhead).  More like C.

C programmer's note: Python's @functools.cache is a drop-in memoization decorator.
It's equivalent to C's static hash map inside a recursive function.

DP in 4 steps:
  1. Define the state: dp[i] means "..."
  2. Write the recurrence: dp[i] = f(dp[i-1], dp[i-2], ...)
  3. Identify base cases
  4. Determine traversal order

Patterns covered:
  1. Fibonacci                  — canonical 1D DP
  2. Climbing Stairs            — 1D DP
  3. House Robber               — 1D DP with skip constraint
  4. Longest Common Subsequence — 2D DP (appears in sequence alignment!)
  5. 0/1 Knapsack               — 2D DP, classic resource allocation
  6. Word Break                 — string DP, relevant to tokenization
  7. Longest Increasing Subsequence — patience sorting variant
"""

from functools import cache


# ---------------------------------------------------------------------------
# Pattern 1: Fibonacci  — the "hello world" of DP
# ---------------------------------------------------------------------------

def fib_naive(n: int) -> int:
    """Exponential time — do NOT use.  Here to show WHY memoization matters."""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)   # O(2^n) calls


def fib_memo(n: int) -> int:
    """Top-down: add @cache to get O(n) time."""
    @cache
    def dp(i: int) -> int:
        if i <= 1:
            return i
        return dp(i - 1) + dp(i - 2)
    return dp(n)


def fib_tabulation(n: int) -> int:
    """Bottom-up: O(n) time, O(1) space."""
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


# ---------------------------------------------------------------------------
# Pattern 2: Climbing Stairs  (LeetCode 70)
# Identical recurrence to Fibonacci. Recognizing this pattern is the skill.
# ---------------------------------------------------------------------------

def climb_stairs(n: int) -> int:
    """Count ways to reach the top (1 or 2 steps at a time).

    dp[i] = dp[i-1] + dp[i-2]   (same as Fibonacci, offset by 1)
    """
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


# ---------------------------------------------------------------------------
# Pattern 3: House Robber  (LeetCode 198)
# Constraint: cannot rob adjacent houses.
# ---------------------------------------------------------------------------

def house_robber(nums: list[int]) -> int:
    """Return max money robbed without robbing adjacent houses.

    State: dp[i] = max money using houses 0..i
    Recurrence: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
      Either skip house i (take dp[i-1]),
      or rob house i and skip house i-1 (take dp[i-2] + nums[i]).
    """
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    prev2, prev1 = nums[0], max(nums[0], nums[1])
    for i in range(2, len(nums)):
        prev2, prev1 = prev1, max(prev1, prev2 + nums[i])
    return prev1


# ---------------------------------------------------------------------------
# Pattern 4: Longest Common Subsequence  (LeetCode 1143)
# Core algorithm behind diff tools, sequence alignment (biology/NLP), BLEU score.
# ---------------------------------------------------------------------------

def lcs(text1: str, text2: str) -> int:
    """Return length of longest common subsequence.

    State: dp[i][j] = LCS of text1[0..i-1] and text2[0..j-1]
    Recurrence:
      if text1[i-1] == text2[j-1]:  dp[i][j] = dp[i-1][j-1] + 1
      else:                          dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    Time:  O(m * n)
    Space: O(m * n)  — can be reduced to O(min(m, n)) with rolling array
    """
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


# ---------------------------------------------------------------------------
# Pattern 5: 0/1 Knapsack
# The template for resource-allocation problems in operations research.
# ---------------------------------------------------------------------------

def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """Return max value achievable with given weight capacity.

    State: dp[i][w] = max value using first i items with weight limit w
    Recurrence:
      Skip item i:  dp[i][w] = dp[i-1][w]
      Take item i:  dp[i][w] = dp[i-1][w - weights[i-1]] + values[i-1]
                               (only if weights[i-1] <= w)

    Optimized to 1D array (rolling row).
    """
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        # Traverse right-to-left to avoid using item i twice
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]


# ---------------------------------------------------------------------------
# Pattern 6: Word Break  (LeetCode 139)
# Related to tokenization — does a string decompose into valid tokens?
# ---------------------------------------------------------------------------

def word_break(s: str, word_dict: list[str]) -> bool:
    """Return True if s can be segmented into words from word_dict.

    State: dp[i] = True if s[0..i-1] can be segmented
    Recurrence: dp[i] = any(dp[j] and s[j..i-1] in word_set) for j in [0, i)

    Time:  O(n^2 * max_word_len)
    Space: O(n)
    """
    word_set = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True   # empty string is always segmentable
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[n]


# ---------------------------------------------------------------------------
# Pattern 7: Longest Increasing Subsequence  (LeetCode 300)
# Two approaches — O(n²) DP and O(n log n) patience sorting
# ---------------------------------------------------------------------------

def lis_dp(nums: list[int]) -> int:
    """O(n²) DP.  Easier to understand, show this first.

    dp[i] = length of LIS ending at index i
    """
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def lis_binary_search(nums: list[int]) -> int:
    """O(n log n) using patience sorting / binary search.

    Maintain `tails`: tails[i] = smallest tail element for all increasing
    subsequences of length i+1.  This array stays sorted, enabling binary search.
    """
    from bisect import bisect_left
    tails: list[int] = []
    for num in nums:
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------
# MEDIUM:
#   1. Coin Change (322)                    — unbounded knapsack variant
#   2. Unique Paths (62)                    — 2D grid DP
#   3. Jump Game (55)                       — greedy, or DP
#   4. Edit Distance (72)                   — LCS variant, used in NLP
#
# HARD:
#   5. Burst Balloons (312)                 — interval DP
#   6. Regular Expression Matching (10)     — 2D DP with wildcards
# ---------------------------------------------------------------------------


def main() -> None:
    # Fibonacci
    assert fib_memo(10) == 55
    assert fib_tabulation(10) == 55
    assert fib_tabulation(0) == 0
    assert fib_tabulation(1) == 1

    # Climbing stairs
    assert climb_stairs(2) == 2
    assert climb_stairs(3) == 3
    assert climb_stairs(10) == 89

    # House Robber
    assert house_robber([1, 2, 3, 1]) == 4
    assert house_robber([2, 7, 9, 3, 1]) == 12

    # LCS
    assert lcs("abcde", "ace") == 3
    assert lcs("abc", "abc") == 3
    assert lcs("abc", "def") == 0

    # Knapsack
    assert knapsack([2, 3, 4, 5], [3, 4, 5, 6], 8) == 10

    # Word Break
    assert word_break("leetcode", ["leet", "code"]) is True
    assert word_break("applepenapple", ["apple", "pen"]) is True
    assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False

    # LIS
    assert lis_dp([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lis_binary_search([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lis_binary_search([0, 1, 0, 3, 2, 3]) == 4


if __name__ == "__main__":
    main()
