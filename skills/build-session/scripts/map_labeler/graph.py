"""Graph utilities for map connectivity.

Computes paths, depth, and reachability from a list of room connections.
Connections are bidirectional unless type is 'one-way'.
"""

from collections import deque


def _build_adjacency(connections: list[dict]) -> dict[str, list[str]]:
    """Build adjacency list from connections. Bidirectional unless one-way."""
    adj: dict[str, list[str]] = {}
    for c in connections:
        a, b = c["from"], c["to"]
        adj.setdefault(a, []).append(b)
        if c.get("type") != "one-way":
            adj.setdefault(b, []).append(a)
    return adj


def reachable_from(start: str, connections: list[dict]) -> set[str]:
    """Return all room IDs reachable from start via BFS."""
    adj = _build_adjacency(connections)
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited


def longest_path(start: str, connections: list[dict]) -> list[str]:
    """Find the longest simple path from start via DFS."""
    adj = _build_adjacency(connections)
    best = [start]

    def dfs(node: str, path: list[str], visited: set[str]):
        nonlocal best
        if len(path) > len(best):
            best = list(path)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, path, visited)
                path.pop()
                visited.remove(neighbor)

    dfs(start, [start], {start})
    return best


def path_depth(start: str, connections: list[dict]) -> int:
    """Length of the longest simple path from start."""
    return len(longest_path(start, connections))
