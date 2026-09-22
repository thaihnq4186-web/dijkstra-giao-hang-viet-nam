import math


def edge_key(edge):
    return frozenset(edge[:2])


def number(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.').replace('.', ',')


class MapView:
    """Vẽ bản đồ, tìm tuyến được bấm và xử lý phóng to/di chuyển."""

    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.view_zoom, self.view_pan_x, self.view_pan_y = 1.0, 0.0, 0.0
        self._pan_anchor = None

    def project(self,x,y):
        return self.offset_x+x*self.scale,self.offset_y+y*self.scale

    def within_map(self,x,y):
        return 0<=x<max(self.canvas.winfo_width(),600) and 50<=y<max(self.canvas.winfo_height(),450)-37

    def node_at(self,x,y):
        if not self.within_map(x,y): return None
        for name,regions in self.node_regions.items():
            for a,b,c,d in regions:
                if a<=x<=c and b<=y<=d: return name
        return None

    def reset_view(self,event=None):
        if event is not None and not self.within_map(event.x,event.y): return
        if event is not None and (self.node_at(event.x,event.y) or self.edge_at(event.x,event.y)):
            return
        self.view_zoom, self.view_pan_x, self.view_pan_y = 1.0, 0.0, 0.0
        self._pan_anchor=None; self.draw()

    def zoom_map(self,event):
        if not self.within_map(event.x,event.y): return
        delta=getattr(event,'delta',0)
        if getattr(event,'num',None)==4: delta=120
        if getattr(event,'num',None)==5: delta=-120
        if not delta: return
        zoom=max(1.0,min(3.0,self.view_zoom*(1.2 if delta>0 else 1/1.2)))
        if zoom==self.view_zoom: return 'break'
        model_x=(event.x-self.offset_x)/self.scale
        model_y=(event.y-self.offset_y)/self.scale
        scale=self.base_scale*zoom
        center_x,center_y=self.map_center
        screen_x,screen_y=self.screen_center
        self.view_pan_x=event.x-screen_x+(center_x-model_x)*scale
        self.view_pan_y=event.y-screen_y+(center_y-model_y)*scale
        self.view_zoom=zoom; self.draw()
        return 'break'

    def on_map_press(self,event):
        self._pan_anchor=None
        if not self.within_map(event.x,event.y): return
        if self.node_at(event.x,event.y) or self.edge_at(event.x,event.y):
            self.app.click_map(event)
        else:
            self._pan_anchor=(event.x-self.view_pan_x,event.y-self.view_pan_y)
            self.canvas.configure(cursor='fleur')

    def pan_map(self,event):
        if self._pan_anchor is not None:
            self.view_pan_x=event.x-self._pan_anchor[0]
            self.view_pan_y=event.y-self._pan_anchor[1]
            self.draw()

    def end_pan(self,event):
        self._pan_anchor=None; self.canvas.configure(cursor='')

    def edge_at(self,x,y):
        if not self.within_map(x,y): return None
        for key,(a,b,c,d) in self.edge_labels.items():
            if a<=x<=c and b<=y<=d: return key
        nearest,limit=None,8
        for key,points in self.edge_points.items():
            for (a,b),(c,d) in zip(points,points[1:]):
                dx,dy=c-a,d-b
                t=max(0,min(1,((x-a)*dx+(y-b)*dy)/max(.001,dx*dx+dy*dy)))
                distance=math.hypot(x-a-t*dx,y-b-t*dy)
                if distance<limit: nearest,limit=key,distance
        return nearest

    def draw(self):
        c=self.canvas; c.delete('all')
        width,height=max(c.winfo_width(),600),max(c.winfo_height(),450)
        model_points=[point for route in self.app.network['routes'].values() for point in route['points']]
        model_points.extend((node['x'],node['y']) for node in self.app.network['nodes'].values())
        left,right=min(p[0] for p in model_points),max(p[0] for p in model_points)
        top,bottom=min(p[1] for p in model_points),max(p[1] for p in model_points)
        self.map_center=((left+right)/2,(top+bottom)/2)
        self.screen_center=(width/2,height/2-5)
        self.base_scale=min((width-200)/max(right-left,1),(height-165)/max(bottom-top,1))
        self.scale=self.base_scale*self.view_zoom
        self.offset_x=self.screen_center[0]-self.map_center[0]*self.scale+self.view_pan_x
        self.offset_y=self.screen_center[1]-self.map_center[1]*self.scale+self.view_pan_y
        self.node_boxes,self.node_regions,self.edge_points,self.edge_labels={},{},{},{}
        def line(points,**options):
            return c.create_line(*(value for point in points for value in self.project(*point)),**options)
        # Nền nhẹ giúp tuyến và tên đường nổi rõ; dữ liệu vẫn là sơ đồ minh họa.
        for x,y,w,h in [(1100,1150,750,480),(2850,750,850,430),(1150,2350,430,500),(2450,2700,480,300),(2800,3400,440,190)]:
            a,b=self.project(x,y); d,e=self.project(x+w,y+h)
            c.create_rectangle(a,b,d,e,fill='#e0eadd',outline='#d7e3d4')
        chosen=[]
        if self.app.mode=='prim' and self.app.result: chosen=self.app.result['steps'][self.app.index]['edges']
        elif self.app.mode=='route' and self.app.result: chosen=self.app.result['edges']
        selected={edge_key(e) for e in chosen}
        selected_color='#087e67' if self.app.mode=='prim' else '#e87016'
        for u,v,w in self.app.network['edges']:
            key=edge_key((u,v,w)); points=self.app.network['routes'][key]['points']
            self.edge_points[key]=[self.project(*p) for p in points]
            line(points,fill='#99aaa9',width=21,joinstyle='round',capstyle='round')
            line(points,fill='white',width=17,joinstyle='round',capstyle='round')
        for u,v,w in self.app.network['edges']:
            key=edge_key((u,v,w)); points=self.app.network['routes'][key]['points']
            if key in self.app.blocked:
                line(points,fill='#c53c36',width=6,dash=(9,6),joinstyle='round')
            elif key in selected:
                line(points,fill=selected_color,width=8,joinstyle='round',capstyle='round')
            elif key==self.app.hovered:
                line(points,fill='#2a759e',width=5,joinstyle='round')
            else:
                line(points,fill='#859b9d',width=2,dash=(5,6),joinstyle='round')
        obstacles=[]
        for index,(name,node) in enumerate(self.app.network['nodes'].items(),1):
            x,y=self.project(node['x'],node['y'])
            start=name==self.app.source.get(); end=name==self.app.target.get()
            color='#176991' if start else '#b56016' if end else '#344f62'
            c.create_oval(x-25,y-25,x+25,y+25,fill='white',outline=color,width=3,tags='warehouse')
            c.create_rectangle(x-15,y-11,x+15,y+13,fill=color,outline='',tags='warehouse')
            c.create_polygon(x-19,y-11,x,y-26,x+19,y-11,fill=color,outline='',tags='warehouse')
            c.create_text(x,y+1,text=str(index),fill='white',font=('Segoe UI',11,'bold'),tags='warehouse')
            badge='ĐI / ĐẾN' if start and end else 'ĐIỂM ĐI' if start else 'ĐIỂM ĐẾN' if end else ''
            if badge: c.create_text(x,y-39,text=badge,fill=color,font=('Segoe UI',9,'bold'),tags='warehouse')
            text=c.create_text(x,y+46,text=name,width=174,fill='#183448',font=('Segoe UI',11,'bold'),tags='warehouse_name')
            a,b,d,e=c.bbox(text)
            box=(a-7,b-5,d+7,e+5)
            background=c.create_rectangle(*box,fill='white',outline=color if start or end else '#c1d0d0',width=1)
            c.tag_lower(background,text)
            icon=(x-27,y-49 if badge else y-28,x+27,y+27)
            self.node_regions[name]=[icon,box]
            self.node_boxes[name]=(min(icon[0],box[0]),icon[1],max(icon[2],box[2]),box[3])
            obstacles.extend([icon,box])
        road_boxes=[]
        def overlap(a,b):
            return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
        # Mỗi tuyến có một nhãn ngang, bấm được; số km nằm cùng nhãn để tránh chồng chữ.
        for u,v,w in self.app.network['edges']:
            key=edge_key((u,v,w)); points=self.edge_points[key]
            title=self.app.network['routes'][key]['street'].replace(' / ','\n')
            blocked=key in self.app.blocked; active=key in selected
            if blocked: title+='\nBẢO TRÌ'
            elif active or key==self.app.hovered: title+='\n'+number(w)+' km'
            color='#ae302b' if blocked else selected_color if active else '#273f4b'
            item=c.create_text(0,0,text=title,width=157,fill=color,font=('Segoe UI',10,'bold' if active or blocked else 'normal'),tags='street_name')
            segments=sorted(zip(points,points[1:]),key=lambda pair:math.dist(*pair),reverse=True)[:3]
            candidates=[]
            for rank,((ax,ay),(bx,by)) in enumerate(segments):
                for fraction in (.5,.3,.7):
                    anchor_x=ax+(bx-ax)*fraction; anchor_y=ay+(by-ay)*fraction
                    for dx,dy in [(0,-24),(0,24),(-70,0),(70,0),(0,-48),(0,48),(-100,0),(100,0),(-65,-40),(65,40),(0,-75),(0,75),(-130,-40),(130,40),(-130,40),(130,-40)]:
                        tx,ty=anchor_x+dx,anchor_y+dy
                        c.coords(item,tx,ty)
                        a,b,d,e=c.bbox(item); box=(a-6,b-4,d+6,e+4)
                        score=sum(overlap(box,other) for other in obstacles)*1000+sum(overlap(box,other) for other in road_boxes)*100
                        score+=math.hypot(dx,dy)+rank*8+abs(fraction-.5)*20
                        if self.view_zoom==1 and (box[0]<8 or box[1]<52 or box[2]>width-8 or box[3]>height-48): score+=1000000
                        candidates.append((score,tx,ty,box,anchor_x,anchor_y))
            best=min(candidates,key=lambda item:item[0])
            if self.view_zoom==1 and any(overlap(best[3],other) for other in obstacles+road_boxes):
                # Cửa sổ nhỏ: tìm thêm chỗ trống cho nhãn dài và nối nhãn về đúng tuyến.
                label_w=best[3][2]-best[3][0]; label_h=best[3][3]-best[3][1]
                free=[]
                for ty in range(65,height-55,18):
                    for tx in range(20,width-20,18):
                        box=(tx-label_w/2,ty-label_h/2,tx+label_w/2,ty+label_h/2)
                        if box[0]<8 or box[1]<52 or box[2]>width-8 or box[3]>height-48: continue
                        if any(overlap(box,other) for other in obstacles+road_boxes): continue
                        anchors=[]
                        for (sx,sy),(ex,ey) in zip(points,points[1:]):
                            dx,dy=ex-sx,ey-sy
                            fraction=max(0,min(1,((tx-sx)*dx+(ty-sy)*dy)/max(.001,dx*dx+dy*dy)))
                            ax,ay=sx+dx*fraction,sy+dy*fraction
                            anchors.append((math.hypot(tx-ax,ty-ay),ax,ay))
                        distance,ax,ay=min(anchors)
                        free.append((distance,tx,ty,box,ax,ay))
                if free: best=min(free,key=lambda item:item[0])
            _,tx,ty,box,ax,ay=best
            c.coords(item,tx,ty); road_boxes.append(box); self.edge_labels[key]=box
            lx,ly=max(box[0],min(ax,box[2])),max(box[1],min(ay,box[3]))
            leader=c.create_line(ax,ay,lx,ly,fill='#9aaba9',width=1)
            background=c.create_rectangle(*box,fill='#fff3f0' if blocked else 'white',outline=color if active or blocked else '#bdccca',width=1)
            c.tag_lower(leader,item); c.tag_lower(background,item)
        # Lớp thông tin cố định luôn đọc được khi phóng to hoặc di chuyển bản đồ.
        c.create_rectangle(0,0,width,49,fill='#f8faf9',outline='')
        c.create_text(16,17,anchor='w',text='BÌNH THẠNH  ·  8 KHO HÀNG',fill='#234654',font=('Segoe UI',11,'bold'))
        c.create_text(16,36,anchor='w',text='Cuộn chuột: phóng to  ·  Kéo nền: di chuyển  ·  Nhấp đúp nền: xem toàn bộ',fill='#536e76',font=('Segoe UI',9))
        c.create_text(width-16,18,anchor='e',text=f'{round(self.view_zoom*100)}%',fill='#234654',font=('Segoe UI',11,'bold'))
        c.create_rectangle(0,height-37,width,height,fill='#f8faf9',outline='')
        scale_m=500 if self.view_zoom>=2 else 1000
        c.create_line(18,height-23,18+scale_m*self.scale,height-23,fill='#355c65',width=3,tags='scale_bar')
        c.create_text(18,height-10,anchor='w',text=f'{scale_m:g} m · tỷ lệ sơ đồ',fill='#355c65',font=('Segoe UI',9))
        c.create_text(width-16,height-17,anchor='e',text='Vị trí và quãng đường minh họa',fill='#647d83',font=('Segoe UI',9))
        self.app.truck.draw()
