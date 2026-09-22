def bfs(danh_sach_ke, bat_dau):
    """Nhận {đỉnh: [(đỉnh kề, trọng số), ...]} và trả dữ liệu kết quả.

    Duyệt hàng xóm theo thứ tự trong danh sách kề, không xét trọng số.
    Đánh dấu ngay khi đưa vào hàng đợi để không thêm trùng một đỉnh.
    """
    if bat_dau not in danh_sach_ke:
        raise ValueError(f'Không có đỉnh {bat_dau} trong đồ thị.')

    hang_doi = [bat_dau]
    dau = 0  # Phần hàng đợi chưa xử lý là hang_doi[dau:].
    da_phat_hien = {bat_dau}
    thu_tu, canh_duyet, cac_buoc = [], [], []
    khung_hinh = []

    def ghi_khung(ghi_chu, hien_tai=None):
        # Sao chép ngay tại thời điểm chạy; không suy ra trạng thái từ lời giải.
        dang_cho = hang_doi[dau:]
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

    ghi_khung(f'BFS: đưa {bat_dau} vào hàng đợi. Hàng đợi xử lý từ trái sang phải.')

    while dau < len(hang_doi):
        u = hang_doi[dau]
        dau += 1
        thu_tu.append(u)
        moi = []
        for v, _ in danh_sach_ke[u]:
            if v not in da_phat_hien:
                da_phat_hien.add(v)
                hang_doi.append(v)
                canh_duyet.append((u, v))
                moi.append(v)
        cac_buoc.append({
            'hanh_dong': f'Lấy {u} khỏi hàng đợi; thêm: {", ".join(moi) or "không có"}.',
            'dang_cho': hang_doi[dau:],
            'thu_tu': thu_tu.copy(),
        })
        ghi_khung(cac_buoc[-1]['hanh_dong'], u)

    chua_den_duoc = [v for v in danh_sach_ke if v not in da_phat_hien]
    ghi_khung(
        f'BFS hoàn tất: {" → ".join(map(str, thu_tu))}. '
        f'Không đến được từ {bat_dau}: {", ".join(map(str, chua_den_duoc)) or "không có"}.'
    )

    return {
        'thuat_toan': 'BFS', 'bat_dau': bat_dau,
        'thu_tu': thu_tu, 'canh_duyet': canh_duyet,
        'chua_den_duoc': chua_den_duoc,
        'cac_buoc': cac_buoc, 'khung_hinh': khung_hinh,
    }
