from pathlib import Path
import sys
from input import nhap_tu_ban_phim, doc_tu_file, HuyNhap
from output import (in_do_thi, ghi_ra_file, in_cac_bieu_dien,
                    in_ket_qua_duyet, in_ket_qua_hai_phia, in_ket_qua_duong_di, in_ket_qua_nang_cao)
from visualization import hien_thi_ket_qua, tao_ket_qua_truc_quan
from representation import danh_sach_ke

THU_MUC = Path(__file__).resolve().parent
THU_MUC_DU_LIEU = THU_MUC / 'du lieu'
# Tìm các thuật toán theo vị trí dự án, không phụ thuộc thư mục terminal.
sys.path.insert(0, str(THU_MUC.parent / 'algorithms' / 'nang cao'))
sys.path.insert(0, str(THU_MUC.parent))
from algorithms import bfs, dfs, kiem_tra_hai_phia, dijkstra, bellman_ford
from fleury import fleury
from hierholzer import hierholzer
from prim import prim
from kruskal import kruskal


def duong_dan(ten):
    path = Path(ten.strip().strip('"'))
    if path.is_absolute():
        return path
    # Chỉ nhập tên file thì đọc/lưu trong du lieu; đường dẫn tương đối tính từ input output.
    return (THU_MUC_DU_LIEU if path.parent == Path('.') else THU_MUC) / path


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    do_thi = None
    while True:
        try:
            print('''
ĐỒ THỊ — INPUT / OUTPUT / BIỂU DIỄN / DUYỆT
1. Nhập đồ thị từ bàn phím
2. Đọc đồ thị từ file TXT
3. In đồ thị ra terminal
4. Lưu đồ thị ra file TXT
5. Hiển thị cả ba cách biểu diễn
6. Duyệt BFS (chiều rộng)
7. Duyệt DFS (chiều sâu)
8. Kiểm tra đồ thị hai phía
9. Đường đi ngắn nhất (Dijkstra)
10. Đường đi ngắn nhất (Bellman–Ford)
11. Fleury
12. Hierholzer
13. Prim
14. Kruskal
0. Thoát
''')
            if do_thi is None:
                print('Hiện tại: chưa có đồ thị.')
            else:
                print(f'Hiện tại: {len(do_thi["dinh"])} đỉnh, {len(do_thi["canh"])} cạnh.')
            chon = input('Chọn chức năng: ').strip()
            if chon == '0':
                print('Đã thoát.'); return
            if chon == '1':
                moi = nhap_tu_ban_phim()
                do_thi = moi
                in_do_thi(do_thi)
            elif chon == '2':
                print('4 FILE DEMO:')
                print('Thư mục dữ liệu:', THU_MUC_DU_LIEU)
                print('  anh_co_huong.txt       : BFS, DFS, Dijkstra, Bellman–Ford')
                print('  anh_vo_huong.txt       : Prim, Kruskal; kiểm tra không hai phía')
                print('  euler_lon_vo_huong.txt : Fleury, Hierholzer; kiểm tra hai phía')
                print('  canh_am.txt            : Bellman–Ford với cạnh âm')
                ten = input('Tên/đường dẫn file (Enter để quay lại): ').strip()
                if not ten:
                    continue
                moi = doc_tu_file(duong_dan(ten))
                do_thi = moi
                in_do_thi(do_thi)
            elif chon in tuple(str(i) for i in range(3, 15)):
                if do_thi is None:
                    print('Hãy nhập hoặc đọc đồ thị trước.'); continue
                if chon == '3':
                    in_do_thi(do_thi)
                elif chon in ('11', '12', '13', '14'):
                    if chon in ('11', '12', '13'):
                        print('Các đỉnh:', ', '.join(do_thi['dinh']))
                        bat_dau = input('Đỉnh bắt đầu (Enter để tự chọn): ').strip() or None
                        ham = {'11': fleury, '12': hierholzer, '13': prim}[chon]
                        ket_qua = ham(do_thi, bat_dau)
                    else:
                        ket_qua = kruskal(do_thi)
                    in_ket_qua_nang_cao(ket_qua)
                    print('Mở cửa sổ trực quan. Đóng cửa sổ để quay lại terminal.')
                    hien_thi_ket_qua(do_thi, ket_qua)
                elif chon == '5':
                    in_cac_bieu_dien(do_thi)
                elif chon == '8':
                    ket_qua = kiem_tra_hai_phia(danh_sach_ke(do_thi))
                    in_ket_qua_hai_phia(ket_qua, do_thi['co_huong'])
                elif chon in ('9', '10'):
                    print('Các đỉnh:', ', '.join(do_thi['dinh']))
                    bat_dau = input('Đỉnh bắt đầu (Enter để quay lại): ').strip()
                    if not bat_dau:
                        continue
                    dich = input('Đỉnh đích (Enter để quay lại): ').strip()
                    if not dich:
                        continue
                    ke = danh_sach_ke(do_thi)
                    ket_qua = dijkstra(ke, bat_dau, dich) if chon == '9' else bellman_ford(ke, bat_dau, dich)
                    in_ket_qua_duong_di(ket_qua)
                elif chon in ('6', '7'):
                    print('Các đỉnh:', ', '.join(do_thi['dinh']))
                    bat_dau = input('Đỉnh bắt đầu (Enter để quay lại): ').strip()
                    if not bat_dau:
                        continue
                    ke = danh_sach_ke(do_thi)
                    ket_qua = bfs(ke, bat_dau) if chon == '6' else dfs(ke, bat_dau)
                    in_ket_qua_duyet(ket_qua)
                elif chon == '4':
                    ten = input('Tên file lưu (Enter = ket_qua.txt): ').strip() or 'ket_qua.txt'
                    path = duong_dan(ten)
                    if path.exists() and input('File đã tồn tại. Ghi đè? (y/n): ').strip().lower() != 'y':
                        print('Không ghi đè.'); continue
                    print('Đã lưu:', ghi_ra_file(do_thi, path))
                if chon in ('6', '7', '8', '9', '10'):
                    ket_qua_truc_quan = tao_ket_qua_truc_quan(do_thi, ket_qua)
                    print('Mở cửa sổ trực quan. Đóng cửa sổ để quay lại terminal.')
                    hien_thi_ket_qua(do_thi, ket_qua_truc_quan)
            else:
                print('Hãy chọn từ 0 đến 14.')
        except HuyNhap as loi:
            print(loi)
        except (ValueError, OSError, UnicodeError) as loi:
            print('Lỗi:', loi)
            print('Đồ thị trước đó vẫn được giữ nguyên.')
        except (EOFError, KeyboardInterrupt):
            print('\nĐã thoát.'); return

if __name__ == '__main__':
    main()
