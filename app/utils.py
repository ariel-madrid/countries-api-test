from collections import deque

# Breadth-First Search (BFS) to find the shortest path in an unweighted graph
# graph: dict where keys are node identifiers and values are lists of neighboring node identifiers
# from_: starting node identifier
# to: target node identifier
def bfs_shortest_path(graph, from_, to):
    queue = deque([(from_, [from_])])
    visited = set()

    while queue:
        current, path = queue.popleft()

        if current == to:
            return {"route": path}

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return {"message": "No land route found between the specified countries."}