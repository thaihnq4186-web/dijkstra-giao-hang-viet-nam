def dfs(danh_sach_ke, bat_dau):
    """Mỗi phần tử stack là (đỉnh, chỉ số hàng xóm tiếp theo cần xét).

    Cách này mô phỏng DFS đệ quy: đi sâu theo thứ tự danh sách kề,
    hết hàng xóm thì quay lui. Trọng số không ảnh hưởng thứ tự duyệt.
    """
    if bat_dau not in danh_sach_ke:
        raise ValueError(f'Không có đỉnh {bat_dau} trong đồ thị.')

    ngan_xep = [(bat_dau, 0)]
    da_tham = {bat_dau}
    thu_tu = [bat_dau]
    canh_duyet = []
    cac_buoc = [{
        'hanh_dong': f'Thăm {bat_dau}, đưa vào ngăn xếp.',
        'dang_cho': [bat_dau], 'thu_tu': thu_tu.copy(),
    }]
    khung_hinh = []

    def ghi_khung(ghi_chu, hien_tai=None):
        dang_cho = [dinh for dinh, _ in ngan_xep]
        mau_dinh = {v: '#16a34a' for v in thu_tu}
        mau_dinh.update({v: '#38bdf8' for v in dang_cho})
        if hien_tai is not None:
            mau_dinh[hien_tai] = '#f59e0b'
        khung_hinh.append({
            'note': ghi_chu, 'nodes': thu_tu.copy(),
            'edges': canh_duyet.copy(),
            'labels': {v: f'#{i}' for i, v in enumerate(thu_tu, 1)},
            'frontier': dang_cho, 'current': hien_tai,
            'node_colors': mau_dinh,
        })

    ghi_khung(cac_buoc[0]['hanh_dong'] + ' Đỉnh ngăn xếp ở bên phải.', bat_dau)

    while ngan_xep:
        u, vi_tri = ngan_xep[-1]
        if vi_tri == len(danh_sach_ke[u]):
            ngan_xep.pop()
            cac_buoc.append({
                'hanh_dong': f'{u} đã xét hết hàng xóm: lấy khỏi ngăn xếp, quay lui.',
                'dang_cho': [dinh for dinh, _ in ngan_xep],
                'thu_tu': thu_tu.copy(),
            })
            ghi_khung(cac_buoc[-1]['hanh_dong'], ngan_xep[-1][0] if ngan_xep else None)
            continue

        v, _ = danh_sach_ke[u][vi_tri]
        ngan_xep[-1] = (u, vi_tri + 1)
        if v in da_tham:
            continue
        da_tham.add(v)
        thu_tu.append(v)
        canh_duyet.append((u, v))
        ngan_xep.append((v, 0))
        cac_buoc.append({
            'hanh_dong': f'Đi từ {u} sang {v}: thăm {v}, đưa vào ngăn xếp.',
            'dang_cho': [dinh for dinh, _ in ngan_xep],
            'thu_tu': thu_tu.copy(),
        })
        ghi_khung(cac_buoc[-1]['hanh_dong'], v)

    chua_den_duoc = [v for v in danh_sach_ke if v not in da_tham]
    ghi_khung(
        f'DFS hoàn tất: {" → ".join(map(str, thu_tu))}. '
        f'Không đến được từ {bat_dau}: {", ".join(map(str, chua_den_duoc)) or "không có"}.'
    )

    return {
        'thuat_toan': 'DFS', 'bat_dau': bat_dau,
        'thu_tu': thu_tu, 'canh_duyet': canh_duyet,
        'chua_den_duoc': chua_den_duoc,
        'cac_buoc': cac_buoc, 'khung_hinh': khung_hinh,
    }
