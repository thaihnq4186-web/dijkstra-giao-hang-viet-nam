from algorithms.advanced_common import DoThi, Result, prepare_euler, finish_euler


def fleury(do_thi, bat_dau=None):
    g = DoThi(do_thi)
    if g.directed:
        raise ValueError('Fleury áp dụng cho đồ thị vô hướng; có hướng hãy chọn Hierholzer.')
    start, adj = prepare_euler(g, bat_dau)
    result, used = Result('Fleury'), set()
    result.step(f'Bắt đầu tại {start}.', [start], current=start)

    def reach(root, omit=None):
        """Đếm số đỉnh tới được khi tạm bỏ một cạnh để nhận biết cầu."""
        seen, pending = set(), [root]
        while pending:
            u = pending.pop()
            if u in seen:
                continue
            seen.add(u)
            for v, i in adj[u]:
                if i not in used and i != omit and v not in seen:
                    pending.append(v)
        return len(seen)

    path, route, u = [start], [], start
    while len(used) < len(g.edges):
        candidates = [(v, i) for v, i in adj[u] if i not in used]
        before = reach(u)
        selected = None
        for v, i in candidates:
            if len(candidates) == 1 or reach(u, i) == before:
                selected = v, i
                break
            result.step(f'Tạm bỏ qua {u} — {v}: là cầu, vẫn còn lựa chọn khác.', path, route,
                        edge_colors={str(i): '#dc2626'}, current=u)
        if selected is None:
            raise ValueError('Không thể tiếp tục đường Euler.')
        v, i = selected
        used.add(i); route.append(i); path.append(v)
        reason = 'cạnh duy nhất còn lại' if len(candidates) == 1 else 'không phải cầu'
        result.step(f'Đi {u} → {v}: {reason}. Đường hiện tại: {" → ".join(path)}', path, route,
                    edge_colors={str(i): '#2563eb'}, current=v)
        u = v
    return finish_euler(g, result, path, route)
