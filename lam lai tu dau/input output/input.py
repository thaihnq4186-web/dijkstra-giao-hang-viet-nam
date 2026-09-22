import math
from pathlib import Path


class HuyNhap(Exception):
    """Người dùng chủ động hủy nhập; đồ thị cũ không thay đổi."""


def _hoi(thong_bao):
    gia_tri = input(thong_bao).strip()
    if gia_tri.lower() == 'huy':
        raise HuyNhap('Đã hủy nhập, giữ nguyên đồ thị trước đó.')
    return gia_tri


def _nhap_so_nguyen(thong_bao, nho_nhat, lon_nhat=None):
    while True:
        try:
            so = int(_hoi(thong_bao))
            if so < nho_nhat or (lon_nhat is not None and so > lon_nhat):
                raise ValueError
            return so
        except ValueError:
            mien = f'{nho_nhat} đến {lon_nhat}' if lon_nhat is not None else f'{nho_nhat} trở lên'
            print(f'  Lỗi: nhập số nguyên từ {mien}.')


def _kiem_tra_dinh(danh_sach):
    if not danh_sach:
        raise ValueError('Đồ thị cần ít nhất một đỉnh.')
    da_gap = set()
    for dinh in danh_sach:
        if not isinstance(dinh, str) or not dinh or dinh.startswith('#') or any(c.isspace() for c in dinh):
            raise ValueError('Tên đỉnh không rỗng, không chứa khoảng trắng và không bắt đầu bằng #.')
        if dinh in da_gap:
            raise ValueError(f'Đỉnh {dinh} bị trùng.')
        da_gap.add(dinh)


def _them_canh(do_thi, u, v, trong_so):
    if u not in do_thi['dinh'] or v not in do_thi['dinh']:
        raise ValueError(f'Đỉnh {u} hoặc {v} chưa có trong danh sách đỉnh.')
    if u == v:
        raise ValueError('Đồ thị đơn không nhận cạnh nối một đỉnh với chính nó.')
    try:
        w = float(trong_so)
    except (TypeError, ValueError):
        raise ValueError('Trọng số phải là số, ví dụ 3, 0 hoặc -2.5.') from None
    if not math.isfinite(w):
        raise ValueError('Trọng số phải hữu hạn, không nhận inf hoặc nan.')
    for a, b, _ in do_thi['canh']:
        if (a == u and b == v) or (not do_thi['co_huong'] and a == v and b == u):
            raise ValueError(f'Cạnh {u} — {v} đã tồn tại.')
    do_thi['canh'].append((u, v, w))


def kiem_tra_do_thi(do_thi):
    """Kiểm tra dữ liệu trước khi xuất; không sửa dữ liệu truyền vào."""
    if not isinstance(do_thi, dict) or type(do_thi.get('co_huong')) is not bool:
        raise ValueError('Dữ liệu cần co_huong kiểu True/False, danh sách dinh và canh.')
    if not isinstance(do_thi.get('dinh'), list) or not isinstance(do_thi.get('canh'), list):
        raise ValueError('dinh và canh phải là danh sách.')
    _kiem_tra_dinh(do_thi['dinh'])
    ban_sao = {'co_huong': do_thi['co_huong'], 'dinh': do_thi['dinh'], 'canh': []}
    for canh in do_thi['canh']:
        if not isinstance(canh, (list, tuple)) or len(canh) != 3:
            raise ValueError('Mỗi cạnh phải có ba giá trị (đỉnh đầu, đỉnh cuối, trọng số).')
        _them_canh(ban_sao, *canh)


def nhap_tu_ban_phim():
    print('\n--- NHẬP ĐỒ THỊ ---')
    print('Gõ huy ở bất kỳ bước nào để quay về menu.')
    loai = _nhap_so_nguyen('Loại đồ thị (0 = vô hướng, 1 = có hướng): ', 0, 1)
    n = _nhap_so_nguyen('Số đỉnh: ', 1)
    while True:
        ten = _hoi(f'Nhập {n} tên đỉnh, cách nhau bằng dấu cách (Enter = 1 đến {n}): ')
        dinh = ten.split() if ten else [str(i) for i in range(1, n + 1)]
        try:
            if len(dinh) != n:
                raise ValueError(f'Cần đúng {n} tên đỉnh.')
            _kiem_tra_dinh(dinh)
            break
        except ValueError as loi:
            print('  Lỗi:', loi)
    toi_da = n * (n - 1) if loai else n * (n - 1) // 2
    m = _nhap_so_nguyen(f'Số cạnh (0 đến {toi_da}): ', 0, toi_da)
    do_thi = {'co_huong': bool(loai), 'dinh': dinh, 'canh': []}
    print('Mỗi cạnh nhập: đỉnh_đầu đỉnh_cuối trọng_số. Ví dụ: A B 5')
    print('Có thể bỏ trọng số để mặc định bằng 1. Vô hướng chỉ nhập mỗi cạnh một lần.')
    while len(do_thi['canh']) < m:
        chuoi = _hoi(f'Cạnh {len(do_thi["canh"]) + 1}/{m}: ').split()
        try:
            if len(chuoi) not in (2, 3):
                raise ValueError('Nhập dạng A B hoặc A B 5.')
            _them_canh(do_thi, chuoi[0], chuoi[1], chuoi[2] if len(chuoi) == 3 else 1)
        except ValueError as loi:
            print('  Lỗi:', loi, 'Hãy nhập lại cạnh này.')
    return do_thi


def doc_tu_file(duong_dan):
    """TXT: loại đồ thị / n m / tên đỉnh / m dòng cạnh."""
    path = Path(duong_dan)
    if path.suffix.lower() != '.txt':
        raise ValueError('Chỉ đọc file .txt.')
    noi_dung = path.read_text(encoding='utf-8-sig')
    dong = [(i, text.strip()) for i, text in enumerate(noi_dung.splitlines(), 1)
            if text.strip() and not text.lstrip().startswith('#')]
    if len(dong) < 3:
        raise ValueError('File cần ít nhất 3 dòng: loại đồ thị; n m; danh sách đỉnh.')
    if dong[0][1] not in ('0', '1'):
        raise ValueError('Dòng đầu phải là 0 (vô hướng) hoặc 1 (có hướng).')
    try:
        n, m = map(int, dong[1][1].split())
    except ValueError:
        raise ValueError('Dòng thứ hai phải gồm hai số nguyên n m.') from None
    dinh = dong[2][1].split()
    if n < 1 or m < 0 or len(dinh) != n:
        raise ValueError('Cần n >= 1, m >= 0 và đúng n tên đỉnh.')
    _kiem_tra_dinh(dinh)
    if len(dong) - 3 != m:
        raise ValueError(f'Khai báo {m} cạnh nhưng có {len(dong) - 3} dòng cạnh.')
    do_thi = {'co_huong': dong[0][1] == '1', 'dinh': dinh, 'canh': []}
    for so_dong, text in dong[3:]:
        try:
            canh = text.split()
            if len(canh) not in (2, 3):
                raise ValueError('Cạnh phải có dạng A B hoặc A B 5.')
            _them_canh(do_thi, canh[0], canh[1], canh[2] if len(canh) == 3 else 1)
        except ValueError as loi:
            raise ValueError(f'Dòng {so_dong}: {loi}') from loi
    return do_thi
