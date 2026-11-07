from pathlib import Path
import re,json,hashlib,zipfile
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
from report_content import P,INTRO,REFERENCES

BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]
OUT=ROOT/'Bao cao NCKH theo dan y.docx'
MAN=json.loads((BASE/'figures/manifest.json').read_text(encoding='utf-8'))
doc=Document(); sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(2.5);sec.bottom_margin=Cm(2.5)
sec.left_margin=Cm(3.5);sec.right_margin=Cm(2.5)
sec.footer_distance=Cm(1.2);sec.header_distance=Cm(1.2)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','TOC Heading']:
    sty=doc.styles[name];sty.font.name='Times New Roman';sty.font.size=Pt(13);sty.font.color.rgb=RGBColor(0,0,0)
    fonts=sty._element.get_or_add_rPr().get_or_add_rFonts()
    for key in list(fonts.attrib):
        if 'theme' in key.lower():del fonts.attrib[key]
    for key in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+key),'Times New Roman')
    for e in sty._element.xpath('.//w:pBdr'):e.getparent().remove(e)
norm=doc.styles['Normal'].paragraph_format
norm.line_spacing=1.25;norm.space_after=Pt(6);norm.widow_control=True;norm.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,sz in [('Heading 1',15),('Heading 2',13),('Heading 3',13)]:
    sty=doc.styles[name];sty.font.size=Pt(sz);sty.font.bold=True
    pf=sty.paragraph_format;pf.space_before=Pt(11);pf.space_after=Pt(6);pf.line_spacing=1.1
    pf.keep_with_next=True;pf.alignment=WD_ALIGN_PARAGRAPH.LEFT
doc.styles['Heading 1'].paragraph_format.page_break_before=True
doc.styles['Title'].font.size=Pt(19);doc.styles['Title'].font.bold=True
doc.styles['Title'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.styles['Title'].paragraph_format.space_after=Pt(18)
doc.styles['Caption'].font.size=Pt(11);doc.styles['Caption'].font.italic=True
doc.styles['Caption'].paragraph_format.line_spacing=1.1
doc.styles['Caption'].paragraph_format.space_after=Pt(8)
doc.styles['Caption'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
for name in ['TOC 1','TOC 2','TOC 3']:
    if name not in doc.styles:
        from docx.enum.style import WD_STYLE_TYPE
        doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    sty=doc.styles[name];sty.font.name='Times New Roman';sty.font.size=Pt(11)
    sty.paragraph_format.line_spacing=1.05;sty.paragraph_format.space_after=Pt(3)
    sty.paragraph_format.keep_with_next=False
doc.core_properties.title='Xây dựng ứng dụng quản lý công việc theo kiến trúc đa thuê bao'
doc.core_properties.author='Ngô Hưng Thịnh và nhóm nghiên cứu'
doc.core_properties.subject='Cơ sở lý thuyết so sánh kiến trúc và thiết kế ứng dụng Kanban đa thuê bao'

def p(text,style=None):return doc.add_paragraph(text,style)
def center(text,size=13,bold=False,before=0,after=6):
    pp=p(text);pp.alignment=WD_ALIGN_PARAGRAPH.CENTER;pp.paragraph_format.space_before=Pt(before);pp.paragraph_format.space_after=Pt(after)
    for r in pp.runs:r.font.size=Pt(size);r.bold=bold
    return pp
def head(text,level=1):return p(text,'Heading '+str(level))
def prehead(text):
    pp=p(text,'TOC Heading');pp.paragraph_format.page_break_before=True;pp.paragraph_format.keep_with_next=True
    pp.paragraph_format.space_after=Pt(14);pp.runs[0].bold=True;pp.runs[0].font.size=Pt(15)
    return pp
def field(pp,instr,placeholder=''):
    e=OxmlElement('w:fldSimple');e.set(qn('w:instr'),instr)
    if placeholder:
        r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=placeholder;r.append(t);e.append(r)
    pp._p.append(e)
def table(caption,headers,rows,widths):
    cp=p(caption,'Caption');cp.paragraph_format.keep_with_next=True
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    for col,w in zip(t.columns,widths):col.width=Cm(w)
    for c,txt,w in zip(t.rows[0].cells,headers,widths):c.text=txt;c.width=Cm(w)
    for row in rows:
        for c,txt,w in zip(t.add_row().cells,row,widths):c.text=txt;c.width=Cm(w)
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        x=OxmlElement('w:'+side);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'5');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    t._tbl.tblPr.append(borders)
    for ri,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if ri==0:trpr.append(OxmlElement('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EDF1' if ri==0 else 'FFFFFF');tcpr.append(sh)
            margins=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');margins.append(e)
            tcpr.append(margins)
            for pp in c.paragraphs:
                pf=pp.paragraph_format;pf.line_spacing=1.1;pf.space_before=Pt(2);pf.space_after=Pt(3)
                pf.keep_with_next=(ri==0)
                pf.alignment=WD_ALIGN_PARAGRAPH.CENTER if ci==0 else WD_ALIGN_PARAGRAPH.LEFT
                for r in pp.runs:r.font.size=Pt(11);r.bold=(ri==0)
    pp=p('');pp.paragraph_format.space_after=Pt(0);pp.paragraph_format.line_spacing=1;pp.paragraph_format.space_before=Pt(0)
    pp.runs if False else None
    return t

FIG_EXPLAINS={
'hinh_1_1_tien_trinh':'Các khối nêu đơn vị chia sẻ nổi bật ở mỗi hướng phát triển. Mũi tên là quan hệ kế thừa; điểm mới của SaaS đa thuê bao trong phạm vi báo cáo là quản lý dữ liệu và cấu hình ở cấp tổ chức.',
'hinh_1_2_tco':'Hai đường cùng biểu diễn tổng chi phí trong một kỳ. Giao điểm n* là quy mô cân bằng chi phí của hai phương án theo giả thiết; không phải điểm hòa vốn doanh thu hay ngưỡng đã đo của ứng dụng.',
'hinh_1_3_st_mi_mu_mt':'ST xác định một tenant được phục vụ ở tầng xét; MI đếm các bản đang chạy; MU xác định nhiều cá nhân; MT xác định nhiều tổ chức có phạm vi riêng. Bốn khung là bốn góc nhìn, không phải các bước nâng cấp bắt buộc.',
'hinh_1_4_truong_thanh':'Hàng được tô xanh định vị kiến trúc mục tiêu. Điểm phân biệt là metadata được chọn theo tenant trong lúc ứng dụng chung đang chạy; mở rộng thành tập instance là một năng lực bổ sung cần kiểm chứng riêng.',
'hinh_1_5_ba_tang':'Mũi tên nối chủ thể sử dụng, dịch vụ và môi trường thực thi. Web/Application Server và Database Server là ví dụ instance cụ thể; một tenant không được đồng nhất với một máy chủ hay một tài khoản.',
'hinh_1_6_tich_hop':'Các đường nét đứt chỉ quan hệ áp dụng kiểm soát, không biểu diễn đường đi mạng hoặc các dịch vụ phải triển khai riêng. Cơ chế tại ứng dụng phối hợp với database và tài nguyên để duy trì phạm vi thuê bao.',
'hinh_2_1_silo':'Mỗi tenant đi vào đúng App và database của mình. Sơ đồ chỉ xác nhận tách ở hai tầng được vẽ; nó không khẳng định các máy vật lý bên dưới cũng dành riêng.',
'hinh_2_2_pool':'A, B, C cùng đi vào một App và bảng dữ liệu chung. TenantContext chọn cấu hình và phạm vi xử lý; tenant_id phân biệt hàng dữ liệu, còn chính sách truy cập thực thi quyền.',
'hinh_2_3_bridge':'Backend dùng chung chọn schema hoặc database tương ứng tenant đã xác minh. Hai cách lưu trữ là các lựa chọn thay thế trong ví dụ, không phải yêu cầu cùng tạo cả schema lẫn database riêng.',
'hinh_2_4_hybrid':'A và B dùng cùng App, database; C được bố trí nguồn riêng. Phương án này phát sinh trách nhiệm quản lý ánh xạ tenant và cập nhật đồng bộ giữa các nhóm triển khai.',
'hinh_3_1_use_case':'Các đường nối biểu diễn tác nhân tham gia nhóm chức năng, không phải luồng thực thi. Quyền trên tài nguyên cụ thể được kiểm tra thêm theo membership và phạm vi công việc.',
'hinh_3_2_kien_truc':'Các thành phần bên trong khung backend là mô-đun cùng một instance. Cả hai trình duyệt đều qua xác thực và kiểm tra membership trước nghiệp vụ; database lưu chung danh mục, metadata và dữ liệu Kanban.',
'hinh_3_3_luong_yeu_cau':'Sơ đồ biểu diễn nhánh hợp lệ; lỗi xác thực kết thúc trước nghiệp vụ. Backend gửi lệnh kết thúc transaction, nhận kết quả rồi dọn context trong finally. Việc dọn vẫn phải diễn ra khi có ngoại lệ.',
'hinh_3_4_erd':'Các nhãn 1:N, N:1 đọc theo vị trí từ trái sang phải hoặc từ trên xuống dưới. Các khóa ngoại nghiệp vụ mang tenant_id; người được giao việc phải là thành viên hợp lệ của cùng workspace. Lược đồ trình bày nhóm thực thể cốt lõi.',
'hinh_3_5_metadata':'Cấu hình A được cập nhật trên backend đang chạy, sau đó được chọn bởi context A. B giữ cấu hình riêng. Hình minh họa hành vi thiết kế; hiệu lực runtime được xác nhận bằng ca kiểm chứng tương ứng.',
'hinh_3_6_giao_dien':'Wireframe thể hiện workspace hiện hành, dự án và các cột Kanban. Tên, màu và quy tắc WIP được chọn từ metadata; quyền thực hiện thao tác vẫn do backend quyết định.',
'hinh_3_7_trien_khai':'Web Server và Database Server là các vai trò khác với backend nghiệp vụ. A và B truy cập cùng backend; không tạo container ứng dụng theo tenant. Luồng database là kết nối nội bộ trong môi trường máy chủ thử nghiệm.'
}

def figure(info):
    image=BASE/'figures/png'/(info['stem']+'.png')
    pp=p('');pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
    pp.paragraph_format.keep_with_next=True;pp.paragraph_format.space_before=Pt(5);pp.paragraph_format.space_after=Pt(4)
    shape=pp.add_run().add_picture(str(image),width=Cm(15))
    props=shape._inline.docPr;props.set('descr',info['caption']+'. '+info['meaning']);props.set('title',info['caption'])
    p(info['caption'],'Caption')
    pp=p(FIG_EXPLAINS[info['stem']]);pp.paragraph_format.space_after=Pt(8)

TABLES={
'1.3.5':('Bảng 1.1 Đối chiếu các cách tổ chức hệ thống',['Khái niệm','Đơn vị xét','Quan hệ với ứng dụng'],[
['ST','Một tenant','Tài nguyên tầng xét dành cho một tổ chức.'],['MI','Nhiều instance','Mỗi instance có thể phục vụ một hoặc nhiều tenant.'],['MU','Nhiều user','Nhiều cá nhân truy cập; có thể cùng một tổ chức.'],['MT','Nhiều tenant','Dữ liệu, quyền và cấu hình quản lý theo tổ chức.']],[2.1,3.5,9.4]),
'1.4.6':('Bảng 1.2 So sánh tổ chức mã nguồn và tài nguyên theo mức trưởng thành',['Mức','Mã và cấu hình','App và dữ liệu','Định vị'],[
['Ad Hoc / Custom','Biến thể mã theo khách hàng','App và DB riêng','Bối cảnh đối chiếu'],['Configurable','Codebase chung; config trước khi chạy','App và DB riêng theo tenant','Chuẩn hóa mã'],['Multi-Tenant-Efficient','Codebase chung; metadata runtime','App chung; bảng chung có Tenant ID','Mục tiêu đề tài'],['Scalable Multi-Tenant-Efficient','Kế thừa cấu hình và context tenant','Nhiều App phối hợp; mở rộng dữ liệu','Hướng phát triển']],[3,4.1,4.8,3.1]),
'1.6.6':('Bảng 1.3 Liên hệ đặc trưng với nội dung kiểm chứng',['Đặc trưng','Biểu hiện trong thiết kế','Bằng chứng cần có'],[
['Chia sẻ','App và database chung','Cấu hình triển khai, instance_id và lược đồ.'],['Tùy biến runtime','Metadata riêng theo tenant','Đổi cấu hình A lúc chạy; B giữ nguyên.'],['Cô lập','Context, quyền và Tenant ID','Thử đọc/ghi chéo, thiếu tenant và nhánh lỗi.'],['Vòng đời','Khởi tạo tenant bằng dữ liệu','Kiểm tra tạo đầy đủ hoặc rollback.'],['Quan sát','Chỉ số và log theo tenant','Request, tenant và instance nối được với thao tác.']],[3,5.7,6.3]),
'2.2.5':('Bảng 2.1 So sánh các mô hình triển khai',['Mô hình','Phạm vi minh họa','Thuận lợi','Đánh đổi'],[
['Silo','App, DB riêng','Quản lý môi trường độc lập','Nhiều đơn vị cấp phát và bảo trì.'],['Pool','App, bảng chung','Chia sẻ tài nguyên và cập nhật','Phụ thuộc kiểm soát logic; cạnh tranh tài nguyên.'],['Bridge','App chung; dữ liệu tách','Thêm đơn vị quản lý dữ liệu','Định tuyến và cập nhật nhiều nguồn.'],['Hybrid','Kết hợp theo nhóm tenant','Đáp ứng nhu cầu khác nhau','Tăng cấu hình, điều phối và vận hành.']],[2,4,4,5]),
'2.3.2':('Bảng 2.2 Đối chiếu các phương án lưu trữ',['Phương án','Đơn vị tách','Trách nhiệm vận hành'],[
['Database-per-Tenant','Database riêng','Quản lý kết nối, migration và sao lưu nhiều DB.'],['Schema-per-Tenant','Nhóm bảng/schema riêng','Chọn đúng schema; quản lý nhiều nhóm bảng.'],['Shared-Database / Shared-Schema','Bảng chung có tenant_id','Thực thi quyền và ràng buộc dữ liệu theo tenant.']],[4.3,3.8,6.9]),
'2.4.4':('Bảng 2.3 So sánh các kịch bản kiến trúc',['Ưu tiên','Phương án xem xét','Điều kiện và đánh đổi'],[
['Chi phí, khởi tạo nhanh','Pool','Nghiệp vụ tương đối đồng nhất; kiểm soát dữ liệu chung.'],['Vận hành độc lập','Silo hoặc Bridge','Cần đơn vị dữ liệu/môi trường riêng; tăng chi phí quản lý.'],['Nhiều phân khúc','Hybrid; Cell khi cần','Quản lý vị trí tenant và chính sách khác nhau; tăng điều phối.']],[3.6,3.7,7.7]),
'2.6.1':('Bảng 2.4 Các nhóm bằng chứng của kiến trúc được lựa chọn',['Nhóm tiêu chí','Bằng chứng kiểm chứng'],[
['Mã chung và metadata runtime','Phiên bản mã chung; đổi cấu hình A khi backend vẫn chạy; A đổi hành vi, B giữ nguyên.'],['Một instance, nhiều tenant','Yêu cầu A, B chồng lấn thời gian và cùng instance_id.'],['Database chung, cô lập logic','Cùng bảng có bản ghi A, B; thao tác chéo bị từ chối; context được dọn sau lỗi.']],[4.4,10.6]),
'3.1.2':('Bảng 3.1 Các nhóm yêu cầu chức năng',['Mã','Chức năng','Phạm vi'],[
['F1','Quản lý tenant','Khởi tạo, tạm ngưng, cấu hình mặc định.'],['F2','Quản lý membership','Mời, gán vai trò, thu hồi quyền theo workspace.'],['F3','Quản lý dự án và board','Tạo, xem, cập nhật; xóa theo quyền quản trị.'],['F4','Quản lý công việc','Giao việc, cập nhật trạng thái và thời hạn.'],['F5','Tùy biến workspace','Tên, màu và quy tắc WIP qua metadata.'],['F6','Tài nguyên, thông báo','Tệp gắn công việc, nhắc thời hạn và thông báo cơ bản.']],[1.1,4.9,9]),
'3.3.1':('Bảng 3.2 Vai trò và ràng buộc của các nhóm dữ liệu',['Nhóm bảng','Vai trò','Ràng buộc chính'],[
['tenant','Workspace và trạng thái','tenant_id duy nhất.'],['app_user, membership','Tài khoản và quan hệ thành viên','Cặp tenant_id, user_id không trùng.'],['tenant_config','Metadata và phiên bản cấu hình','Một bộ cấu hình theo tenant; giá trị hợp lệ.'],['project, board, kanban_column','Cấu trúc quản lý công việc','Khóa ngoại cha–con có cùng tenant_id.'],['card','Thẻ, người được giao, version','Cột và membership hợp lệ trong tenant.'],['attachment','Tài nguyên của công việc','Khóa tệp gắn tenant và quyền trên card.'],['notification, activity_log','Thông báo và lịch sử thao tác','Người nhận, đối tượng thuộc đúng tenant.']],[4.2,4.4,6.4]),
'3.4.2':('Bảng 3.3 Ma trận quyền chức năng trong phạm vi đề xuất',['Thao tác','Quản trị hệ thống','Quản trị tenant','Thành viên'],[
['Khởi tạo, ngừng tenant','Có','Không','Không'],['Quản lý thành viên, metadata','Không qua API nghiệp vụ','Trong tenant mình','Không'],['Tạo, xóa board','Không qua API nghiệp vụ','Trong tenant mình','Không'],['Xem board, công việc','Không mặc định','Trong tenant mình','Theo phạm vi được cấp'],['Cập nhật thẻ, tệp','Không mặc định','Theo quyền trong tenant','Theo phạm vi được cấp']],[4.1,3.7,3.7,3.5]),
'3.6.2':('Bảng 3.4 Ma trận thiết kế và ca kiểm chứng dự kiến',['Mã','Thao tác kiểm chứng','Kết quả kỳ vọng'],[
['K1','Tạo A, B trên cùng triển khai','Không tạo backend hoặc DB theo tenant.'],['K2','Gửi request A, B chồng lấn','Cùng instance xử lý; dữ liệu không lẫn.'],['K3','Đổi tên/màu và quy tắc WIP của A','Có hiệu lực lúc chạy; B giữ cấu hình.'],['K4','Đọc, sửa, xóa ID đối tượng B bằng user A','Không vượt quyền; dữ liệu B không đổi.'],['K5','Thiếu hoặc giả tenant; body mang tenant khác','Từ chối hoặc giới hạn theo context tin cậy.'],['K6','Xen kẽ A, B sau lỗi và rollback','Không còn context A khi phục vụ B.'],['K7','Tạo liên kết dữ liệu chéo tenant','Ràng buộc hoặc nghiệp vụ từ chối.'],['K8','Hai user cập nhật cùng thẻ/cột giới hạn WIP','Không ghi đè mất cập nhật hoặc vượt giới hạn do cạnh tranh.']],[1.1,7.2,6.7]),
}

# Cover metadata is retained from Report.docx, without filling unpublished results.
center('BỘ GIÁO DỤC VÀ ĐÀO TẠO',13,True)
center('TRƯỜNG ĐẠI HỌC CẦN THƠ',14,True)
center('TRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG',12,True)
center('BÁO CÁO NGHIÊN CỨU KHOA HỌC SINH VIÊN',15,True,before=65,after=30)
p('XÂY DỰNG ỨNG DỤNG\nQUẢN LÝ CÔNG VIỆC\nTHEO KIẾN TRÚC ĐA THUÊ BAO','Title')
center('Mã số đề tài THS2026-67',13,before=12,after=35)
center('Chủ nhiệm đề tài  Ngô Hưng Thịnh',13)
center('Giảng viên hướng dẫn  TS. Ngô Bá Hùng',13,after=20)
center('Sinh viên thực hiện',13,True)
for name in ['Ngô Hưng Thịnh','Nguyễn Thanh Trọng','Trang Minh Chánh','Huỳnh Hồng Ân','Cao Tường Hưng']:center(name,13,after=3)
center('Cần Thơ tháng 11 năm 2026',13,before=45)

prehead('Tóm tắt')
p('Đề tài nghiên cứu kiến trúc đa thuê bao thông qua bài toán quản lý công việc Kanban trong môi trường đại học. Báo cáo hệ thống hóa khái niệm, so sánh các cách chia sẻ và cô lập tài nguyên, sau đó đề xuất ứng dụng có khả năng cấu hình và phục vụ nhiều tổ chức trên mã nguồn, backend và cơ sở dữ liệu dùng chung. Tenant ID, ngữ cảnh đã xác minh và metadata lúc chạy được kết hợp để duy trì dữ liệu, quyền và cấu hình riêng theo workspace. Phần thiết kế cụ thể hóa các cơ chế thành mô-đun, lược đồ dữ liệu và luồng nghiệp vụ; ma trận kiểm chứng xác định bằng chứng cần thu thập khi hiện thực. Khả năng mở rộng ngang được đặt ở hướng phát triển.')
p('Từ khóa: multi-tenancy; SaaS; Kanban; Tenant ID; TenantContext; metadata runtime.')
pp=p('Mở đầu');pp.runs[0].bold=True;pp.paragraph_format.space_before=Pt(14)
p('Giảng viên và sinh viên cần một công cụ tổ chức, giao việc và theo dõi tiến độ cho nhiều nhóm học tập hoặc nghiên cứu. Triển khai một nền tảng dùng chung giúp tập trung vận hành, nhưng đặt ra yêu cầu giữ riêng thành viên, dữ liệu và cấu hình của từng nhóm. Đề tài lựa chọn workspace làm đơn vị tenant và Kanban làm nghiệp vụ minh họa cho các cơ chế kiến trúc này.')
p('Mục tiêu là đề xuất thiết kế, xây dựng và kiểm chứng ứng dụng có khả năng cấu hình và phục vụ đa thuê bao hiệu quả. Câu hỏi nghiên cứu tập trung vào cách xác định đúng tenant trên từng yêu cầu, cô lập dữ liệu trên bảng chung và áp dụng biến thể nghiệp vụ qua metadata mà không tạo mã hoặc bản chạy riêng. Phạm vi gồm ứng dụng Web và triển khai thử nghiệm trên máy chủ ảo; không phát triển sản phẩm thương mại đầy đủ hoặc hạ tầng phân tán quy mô lớn.')
p('Phương pháp kết hợp tổng hợp tài liệu, phân tích yêu cầu trong thuyết minh, thiết kế kiến trúc và xác định các tình huống kiểm chứng có thể tái lập. Báo cáo gồm ba chương: cơ sở lý thuyết; so sánh cơ chế và đánh đổi; phân tích, thiết kế ứng dụng. Các kết quả kỳ vọng trong ma trận kiểm chứng là điều kiện đánh giá; kết luận thực nghiệm cần được bổ sung từ quá trình chạy thử thực tế.')

prehead('Mục lục')
field(p(''),'TOC \\o "1-3" \\h \\z \\u','Mục lục được cập nhật trong Microsoft Word.')
prehead('Danh mục hình')
for info in MAN:
    pp=p(info['caption']);pp.paragraph_format.line_spacing=1.05;pp.paragraph_format.space_after=Pt(5)
    for r in pp.runs:r.font.size=Pt(11)

outline=[]
for raw in (ROOT/'dany.md').read_text(encoding='utf-8').splitlines():
    line=raw.strip().strip('*').strip()
    if not line:continue
    if line.startswith('CHƯƠNG'):
        ch=re.match(r'CHƯƠNG\s+(\d+)',line).group(1)
        head(line,1);p(INTRO[ch]);outline.append(line)
        continue
    match=re.match(r'^(\d+\.\d+(?:\.\d+)?)\.\s+(.+)$',line)
    if not match:raise ValueError('Unrecognized outline: '+line)
    key=match.group(1);level=3 if key.count('.')==2 else 2
    head(line,level);outline.append(line)
    if key in P:
        parts=P[key];p(parts[0])
        for info in MAN:
            if info['section']==key:figure(info)
        for text in parts[1:]:p(text)
    if key in TABLES:table(*TABLES[key])

head('TÀI LIỆU THAM KHẢO',1)
for ref in REFERENCES:
    pp=p(ref);pp.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT;pp.paragraph_format.keep_together=True
    for r in pp.runs:r.font.size=Pt(12)
p('Các tài liệu kỹ thuật trực tuyến [5]–[10] được đối chiếu ngày 07/11/2026. Mô hình và sơ đồ trong báo cáo do nhóm biên soạn lại để giải thích hoặc đề xuất thiết kế; các bảng kiểm chứng không chứa số đo thực nghiệm.')
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field(footer,'PAGE','1')
settings=doc.settings.element
uf=OxmlElement('w:updateFields');uf.set(qn('w:val'),'true');settings.append(uf)
# Do not let theme colors or built-in title borders override the source report's typography.
for element in [doc.styles.element,doc.element]:
    for b in element.xpath('.//w:pBdr'):b.getparent().remove(b)
doc.save(OUT)

facts={'output':str(OUT),'source_report_sha256':hashlib.sha256((ROOT/'Report.docx').read_bytes()).hexdigest(),'outline_headings':outline,'outline_heading_count':len(outline),'prose_words':sum(len(x.split()) for ps in P.values() for x in ps),'figures':len(doc.inline_shapes),'tables':len(doc.tables),'design_status':'Proposed architecture and verification plan; no empirical result invented'}
(BASE/'build-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'artifact.md').write_text('Design authority: Report.docx typography and institutional metadata; dany.md exact chapter and subsection order. A4, Times New Roman 13 pt, 1.25 line spacing, left margin 3.5 cm. New manuscript keeps three chapters and replaces the 9-layer discussion with the agreed three-layer model. Seventeen original editable technical diagrams accompany concise descriptions. No implementation results are asserted.\n',encoding='utf-8')
print(json.dumps({k:v for k,v in facts.items() if k!='outline_headings'},ensure_ascii=False),flush=True)
