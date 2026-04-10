"""
Arrays & Hashing — the foundation of 70% of LeetCode problems.

C programmer's translation guide:
  C array + manual index bookkeeping  ->  Python list with enumerate/zip
  C hash map (open addressing)        ->  Python dict (open addressing under hood)
  C counting array                    ->  collections.Counter

Key insight: Python dict lookup is O(1) amortized, same as C hash map.
The difference is Python hides the hash function and collision handling.
You can inspect it: hash("hello"), hash(42), hash((1, 2)).

Patterns covered:
  1. Two Sum          — store complement in a dict while scanning
  2. Contains Dup     — set membership is O(1)
  3. Group Anagrams   — sorted string as canonical key
  4. Top-K Frequent   — Counter + heap or bucket sort
  5. Product Except   — prefix/suffix product, no division
"""

from collections import Counter, defaultdict
import heapq
from typing import Optional


# ---------------------------------------------------------------------------
# Pattern 1: Two Sum
# C equivalent: for (i=0; i<n; i++) if (map[target-arr[i]]) return {map[...], i}
# ---------------------------------------------------------------------------

def two_sum(nums: list[int], target: int) -> list[int]:
    """Return indices of the two numbers that add to target.

    Time:  O(n)   — one pass, dict lookup is O(1)
    Space: O(n)   — dict stores up to n complements
    """
    seen: dict[int, int] = {}   # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


# ---------------------------------------------------------------------------
# Pattern 2: Contains Duplicate
# ---------------------------------------------------------------------------

def contains_duplicate(nums: list[int]) -> bool:
    """Return True if any value appears at least twice.

    Time:  O(n)
    Space: O(n)
    """
    return len(nums) != len(set(nums))


def contains_duplicate_early_exit(nums: list[int]) -> bool:
    """Same logic, but exits as soon as a duplicate is found.

    Prefer this in interviews — shows awareness of early termination.
    """
    seen: set[int] = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False


# ---------------------------------------------------------------------------
# Pattern 3: Group Anagrams
# Sort the string -> canonical key. All anagrams share the same sorted form.
# ---------------------------------------------------------------------------

def group_anagrams(strs: list[str]) -> list[list[str]]:
    """Group strings that are anagrams of each other.

    Time:  O(n * k log k)  where k = average string length
    Space: O(n * k)
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))   # sorted() returns a list, join makes it str
        groups[key].append(s)
    return list(groups.values())


def group_anagrams_count_key(strs: list[str]) -> list[list[str]]:
    """Variant: use character-count tuple as key instead of sorting.

    Time:  O(n * k)  — counting is linear, no sort
    This is the O(n*k) version interviewers love to hear about.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for ch in s:
            count[ord(ch) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())


# ---------------------------------------------------------------------------
# Pattern 4: Top-K Frequent Elements
# ---------------------------------------------------------------------------

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """Return the k most frequent elements.

    Approach A: Counter + heap  — O(n log k)
    Approach B: Bucket sort     — O(n)       <- tell the interviewer both
    """
    count = Counter(nums)
    # nlargest uses a min-heap of size k internally — O(n log k)
    return [num for num, _ in count.most_common(k)]


def top_k_frequent_bucket(nums: list[int], k: int) -> list[int]:
    """Bucket sort variant — O(n) time.

    Key observation: frequency can be at most n (all same element),
    so use frequency as array index.
    """
    count = Counter(nums)
    # buckets[i] = list of elements with frequency i
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)
    result: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        result.extend(buckets[freq])
        if len(result) >= k:
            break
    return result[:k]


# ---------------------------------------------------------------------------
# Pattern 5: Product of Array Except Self  (no division allowed)
# Classic prefix/suffix product — linear time, no extra space (besides output)
# ---------------------------------------------------------------------------

def product_except_self(nums: list[int]) -> list[int]:
    """Return array where output[i] = product of all elements except nums[i].

    Time:  O(n)
    Space: O(1) extra  (output array does not count)

    C mental model: two passes, like building a prefix sum table.
    Pass 1 (left->right): result[i] = product of nums[0..i-1]
    Pass 2 (right->left): multiply in suffix product on the fly
    """
    n = len(nums)
    result = [1] * n

    # Forward pass: result[i] holds product of all elements to the LEFT
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]

    # Backward pass: multiply in product of all elements to the RIGHT
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]

    return result


# ---------------------------------------------------------------------------
# Exercises  (try to solve these before looking at solutions above)
# ---------------------------------------------------------------------------
# EASY:
#   1. Valid Anagram (LeetCode 242)         — use Counter comparison
#   2. Valid Palindrome (LeetCode 125)      — two pointers + isalnum()
#
# MEDIUM:
#   3. Longest Consecutive Sequence (128)  — put all nums in set, then walk
#   4. Encode/Decode Strings (271)         — length-prefix encoding
#
# Think in C first. Write the brute force. Then ask: what can I cache?
# ---------------------------------------------------------------------------


def main() -> None:
    # Two Sum
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert two_sum([3, 3], 6) == [0, 1]

    # Contains Duplicate
    assert contains_duplicate([1, 2, 3, 1]) is True
    assert contains_duplicate([1, 2, 3, 4]) is False
    assert contains_duplicate_early_exit([1, 2, 3, 1]) is True

    # Group Anagrams
    result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert len(result) == 3
    result2 = group_anagrams_count_key(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert len(result2) == 3

    # Top-K Frequent
    assert set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}
    assert set(top_k_frequent_bucket([1, 1, 1, 2, 2, 3], 2)) == {1, 2}

    # Product Except Self
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]


if __name__ == "__main__":
    main()
