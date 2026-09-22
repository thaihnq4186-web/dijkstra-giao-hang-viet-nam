from algorithms.advanced_common import DoThi, Result, fmt


class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, v):
        while v != self.parent[v]:
            self.parent[v] = self.parent[self.parent[v]]
            v = self.parent[v]
        return v

    def union(self, u, v):
        a, b = self.find(u), self.find(v)
        if a == b:
            return False
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return True


def merge_sort(items, key):
    if len(items) <= 1:
        return items[:]
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key), merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]


def kruskal(do_thi):
    g = DoThi(do_thi)
    if g.directed:
        raise ValueError('Kruskal yêu cầu đồ thị vô hướng.')
    result, chosen, total = Result('Kruskal'), [], 0
    result.step('Khởi tạo mỗi đỉnh là một tập hợp riêng.')
    dsu = DisjointSet(g.vertices)
    components = len(g.vertices)
    for i in merge_sort(list(range(len(g.edges))), key=lambda k: g.edges[k][2]):
        u, v, w = g.edges[i]
        if dsu.union(u, v):
            components -= 1
            chosen.append(i); total += w
            result.step(f'Chọn {u} — {v}, w={fmt(w)}; tổng={fmt(total)}', edges=chosen,
                        edge_colors={str(i): '#2563eb'})
        else:
            result.step(f'Bỏ {u} — {v}: tạo chu trình.', edges=chosen,
                        edge_colors={str(i): '#dc2626'})
    result.lines = [f'Số thành phần: {components}',
                    'Kết quả: ' + ('cây khung nhỏ nhất' if components == 1 else 'rừng khung nhỏ nhất'),
                    f'Tổng trọng số: {fmt(total)}', f'Các cạnh: {[g.edges[i] for i in chosen]}']
    result.step('Kết quả cuối cùng: tổng trọng số ' + fmt(total), g.vertices, chosen)
    result.data = dict(weight=total, edges=chosen, components=components)
    return result
