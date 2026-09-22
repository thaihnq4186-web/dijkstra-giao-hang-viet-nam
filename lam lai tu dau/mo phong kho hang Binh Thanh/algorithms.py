import math


def _active_edges(network, blocked):
    """Mỗi cạnh là một tuyến hai chiều; tuyến bị chặn không tham gia tính toán."""
    blocked = {frozenset(pair) for pair in blocked}
    return [edge for edge in network["edges"]
            if frozenset(edge[:2]) not in blocked]


def prim(network, blocked=(), start=None):
    """Prim O(VE): cây khung nhỏ nhất, hoặc rừng khung nếu mạng bị chia cắt."""
    names = list(network["nodes"])
    if not names:
        raise ValueError("Mạng chưa có kho.")
    if start is not None and start not in network["nodes"]:
        raise ValueError("Kho bắt đầu không có trong mạng.")
    if start is not None:
        names.remove(start)
        names.insert(0, start)
    available = _active_edges(network, blocked)
    visited, selected, components, steps = set(), [], [], []
    total = 0.0

    def record(note):
        steps.append({"edges": selected.copy(), "visited": visited.copy(),
                      "note": note, "total": total})

    for root in names:
        if root in visited:
            continue
        component = [root]
        components.append(component)
        visited.add(root)
        record(f"Bắt đầu nhóm {len(components)} tại {root}.")
        while True:
            best = None
            # Chọn cạnh nhẹ nhất băng qua tập kho đã thăm/chưa thăm.
            # Khi bằng nhau, giữ tuyến xuất hiện trước trong TXT.
            for u, v, weight in available:
                if (u in visited) != (v in visited):
                    if best is None or weight < best[2]:
                        best = (u, v, weight)
            if best is None:
                break
            u, v, weight = best
            new_node = v if u in visited else u
            visited.add(new_node)
            component.append(new_node)
            selected.append(best)
            total += weight
            record(f"Chọn {u} — {v}: {weight:g} km; tổng {total:g} km.")
    return {"edges": selected, "total": total,
            "components": components, "steps": steps}


def dijkstra(network, source, target, blocked=()):
    """Dijkstra O(V² + E), chạy trên toàn bộ tuyến còn mở, không dùng cây Prim."""
    nodes = network["nodes"]
    if source not in nodes or target not in nodes:
        raise ValueError("Kho xuất phát và kho đích phải có trong mạng.")
    available = _active_edges(network, blocked)
    adjacency = {name: [] for name in nodes}
    for u, v, weight in available:
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Dijkstra yêu cầu độ dài hữu hạn và không âm.")
        adjacency[u].append((v, weight))
        adjacency[v].append((u, weight))
    distances = {name: math.inf for name in nodes}
    distances[source] = 0.0
    previous, visited, steps = {}, set(), []

    def record(current, note):
        steps.append({"visited": visited.copy(), "distances": distances.copy(),
                      "current": current, "note": note})

    record(None, f"Xuất phát từ {source}; tìm đường tới {target}.")
    while True:
        current = None
        for name in nodes:
            if name not in visited and math.isfinite(distances[name]):
                if current is None or distances[name] < distances[current]:
                    current = name
        if current is None:
            record(None, f"Không có đường từ {source} tới {target}.")
            return {"path": [], "distance": math.inf, "edges": [], "steps": steps}
        visited.add(current)
        if current == target:
            record(current, f"Đến {target}: {distances[target]:g} km.")
            break
        for neighbor, weight in adjacency[current]:
            candidate = distances[current] + weight
            if neighbor not in visited and candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = (current, weight)
        record(current, f"Xét {current}: {distances[current]:g} km từ {source}.")

    path, route_edges = [target], []
    current = target
    while current != source:
        parent, weight = previous[current]
        route_edges.append((parent, current, weight))
        path.append(parent)
        current = parent
    path.reverse()
    route_edges.reverse()
    return {"path": path, "distance": distances[target],
            "edges": route_edges, "steps": steps}
