import tkinter as tk
from tkinter import ttk
from data import load_network
from algorithms import prim, dijkstra
from map_view import MapView, edge_key, number
from truck import DeliveryTruck


class WarehouseApp:
    """Tạo giao diện và nối các thao tác người dùng với bản đồ, xe và thuật toán."""

    def __init__(self, root, network=None):
        self.root = root
        self.network = network if network is not None else load_network()
        self.names = list(self.network['nodes'])
        self.blocked = set()
        self.mode, self.result, self.timer = 'idle', None, None
        self.playing, self.index, self.hovered = False, 0, None
        self.hovered_node = None
        self.pick_phase = 'source'
        root.title('Kho hàng Bình Thạnh — Prim và Dijkstra')
        window_width=max(1020,min(1280,root.winfo_screenwidth()-60))
        window_height=max(700,min(850,root.winfo_screenheight()-90))
        root.geometry(f'{window_width}x{window_height}'); root.minsize(1020,700)
        root.configure(bg='#f5f7fa')
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.bind('<F11>', lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
        root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
        style = ttk.Style(root)
        style.configure('TButton', font=('Segoe UI',10), padding=(10,8))
        style.configure('TCombobox', padding=6)
        header = tk.Frame(root, bg='#f5f7fa'); header.pack(fill='x', padx=20, pady=(10,8))
        tk.Label(header, text='KHO HÀNG BÌNH THẠNH', bg='#f5f7fa', fg='#17334a', font=('Segoe UI',20,'bold')).pack(anchor='w')
        tk.Label(header, text='TP. HỒ CHÍ MINH  /  Mạng kết nối và đường vận chuyển', bg='#f5f7fa', fg='#5d7280', font=('Segoe UI',10)).pack(anchor='w', pady=(3,0))
        body = tk.Frame(root, bg='#f5f7fa'); body.pack(fill='both', expand=True, padx=18)
        self.canvas = tk.Canvas(body, bg='#edf2ef', highlightthickness=1, highlightbackground='#cfdbd7')
        self.canvas.pack(side='left', fill='both', expand=True)
        panel = tk.Frame(body, bg='white', width=285); panel.pack(side='right', fill='y', padx=(12,0)); panel.pack_propagate(False)
        def label(text, bold=False):
            tk.Label(panel, text=text, bg='white', fg='#233f53', font=('Segoe UI',10,'bold' if bold else 'normal'), anchor='w').pack(fill='x',padx=16,pady=(12,4))
        label('CHỌN HAI KHO', True)
        self.source = tk.StringVar(root, value=self.names[0])
        self.target = tk.StringVar(root, value=self.names[-1])
        label('Kho xuất phát')
        self.source_box = ttk.Combobox(panel, textvariable=self.source, values=self.names, state='readonly')
        self.source_box.pack(fill='x', padx=16)
        label('Kho nhận hàng')
        self.target_box = ttk.Combobox(panel, textvariable=self.target, values=self.names, state='readonly')
        self.target_box.pack(fill='x', padx=16)
        self.source_box.bind('<<ComboboxSelected>>', self.selection_changed)
        self.target_box.bind('<<ComboboxSelected>>', self.selection_changed)
        self.prim_button = ttk.Button(panel, text='Chạy Prim', command=self.run_prim)
        self.prim_button.pack(fill='x', padx=16, pady=(18,7))
        ttk.Button(panel, text='Tìm đường ngắn nhất', command=self.run_route).pack(fill='x',padx=16,pady=(0,7))
        ttk.Button(panel, text='Làm lại', command=self.reset).pack(fill='x',padx=16)
        label('KẾT QUẢ', True)
        self.summary = tk.StringVar(root, value='Chọn thuật toán để bắt đầu.')
        tk.Label(panel,textvariable=self.summary,bg='white',fg='#176c76',wraplength=250,justify='left',font=('Segoe UI',12,'bold')).pack(fill='x',padx=16,pady=(3,8))
        self.details = tk.Text(panel, height=8, wrap='word', relief='flat', bg='white', fg='#385166', font=('Segoe UI',10), state='disabled', cursor='arrow')
        self.details.pack(fill='both',expand=True,padx=16,pady=(0,10))
        self.hint = tk.StringVar(root, value='Bấm lần lượt hai kho để chọn nơi gửi và nơi nhận. Bấm một tuyến để bật/tắt trạng thái bảo trì.')
        tk.Label(root,textvariable=self.hint,bg='#f5f7fa',fg='#264355',font=('Segoe UI',10),anchor='w',wraplength=1150).pack(fill='x',padx=20,pady=(10,4))
        tk.Label(root,text='Xanh lá: Prim  ·  Cam: đường ngắn nhất  ·  Đỏ đứt nét: đường đang bảo trì  ·  F11: toàn màn hình',bg='#f5f7fa',fg='#566c79',font=('Segoe UI',9),anchor='w').pack(fill='x',padx=20)
        tk.Label(root,text='Sơ đồ minh họa Bình Thạnh, phạm vi 5 × 4 km. Vị trí kho và số km là dữ liệu giả lập.',bg='#f5f7fa',fg='#6b7c87',font=('Segoe UI',9),anchor='w').pack(fill='x',padx=20,pady=(3,12))
        self.map = MapView(self)
        self.truck = DeliveryTruck(self)
        self.canvas.bind('<Configure>',lambda e:self.map.draw())
        self.canvas.bind('<Button-1>',self.map.on_map_press)
        self.canvas.bind('<B1-Motion>',self.map.pan_map)
        self.canvas.bind('<ButtonRelease-1>',self.map.end_pan)
        self.canvas.bind('<Double-Button-1>',self.map.reset_view)
        self.canvas.bind('<MouseWheel>',self.map.zoom_map)
        self.canvas.bind('<Button-4>',self.map.zoom_map)
        self.canvas.bind('<Button-5>',self.map.zoom_map)
        self.canvas.bind('<Motion>',self.hover_map)
        self.canvas.bind('<Leave>',self.leave_map)
        self.set_details('Prim: chọn các tuyến nối toàn bộ kho với tổng số km nhỏ nhất.\n\nDijkstra: tìm đường ngắn nhất từ kho xuất phát đến kho nhận trên mọi tuyến đang mở.')
        self.map.draw()

    def set_details(self,text):
        self.details.configure(state='normal'); self.details.delete('1.0','end')
        self.details.insert('1.0',text); self.details.configure(state='disabled')

    def pause(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer); self.timer=None
        self.playing=False
        self.prim_button.configure(text='Chạy Prim')

    def run_prim(self, animate=True):
        self.truck.stop()
        self.hint.set('Prim chọn mạng nối các kho. Bấm một tuyến để bật/tắt trạng thái bảo trì.')
        if animate and self.playing:
            self.pause(); self.prim_button.configure(text='Tiếp tục Prim'); return
        if animate and self.mode=='prim' and self.result and self.index<len(self.result['steps'])-1:
            self.playing=True; self.prim_button.configure(text='Tạm dừng Prim')
            self.timer=self.root.after(700,self.tick); return
        self.pause(); self.mode='prim'
        self.result=prim(self.network,self.blocked,self.source.get())
        self.index=0 if animate else len(self.result['steps'])-1
        print('\nPRIM — MẠNG KẾT NỐI CÁC KHO',flush=True)
        for step in self.result['steps']: print(step['note'],flush=True)
        self.show_prim()
        if animate and len(self.result['steps'])>1:
            self.playing=True; self.prim_button.configure(text='Tạm dừng Prim')
            self.timer=self.root.after(700,self.tick)

    def tick(self):
        self.timer=None
        if not self.playing: return
        self.index=min(self.index+1,len(self.result['steps'])-1); self.show_prim()
        if self.index==len(self.result['steps'])-1: self.pause()
        else: self.timer=self.root.after(700,self.tick)

    def show_prim(self):
        frame=self.result['steps'][self.index]
        finished=self.index==len(self.result['steps'])-1
        count=len(self.result['components'])
        status='Đã nối toàn bộ kho' if count==1 else f'Mạng bị chia thành {count} nhóm'
        self.summary.set(f'{status if finished else "Đang chọn tuyến…"}\n{len(frame["edges"])} tuyến · {number(frame["total"])} km')
        text=frame['note']+'\n\n'
        if finished and count>1: text+='Không có cây khung nối toàn bộ kho. Các tuyến xanh là rừng khung nhỏ nhất.\n\n'
        text+='\n'.join(f'{u.removeprefix("Kho ")} ↔ {v.removeprefix("Kho ")}: {number(w)} km' for u,v,w in frame['edges'])
        self.set_details(text); self.map.draw()

    def run_route(self):
        self.pause(); self.truck.stop(); self.mode='route'
        self.result=dijkstra(self.network,self.source.get(),self.target.get(),self.blocked)
        path=self.result['path']
        if path:
            self.summary.set(f'Đường ngắn nhất: {number(self.result["distance"])} km\n{len(path)-1} chặng vận chuyển')
            self.set_details('DIJKSTRA\n\n'+'\n↓\n'.join(path)+'\n\nTính trên tất cả tuyến đang mở.')
        else:
            self.summary.set('Không có đường đi')
            self.set_details(f'{self.source.get()}\n→ {self.target.get()}\n\nCác tuyến đang mở không nối được hai kho. Hãy mở lại đường đang bảo trì.')
        print(f'\nDIJKSTRA — {self.source.get()} → {self.target.get()}',flush=True)
        for step in self.result['steps']: print(step['note'],flush=True)
        print(' → '.join(path) if path else 'Không có đường đi.',flush=True)
        print(self.summary.get(),flush=True)
        self.truck.start(path)
        self.map.draw()

    def selection_changed(self,event=None):
        self.pick_phase='source'; self.recalculate()

    def recalculate(self):
        self.truck.stop()
        if self.mode=='prim': self.run_prim(animate=False)
        elif self.mode=='route': self.run_route()
        else: self.map.draw()

    def reset(self):
        self.pause(); self.truck.stop(); self.blocked.clear(); self.result=None; self.mode='idle'
        self.hovered=None; self.hovered_node=None; self.pick_phase='source'
        self.source.set(self.names[0]); self.target.set(self.names[-1])
        self.summary.set('Đã mở lại mọi tuyến.')
        self.set_details('Chọn Chạy Prim để nối các kho hoặc Tìm đường ngắn nhất để vận chuyển giữa hai kho.')
        self.hint.set('Bấm lần lượt hai kho để chọn nơi gửi và nơi nhận. Bấm một tuyến để bật/tắt trạng thái bảo trì.'); self.map.reset_view()

    def click_map(self,event):
        node=self.map.node_at(event.x,event.y)
        if node:
            if self.pick_phase=='source':
                self.source.set(node); self.pick_phase='target'
                text=f'Xuất phát: {node}. Bấm một kho nữa để chọn nơi nhận.'
            else:
                self.target.set(node); self.pick_phase='source'
                text=f'{self.source.get()} → {node}. Bấm Tìm đường ngắn nhất để xem kết quả.'
            self.recalculate(); self.hint.set(text); return
        key=self.map.edge_at(event.x,event.y)
        if key is not None:
            if key in self.blocked: self.blocked.remove(key); action='Đường đã mở lại'
            else: self.blocked.add(key); action='Đường đang bảo trì'
            self.recalculate(); self.hint.set(action+': '+' ↔ '.join(sorted(key)))

    def hover_map(self,event):
        node=self.map.node_at(event.x,event.y)
        self.hovered_node=node
        key=None if node else self.map.edge_at(event.x,event.y)
        self.canvas.configure(cursor='hand2' if node or key is not None else '')
        if key!=self.hovered: self.hovered=key; self.map.draw()
        if node: self.hint.set(f'{node} · Bấm để chọn '+('kho xuất phát.' if self.pick_phase=='source' else 'kho nhận hàng.'))
        elif key is not None:
            u,v,w=next(e for e in self.network['edges'] if edge_key(e)==key)
            street=self.network['routes'][key]['street']
            self.hint.set(f'{street} · {number(w)} km · '+('Đường đang bảo trì; bấm để mở lại.' if key in self.blocked else 'Bấm để đặt đường vào trạng thái bảo trì.'))
        elif self.truck.delivery_status: self.hint.set(self.truck.delivery_status)

    def leave_map(self,event):
        self.hovered=None; self.hovered_node=None
        if self.truck.delivery_status: self.hint.set(self.truck.delivery_status)
        self.map.draw()

    def close(self):
        self.pause(); self.truck.stop(); self.root.destroy()
