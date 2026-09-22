import math
from pathlib import Path


def load_network(path=None):
    """Đọc TXT; km của mỗi tuyến được tính từ đường gấp khúc trên sơ đồ."""
    path = Path(path) if path is not None else Path(__file__).with_name("du_lieu.txt")
    nodes, edges, routes, seen_edges = {}, [], {}, set()
    pending, section = [], None
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise ValueError(f"Không đọc được dữ liệu: {path.name}. {exc}") from exc
    except UnicodeError as exc:
        raise ValueError("File dữ liệu phải được lưu bằng UTF-8.") from exc

    for line_no, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in ("[KHO]", "[TUYEN]"):
            section = line
            continue
        parts = [part.strip() for part in line.split("|")]
        prefix = f"Dòng {line_no}: "
        if section not in ("[KHO]", "[TUYEN]"):
            raise ValueError(prefix + "cần khai báo [KHO] hoặc [TUYEN] trước dữ liệu.")
        expected = 3 if section == "[KHO]" else 4
        if len(parts) != expected or not all(parts):
            raise ValueError(prefix + f"cần đúng {expected} giá trị, ngăn cách bằng dấu |.")
        if section == "[KHO]":
            name, x, y = parts
            if name in nodes:
                raise ValueError(prefix + f"tên kho '{name}' bị trùng.")
            try:
                x, y = float(x), float(y)
            except ValueError as exc:
                raise ValueError(prefix + "tọa độ phải là số.") from exc
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError(prefix + "tọa độ phải là số hữu hạn.")
            if not (0 <= x <= 5000 and 0 <= y <= 4000):
                raise ValueError(prefix + "tọa độ phải nằm trong bản đồ 5000 × 4000 m.")
            nodes[name] = {"x": x, "y": y}
        else:
            pending.append((line_no, parts))

    if not nodes:
        raise ValueError("Dữ liệu phải có ít nhất một kho trong phần [KHO].")
    for line_no, (u, v, street, raw_points) in pending:
        prefix = f"Dòng {line_no}: "
        if u not in nodes or v not in nodes:
            raise ValueError(prefix + "tuyến đường chứa tên kho chưa khai báo.")
        if u == v:
            raise ValueError(prefix + "hai đầu tuyến phải là hai kho khác nhau.")
        key = frozenset((u, v))
        if key in seen_edges:
            raise ValueError(prefix + f"tuyến '{u} — {v}' bị trùng.")
        points = []
        for raw_point in raw_points.split(";"):
            try:
                x, y = (float(part.strip()) for part in raw_point.split(","))
            except ValueError as exc:
                raise ValueError(prefix + "điểm trên tuyến phải có dạng x,y; các điểm cách nhau bằng dấu ;.") from exc
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError(prefix + "tọa độ tuyến phải là số hữu hạn.")
            if not (0 <= x <= 5000 and 0 <= y <= 4000):
                raise ValueError(prefix + "điểm trên tuyến nằm ngoài sơ đồ 5000 × 4000 m.")
            points.append((x, y))
        if len(points) < 2:
            raise ValueError(prefix + "tuyến cần ít nhất hai điểm, gồm kho đầu và kho cuối.")
        if points[0] != (nodes[u]["x"], nodes[u]["y"]) or points[-1] != (nodes[v]["x"], nodes[v]["y"]):
            raise ValueError(prefix + "điểm đầu/cuối tuyến phải trùng tọa độ hai kho theo đúng thứ tự.")
        weight = round(sum(math.hypot(b[0] - a[0], b[1] - a[1])
                           for a, b in zip(points, points[1:])) / 1000, 3)
        seen_edges.add(key)
        edges.append((u, v, weight))
        routes[key] = {"street": street, "points": points}
    return {"nodes": nodes, "edges": edges,
            "routes": routes, "map_width": 5000.0, "map_height": 4000.0}


