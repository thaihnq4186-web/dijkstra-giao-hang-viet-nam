import math
import time
import tkinter as tk
from pathlib import Path


class DeliveryTruck:
    """Nạp ảnh xe và cập nhật vị trí xe theo tuyến vận chuyển."""

    def __init__(self, app):
        self.app = app
        root = app.root
        self.delivery_timer, self.delivery_running = None, False
        self.delivery_points, self.delivery_lengths = [], []
        self.delivery_position, self.delivery_distance = None, 0.0
        self.delivery_total, self.delivery_started = 0.0, 0.0
        self.delivery_status = ''
        picture = Path(__file__).with_name('xe_tai.png')
        if not picture.is_file():
            raise ValueError('Thiếu hình xe tải xe_tai.png. Hãy giữ hình cùng thư mục main.py.')
        try:
            original = tk.PhotoImage(master=root, file=str(picture))
        except tk.TclError as error:
            raise ValueError('Không đọc được hình xe tải xe_tai.png.') from error
        shrink = max(1, math.ceil(max(original.width(), original.height()) / 56))
        self.truck_right = original.subsample(shrink, shrink)
        # Giữ chiều biểu tượng để chữ SPX vẫn đọc đúng khi xe chạy về bên trái.
        self.truck_left = self.truck_right
        self.delivery_facing = 'right'

    def stop(self):
        """Hủy chuyến cũ trước khi đổi kho, bảo trì đường hoặc đổi thuật toán."""
        if self.delivery_timer is not None:
            self.app.root.after_cancel(self.delivery_timer)
            self.delivery_timer = None
        self.delivery_running = False
        self.delivery_points, self.delivery_lengths = [], []
        self.delivery_position, self.delivery_distance = None, 0.0
        self.delivery_total, self.delivery_status = 0.0, ''
        self.app.canvas.delete('delivery_truck')

    def start(self, path):
        if not path:
            self.delivery_status = 'Không có tuyến vận chuyển tới kho nhận; xe chưa xuất phát.'
            self.app.hint.set(self.delivery_status)
            return
        start = self.app.network['nodes'][path[0]]
        self.delivery_points = [(start['x'], start['y'])]
        for source, target in zip(path, path[1:]):
            key = frozenset((source, target))
            points = list(self.app.network['routes'][key]['points'])
            node = self.app.network['nodes'][source]
            # Dữ liệu tuyến hai chiều chỉ lưu một lần; đảo điểm khi xe đi ngược.
            if points[0] != (node['x'], node['y']):
                points.reverse()
            for point in points[1:]:
                if point != self.delivery_points[-1]:
                    self.delivery_points.append(point)
        self.delivery_lengths = [math.dist(a, b) for a, b in zip(self.delivery_points, self.delivery_points[1:])]
        self.delivery_total = sum(self.delivery_lengths)
        self.delivery_position = self.delivery_points[0]
        self.delivery_distance = 0.0
        if self.delivery_total == 0:
            self.delivery_status = f'Đã giao hàng tới {self.app.target.get()}.'
            if len(path) == 1:
                self.delivery_status += ' Kho gửi và kho nhận trùng nhau.'
            self.app.hint.set(self.delivery_status)
            return
        self.delivery_started = time.monotonic()
        self.delivery_running = True
        self.delivery_status = f'Xe đang chở hàng: {self.app.source.get()} → {self.app.target.get()}.'
        self.app.hint.set(self.delivery_status)
        self.update_position(0.0)
        self.delivery_timer = self.app.root.after(40, self.tick)

    def update_position(self, distance):
        """Nội suy theo mét trên đường gấp khúc, độc lập với kích thước cửa sổ."""
        self.delivery_distance = max(0.0, min(distance, self.delivery_total))
        remaining = self.delivery_distance
        for (a, b), length in zip(zip(self.delivery_points, self.delivery_points[1:]), self.delivery_lengths):
            if remaining <= length:
                fraction = remaining / length if length else 0.0
                self.delivery_position = (a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction)
                if b[0] != a[0]:
                    self.delivery_facing = 'right' if b[0] > a[0] else 'left'
                return
            remaining -= length
        if self.delivery_points:
            self.delivery_position = self.delivery_points[-1]

    def tick(self):
        self.delivery_timer = None
        if not self.delivery_running or self.app.mode != 'route':
            return
        # 12 giây cho một chuyến demo; đây là tốc độ trình chiếu, không phải thời gian giao thực tế.
        progress = min(1.0, (time.monotonic() - self.delivery_started) / 12.0)
        self.update_position(self.delivery_total * progress)
        if progress >= 1.0:
            self.delivery_running = False
            self.delivery_status = f'Đã giao hàng tới {self.app.target.get()}.'
        else:
            self.delivery_status = f'Xe đang chở hàng tới {self.app.target.get()} · {round(progress * 100)}% hành trình.'
            self.delivery_timer = self.app.root.after(40, self.tick)
        if self.app.hovered is None and self.app.hovered_node is None:
            self.app.hint.set(self.delivery_status)
        # Chỉ vẽ lại xe mỗi khung hình để chuyển động mượt, giữ nguyên nền bản đồ.
        self.draw()

    def draw(self):
        self.app.canvas.delete('delivery_truck')
        if self.app.mode == 'route' and self.delivery_position is not None:
            x, y = self.app.map.project(*self.delivery_position)
            if not self.app.map.within_map(x,y): return
            picture = self.truck_right if self.delivery_facing == 'right' else self.truck_left
            self.app.canvas.create_image(x, y, image=picture, tags='delivery_truck')

