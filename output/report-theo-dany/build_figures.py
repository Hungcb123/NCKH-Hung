from pathlib import Path
import xml.etree.ElementTree as ET
import json, subprocess, sys, importlib.util, math

BASE=Path(__file__).resolve().parent
FIG=BASE/'figures'
SRC=FIG/'drawio'; PNG=FIG/'png'; SVG=FIG/'svg'
for d in (SRC,PNG,SVG): d.mkdir(parents=True,exist_ok=True)
EXE=Path(r'D:\NCKH\.diagram-tools\drawio\draw.io.exe')
PALETTE={'blue':('#EDF3F8','#57748C'),'green':('#EAF4EC','#5C8168'),'orange':('#FFF3E6','#AF7D46'),'purple':('#F1EDF7','#837294'),'grey':('#F5F5F5','#7D858B'),'red':('#FAEEEC','#AE756C')}
MAN=[]

class G:
    def __init__(self,stem,title,w=1100,h=600):
        self.stem=stem; self.w=w; self.h=h; self.n=2
        self.xml=ET.Element('mxfile',host='drawio',version='32.6.10')
        dia=ET.SubElement(self.xml,'diagram',id=stem,name=title)
        model=ET.SubElement(dia,'mxGraphModel',grid='1',gridSize='10',page='0',background='#ffffff',math='0',shadow='0')
        self.root=ET.SubElement(model,'root')
        ET.SubElement(self.root,'mxCell',id='0'); ET.SubElement(self.root,'mxCell',id='1',parent='0')
        # Fixed frame guarantees stable aspect ratios across exports.
        self.cell('',0,0,w,h,'fillColor=none;strokeColor=none;pointerEvents=0;',kind='frame')
    def cell(self,label,x,y,w,h,style='',parent='1',kind='node'):
        i=str(self.n);self.n+=1
        base='html=1;whiteSpace=wrap;fontFamily=Arial;fontColor=#16232D;fontSize=24;spacing=10;align=center;verticalAlign=middle;'
        c=ET.SubElement(self.root,'mxCell',id=i,value=label,style=base+style,vertex='1',parent=parent)
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
        return i
    def text(self,label,x,y,w,h,size=24,bold=False,align='center'):
        return self.cell(label,x,y,w,h,f'text;strokeColor=none;fillColor=none;fontSize={size};fontStyle={1 if bold else 0};align={align};spacing=0;')
    def box(self,label,x,y,w,h,color='blue',db=False,ellipse=False):
        fill,stroke=PALETTE[color]
        shape='shape=cylinder3;size=15;boundedLbl=1;' if db else ('ellipse;' if ellipse else 'rounded=1;arcSize=8;')
        return self.cell(label,x,y,w,h,shape+f'fillColor={fill};strokeColor={stroke};strokeWidth=1.8;')
    def group(self,label,x,y,w,h,color='blue',dash=False):
        fill,stroke=PALETTE[color]
        return self.cell(label,x,y,w,h,f'swimlane;startSize=42;container=1;pointerEvents=0;collapsible=0;horizontal=1;fontSize=22;fontStyle=1;fillColor={fill};swimlaneFillColor=#FFFFFF;strokeColor={stroke};strokeWidth=2;'+('dashed=1;' if dash else ''))
    def edge(self,a,b,label='',exit=(.5,1),entry=(.5,0),pts=None,dashed=False,arrow='block',color='#425C70'):
        i=str(self.n);self.n+=1
        sty=f'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;fontFamily=Arial;fontSize=21;fontColor=#16232D;labelBackgroundColor=#FFFFFF;strokeColor={color};strokeWidth=2;endArrow={arrow};endFill=1;exitX={exit[0]};exitY={exit[1]};entryX={entry[0]};entryY={entry[1]};'+('dashed=1;' if dashed else '')
        c=ET.SubElement(self.root,'mxCell',id=i,value=label,style=sty,edge='1',parent='1',source=a,target=b)
        geo=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        if pts:
            arr=ET.SubElement(geo,'Array',**{'as':'points'})
            for x,y in pts: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        return i
    def line(self,x1,y1,x2,y2,color='#425C70',dashed=False,arrow='none',width=2,label=''):
        i=str(self.n);self.n+=1
        c=ET.SubElement(self.root,'mxCell',id=i,value=label,style=f'html=1;rounded=0;endArrow={arrow};endFill=1;strokeColor={color};strokeWidth={width};'+('dashed=1;' if dashed else ''),edge='1',parent='1')
        geo=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        ET.SubElement(geo,'mxPoint',x=str(x1),y=str(y1),**{'as':'sourcePoint'})
        ET.SubElement(geo,'mxPoint',x=str(x2),y=str(y2),**{'as':'targetPoint'})
        return i
    def save(self,caption,section,meaning):
        path=SRC/(self.stem+'.drawio'); ET.indent(self.xml,space='  ');ET.ElementTree(self.xml).write(path,encoding='utf-8',xml_declaration=True)
        MAN.append({'stem':self.stem,'caption':caption,'section':section,'meaning':meaning,'width':self.w,'height':self.h})

# 1.1: history is an explanatory lineage, not a mandatory replacement sequence.
g=G('hinh_1_1_tien_trinh','Tiến trình chia sẻ tài nguyên',1100,430)
items=[('Time-sharing','Chia sẻ thời gian CPU'),('ASP','Vận hành ứng dụng từ xa'),('Web multi-user','Nhiều tài khoản người dùng'),('SaaS multi-tenant','Ngữ cảnh và cấu hình tổ chức')]
ids=[]
for i,(a,b) in enumerate(items):
    ids.append(g.box(a+'\n'+b,20+i*275,100,235,180,'blue'))
for i in range(3):g.edge(ids[i],ids[i+1],exit=(1,.5),entry=(0,.5))
g.text('Trọng tâm chia sẻ chuyển từ năng lực tính toán sang ứng dụng có quản trị theo tổ chức.',30,325,1040,70,23)
g.save('Hình 1.1 Các hướng phát triển của mô hình chia sẻ tài nguyên','1.1.2','Các mô hình có thể cùng tồn tại; mũi tên biểu diễn sự kế thừa ý tưởng.')

# 1.2: conceptual cost chart. Coordinates carry no measured numeric values.
g=G('hinh_1_2_tco','Chi phí sở hữu của nhà cung cấp',1100,720)
g.text('Chi phí sở hữu của nhà cung cấp trong cùng kỳ đánh giá',60,15,1000,50,27,True)
g.line(110,580,1040,580,arrow='block',width=2)
g.line(110,580,110,100,arrow='block',width=2)
g.text('Chi phí sở hữu (TCO)',130,85,470,50,26,True,align='left')
g.line(110,540,980,170,color='#2B658E',width=4)
g.line(110,400,980,310,color='#A25F34',width=4)
cx=110+870*(140/280);cy=540-370*(140/280)
g.line(cx,cy,cx,580,dashed=True,color='#7D858B')
g.cell('',cx-5,cy-5,10,10,'ellipse;fillColor=#16232D;strokeColor=#16232D;')
g.text('n*',cx-25,585,60,35,24)
g.text('Single-tenant',760,130,260,50,26,True)
g.text('Multi-tenant',750,245,260,50,26,True)
g.text('Quy mô nhỏ\nSingle-tenant có thể rẻ hơn',155,200,350,85,24)
g.text('Sau điểm giao\nMulti-tenant có lợi thế chi phí',650,430,350,80,24)
g.text('Số lượng tổ chức thuê dịch vụ (tenant)',130,625,900,45,26,True)
g.text('Đồ thị khái niệm, không phải số liệu thực nghiệm; n* phụ thuộc giả định chi phí.',60,680,1000,35,21)
g.save('Hình 1.2 Chi phí sở hữu của nhà cung cấp theo số tenant','1.1.4','Trục hoành là số tổ chức; trục tung là tổng chi phí trong cùng kỳ; điểm giao là cân bằng chi phí hai phương án.')

# 1.3: four orthogonal organizational concepts, with real component relationships.
g=G('hinh_1_3_st_mi_mu_mt','Phân biệt ST MI MU MT',1100,850)
for i,title in enumerate(['Single-Tenant (ST)','Multi-Instance (MI)','Multi-User (MU)','Multi-Tenant (MT)']):
    x=10+(i%2)*550;y=10+(i//2)*420
    g.group(title,x,y,530,395,'grey')
    if i==0:
        a=g.box('Tenant A\nUser A1, A2',x+30,y+75,200,100)
        b=g.box('App dành riêng A',x+290,y+75,210,100)
        c=g.box('DB A',x+290,y+240,210,100,'green',True)
        g.edge(a,b,exit=(1,.5),entry=(0,.5));g.edge(b,c)
    elif i==1:
        a=g.box('App instance 1',x+30,y+85,210,95)
        b=g.box('App instance 2',x+290,y+85,210,95)
        c=g.box('Nguồn dữ liệu\nchung hoặc riêng',x+160,y+250,210,105,'green',True)
        g.edge(a,c,exit=(.5,1),entry=(.25,0));g.edge(b,c,exit=(.5,1),entry=(.75,0))
        g.text('Số instance không xác định số tenant.',x+20,y+355,490,35,21)
    elif i==2:
        a=g.box('User 1, User 2, User 3',x+40,y+75,450,80)
        b=g.box('Ứng dụng phục vụ nhiều user',x+40,y+220,450,90)
        g.edge(a,b);g.text('Có thể chỉ phục vụ một tổ chức.',x+20,y+330,490,45,21)
    else:
        a=g.box('Tenant A\nUser A1, A2',x+25,y+65,215,90)
        b=g.box('Tenant B\nUser B1, B2',x+290,y+65,215,90)
        c=g.box('App dùng chung\nDữ liệu và cấu hình theo tenant',x+80,y+235,370,110,'green')
        g.edge(a,c,entry=(.25,0));g.edge(b,c,entry=(.75,0))
g.save('Hình 1.3 Phân biệt đơn vị tổ chức của ST MI MU và MT','1.3.5','MI mô tả số bản chạy, MU mô tả nhiều cá nhân; ST và MT mô tả phạm vi phục vụ thuê bao.')

# 1.4: maturity uses a compact table-like picture of actual deployment units.
g=G('hinh_1_4_truong_thanh','Bốn cấp độ trưởng thành SaaS',1100,1020)
stages=[('Ad Hoc / Custom','Mã A riêng; mã B riêng','App A → DB A\nApp B → DB B'),('Configurable','Một codebase; file cấu hình trước khi chạy','App A (config A) → DB A\nApp B (config B) → DB B'),('Configurable, Multi-Tenant-Efficient','Một codebase; metadata theo tenant lúc chạy','Tenant A, B → một App chung\n→ DB và bảng chung có Tenant ID'),('Scalable, Configurable, Multi-Tenant-Efficient','Kế thừa cấu hình và ngữ cảnh tenant','Cân bằng tải → nhiều App instance\nMở rộng và phân bố dữ liệu theo nhu cầu')]
for i,(name,code,runtime) in enumerate(stages):
    y=15+i*250
    g.box('CẤP ĐỘ '+str(i+1),15,y,170,205,'green' if i==2 else 'grey')
    g.box(name+'\n\n'+code,220,y,420,205,'green' if i==2 else 'blue')
    g.box(runtime,680,y,405,205,'green' if i==2 else 'grey')
    g.edge(str(g.n-3),str(g.n-2),exit=(1,.5),entry=(0,.5)) if False else None
g.save('Hình 1.4 Tổ chức mã nguồn ứng dụng và dữ liệu qua bốn cấp độ trưởng thành','1.4.6','Phương án database và cấu hình được diễn giải theo phạm vi đối chiếu của đề tài; mở rộng ngang là hướng phát triển.')

# 1.5: three roles/layers, not a nine-level isolation taxonomy.
g=G('hinh_1_5_ba_tang','Mô hình ba tầng',1100,660)
a=g.box('TẦNG NGƯỜI THUÊ\nTenant A và các user A | Tenant B và các user B',30,20,1040,150)
b=g.box('TẦNG NHÀ CUNG CẤP DỊCH VỤ\nQuản lý tenant · Dịch vụ Kanban · Metadata và phân quyền',30,250,1040,150,'purple')
c=g.box('TẦNG INSTANCE VÀ HẠ TẦNG\nApp/Web Server instance · Database Server · Lưu trữ',30,480,1040,150,'green')
g.edge(a,b,'Yêu cầu có định danh người dùng và tenant');g.edge(b,c,'Thực thi trên tài nguyên được bố trí')
g.save('Hình 1.5 Quan hệ ba tầng trong cung ứng dịch vụ đa thuê bao','1.5.3','Các tầng diễn tả vai trò cung ứng; không đồng nhất với ba lớp giao diện nghiệp vụ truy cập dữ liệu.')

# 1.6: integrated model with cross-cutting controls without implying network hops.
g=G('hinh_1_6_tich_hop','Mô hình tổng thể và kiểm soát xuyên tầng',1100,750)
g.text('MÔ HÌNH BA TẦNG',30,15,560,45,25,True)
g.text('CÁC CƠ CHẾ KIỂM SOÁT',650,15,420,45,25,True)
a=g.box('Người thuê\nTenant A, B và các user',30,90,550,120)
b=g.box('Nhà cung cấp dịch vụ\nNghiệp vụ + cấu hình + quyền',30,300,550,130,'purple')
c=g.box('Instance và hạ tầng\nApp Server + Database Server',30,520,550,120,'green')
g.edge(a,b);g.edge(b,c)
for i,(title,col) in enumerate([('Định danh và ngữ cảnh','blue'),('Dữ liệu và lưu trữ','green'),('Hiệu năng và tài nguyên','grey'),('Logic và cấu hình','orange')]):
    k=g.box(title,670,85+i*145,400,100,col)
    g.edge(k,b,exit=(0,.5),entry=(1,(i+1)/5),dashed=True,arrow='none',pts=[(625,135+i*145),(625,300+130*(i+1)/5)])
g.text('Bảo vệ phạm vi dữ liệu · Quyền thay đổi trạng thái · Kiểm soát tiêu thụ tài nguyên',25,680,1050,55,23,True)
g.save('Hình 1.6 Mô hình tổng thể và các cơ chế kiểm soát xuyên tầng','1.5.5','Đường liền là quan hệ phục vụ, nét đứt là phạm vi kiểm soát, không phải luồng request.')

# 2.1-2.4: one coherent visual vocabulary across deployment variants.
for mode,cap,sec in [('silo','Hình 2.1 Tài nguyên ứng dụng và dữ liệu dành riêng theo tenant','2.2.1'),('pool','Hình 2.2 Ứng dụng và bảng dữ liệu dùng chung có nhận biết tenant','2.2.2'),('bridge','Hình 2.3 Chia sẻ ứng dụng và phân tách nguồn dữ liệu','2.2.3'),('hybrid','Hình 2.4 Phối hợp tài nguyên dùng chung và dành riêng','2.2.4')]:
    g=G('hinh_'+cap.split()[1].replace('.','_')+'_'+mode,mode,1100,600)
    ta=g.box('Tenant A',50,20,280,80);tb=g.box('Tenant B',420,20,280,80);tc=g.box('Tenant C',790,20,260,80)
    if mode=='silo':
        for tenant,x,name in [(ta,50,'A'),(tb,420,'B'),(tc,790,'C')]:
            app=g.box('App '+name, x,220,260,100)
            db=g.box('DB '+name,x,430,260,120,'green',True)
            g.edge(tenant,app);g.edge(app,db)
        g.text('Dành riêng ở tầng ứng dụng và database; phần cứng bên dưới có thể vẫn dùng chung.',20,555,1060,40,21)
    elif mode=='pool':
        app=g.box('Một App instance chung\nTenantContext + nghiệp vụ + metadata',230,210,640,125)
        db=g.box('Một database, các bảng chung\nHàng A: tenant_id=A | Hàng B: tenant_id=B | Hàng C: tenant_id=C',170,430,760,130,'green',True)
        for i,t in enumerate([ta,tb,tc]):g.edge(t,app,entry=((i+1)/4,0))
        g.edge(app,db)
    elif mode=='bridge':
        app=g.box('App chung\nChọn đúng nguồn dữ liệu theo tenant',220,210,660,110)
        for i,t in enumerate([ta,tb,tc]):g.edge(t,app,entry=((i+1)/4,0))
        for i,name in enumerate('ABC'):
            db=g.box('Schema hoặc DB '+name,40+i*370,430,280,120,'green',True)
            g.edge(app,db,exit=((i+1)/4,1))
    else:
        app=g.box('App chung cho A và B',50,220,620,100)
        dedicated=g.box('App riêng cho C',780,220,270,100,'orange')
        db=g.box('DB chung: dữ liệu A và B',100,430,520,120,'green',True)
        dbc=g.box('DB C',790,430,250,120,'green',True)
        g.edge(ta,app,entry=(.25,0));g.edge(tb,app,entry=(.75,0));g.edge(tc,dedicated)
        g.edge(app,db);g.edge(dedicated,dbc)
    g.save(cap,sec,'Quan hệ mũi tên xác định App và dữ liệu phục vụ tenant; tên mô hình không tự bảo đảm mức cô lập vật lý.')

# 3.1: use cases: role-specific capabilities, no accidental platform access.
g=G('hinh_3_1_use_case','Ca sử dụng theo vai trò',1100,740)
actors=[g.cell('',30,y,100,105,'shape=umlActor;') for y in (70,305,540)]
for label,y in [('Quản trị hệ thống',180),('Quản trị tenant',415),('Thành viên',650)]:g.text(label,0,y,190,55,22,True)
g.group('Ứng dụng quản lý công việc đa thuê bao',240,20,840,695,'grey')
cases=[('Khởi tạo và quản lý\ntrạng thái tenant',300,80),('Quản lý thành viên\nvà cấu hình workspace',300,300),('Quản lý dự án\nvà bảng Kanban',730,300),('Xem và cập nhật\ncông việc được cấp quyền',300,540),('Chia sẻ tệp và nhận\nthông báo công việc',730,540)]
cs=[g.box(label,x,y,290,120,'blue',ellipse=True) for label,x,y in cases]
g.edge(actors[0],cs[0],exit=(1,.5),entry=(0,.5),arrow='none')
g.edge(actors[1],cs[1],exit=(1,.5),entry=(0,.5),arrow='none')
g.edge(actors[1],cs[2],exit=(1,.7),entry=(0,.5),pts=[(210,480),(680,480),(680,360)],arrow='none')
g.edge(actors[2],cs[3],exit=(1,.5),entry=(0,.5),arrow='none')
g.edge(actors[2],cs[4],exit=(1,.8),entry=(0,.5),pts=[(210,690),(680,690),(680,600)],arrow='none')
g.save('Hình 3.1 Nhóm ca sử dụng theo vai trò của ứng dụng','3.1.2','Đường nối là quan hệ tham gia chức năng; quyền chi tiết được xác định trong ma trận phân quyền.')

# 3.2: a single application process contains modules; no microservice inference.
g=G('hinh_3_2_kien_truc','Kiến trúc thành phần đề xuất',1100,800)
a=g.box('Trình duyệt A\nWorkspace A',20,20,340,95);b=g.box('Trình duyệt B\nWorkspace B',740,20,340,95)
g.group('MỘT BACKEND INSTANCE',80,200,940,350,'blue')
auth=g.box('Xác thực + membership\nTenantContext',120,280,350,115,'purple')
biz=g.box('Nghiệp vụ Kanban\nÁp dụng metadata',620,280,350,115)
data=g.box('Truy cập dữ liệu theo tenant\nTransaction + RLS',330,440,440,85,'green')
g.edge(a,auth,entry=(.3,0));g.edge(b,auth,entry=(.7,0),pts=[(910,155),(365,155)])
g.edge(auth,biz,'Context\nđã xác minh',exit=(1,.5),entry=(0,.5))
g.edge(biz,data,exit=(.5,1),entry=(.8,0))
db=g.box('PostgreSQL dùng chung\nTenant + membership + metadata + dữ liệu Kanban',170,650,760,120,'green',True)
g.edge(data,db)
g.text('A và B dùng cùng backend;\nngữ cảnh được tách theo request.',35,575,410,65,22)
g.save('Hình 3.2 Kiến trúc thành phần của ứng dụng được đề xuất','3.2.2','Các khối trong backend là mô-đun cùng một instance; sơ đồ không biểu diễn nhiều dịch vụ triển khai độc lập.')

# 3.3: deterministic request sequence, generated by the skill's layout engine.
seq={'title':'Luồng tạo thẻ theo tenant','participants':[{'id':'browser','label':'Trình duyệt'},{'id':'filter','label':'Xác thực và context'},{'id':'service','label':'Nghiệp vụ Kanban'},{'id':'db','label':'Database chung'}], 'messages':[
 {'from':'browser','to':'filter','label':'1. Token + tenant được chọn'},
 {'from':'filter','to':'db','label':'2. Xác minh membership'},
 {'from':'db','to':'filter','label':'3. Quyền trong workspace','return':True},
 {'from':'filter','to':'service','label':'4. TenantContext đã xác minh'},
 {'from':'service','to':'db','label':'5. BEGIN; đặt context transaction'},
 {'from':'service','to':'db','label':'6. Đọc metadata và dữ liệu'},
 {'from':'db','to':'service','label':'7. Dữ liệu đúng tenant','return':True},
 {'from':'service','to':'service','label':'8. Kiểm tra quyền và quy tắc'},
 {'from':'service','to':'db','label':'9. Ghi thẻ; COMMIT / ROLLBACK'},
 {'from':'db','to':'service','label':'10. Kết quả transaction','return':True},
 {'from':'service','to':'filter','label':'11. Kết quả nghiệp vụ','return':True},
 {'from':'filter','to':'filter','label':'12. Dọn context trong finally'},
 {'from':'filter','to':'browser','label':'13. Phản hồi','return':True}]}
(BASE/'sequence.json').write_text(json.dumps(seq,ensure_ascii=False),encoding='utf-8')
spec=importlib.util.spec_from_file_location('seqlayout',r'D:\NCKH\AIDraw\drawio-skill\scripts\seqlayout.py')
seqmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(seqmod)
seqmod.LIFELINE_W=180;seqmod.HEADER_H=70;seqmod.MIN_SPACING=310;seqmod.ROW=65
seqmod.LIFELINE=seqmod.LIFELINE.replace('size=40;','size=70;')
sx=ET.fromstring(seqmod.layout(seq))
for cell in sx.iter('mxCell'):
    if 'style' in cell.attrib:cell.set('style',cell.get('style')+'fontFamily=Arial;fontSize=20;fontColor=#16232D;')
ET.ElementTree(sx).write(SRC/'hinh_3_3_luong_yeu_cau.drawio',encoding='utf-8',xml_declaration=True)
MAN.append({'stem':'hinh_3_3_luong_yeu_cau','caption':'Hình 3.3 Luồng tạo thẻ có xác lập và giải phóng ngữ cảnh tenant','section':'3.2.3','meaning':'Luồng hợp lệ; lỗi xác thực bị từ chối trước nghiệp vụ; mọi nhánh đều dọn ngữ cảnh.','width':1100,'height':850})

# 3.4: core logical schema. All inter-business links carry tenant_id.
g=G('hinh_3_4_erd','Lược đồ dữ liệu cốt lõi',1100,1060)
tables=[('tenant','PK tenant_id\nname, status',30,30),('app_user','PK user_id\nemail',770,30),('membership','PK/FK tenant_id\nPK/FK user_id\nrole',400,30),('tenant_config','PK/FK tenant_id\nversion\nui_config, rules',30,340),('project','PK project_id\nFK tenant_id\nname',400,340),('board','PK board_id\nFK tenant_id, project_id\nname',770,340),('card','PK card_id\nFK tenant_id, column_id\nFK assignee_user_id\nversion, position, due_date',400,740),('kanban_column','PK column_id\nFK tenant_id, board_id\nname, wip_limit',770,740)]
ids={}
for name,fields,x,y in tables:ids[name]=g.box(name+'\n────────────\n'+fields,x,y,300,220 if name!='card' else 270,'green' if name not in ['app_user','membership'] else 'blue')
g.edge(ids['tenant'],ids['membership'],'1 : N',exit=(1,.5),entry=(0,.5),arrow='none')
g.edge(ids['app_user'],ids['membership'],'N : 1',exit=(0,.5),entry=(1,.5),arrow='none')
g.edge(ids['tenant'],ids['tenant_config'],'1 : 1',arrow='none')
g.edge(ids['tenant'],ids['project'],'1 : N',exit=(1,.8),entry=(.2,0),pts=[(360,206),(360,280),(460,280)],arrow='none')
g.edge(ids['project'],ids['board'],'1 : N',exit=(1,.5),entry=(0,.5),arrow='none')
g.edge(ids['board'],ids['kanban_column'],'1 : N',arrow='none')
g.edge(ids['kanban_column'],ids['card'],'N : 1',exit=(0,.5),entry=(1,.5),arrow='none')
g.text('Khóa ngoại nghiệp vụ ghép tenant_id với khóa đối tượng.\nBảng tệp, thông báo và nhật ký được mô tả riêng.',30,585,650,120,22)
g.save('Hình 3.4 Lược đồ logic các thực thể dữ liệu cốt lõi','3.3.1','Một workspace tương ứng một tenant; FK nghiệp vụ có cùng tenant_id; ký hiệu 1:N biểu diễn lực lượng quan hệ.')

# 3.5: configuration change is observable on same running instance.
g=G('hinh_3_5_metadata','Áp dụng metadata lúc chạy',1100,680)
a=g.box('Quản trị tenant A\nĐổi quy tắc WIP',30,20,390,100,'orange')
b=g.box('Kiểm tra quyền và giá trị\nLưu config A, tăng version',650,20,420,100)
g.edge(a,b,exit=(1,.5),entry=(0,.5))
c=g.box('Một backend đang chạy\nĐọc metadata theo TenantContext',220,250,660,120,'purple')
g.edge(b,c,exit=(.5,1),entry=(.8,0))
d=g.box('Yêu cầu A\nÁp dụng quy tắc WIP mới',30,490,460,110,'green')
e=g.box('Yêu cầu B\nGiữ quy tắc của B',610,490,460,110)
g.edge(c,d,exit=(.25,1));g.edge(c,e,exit=(.75,1))
g.text('Không thay mã nguồn, không build lại, không tạo instance riêng cho A.',35,620,1030,45,23,True)
g.save('Hình 3.5 Cập nhật và áp dụng metadata theo tenant khi ứng dụng đang chạy','3.4.3','Thay đổi cấu hình không thay thế phân quyền; backend vẫn kiểm tra quy tắc khi gọi API trực tiếp.')

# 3.6: native wireframe. It is explicitly a design, not an application screenshot.
g=G('hinh_3_6_giao_dien','Thiết kế giao diện Kanban',1100,690)
g.box('WORKSPACE A   |   Dự án nghiên cứu   |   Thành viên   |   Cấu hình',15,15,1070,75)
g.box('Không gian A\n\nDự án\nBảng Kanban\nTài nguyên\nThông báo',15,120,220,500,'grey')
g.text('BẢNG CÔNG VIỆC',270,110,780,50,27,True,align='left')
for i,(title,cards) in enumerate([('Cần làm',['Đặc tả yêu cầu','Thiết kế dữ liệu']),('Đang làm · WIP 2',['Vẽ kiến trúc']),('Hoàn thành',['Thống nhất phạm vi'])]):
    x=270+i*275
    g.group(title,x,190,250,430,'blue' if i!=1 else 'orange')
    for j,t in enumerate(cards):g.box(t,x+15,260+j*120,220,85,'grey')
g.text('Bản thiết kế giao diện: tên, màu workspace và quy tắc WIP được chọn từ metadata của tenant.',20,640,1060,40,21)
g.save('Hình 3.6 Thiết kế giao diện quản lý công việc theo workspace','3.5.3','Wireframe đề xuất; không được dùng như bằng chứng ứng dụng đã chạy hoặc đã vượt kiểm thử.')

# 3.7: deployed instance count and private data path must be unambiguous.
g=G('hinh_3_7_trien_khai','Mô hình triển khai thử nghiệm',1100,760)
a=g.box('Trình duyệt tenant A',40,20,420,85);b=g.box('Trình duyệt tenant B',640,20,420,85)
g.group('MÁY CHỦ ẢO THỬ NGHIỆM',70,210,960,535,'grey')
rp=g.box('Web Server / reverse proxy\nHTTPS và giao diện web',260,290,580,100)
app=g.box('Backend instance duy nhất\nCác mô-đun nghiệp vụ và tenant',260,470,580,100,'purple')
db=g.box('Database Server\nMột PostgreSQL database chung',290,625,520,110,'green',True)
g.edge(a,rp,'HTTPS',entry=(.25,0));g.edge(b,rp,'HTTPS',entry=(.75,0))
g.edge(rp,app,'API nội bộ');g.edge(app,db,'Kết nối DB nội bộ')
g.save('Hình 3.7 Mô hình triển khai ứng dụng phục vụ nhiều tenant trên máy chủ thử nghiệm','3.6.1','Chỉ backend được tính là instance ứng dụng nghiệp vụ; database không công khai trực tiếp ra Internet.')

(FIG/'manifest.json').write_text(json.dumps(MAN,ensure_ascii=False,indent=2),encoding='utf-8')
print('Created',len(MAN),'editable figures',flush=True)

if '--export' in sys.argv:
    # Batch rendering uses one Electron process per output format.
    for fmt,target in [('png',PNG),('svg',SVG)]:
        args=[str(EXE),'-x','-f',fmt,'-b','15','--theme','light','--timeout','40','-o',str(target),str(SRC),'--disable-gpu']
        if fmt=='png':args+=['--width','2000']
        else:args+=['-e']
        result=subprocess.run(args,capture_output=True,timeout=240)
        print(result.stdout.decode('utf-8',errors='replace'),flush=True)
        if result.returncode:raise RuntimeError(result.stderr.decode('utf-8',errors='replace'))
    print('Export complete',flush=True)
