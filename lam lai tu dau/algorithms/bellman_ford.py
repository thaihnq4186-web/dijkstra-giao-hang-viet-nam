from .shortest_path_common import (kiem_tra, tao_ket_qua, tao_khung,
                                   them_khung_ket_qua, dinh_dang_so)


def bellman_ford(danh_sach_ke, bat_dau, dich):
    kiem_tra(danh_sach_ke, bat_dau, dich)
    cung = [(u, v, w) for u, hang in danh_sach_ke.items() for v, w in hang]
    d = {v: float('inf') for v in danh_sach_ke}
    d[bat_dau] = 0
    cha = {}
    cac_buoc = [{'mo_ta': f'Khởi tạo d({bat_dau}) = 0, các đỉnh khác = ∞.', 'khoang_cach': d.copy()}]
    khung_hinh = [tao_khung(cac_buoc[0]['mo_ta'], d, cha, hien_tai=bat_dau)]
    for luot in range(len(danh_sach_ke) - 1):
        cap_nhat = []
        for u, v, w in cung:
            if d[u] != float('inf') and d[u] + w < d[v]:
                cu = d[v]
                d[v], cha[v] = d[u] + w, u
                cap_nhat.append(f'd({v})={d[v]:g} qua {u}')
                khung_hinh.append(tao_khung(
                    f'Lượt {luot + 1}, nới lỏng {u} → {v} (w = {w:g}): '
                    f'd({v}) từ {dinh_dang_so(cu)} xuống {d[v]:g}, cha({v}) = {u}.',
                    d, cha, hien_tai=v, canh_moi=(u, v)))
        cac_buoc.append({'mo_ta': f'Lượt {luot + 1}: ' +
                         ('; '.join(cap_nhat) if cap_nhat else 'không thay đổi, dừng sớm.'),
                         'khoang_cach': d.copy()})
        khung_hinh.append(tao_khung(
            f'Kết thúc lượt {luot + 1}: ' +
            (f'{len(cap_nhat)} lần cập nhật.' if cap_nhat else 'không thay đổi, dừng sớm.'),
            d, cha))
        if not cap_nhat:
            break
    # Cạnh vẫn nới lỏng được chứng tỏ chu trình âm tới được từ nguồn.
    # Lan theo chiều cung: chỉ kết luận -∞ cho các đỉnh chịu ảnh hưởng.
    anh_huong, hang_doi = set(), []
    for u, v, w in cung:
        if d[u] != float('inf') and d[u] + w < d[v] and v not in anh_huong:
            anh_huong.add(v)
            hang_doi.append(v)
    dau = 0
    while dau < len(hang_doi):
        u = hang_doi[dau]
        dau += 1
        for v, _ in danh_sach_ke[u]:
            if v not in anh_huong:
                anh_huong.add(v)
                hang_doi.append(v)
    if anh_huong:
        for v in anh_huong:
            d[v] = -float('inf')
        cac_buoc.append({'mo_ta': 'Đánh dấu -∞ cho các đỉnh chịu ảnh hưởng chu trình âm.',
                         'khoang_cach': d.copy()})
        khung_hinh.append(tao_khung(
            'Phát hiện chu trình âm tới được từ nguồn. Các đỉnh màu đỏ chịu ảnh hưởng: d = −∞.',
            d, cha, anh_huong=anh_huong))
    ket_qua = tao_ket_qua('Bellman–Ford', bat_dau, dich, d, cha, cac_buoc, anh_huong)
    return them_khung_ket_qua(ket_qua, cha, khung_hinh)
