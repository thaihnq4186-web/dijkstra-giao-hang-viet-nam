from pathlib import Path
from input import kiem_tra_do_thi
from representation import danh_sach_canh, danh_sach_ke, ma_tran_ke


def in_do_thi(do_thi):
    kiem_tra_do_thi(do_thi)
    print()
    print('THÔNG TIN ĐỒ THỊ')
    print('Loại đồ thị :', 'Có hướng' if do_thi['co_huong'] else 'Vô hướng')
    print('Số đỉnh     :', len(do_thi['dinh']))
    print('Số cạnh     :', len(do_thi['canh']))
    print('Danh sách đỉnh:', ', '.join(do_thi['dinh']))
    in_danh_sach_canh(do_thi)


def in_danh_sach_canh(do_thi):
    canh = danh_sach_canh(do_thi)
    print('\nDANH SÁCH CẠNH')
    print('Ký hiệu:', 'u → v (có hướng)' if do_thi['co_huong'] else 'u — v (vô hướng, mỗi cạnh một lần)')
    width = max(10, max(len(v) for v in do_thi['dinh']) + 2)
    print(f'{"STT":<5}{"Đỉnh đầu":<{width}}{"Đỉnh cuối":<{width}}Trọng số')
    for i, (u, v, w) in enumerate(canh, 1):
        print(f'{i:<5}{u:<{width}}{v:<{width}}{float(w):g}')
    if not canh:
        print('(Không có cạnh.)')


def in_danh_sach_ke(do_thi):
    ke = danh_sach_ke(do_thi)
    print('\nDANH SÁCH KỀ')
    print('Mỗi mục: đỉnh_kề(trọng_số).')
    width = max(len(v) for v in do_thi['dinh'])
    for dinh, hang_xom in ke.items():
        noi_dung = ', '.join(f'{v}({w:g})' for v, w in hang_xom) or '(rỗng)'
        print(f'{dinh:<{width}}: {noi_dung}')


def in_ma_tran_ke(do_thi):
    ma_tran = ma_tran_ke(do_thi)
    print('\nMA TRẬN KỀ (TRỌNG SỐ)')
    print('Hàng = đỉnh đầu, cột = đỉnh cuối.')
    print('Dấu . = không có cạnh; số 0 = cạnh có trọng số 0.')
    bang = [['.' if w is None else f'{w:g}' for w in hang] for hang in ma_tran]
    width = max([3] + [len(v) + 2 for v in do_thi['dinh']] +
                [len(o) + 2 for hang in bang for o in hang])
    print(''.rjust(width) + ''.join(v.rjust(width) for v in do_thi['dinh']))
    for dinh, hang in zip(do_thi['dinh'], bang):
        print(dinh.rjust(width) + ''.join(o.rjust(width) for o in hang))


def in_cac_bieu_dien(do_thi):
    """Hiển thị đồng thời ba dạng để dễ đối chiếu."""
    kiem_tra_do_thi(do_thi)
    print()
    print('BA CÁCH BIỂU DIỄN —', 'CÓ HƯỚNG' if do_thi['co_huong'] else 'VÔ HƯỚNG')
    print('Thứ tự đỉnh:', ', '.join(do_thi['dinh']))
    in_danh_sach_canh(do_thi)
    in_danh_sach_ke(do_thi)
    in_ma_tran_ke(do_thi)


def in_ket_qua_duyet(ket_qua):
    """In kết quả do bfs.py hoặc dfs.py trả về."""
    print()
    print(f'{ket_qua["thuat_toan"]} — bắt đầu từ {ket_qua["bat_dau"]}')
    cau_truc = ('Hàng đợi (đầu → cuối)' if ket_qua['thuat_toan'] == 'BFS'
                else 'Ngăn xếp (đáy → đỉnh)')
    for i, buoc in enumerate(ket_qua['cac_buoc'], 1):
        print(f'Bước {i}: {buoc["hanh_dong"]}')
        print(f'  {cau_truc}: {buoc["dang_cho"]}')
        print('  Thứ tự duyệt:', ' → '.join(buoc['thu_tu']))
    print('\nKẾT QUẢ')
    print('Thứ tự duyệt:', ' → '.join(ket_qua['thu_tu']))
    print('Cạnh của cây duyệt:', ', '.join(f'{u} → {v}' for u, v in ket_qua['canh_duyet']) or '(không có)')
    print('Đỉnh không tới được từ đỉnh bắt đầu:', ', '.join(ket_qua['chua_den_duoc']) or '(không có)')


def in_ket_qua_hai_phia(ket_qua, co_huong=False):
    print()
    print('KIỂM TRA ĐỒ THỊ HAI PHÍA')
    if co_huong:
        print('Đồ thị có hướng: bỏ hướng các cung khi kiểm tra hai phía.')
    print('Quy ước: màu 0 thuộc U, màu 1 thuộc V.')
    for i, buoc in enumerate(ket_qua['cac_buoc'], 1):
        print(f'Bước {i}: {buoc}')
    print('\nKẾT QUẢ')
    if ket_qua['la_hai_phia']:
        print('Đồ thị LÀ đồ thị hai phía.')
        print('Tập U = {' + ', '.join(ket_qua['tap_u']) + '}')
        print('Tập V = {' + ', '.join(ket_qua['tap_v']) + '}')
        print('Mọi cạnh đều nối một đỉnh thuộc U với một đỉnh thuộc V.')
    else:
        print('Đồ thị KHÔNG là đồ thị hai phía.')
        u, v = ket_qua['canh_xung_dot']
        print(f'Cạnh xung đột: {u} — {v}, hai đỉnh cùng màu.')
        chu_trinh = ket_qua['chu_trinh_le']
        print('Chu trình lẻ:', ' — '.join(chu_trinh))
        print(f'Số cạnh của chu trình: {len(chu_trinh) - 1}.')


def in_ket_qua_duong_di(ket_qua):
    def hien_so(so):
        if so == float('inf'):
            return '∞'
        if so == -float('inf'):
            return '-∞'
        return f'{so:g}'

    print()
    print(f'{ket_qua["thuat_toan"]}: {ket_qua["bat_dau"]} → {ket_qua["dich"]}')
    for i, buoc in enumerate(ket_qua['cac_buoc'], 1):
        print(f'Bước {i}: {buoc["mo_ta"]}')
        print('  ' + ' | '.join(f'{v}: {hien_so(d)}' for v, d in buoc['khoang_cach'].items()))
    print('\nKẾT QUẢ')
    if ket_qua['trang_thai'] == 'tim_thay':
        print('Đường đi ngắn nhất:', ' → '.join(ket_qua['duong_di']))
        print('Tổng trọng số:', hien_so(ket_qua['tong_trong_so']))
    elif ket_qua['trang_thai'] == 'khong_co_duong':
        print('Không có đường đi từ đỉnh bắt đầu tới đỉnh đích.')
    else:
        print('Không có đường đi ngắn nhất hữu hạn: chu trình âm ảnh hưởng tới đích.')
        print('Tổng trọng số có thể giảm không giới hạn (-∞).')
    if ket_qua['anh_huong_chu_trinh_am']:
        print('Đỉnh chịu ảnh hưởng chu trình âm:', ', '.join(ket_qua['anh_huong_chu_trinh_am']))


def in_ket_qua_nang_cao(ket_qua):
    print()
    print(ket_qua.title)
    for i, buoc in enumerate(ket_qua.frames, 1):
        print(f'Bước {i}: {buoc["note"]}')
    print('\nKẾT QUẢ')
    for dong in ket_qua.lines:
        print(dong)


def ghi_ra_file(do_thi, duong_dan):
    """Lưu đúng định dạng mà doc_tu_file() đọc được."""
    kiem_tra_do_thi(do_thi)
    path = Path(duong_dan)
    if path.suffix.lower() != '.txt':
        raise ValueError('Tên file lưu phải kết thúc bằng .txt.')
    dong = [str(int(do_thi['co_huong'])),
            f'{len(do_thi["dinh"])} {len(do_thi["canh"])}',
            ' '.join(do_thi['dinh'])]
    # repr giữ độ chính xác khi đọc lại trọng số số thực.
    dong += [f'{u} {v} {float(w)!r}' for u, v, w in do_thi['canh']]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(dong) + '\n', encoding='utf-8')
    return path.resolve()
