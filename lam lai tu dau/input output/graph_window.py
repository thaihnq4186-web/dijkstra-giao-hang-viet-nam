import math
import tkinter as tk
from tkinter import ttk


class GraphWindow:
    def __init__(self, root, graph, result=None, autoplay=False):
        self.root, self.graph = root, graph
        metadata = result.data if result else {}
        self.frames = result.frames if result and result.frames else [
            dict(note='Đồ thị hiện tại', nodes=[], edges=[], labels={})]
        self.index = 0 if autoplay else len(self.frames) - 1
        self.playing, self.timer, self.closed = False, None, False
        root.title('Đồ thị — ' + (result.title if result else 'Đồ thị hiện tại'))
        width = min(1120, root.winfo_screenwidth() - 60)
        height = min(850, root.winfo_screenheight() - 90)
        root.geometry(f'{width}x{height}')
        root.minsize(660, 500)
        root.configure(background='#edf3f8')
        root.protocol('WM_DELETE_WINDOW', self.close)
        title = result.title if result else 'Đồ thị hiện tại'
        ttk.Label(root, text=title, font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=16, pady=(12, 4))
        kind = 'Có hướng' if graph.directed else 'Vô hướng'
        ttk.Label(root, text=f'{kind} · {len(graph.vertices)} đỉnh · {len(graph.edges)} cạnh. Đóng cửa sổ để quay lại terminal.').pack(anchor='w', padx=16)

        controls = ttk.Frame(root)
        controls.pack(fill='x', padx=16, pady=8)
        self.play_button = ttk.Button(controls, text='Phát', command=self.toggle)
        self.play_button.pack(side='left')
        ttk.Button(controls, text='Phát từ đầu', command=self.restart).pack(side='left', padx=5)
        ttk.Label(controls, text='Tốc độ:').pack(side='left', padx=(10, 4))
        self.speed = tk.StringVar(root, value='Vừa')
        speed_box = ttk.Combobox(controls, textvariable=self.speed, values=['Chậm', 'Vừa', 'Nhanh'], state='readonly', width=8)
        speed_box.pack(side='left')
        speed_box.bind('<<ComboboxSelected>>', self.change_speed)
        self.counter = ttk.Label(controls)
        self.counter.pack(side='right')

        navigation = ttk.Frame(root)
        navigation.pack(fill='x', padx=16)
        self.previous = ttk.Button(navigation, text='← Trước', command=lambda: self.seek(self.index - 1))
        self.previous.pack(side='left')
        self.scale = tk.Scale(navigation, from_=0, to=max(1, len(self.frames) - 1), orient='horizontal',
                              showvalue=False, resolution=1, command=self.slider_changed,
                              borderwidth=0, highlightthickness=0)
        self.scale.pack(side='left', fill='x', expand=True, padx=8)
        self.following = ttk.Button(navigation, text='Sau →', command=lambda: self.seek(self.index + 1))
        self.following.pack(side='left')
        ttk.Button(navigation, text='Kết quả', command=lambda: self.seek(len(self.frames) - 1)).pack(side='left', padx=(5, 0))

        self.canvas = tk.Canvas(root, background='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=16, pady=8)
        self.canvas.bind('<Configure>', lambda event: self.draw())
        ttk.Label(root, text=metadata.get('legend', 'Đen: cạnh chưa chọn · Đỏ nét đậm: cạnh được chọn trong bước hiện tại'),
                  wraplength=1000).pack(anchor='w', padx=16)
        ttk.Label(root, text=metadata.get('help', 'Bấm Trước/Sau để xem từng bước. Euler: bước cuối ghi thứ tự đi qua mỗi cạnh.'),
                  wraplength=1000).pack(anchor='w', padx=16, pady=(2, 4))
        note_frame = ttk.Frame(root)
        note_frame.pack(fill='x', padx=16, pady=(0, 12))
        self.note = tk.Text(note_frame, height=3, wrap='word', font=('Segoe UI', 10), relief='flat')
        self.note.pack(side='left', fill='x', expand=True)
        scrollbar = ttk.Scrollbar(note_frame, command=self.note.yview)
        scrollbar.pack(side='right', fill='y')
        self.note.configure(yscrollcommand=scrollbar.set)
        if len(self.frames) == 1:
            self.scale.configure(state='disabled')
            self.play_button.configure(state='disabled')
        self.draw()
        if autoplay:
            self.play()

    def draw(self):
        if self.closed:
            return
        canvas, frame = self.canvas, self.frames[self.index]
        canvas.delete('all')
        width, height = max(canvas.winfo_width(), 300), max(canvas.winfo_height(), 200)
        radius = 23
        rx, ry = max(55, width / 2 - 85), max(35, height / 2 - 68)
        positions = {}
        for i, v in enumerate(self.graph.vertices):
            angle = -math.pi / 2 + 2 * math.pi * i / len(self.graph.vertices)
            positions[v] = (width / 2, height / 2) if len(self.graph.vertices) == 1 else (
                width / 2 + rx * math.cos(angle), height / 2 + ry * math.sin(angle))
        if self.graph.layout:
            for v, (x, y) in self.graph.layout['positions'].items():
                positions[v] = (65 + x * max(170, width-130), 45 + y * max(110, height-110))
        pairs = {(u, v) for u, v, _ in self.graph.edges}
        edge_labels = frame.get('labels', {}).get('edge_labels', {})
        if not isinstance(edge_labels, dict):
            edge_labels = {}
        for i, (u, v, weight) in enumerate(self.graph.edges):
            x, y = positions[u]; xx, yy = positions[v]
            distance = math.hypot(xx - x, yy - y)
            ux, uy = (xx - x) / distance, (yy - y) / distance
            sx, sy = x + ux * (radius + 2), y + uy * (radius + 2)
            ex, ey = xx - ux * (radius + 4), yy - uy * (radius + 4)
            bend = 42 if self.graph.directed and (v, u) in pairs else 0
            if str(i) in self.graph.layout.get('bends', {}):
                bend = self.graph.layout['bends'][str(i)] * height
            cx, cy = (x + xx) / 2 - uy * bend, (y + yy) / 2 + ux * bend
            points = []
            for step in range(25):
                t = step / 24
                points.extend(((1-t)**2*sx + 2*(1-t)*t*cx + t*t*ex,
                               (1-t)**2*sy + 2*(1-t)*t*cy + t*t*ey))
            selected = i in frame.get('edges', [])
            canvas.create_line(*points, fill='#dc2626' if selected else '#000000', width=5 if selected else 2,
                               arrow='last' if self.graph.directed else 'none', arrowshape=(10, 12, 5),
                               tags=('edge', f'edge_{i}'))
            lx, ly = (sx + 2*cx + ex) / 4, (sy + 2*cy + ey) / 4 - 9
            label = canvas.create_text(lx, ly, text=str(edge_labels.get(str(i), f'{weight:g}')),
                                       fill='#173047', font=('Segoe UI', 10),
                                       tags=('edge_label', f'edge_label_{i}'))
            bounds = canvas.bbox(label)
            padding = 2
            background = canvas.create_rectangle(bounds[0]-padding, bounds[1]-2, bounds[2]+padding, bounds[3]+2,
                                                 fill='white', outline='', tags='label_background')
            canvas.tag_lower(background, label)
        # Nhãn luôn ở trên các cạnh vẽ sau để không bị đường cắt ngang.
        canvas.tag_raise('label_background')
        canvas.tag_raise('edge_label')
        for v, (x, y) in positions.items():
            label = frame['node_labels'].get(v) if 'node_labels' in frame else (frame.get('labels', {}).get(v) if v != 'edge_labels' else None)
            current = frame.get('current') == v
            canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill='white',
                               outline='#1f2937', width=4 if current else 2,
                               tags=('node', f'node_{v}'))
            canvas.create_text(x, y, text=v, fill='#111827', font=('Segoe UI', 10, 'bold'), tags='node_label')
            if label is not None:
                canvas.create_text(x, y+40, text=str(label), fill='#526b80', font=('Segoe UI', 9), tags='annotation')
        self.counter.configure(text=f'Bước {self.index + 1}/{len(self.frames)}')
        self.previous.configure(state='disabled' if self.index == 0 else 'normal')
        self.following.configure(state='disabled' if self.index == len(self.frames)-1 else 'normal')
        if self.scale.get() != self.index:
            self.scale.set(self.index)
        self.note.configure(state='normal')
        self.note.delete('1.0', 'end')
        self.note.insert('1.0', frame.get('note', ''))
        self.note.configure(state='disabled')

    def slider_changed(self, value):
        index = max(0, min(int(float(value)), len(self.frames)-1))
        if index != self.index:
            self.seek(index)

    def seek(self, index):
        self.pause()
        self.index = max(0, min(index, len(self.frames)-1))
        self.draw()

    def pause(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.playing = False
        if not self.closed:
            self.play_button.configure(text='Phát')

    def schedule(self):
        self.timer = self.root.after({'Chậm':1400, 'Vừa':800, 'Nhanh':350}[self.speed.get()], self.tick)

    def play(self):
        if self.closed or self.playing or len(self.frames) <= 1:
            return
        if self.index == len(self.frames)-1:
            self.index = 0
        self.playing = True
        self.play_button.configure(text='Tạm dừng')
        self.draw()
        self.schedule()

    def tick(self):
        self.timer = None
        if not self.playing or self.closed:
            return
        self.index = min(self.index+1, len(self.frames)-1)
        self.draw()
        if self.index == len(self.frames)-1:
            self.pause()
        else:
            self.schedule()

    def toggle(self):
        self.pause() if self.playing else self.play()

    def restart(self):
        self.seek(0)
        self.play()

    def change_speed(self, event=None):
        if self.playing:
            self.pause()
            self.play()

    def close(self):
        self.pause()
        self.closed = True
        self.root.destroy()
