from dataclasses import dataclass, field
import math


class DoThi:
    """Bản sao dữ liệu dict hiện có, không sửa đồ thị người dùng nhập."""
    def __init__(self, data):
        self.directed = data['co_huong']
        self.vertices = list(data['dinh'])
        self.edges = [(u, v, float(w)) for u, v, w in data['canh']]
        self.layout = {}
        if type(self.directed) is not bool or not self.vertices or len(set(self.vertices)) != len(self.vertices):
            raise ValueError('Loại đồ thị hoặc danh sách đỉnh không hợp lệ.')
        seen = set()
        for u, v, w in self.edges:
            self.require_vertex(u); self.require_vertex(v)
            key = (u, v) if self.directed else frozenset((u, v))
            if u == v or key in seen or not math.isfinite(w):
                raise ValueError('Cạnh trùng, khuyên hoặc trọng số không hữu hạn.')
            seen.add(key)

    def require_vertex(self, name):
        if name not in self.vertices:
            raise ValueError(f'Không có đỉnh {name}.')


@dataclass
class Result:
    """title: tên; lines: kết quả terminal; frames: hình từng bước; data: kết quả số."""
    title: str
    lines: list = field(default_factory=list)
    frames: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def step(self, note, nodes=(), edges=(), labels=None, **visual):
        self.frames.append(dict(note=note, nodes=list(nodes), edges=list(edges),
                                labels=labels or {}, **visual))


def fmt(value):
    return f'{value:g}'


def prepare_euler(g, start):
    """Kiểm tra liên thông trên phần có cạnh và điều kiện bậc Euler."""
    if start is not None:
        g.require_vertex(start)
    adj = {v: [] for v in g.vertices}
    weak = {v: [] for v in g.vertices}
    incoming = {v: 0 for v in g.vertices}
    for i, (u, v, _) in enumerate(g.edges):
        adj[u].append((v, i)); incoming[v] += 1
        weak[u].append(v); weak[v].append(u)
        if not g.directed:
            adj[v].append((u, i))
    active = [v for v in g.vertices if weak[v]]
    if not active:
        return start or g.vertices[0], adj
    seen, stack = set(), [active[0]]
    while stack:
        u = stack.pop()
        if u not in seen:
            seen.add(u); stack.extend(weak[u])
    if any(v not in seen for v in active):
        raise ValueError('Không có đường Euler: các đỉnh có cạnh không liên thông.')
    if g.directed:
        balance = {v: len(adj[v]) - incoming[v] for v in g.vertices}
        plus = [v for v in g.vertices if balance[v] == 1]
        minus = [v for v in g.vertices if balance[v] == -1]
        if any(abs(b) > 1 for b in balance.values()) or (len(plus), len(minus)) not in ((0, 0), (1, 1)):
            raise ValueError('Không có đường Euler: bậc vào/ra không phù hợp.')
        required = plus
    else:
        required = [v for v in g.vertices if len(adj[v]) % 2]
        if len(required) not in (0, 2):
            raise ValueError('Không có đường Euler: cần 0 hoặc 2 đỉnh bậc lẻ.')
    start = start if start is not None else (required[0] if required else active[0])
    if start not in active or (required and start not in required):
        raise ValueError('Đỉnh bắt đầu không hợp lệ cho đường Euler.')
    return start, adj


def finish_euler(g, result, path, route):
    if len(route) != len(g.edges):
        raise ValueError('Không dùng hết các cạnh.')
    kind = 'Chu trình Euler' if path[0] == path[-1] else 'Đường đi Euler'
    result.lines = [kind + ': ' + ' → '.join(path), f'Đã dùng {len(route)}/{len(g.edges)} cạnh đúng một lần.']
    labels = {str(i): f'#{j+1} | w={fmt(g.edges[i][2])}' for j, i in enumerate(route)}
    result.step(result.lines[0], path, route, {'edge_labels': labels})
    result.data = dict(path=path, edges=route)
    return result
