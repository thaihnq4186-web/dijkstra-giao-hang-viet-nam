from .shortest_path_common import (kiem_tra, tao_ket_qua, tao_khung,
                                   them_khung_ket_qua, dinh_dang_so)


def dijkstra(danh_sach_ke, bat_dau, dich):
    kiem_tra(danh_sach_ke, bat_dau, dich)
    if any(w < 0 for hang in danh_sach_ke.values() for _, w in hang):
        raise ValueError('Dijkstra không áp dụng khi có cạnh âm. Hãy chọn Bellman–Ford.')
    d = {v: float('inf') for v in danh_sach_ke}
    d[bat_dau] = 0
    cha, da_chot = {}, set()
    cac_buoc = [{'mo_ta': f'Khởi tạo d({bat_dau}) = 0, các đỉnh khác = ∞.', 'khoang_cach': d.copy()}]
    khung_hinh = [tao_khung(cac_buoc[0]['mo_ta'], d, cha, cho_xet=[bat_dau])]
    while True:
        u, nho_nhat = None, float('inf')
        for v in danh_sach_ke:
            if v not in da_chot and d[v] < nho_nhat:
                u, nho_nhat = v, d[v]
        if u is None:
            break
        da_chot.add(u)
        khung_hinh.append(tao_khung(
            f'Chốt {u}: d = {d[u]:g}, nhỏ nhất trong các đỉnh chưa chốt.',
            d, cha, hien_tai=u,
            cho_xet=[v for v in d if v not in da_chot and d[v] != float('inf')]))
        cap_nhat = []
        for v, w in danh_sach_ke[u]:
            if v not in da_chot and d[u] + w < d[v]:
                cu = d[v]
                d[v], cha[v] = d[u] + w, u
                cap_nhat.append(f'd({v})={d[v]:g} qua {u}')
                khung_hinh.append(tao_khung(
                    f'Nới lỏng {u} → {v} (w = {w:g}): '
                    f'd({v}) từ {dinh_dang_so(cu)} xuống {d[v]:g}, cha({v}) = {u}.',
                    d, cha, hien_tai=u, canh_moi=(u, v),
                    cho_xet=[x for x in d if x not in da_chot and d[x] != float('inf')]))
        cac_buoc.append({'mo_ta': f'Chốt {u}; ' + ('; '.join(cap_nhat) or 'không cập nhật.'),
                         'khoang_cach': d.copy()})
    ket_qua = tao_ket_qua('Dijkstra', bat_dau, dich, d, cha, cac_buoc)
    return them_khung_ket_qua(ket_qua, cha, khung_hinh)
