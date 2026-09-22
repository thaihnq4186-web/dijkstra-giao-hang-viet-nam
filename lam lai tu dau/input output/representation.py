from input import kiem_tra_do_thi


def danh_sach_canh(do_thi):
    """Trả về [(đỉnh đầu, đỉnh cuối, trọng số), ...].

    Với đồ thị vô hướng, mỗi cạnh chỉ xuất hiện một lần.
    """
    kiem_tra_do_thi(do_thi)
    return [(u, v, float(w)) for u, v, w in do_thi['canh']]


def danh_sach_ke(do_thi):
    """Trả về {đỉnh: [(đỉnh kề, trọng số), ...]}.

    Có hướng: chỉ thêm v vào danh sách kề của u khi có cung u -> v.
    Vô hướng: thêm cả hai chiều. Đỉnh cô lập có danh sách rỗng.
    """
    kiem_tra_do_thi(do_thi)
    ket_qua = {dinh: [] for dinh in do_thi['dinh']}
    for u, v, w in do_thi['canh']:
        ket_qua[u].append((v, float(w)))
        if not do_thi['co_huong']:
            ket_qua[v].append((u, float(w)))
    return ket_qua


def ma_tran_ke(do_thi):
    """Trả về ma trận trọng số theo thứ tự do_thi['dinh'].

    M[i][j] là trọng số cạnh từ đỉnh thứ i tới đỉnh thứ j.
    None = không có cạnh; 0 = có cạnh trọng số 0.
    Đồ thị vô hướng có ma trận đối xứng.
    """
    kiem_tra_do_thi(do_thi)
    n = len(do_thi['dinh'])
    vi_tri = {dinh: i for i, dinh in enumerate(do_thi['dinh'])}
    ket_qua = [[None for _ in range(n)] for _ in range(n)]
    for u, v, w in do_thi['canh']:
        i, j = vi_tri[u], vi_tri[v]
        ket_qua[i][j] = float(w)
        if not do_thi['co_huong']:
            ket_qua[j][i] = float(w)
    return ket_qua
