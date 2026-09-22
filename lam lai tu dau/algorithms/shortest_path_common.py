import math


def dinh_dang_so(so):
    if so == float('inf'):
        return '∞'
    if so == -float('inf'):
        return '−∞'
    return f'{so:g}'


def tao_khung(mo_ta, khoang_cach, cha, hien_tai=None, cho_xet=(),
             canh_moi=None, anh_huong=(), canh_ket_qua=None):
    """Chụp trạng thái độc lập; các cung giữ nguyên chiều u -> v."""
    cac_canh = ([(u, v) for v, u in cha.items()]
                if canh_ket_qua is None else list(canh_ket_qua))
    mau_canh = {canh: '#f59e0b' for canh in cac_canh}
    if canh_moi is not None:
        mau_canh[canh_moi] = '#2563eb'
    return {
        'note': mo_ta,
        'nodes': [v for v, d in khoang_cach.items() if d != float('inf')],
        'edges': cac_canh,
        'labels': {v: f'd = {dinh_dang_so(d)}' for v, d in khoang_cach.items()},
        'current': hien_tai,
        'frontier': list(cho_xet),
        'edge_colors': mau_canh,
        'node_colors': {v: '#fecaca' for v in anh_huong},
    }


def them_khung_ket_qua(ket_qua, cha, khung_hinh):
    """Khung cuối chỉ tô đường đến đích, không nhầm với cây cha tạm."""
    ten, dau, dich = (ket_qua[k] for k in ('thuat_toan', 'bat_dau', 'dich'))
    duong = ket_qua['duong_di']
    anh_huong = ket_qua['anh_huong_chu_trinh_am']
    if ket_qua['trang_thai'] == 'chu_trinh_am':
        mo_ta = (f'{ten}: không có đường đi ngắn nhất hữu hạn từ {dau} đến {dich}; '
                 'đích chịu ảnh hưởng chu trình âm (d = −∞).')
    elif ket_qua['trang_thai'] == 'khong_co_duong':
        mo_ta = f'{ten}: không có đường đi từ {dau} đến {dich} (d = ∞).'
    else:
        mo_ta = (f'{ten}: {" → ".join(map(str, duong))}; '
                 f'tổng trọng số = {dinh_dang_so(ket_qua["tong_trong_so"])}.')
    if anh_huong and dich not in anh_huong:
        mo_ta += ' Có chu trình âm tới được từ nguồn, nhưng không ảnh hưởng đến đích.'
    khung_hinh.append(tao_khung(
        mo_ta, ket_qua['khoang_cach'], cha, anh_huong=anh_huong,
        canh_ket_qua=list(zip(duong, duong[1:]))))
    ket_qua['khung_hinh'] = khung_hinh
    return ket_qua


def kiem_tra(ke, dau, dich):
    for v in (dau, dich):
        if v not in ke:
            raise ValueError(f'Không có đỉnh {v} trong đồ thị.')
    for u, hang in ke.items():
        for v, w in hang:
            if v not in ke or not math.isfinite(w):
                raise ValueError(f'Cạnh từ {u} có đỉnh hoặc trọng số không hợp lệ.')


def tao_ket_qua(ten, dau, dich, khoang_cach, cha, cac_buoc, anh_huong=()):
    duong_di = []
    if dich in anh_huong:
        trang_thai = 'chu_trinh_am'
    elif khoang_cach[dich] == float('inf'):
        trang_thai = 'khong_co_duong'
    else:
        trang_thai = 'tim_thay'
        v = dich
        while True:
            duong_di.append(v)
            if v == dau:
                break
            v = cha[v]
        duong_di.reverse()
    return {
        'thuat_toan': ten, 'bat_dau': dau, 'dich': dich,
        'trang_thai': trang_thai, 'duong_di': duong_di,
        'tong_trong_so': khoang_cach[dich], 'khoang_cach': khoang_cach,
        'anh_huong_chu_trinh_am': [v for v in khoang_cach if v in anh_huong],
        'cac_buoc': cac_buoc,
    }
