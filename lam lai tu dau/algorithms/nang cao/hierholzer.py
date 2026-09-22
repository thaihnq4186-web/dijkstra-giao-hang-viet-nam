from algorithms.advanced_common import DoThi, Result, prepare_euler, finish_euler


def hierholzer(do_thi, bat_dau=None):
    g = DoThi(do_thi)
    start, adj = prepare_euler(g, bat_dau)
    result, used = Result('Hierholzer'), set()
    result.step(f'Bắt đầu tại {start}.', [start], current=start)
    stack, reverse_path, reverse_edges = [(start, None)], [], []
    cursor = {v: 0 for v in g.vertices}
    while stack:
        u, entering = stack[-1]
        while cursor[u] < len(adj[u]) and adj[u][cursor[u]][1] in used:
            cursor[u] += 1
        if cursor[u] == len(adj[u]):
            stack.pop(); reverse_path.append(u)
            if entering is not None:
                reverse_edges.append(entering)
            result.step(f'Rút {u}; kết quả đang ghép ngược: {reverse_path}', reverse_path, reverse_edges,
                        current=u)
        else:
            v, i = adj[u][cursor[u]]
            used.add(i); stack.append((v, i))
            result.step(f'Đi {u} → {v}; stack: {[a for a, _ in stack]}',
                        [a for a, _ in stack], used, current=v, edge_colors={str(i): '#2563eb'})
    return finish_euler(g, result, reverse_path[::-1], reverse_edges[::-1])
