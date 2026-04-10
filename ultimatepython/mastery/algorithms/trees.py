"""
Trees — critical for both LeetCode interviews and deep learning (computation graphs).

C programmer's translation guide:
  Linked list node with two pointers  ->  TreeNode class with left/right
  Recursive DFS in C                  ->  same in Python, but no stack management needed
  BFS with explicit queue (C array)   ->  collections.deque (O(1) popleft)

Why trees matter for AI research:
  - Expression trees (autograd computation graphs are trees/DAGs)
  - Decision trees, regression trees
  - Hierarchical clustering
  - Trie structures for vocabulary / tokenizer internals

Patterns covered:
  1. Tree construction from list (BFS order)
  2. Inorder / Preorder / Postorder traversal
  3. BFS level-order traversal
  4. Maximum depth
  5. Lowest Common Ancestor (LCA)
  6. Validate BST
  7. Serialize / Deserialize  (classic interview problem)
"""

from collections import deque
from typing import Optional


class TreeNode:
    """Binary tree node — equivalent to struct TreeNode in C."""

    def __init__(self, val: int = 0,
                 left: Optional["TreeNode"] = None,
                 right: Optional["TreeNode"] = None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"TreeNode({self.val})"


# ---------------------------------------------------------------------------
# Utility: build a tree from a level-order list (LeetCode convention)
# None means absent node
# ---------------------------------------------------------------------------

def build_tree(values: list[Optional[int]]) -> Optional[TreeNode]:
    """Build a binary tree from a BFS-order list.

    Example: [3, 9, 20, None, None, 15, 7]
         3
        / \\
       9  20
         /  \\
        15   7
    """
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue: deque[TreeNode] = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


# ---------------------------------------------------------------------------
# Pattern 1: DFS traversals — recursive (clean) and iterative (interview-ready)
# ---------------------------------------------------------------------------

def inorder(root: Optional[TreeNode]) -> list[int]:
    """Left -> Root -> Right.  BSTs are sorted in inorder."""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def inorder_iterative(root: Optional[TreeNode]) -> list[int]:
    """Iterative inorder — useful when recursion depth is limited.

    C mental model: manually manage the call stack with an explicit stack array.
    """
    result: list[int] = []
    stack: list[TreeNode] = []
    current = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result


def preorder(root: Optional[TreeNode]) -> list[int]:
    """Root -> Left -> Right.  Used in serialization."""
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def postorder(root: Optional[TreeNode]) -> list[int]:
    """Left -> Right -> Root.  Used in expression tree evaluation."""
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


# ---------------------------------------------------------------------------
# Pattern 2: BFS level-order traversal
# ---------------------------------------------------------------------------

def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    """Return node values grouped by level.

    This is the basis for many tree problems. If you understand this,
    you understand BFS on trees.
    """
    if not root:
        return []
    result: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_size = len(queue)         # snapshot: only process THIS level's nodes
        level: list[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


# ---------------------------------------------------------------------------
# Pattern 3: Maximum depth
# ---------------------------------------------------------------------------

def max_depth(root: Optional[TreeNode]) -> int:
    """Return the maximum depth of the tree.

    Base case: empty tree has depth 0.
    Recurrence: depth(node) = 1 + max(depth(left), depth(right))
    """
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


# ---------------------------------------------------------------------------
# Pattern 4: Lowest Common Ancestor
# This exact algorithm appears in segment tree construction and graph theory.
# ---------------------------------------------------------------------------

def lowest_common_ancestor(root: Optional[TreeNode],
                            p: int, q: int) -> Optional[TreeNode]:
    """Return the LCA of nodes with values p and q.

    Key insight: if root is p or q, root IS the LCA for that subtree.
    If p is in left subtree and q is in right subtree (or vice versa),
    current root is the LCA.
    """
    if root is None or root.val == p or root.val == q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root          # p and q are in different subtrees
    return left if left else right


# ---------------------------------------------------------------------------
# Pattern 5: Validate BST
# Common mistake: only checking parent-child, not the full range constraint.
# ---------------------------------------------------------------------------

def is_valid_bst(root: Optional[TreeNode]) -> bool:
    """Return True if the tree is a valid BST.

    BST property: every node in left subtree < node.val < every node in right subtree
    Track the valid range [min_val, max_val] as you recurse.
    """
    def validate(node: Optional[TreeNode],
                 min_val: float, max_val: float) -> bool:
        if node is None:
            return True
        if not (min_val < node.val < max_val):
            return False
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))

    return validate(root, float("-inf"), float("inf"))


# ---------------------------------------------------------------------------
# Pattern 6: Serialize / Deserialize
# LeetCode 297 — this appears in ML system design (model checkpointing!)
# ---------------------------------------------------------------------------

def serialize(root: Optional[TreeNode]) -> str:
    """Encode tree to a string using preorder + null markers."""
    if root is None:
        return "null"
    return f"{root.val},{serialize(root.left)},{serialize(root.right)}"


def deserialize(data: str) -> Optional[TreeNode]:
    """Decode string back to tree."""
    values = iter(data.split(","))

    def build() -> Optional[TreeNode]:
        val = next(values)
        if val == "null":
            return None
        node = TreeNode(int(val))
        node.left = build()
        node.right = build()
        return node

    return build()


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------
# EASY:
#   1. Symmetric Tree (101)         — mirror check
#   2. Path Sum (112)               — DFS with running sum
#
# MEDIUM:
#   3. Binary Tree Right Side View (199)  — BFS, take last of each level
#   4. Count Good Nodes (1448)            — DFS, track max along path
#   5. Kth Smallest in BST (230)          — inorder + counter
#
# HARD:
#   6. Binary Tree Maximum Path Sum (124) — postorder, track max at each node
# ---------------------------------------------------------------------------


def main() -> None:
    # Build test tree:  [3, 9, 20, None, None, 15, 7]
    root = build_tree([3, 9, 20, None, None, 15, 7])
    assert root is not None

    # Traversals
    assert inorder(root) == [9, 3, 15, 20, 7]
    assert inorder_iterative(root) == [9, 3, 15, 20, 7]
    assert preorder(root) == [3, 9, 20, 15, 7]
    assert postorder(root) == [9, 15, 7, 20, 3]

    # BFS
    assert level_order(root) == [[3], [9, 20], [15, 7]]

    # Depth
    assert max_depth(root) == 3
    assert max_depth(None) == 0

    # LCA  on BST [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]
    bst = build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    lca = lowest_common_ancestor(bst, 2, 8)
    assert lca is not None and lca.val == 6
    lca2 = lowest_common_ancestor(bst, 2, 4)
    assert lca2 is not None and lca2.val == 2

    # Validate BST
    valid_bst = build_tree([2, 1, 3])
    invalid_bst = build_tree([5, 1, 4, None, None, 3, 6])
    assert is_valid_bst(valid_bst) is True
    assert is_valid_bst(invalid_bst) is False

    # Serialize / Deserialize
    tree = build_tree([1, 2, 3, None, None, 4, 5])
    encoded = serialize(tree)
    decoded = deserialize(encoded)
    assert preorder(tree) == preorder(decoded)


if __name__ == "__main__":
    main()
