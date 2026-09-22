def tao_ket_qua_truc_quan(do_thi, ket_qua):
    """Đổi các ảnh chụp trạng thái thuật toán sang khung hình dùng chung."""
    from algorithms.advanced_common import DoThi, Result
    if isinstance(ket_qua, Result):
        return ket_qua
    graph = DoThi(do_thi)
    hai_phia = 'la_hai_phia' in ket_qua
    ten = 'Kiểm tra đồ thị hai phía' if hai_phia else ket_qua['thuat_toan']
    if not ket_qua.get('khung_hinh'):
        raise ValueError(f'{ten} chưa có dữ liệu trực quan. Hãy khởi động lại chương trình sau khi cập nhật.')
    vi_tri = {(u, v): i for i, (u, v, _) in enumerate(graph.edges)}
    if not graph.directed:
        vi_tri.update({(v, u): i for i, (u, v, _) in enumerate(graph.edges)})

    def ma_canh(canh):
        u, v = canh
        if (u, v) in vi_tri:
            return vi_tri[u, v]
        if hai_phia and (v, u) in vi_tri:
            return vi_tri[v, u]
        raise ValueError(f'Khung trực quan có cạnh không tồn tại: {u} → {v}.')

    frames = []
    for buoc in ket_qua['khung_hinh']:
        frame = dict(buoc)
        frame['nodes'] = list(buoc.get('nodes', []))
        frame['frontier'] = list(buoc.get('frontier', []))
        frame['edges'] = list(dict.fromkeys(ma_canh(canh) for canh in buoc.get('edges', [])))
        frame['edge_colors'] = {str(ma_canh(canh)): mau for canh, mau in buoc.get('edge_colors', {}).items()}
        # Tách nhãn đỉnh khỏi edge_labels để tên đỉnh bất kỳ vẫn dùng được.
        frame['node_labels'] = dict(buoc.get('labels', {}))
        frame['node_colors'] = dict(buoc.get('node_colors', {}))
        frame['labels'] = {}
        if ten in ('BFS', 'DFS'):
            cau_truc = 'Hàng đợi (đầu → cuối)' if ten == 'BFS' else 'Ngăn xếp (đáy → đỉnh)'
            frame['note'] += '\n' + cau_truc + ': ' + (' → '.join(map(str, frame['frontier'])) or '(rỗng)')
        frames.append(frame)
    if hai_phia:
        legend = 'Nhãn nhóm 0: tập U · Nhãn nhóm 1: tập V · Đỉnh viền đậm: đang xét · Cạnh đỏ nét đậm: cạnh đang xét / chu trình lẻ'
        help_text = 'Kiểm tra mọi thành phần, kể cả đỉnh cô lập. ' + ('Bỏ hướng các cung khi kiểm tra hai phía.' if graph.directed else 'Mọi cạnh phải nối hai đỉnh khác nhóm.')
    elif ten in ('BFS', 'DFS'):
        cau_truc = 'hàng đợi' if ten == 'BFS' else 'ngăn xếp'
        legend = 'Các đỉnh nền trắng · Đỉnh viền đậm: đang xét · Cạnh đỏ nét đậm: cây duyệt'
        help_text = f'Số dưới đỉnh là thứ tự duyệt. Nội dung mỗi bước ghi rõ {cau_truc}; đỉnh không tới được không có số thứ tự.'
    else:
        legend = 'Các đỉnh nền trắng · Đỉnh viền đậm: đang xét · Cạnh đỏ nét đậm: cạnh đang chọn / đường đi cuối'
        help_text = 'd là khoảng cách từ nguồn: ∞ = chưa tới được, −∞ = chịu ảnh hưởng chu trình âm. Bấm Kết quả để xem đường đi cuối.'
    legend = 'Cạnh đen: chưa chọn · ' + legend
    return Result(title=ten, lines=[frames[-1]['note']], frames=frames,
                  data={'legend': legend, 'help': help_text, 'algorithm': ten})


def hien_thi_ket_qua(do_thi, ket_qua, tu_chay=True):
    ket_qua = tao_ket_qua_truc_quan(do_thi, ket_qua)
    try:
        import tkinter as tk
        from graph_window import GraphWindow
    except ImportError as error:
        raise ValueError('Cần Python có Tcl/Tk (Tkinter) để mở cửa sổ đồ thị.') from error
    from algorithms.advanced_common import DoThi
    try:
        root = tk.Tk()
    except tk.TclError as error:
        raise ValueError('Không mở được cửa sổ Tkinter; hãy chạy trong phiên desktop có màn hình.') from error
    try:
        GraphWindow(root, DoThi(do_thi), ket_qua, autoplay=tu_chay)
        root.mainloop()
    finally:
        try:
            if root.winfo_exists():
                root.destroy()
        except tk.TclError:
            pass
