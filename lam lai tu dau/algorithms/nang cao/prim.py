from algorithms.advanced_common import DoThi, Result, fmt


def prim(do_thi, bat_dau=None):
    g = DoThi(do_thi)
    if g.directed:
        raise ValueError('Prim yêu cầu đồ thị vô hướng.')
    if bat_dau is not None:
        g.require_vertex(bat_dau)
    roots = ([bat_dau] if bat_dau is not None else []) + [v for v in g.vertices if v != bat_dau]
    result, chosen, total = Result('Prim'), [], 0
    seen, components = set(), 0
    for root in roots:
        if root in seen:
            continue
        components += 1
        seen.add(root)
        result.step(f'Bắt đầu thành phần {components} tại {root}.', seen, chosen, current=root)
        while True:
            best = None
            for i, (u, v, w) in enumerate(g.edges):
                if (u in seen) != (v in seen):
                    if best is None or w < g.edges[best][2]:
                        best = i
            if best is None:
                break
            u, v, w = g.edges[best]
            chosen.append(best); total += w
            seen.update((u, v))
            result.step(f'Chọn {u} — {v}, w={fmt(w)}; tổng={fmt(total)}', seen, chosen,
                        edge_colors={str(best): '#2563eb'})
    result.lines = [f'Số thành phần: {components}',
                    'Kết quả: ' + ('cây khung nhỏ nhất' if components == 1 else 'rừng khung nhỏ nhất'),
                    f'Tổng trọng số: {fmt(total)}', f'Các cạnh: {[g.edges[i] for i in chosen]}']
    result.step('Kết quả cuối cùng: tổng trọng số ' + fmt(total), seen, chosen)
    result.data = dict(weight=total, edges=chosen, components=components)
    return result
