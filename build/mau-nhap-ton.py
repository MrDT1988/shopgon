# Dựng file mẫu nhập tồn Shop Gọn từ kho máy (12/11/2026, anh Thái).
# Chạy: python3 build/mau-nhap-ton.py   (cần openpyxl) → app/mau-nhap-ton.xlsx
# Tab "Dien thoai": chọn Hãng → Tên máy (danh sách theo hãng) → Cấu hình + Màu (theo đúng máy đó).
# Robot kho máy chạy lại file này sau mỗi lần cập nhật kho để danh sách luôn mới.
import json, os, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as CL

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KHO = json.load(open(os.path.join(GOC, 'kho', 'kho-may.json'), encoding='utf-8'))
RA = os.path.join(GOC, 'app', 'mau-nhap-ton.xlsx')
SO_DONG = 1000

def dlN(d):  # giống app: "8GB+256GB" → "8/256GB"
    d = re.sub(r'\s', '', str(d or '')); d = re.sub(r'GB\+', '+', d, flags=re.I); return d.replace('+', '/', 1)

# gom theo hãng → tên máy → {cfg, màu}
HANG = {}
for hg, ds in (KHO.get('hang') or {}).items():
    hg = 'iPhone' if hg == 'Apple' else hg
    for m in ds or []:
        t = (m.get('ten') or '').strip()
        if not t: continue
        x = HANG.setdefault(hg, {}).setdefault(t, {'cfg': [], 'mau': []})
        for b in m.get('bienThe') or []:
            c = dlN(b.get('dl'))
            if c and c not in x['cfg']: x['cfg'].append(c)
        for z in m.get('mau') or []:
            n = (z or {}).get('ten', '').strip()
            if n and n not in x['mau']: x['mau'].append(n)
UU = ['OPPO', 'Samsung', 'iPhone', 'Xiaomi']
DS_HANG = [h for h in UU if h in HANG] + sorted([h for h in HANG if h not in UU], key=str.lower)
MAY = [(h, t, HANG[h][t]) for h in DS_HANG for t in sorted(HANG[h], key=str.lower)]
MAXC = max([len(v['cfg']) for _, _, v in MAY] + [1]); MAXM = max([len(v['mau']) for _, _, v in MAY] + [1])

wb = Workbook()
TEAL = "0F766E"; hd = PatternFill("solid", fgColor=TEAL); can = PatternFill("solid", fgColor="B45309"); vd = PatternFill("solid", fgColor="F0FDFA")
thin = Side(style="thin", color="CBD5E1"); bd = Border(top=thin, bottom=thin, left=thin, right=thin)

def dau(ws, cols, ghi1, ghi2, rows):
    ws["A1"] = ghi1; ws["A1"].font = Font(bold=True, color=TEAL, size=12)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols))
    ws["A2"] = ghi2; ws["A2"].font = Font(italic=True, color="64748B", size=10); ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(cols)); ws.row_dimensions[2].height = 30
    for i, (ten, w, bb) in enumerate(cols, 1):
        c = ws.cell(row=3, column=i, value=ten); c.font = Font(bold=True, color="FFFFFF"); c.fill = can if bb else hd
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = bd
        ws.column_dimensions[CL(i)].width = w
    ws.row_dimensions[3].height = 32
    for r in range(4, 4 + SO_DONG):
        for i, (ten, _, _) in enumerate(cols, 1):
            c = ws.cell(row=r, column=i); c.border = bd
            if 'IMEI' in ten: c.number_format = '@'
            elif any(k in ten for k in ('Giá', 'Số lượng', 'tối thiểu')): c.number_format = '#,##0'
    for r, row in enumerate(rows, 4):
        for i, v in enumerate(row, 1):
            c = ws.cell(row=r, column=i, value=v); c.fill = vd
    ws.freeze_panes = "A4"

def ds(ws, f, o, canh_bao=True, tb=''):
    v = DataValidation(type="list", formula1=f, allow_blank=True, showDropDown=False)
    if canh_bao:  # cho gõ tay máy ngoài danh sách
        v.errorStyle = 'warning'; v.error = tb or 'Không có trong danh sách. Bấm Có (Yes) để giữ tên gõ tay.'; v.errorTitle = 'Shop Gọn'
    ws.add_data_validation(v); v.add(o)

# ---- tab Điện thoại
ws = wb.active; ws.title = "Dien thoai"
vdu = MAY[0] if MAY else ('OPPO', 'OPPO A6 Pro', {'cfg': ['8/256GB'], 'mau': ['Đen']})
dau(ws, [("Hãng *", 12, 1), ("Tên máy *", 30, 1), ("Cấu hình", 13, 0), ("Màu", 16, 0), ("IMEI *", 20, 1), ("Giá nhập *", 14, 1), ("Giá bán", 14, 0), ("Nhà cung cấp", 20, 0)],
    "ĐIỆN THOẠI — mỗi máy 1 dòng (1 IMEI = 1 dòng)",
    "Chọn Hãng → bấm ô Tên máy chọn trong danh sách (gõ vài chữ để tìm) → chọn Cấu hình, Màu đúng máy đó. Máy ngoài danh sách: gõ tay đủ tên + cấu hình + màu. Xoá dòng ví dụ (nền xanh nhạt) trước khi up.",
    [[vdu[0], vdu[1], (vdu[2]['cfg'] or [''])[0], (vdu[2]['mau'] or [''])[0], "861234567890123", 8990000, 10490000, "NPP Mekong"]])
R = f"4:{3 + SO_DONG}"
ds(ws, '"' + ",".join(DS_HANG + ['Khác']) + '"', f"A{R.replace(':', ':A')}", canh_bao=False)
ds(ws, 'INDIRECT("H_"&SUBSTITUTE($A4," ","_"))', f"B{R.replace(':', ':B')}", tb='Máy không có trong kho máy Shop Gọn. Bấm Có (Yes) để giữ tên gõ tay — nhớ ghi đủ cấu hình + màu.')
ds(ws, f'OFFSET(DM!$C$1,MATCH($B4,DM!$A:$A,0)-1,0,1,MAX(1,INDEX(DM!$B:$B,MATCH($B4,DM!$A:$A,0))))', f"C{R.replace(':', ':C')}")
ds(ws, f'OFFSET(DM!${CL(3 + MAXC)}$1,MATCH($B4,DM!$A:$A,0)-1,0,1,MAX(1,INDEX(DM!${CL(3 + MAXC + MAXM)}:${CL(3 + MAXC + MAXM)},MATCH($B4,DM!$A:$A,0))))', f"D{R.replace(':', ':D')}")

# ---- tab Phụ kiện (tên gõ tự do)
ws2 = wb.create_sheet("Phu kien")
dau(ws2, [("Tên hàng *", 32, 1), ("Nhóm *", 14, 1), ("Số lượng *", 12, 1), ("Giá nhập *", 14, 1), ("Giá bán", 14, 0), ("Tồn tối thiểu", 14, 0)],
    "PHỤ KIỆN · SIM · LINH KIỆN — mỗi món 1 dòng, ghi số lượng",
    "Tên hàng gõ tự do. Món trùng tên với hàng shop đang có sẽ cộng dồn số lượng. Xoá 2 dòng ví dụ trước khi up.",
    [["Cáp sạc OPPO SuperVOOC Type-C", "Phụ kiện", 10, 45000, 90000, 5], ["Sim Viettel 4G", "Sim số", 20, 25000, 50000, 10]])
ds(ws2, '"Phụ kiện,Sim số,Linh kiện,Khác"', "B4:B" + str(3 + SO_DONG), canh_bao=False)

# ---- tab Hướng dẫn
ws3 = wb.create_sheet("Huong dan")
L = ["HƯỚNG DẪN NHẬP TỒN BẰNG EXCEL — SHOP GỌN", "",
     "1. Tab 'Dien thoai': mỗi máy 1 dòng. Chọn Hãng → Tên máy → Cấu hình → Màu từ danh sách có sẵn (đúng tên trong app, có ảnh chính hãng).",
     "   Gõ vài chữ vào ô Tên máy để tìm nhanh (Excel 365 / Excel trên điện thoại). IMEI 15 số, cột đã để dạng chữ.",
     "   Máy đời cũ / ngoài danh sách: gõ tay đủ tên + cấu hình + màu, bấm Có (Yes) khi Excel hỏi.",
     "2. Tab 'Phu kien': mỗi món 1 dòng, gõ tên + số lượng.",
     "3. Cột có dấu * là bắt buộc. Giá bán bỏ trống → app tự điền theo giá niêm yết.",
     "4. Vào app › Nhập hàng › Ảnh / Excel › 📄 Nhập từ Excel › chọn file › xem lại phiếu › Lưu phiếu vào kho.",
     "", "Shop đang dùng phần mềm khác (KiotViet, Sapo…): xuất file tồn kho rồi up thẳng — app tự nhận cột Tên hàng / Số lượng / Giá vốn / Giá bán / IMEI-Serial.",
     "", "Lưu ý: IMEI đã có trong kho tự bỏ qua. Chỉ CỘNG thêm hàng, không ghi đè tồn cũ.",
     f"Danh sách máy: {len(MAY)} mẫu · cập nhật theo kho máy Shop Gọn {str(KHO.get('capNhat') or '')[:10]} — tải lại file mẫu trong app để có máy mới."]
for i, t in enumerate(L, 1):
    c = ws3.cell(row=i, column=1, value=t); c.font = Font(bold=(i == 1), color=TEAL if i == 1 else "0F172A", size=13 if i == 1 else 11)
ws3.column_dimensions["A"].width = 120

# ---- tab DM (ẩn): A tên máy · B số cấu hình · C.. cấu hình · .. số màu · màu ;  cột theo hãng cho danh sách Tên máy
dm = wb.create_sheet("DM")
cM = 3 + MAXC + MAXM  # cột "số màu"
for r, (h, t, v) in enumerate(MAY, 1):
    dm.cell(row=r, column=1, value=t); dm.cell(row=r, column=2, value=len(v['cfg']))
    for j, c in enumerate(v['cfg']): dm.cell(row=r, column=3 + j, value=c)
    for j, c in enumerate(v['mau']): dm.cell(row=r, column=3 + MAXC + j, value=c)
    dm.cell(row=r, column=cM, value=len(v['mau']))
col = cM + 2
for h in DS_HANG:
    ts = sorted(HANG[h], key=str.lower)
    for r, t in enumerate(ts, 1): dm.cell(row=r, column=col, value=t)
    ref = f"DM!${CL(col)}$1:${CL(col)}${len(ts)}"
    wb.defined_names["H_" + re.sub(r'\W', '_', h)] = DefinedName("H_" + re.sub(r'\W', '_', h), attr_text=ref)
    col += 1
dm.sheet_state = 'hidden'
wb.active = 0
wb.save(RA)
print('OK', RA, len(MAY), 'mẫu,', len(DS_HANG), 'hãng')
