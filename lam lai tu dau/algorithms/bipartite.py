def _tim_chu_trinh_le(u, v, cha):
    """Ghép đường lên tổ tiên chung của u, v với cạnh xung đột v-u."""
    trai = [u]
    while cha[trai[-1]] is not None:
        trai.append(cha[trai[-1]])
    vi_tri = {dinh: i for i, dinh in enumerate(trai)}
    phai = [v]
    while phai[-1] not in vi_tri:
        phai.append(cha[phai[-1]])
    chung = phai[-1]
    return trai[:vi_tri[chung] + 1] + list(reversed(phai[:-1])) + [u]


def kiem_tra_hai_phia(danh_sach_ke):
    """Nhận {đỉnh: [(đỉnh kề, trọng số), ...]}, trả dict kết quả.

    Kiểm tra mọi thành phần, kể cả đỉnh cô lập. Với đồ thị có hướng,
    bỏ hướng cạnh để xét khả năng chia hai tập. Trọng số không ảnh hưởng.
    Màu -1: chưa tô; màu 0: tập U; màu 1: tập V.
    """
    # Tạo quan hệ kề vô hướng; khử trùng khi có hai cung ngược chiều.
    ke = {v: [] for v in danh_sach_ke}
    da_them = {v: set() for v in danh_sach_ke}
    for u, hang_xom in danh_sach_ke.items():
        for v, _ in hang_xom:
            if v not in ke:
                raise ValueError(f'Đỉnh {v} chưa có trong danh sách đỉnh.')
            if v not in da_them[u]:
                da_them[u].add(v)
                ke[u].append(v)
            if u not in da_them[v]:
                da_them[v].add(u)
                ke[v].append(u)

    mau = {v: -1 for v in ke}
    cha, cac_buoc = {}, []
    canh_to_mau, khung_hinh = [], []

    def ghi_khung(ghi_chu, hang_doi=(), hien_tai=None, chu_trinh=()):
        dinh_da_to = [v for v in ke if mau[v] != -1]
        mau_dinh = {v: '#16a34a' if mau[v] == 0 else '#3b82f6' for v in dinh_da_to}
        cac_canh = canh_to_mau.copy()
        mau_canh = {}
        for u, v in zip(chu_trinh, chu_trinh[1:]):
            if (u, v) not in cac_canh and (v, u) not in cac_canh:
                cac_canh.append((u, v))
            mau_canh[u, v] = '#dc2626'
            mau_dinh[u] = mau_dinh[v] = '#dc2626'
        khung_hinh.append({
            'note': ghi_chu, 'nodes': dinh_da_to, 'edges': cac_canh,
            'labels': {v: f'nhóm {mau[v]}' for v in dinh_da_to},
            'frontier': list(hang_doi), 'current': hien_tai,
            'node_colors': mau_dinh, 'edge_colors': mau_canh,
        })

    ghi_khung('Tô hai màu: U = nhóm 0, V = nhóm 1. Bỏ hướng cạnh và kiểm tra mọi thành phần.')
    for goc in ke:
        if mau[goc] != -1:
            continue
        mau[goc], cha[goc] = 0, None
        hang_doi, dau = [goc], 0
        cac_buoc.append(f'Bắt đầu thành phần mới tại {goc}: tô màu 0 (U).')
        ghi_khung(cac_buoc[-1], hang_doi, goc)
        while dau < len(hang_doi):
            u = hang_doi[dau]
            dau += 1
            ghi_khung(f'Lấy {u} khỏi hàng đợi để kiểm tra các đỉnh kề.', hang_doi[dau:], u)
            for v in ke[u]:
                if mau[v] == -1:
                    mau[v] = 1 - mau[u]
                    cha[v] = u
                    hang_doi.append(v)
                    canh_to_mau.append((u, v))
                    tap = 'U' if mau[v] == 0 else 'V'
                    cac_buoc.append(f'Xét {u} — {v}: tô {v} màu {mau[v]} ({tap}), khác màu {u}.')
                    ghi_khung(cac_buoc[-1], hang_doi[dau:], v)
                elif mau[v] == mau[u]:
                    chu_trinh = _tim_chu_trinh_le(u, v, cha)
                    cac_buoc.append(f'Xung đột tại {u} — {v}: cả hai cùng màu {mau[u]}.')
                    ghi_khung(
                        cac_buoc[-1] + f' KHÔNG là đồ thị hai phía. Chu trình lẻ: {" → ".join(map(str, chu_trinh))}.',
                        hang_doi[dau:], u, chu_trinh,
                    )
                    return {
                        'la_hai_phia': False, 'mau': mau, 'tap_u': [], 'tap_v': [],
                        'canh_xung_dot': (u, v), 'chu_trinh_le': chu_trinh,
                        'cac_buoc': cac_buoc, 'khung_hinh': khung_hinh,
                    }

    tap_u = [v for v in ke if mau[v] == 0]
    tap_v = [v for v in ke if mau[v] == 1]
    ghi_khung(
        f'LÀ đồ thị hai phía. U (nhóm 0) = {{{", ".join(map(str, tap_u))}}}; '
        f'V (nhóm 1) = {{{", ".join(map(str, tap_v))}}}. Mọi cạnh đều nối hai nhóm khác nhau.'
    )
    return {
        'la_hai_phia': True, 'mau': mau,
        'tap_u': tap_u, 'tap_v': tap_v,
        'canh_xung_dot': None, 'chu_trinh_le': [], 'cac_buoc': cac_buoc,
        'khung_hinh': khung_hinh,
    }
