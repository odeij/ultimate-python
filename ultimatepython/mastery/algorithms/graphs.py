"""
Graphs — essential for robotics path planning, knowledge graphs, and GNNs.

C programmer's translation guide:
  Adjacency list (array of linked lists)  ->  dict[int, list[int]]
  BFS with circular buffer queue          ->  collections.deque
  Visited array (bool visited[N])         ->  set() or list[bool]
  Union-Find with int parent[]            ->  list[int] parent array

Connection to AI research:
  - Message passing in Graph Neural Networks (GNNs) is BFS on a graph
  - Topological sort is how autograd determines backward pass order
  - Shortest path = beam search in sequence models (approximately)

Patterns covered:
  1. BFS — shortest path in unweighted graph
  2. DFS — connected components, cycle detection
  3. Topological sort (Kahn's algorithm)  — critical for DAG processing
  4. Union-Find (Disjoint Set Union)      — connected components, Kruskal MST
  5. Number of Islands                   — classic grid DFS/BFS
"""

from collections import deque


# ---------------------------------------------------------------------------
# Graph representation helpers
# ---------------------------------------------------------------------------

def build_adj_list(n: int, edges: list[tuple[int, int]],
                   directed: bool = False) -> dict[int, list[int]]:
    """Build adjacency list from edge list."""
    graph: dict[int, list[int]] = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph


# ---------------------------------------------------------------------------
# Pattern 1: BFS — shortest path
# ---------------------------------------------------------------------------

def bfs_shortest_path(graph: dict[int, list[int]],
                       start: int, end: int) -> int:
    """Return the shortest path length from start to end (-1 if unreachable).

    Time:  O(V + E)
    Space: O(V)  — visited set + queue

    This is identical to BFS in C except we use deque instead of a ring buffer.
    """
    if start == end:
        return 0
    visited: set[int] = {start}
    queue: deque[tuple[int, int]] = deque([(start, 0)])   # (node, distance)
    while queue:
        node, dist = queue.popleft()
        for neighbor in graph[node]:
            if neighbor == end:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1


# ---------------------------------------------------------------------------
# Pattern 2: DFS — connected components
# ---------------------------------------------------------------------------

def count_connected_components(n: int,
                                edges: list[tuple[int, int]]) -> int:
    """Count connected components in an undirected graph.

    Time:  O(V + E)
    Space: O(V)
    """
    graph = build_adj_list(n, edges)
    visited: set[int] = set()
    components = 0

    def dfs(node: int) -> None:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)

    for node in range(n):
        if node not in visited:
            dfs(node)
            components += 1
    return components


def has_cycle_directed(n: int, edges: list[tuple[int, int]]) -> bool:
    """Return True if a directed graph contains a cycle.

    Uses DFS with three-color marking (white/gray/black):
      white = unvisited
      gray  = in current DFS path (back-edge to gray node = cycle)
      black = fully processed
    """
    graph = build_adj_list(n, edges, directed=True)
    # 0 = unvisited, 1 = in stack, 2 = done
    state = [0] * n

    def dfs(node: int) -> bool:
        state[node] = 1   # gray: in current path
        for neighbor in graph[node]:
            if state[neighbor] == 1:
                return True    # back edge = cycle
            if state[neighbor] == 0 and dfs(neighbor):
                return True
        state[node] = 2   # black: done
        return False

    return any(dfs(i) for i in range(n) if state[i] == 0)


# ---------------------------------------------------------------------------
# Pattern 3: Topological Sort (Kahn's BFS-based algorithm)
# This is how ML frameworks determine the order of operations in a DAG.
# ---------------------------------------------------------------------------

def topological_sort(n: int, prerequisites: list[tuple[int, int]]) -> list[int]:
    """Return a topological ordering of n nodes, or [] if cycle exists.

    prerequisites: list of (course, prerequisite) — must take prereq before course

    Time:  O(V + E)
    Space: O(V + E)

    Kahn's algorithm:
      1. Compute in-degree for every node
      2. Start with all zero-in-degree nodes
      3. Process each, decrement neighbor in-degrees
      4. If a neighbor hits zero, enqueue it
    """
    in_degree = [0] * n
    graph: dict[int, list[int]] = {i: [] for i in range(n)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue: deque[int] = deque(node for node in range(n) if in_degree[node] == 0)
    order: list[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []   # [] means cycle


# ---------------------------------------------------------------------------
# Pattern 4: Union-Find (Disjoint Set Union)
# Fastest way to answer "are these two nodes connected?" repeatedly.
# Used in Kruskal MST and clustering algorithms.
# ---------------------------------------------------------------------------

class UnionFind:
    """Union-Find with path compression and union by rank.

    Path compression: after find(x), make x point directly to root.
    Union by rank:    always attach smaller tree under larger tree.

    Time per operation: O(α(n)) ≈ O(1) amortized (inverse Ackermann function)
    """

    def __init__(self, n: int):
        self.parent = list(range(n))   # parent[i] = i initially (self-loops)
        self.rank = [0] * n
        self.components = n

    def find(self, x: int) -> int:
        """Find root of x with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # compress path
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union the sets containing x and y. Returns True if merged."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False   # already in the same component
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# ---------------------------------------------------------------------------
# Pattern 5: Number of Islands (grid BFS/DFS)
# Classic problem — directly maps to image segmentation and flood fill.
# ---------------------------------------------------------------------------

def num_islands(grid: list[list[str]]) -> int:
    """Return the number of islands ('1' surrounded by '0' or boundary).

    Strategy: whenever we find an unvisited '1', BFS/DFS to mark the
    entire island as visited, then count += 1.

    Time:  O(m * n)
    Space: O(m * n) in worst case (all land, DFS call stack)
    """
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0

    def bfs(r: int, c: int) -> None:
        queue: deque[tuple[int, int]] = deque([(r, c)])
        visited.add((r, c))
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = row + dr, col + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and grid[nr][nc] == "1"
                        and (nr, nc) not in visited):
                    queue.append((nr, nc))
                    visited.add((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                bfs(r, c)
                count += 1
    return count


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------
# MEDIUM:
#   1. Clone Graph (133)                  — BFS + hash map for copies
#   2. Pacific Atlantic Water Flow (417)  — reverse BFS from two oceans
#   3. Course Schedule II (210)           — topological sort, return order
#   4. Redundant Connection (684)         — Union-Find, find cycle edge
#
# HARD:
#   5. Word Ladder (127)                  — BFS on implicit graph
#   6. Alien Dictionary (269)             — topological sort from word order
# ---------------------------------------------------------------------------


def main() -> None:
    # BFS shortest path
    g = build_adj_list(6, [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)])
    assert bfs_shortest_path(g, 0, 5) == 3
    assert bfs_shortest_path(g, 0, 0) == 0

    # Connected components
    assert count_connected_components(5, [(0, 1), (1, 2), (3, 4)]) == 2
    assert count_connected_components(5, [(0, 1), (1, 2), (2, 3), (3, 4)]) == 1

    # Cycle detection
    assert has_cycle_directed(4, [(0, 1), (1, 2), (2, 0), (3, 0)]) is True
    assert has_cycle_directed(4, [(0, 1), (1, 2), (2, 3)]) is False

    # Topological sort
    assert topological_sort(4, [(1, 0), (2, 0), (3, 1), (3, 2)]) == [0, 1, 2, 3]
    assert topological_sort(2, [(0, 1), (1, 0)]) == []  # cycle

    # Union-Find
    uf = UnionFind(5)
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.connected(0, 2) is True
    assert uf.connected(0, 3) is False
    assert uf.components == 3

    # Number of Islands
    grid1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    assert num_islands(grid1) == 1
    grid2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    assert num_islands(grid2) == 3


if __name__ == "__main__":
    main()
