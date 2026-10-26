# BÀN GIAO DỰ ÁN SHOP GỌN — đọc file này TRƯỚC khi sửa bất cứ thứ gì

Cập nhật: 24/10/2026 (chốt phiên tối 24/10). Chủ dự án: anh Duy Thái.

## 1. Shop Gọn là gì
App quản lý bán hàng cho shop điện thoại (shopgon.vn), chạy trên điện thoại, dữ liệu nằm trong Google Drive của chính shop.
Định vị: **một gói đủ 3 việc** — quản lý bán hàng + truyền thông online (thiết kế hình) + website mini (bảng giá online).
**Trạng thái: CHƯA BÁN cho ai.** Đang cập nhật + test toàn bộ, dự kiến mở bán tháng 11/2026.

## 2. Bản đồ repo (MrDT1988/shopgon, GitHub Pages, tên miền shopgon.vn)
| Đường dẫn | Là gì |
|---|---|
| `index.html` | Trang chủ giới thiệu (có thẻ "Kho máy có sẵn ảnh chính hãng" + lịch cập nhật) |
| `app/` | App quản lý shop. `?demo=1` = bản demo cho Sale/đại lý (tồn kho mẫu trong mảng `TON`) |
| `bg/` | Bảng giá online = website mini. Trình sửa cho shop + trang khách (`?d=` link nén, `?demo=1&xem=1` xem demo) |
| `tt/` | Thiết kế hình sản phẩm (ảnh máy + giá + KM → ảnh đăng Zalo/Facebook) |
| `so-sanh.html` | So sánh giá với KiotViet, Sapo, Nhanh.vn, MISA + bảng tính năng |
| `kho/kho-may.json` | Kho máy (đang 225 mẫu, 100% có ảnh) — robot ghi, KHÔNG sửa tay trừ khi dọn dữ liệu |
| `kho/bo-sung.json` | Danh sách máy bổ sung tay (máy web hãng không có) — sửa file này rồi push là robot tự tải ảnh |
| `kho/lay-kho.mjs` | Robot kho máy |
| `kho/anh/` | Ảnh đã tải về (webp, tên = md5 của URL ảnh) |
| `kho/demo-ton.json` | Tồn kho mẫu cho bảng giá demo |
| `.github/workflows/kho-may.yml` | Lịch chạy robot |
| `quantri/` | Trang quản trị |

## 3. Kho máy — luật đã chốt với anh Thái
- **Danh sách máy:** web hãng (OPPO, Samsung, Xiaomi, Apple — robot tự quét) + máy đang bán trên Thế Giới Di Động (TGDD) mà web hãng không có (nằm trong `bo-sung.json`).
- **Ảnh:** có ảnh hãng thì dùng ảnh hãng; hãng không có thì lấy ảnh TGDD (`"nguonAnh":"tgdd"`). Không để máy nào thiếu ảnh. Hiện 34/225 máy dùng ảnh TGDD (Motorola, TECNO, Nubia, Masstel/Mobell/Xphone, REDMI 15, POCO C95 Pro/X8s, Xiaomi 18 Pro/Pro Max, realme C01).
- **Không dùng ảnh có nhân vật bản quyền** (đã bỏ HONOR 600 Pro Molly).
- Chỉ cần phủ ~80% thị trường. Máy ngoài danh sách thì shop tự tải hình lên (nút trong trang Thiết kế hình).
- **Lịch quét: 3 lần/tháng, 03:17 sáng ngày 10, ngày 20 và ngày cuối tháng (giờ VN).** Lịch này đã ghi trên trang chủ, bảng giá, thiết kế hình, so sánh giá để shop biết.

## 4. Robot kho máy (`kho/lay-kho.mjs` + `kho-may.yml`)
- Quét 4 web hãng bằng Playwright → **cộng dồn**: máy hãng gỡ khỏi web vẫn giữ (đánh dấu `ngung`), không bao giờ xoá.
- Nạp `bo-sung.json`: máy mới thì thêm; máy web hãng thiếu ảnh thì vá ảnh.
- Tải ảnh về `kho/anh/`, từ chối ảnh nhỏ hơn 300px, lỗi ghi vào `anhLoi` trong kho-may.json.
- Chạy khi: (1) lịch cron `17 20 9,19,27,28,29,30 * *` + bước "Kiem tra lich" chỉ cho chạy đúng ngày 10/20/cuối tháng giờ VN; (2) push thay đổi `kho/bo-sung.json` → chạy nhanh chế độ `CHI_BO_SUNG` (không quét web hãng, ~2 phút); (3) bấm tay workflow_dispatch.
- Kiểm kết quả: `kho-may.json` → `anhLoi` rỗng, đếm máy có `mau[].file` tồn tại.

## 5. Bảng giá online (`bg/`) — luật đã chốt
- Trang khách **chỉ để xem giá**: KHÔNG giỏ hàng. Khách liên hệ shop qua nút Gọi / Zalo cố định ở đáy + nút **"💬 Hỏi máy này"** dưới từng máy (chép sẵn câu hỏi có tên máy + giá rồi mở zalo.me/<số shop>).
- **Không lộ số tồn:** khách chỉ thấy "✓ Còn hàng" / "Tạm hết hàng"; đầu trang "x mẫu còn hàng". Link khách chỉ mang q=1/0. Trình sửa của shop vẫn có số tồn.
- Khớp hình: `khopKho()` — ưu tiên khớp đúng cả "5G", rồi bỏ "5G", rồi khớp đầu tên; hãng ngoài OPPO/Samsung/Xiaomi/Apple vào tab "Hãng khác" (`dsKho('Khac')` gộp mọi hãng còn lại). `vaAnh()` tự vá ảnh cho bảng đã lưu / link cũ.

## 6. Kênh bán: App Sale (repo riêng tư MrDT1988/dashboard-phu-kien)
- File `bc-sale-app.js`, tab **🧰 Công cụ** của Sale, thẻ `card('saSG', …)` **"🛒 Shop Gọn — giới thiệu cho đại lý"** ngay dưới thẻ "App của bạn", 4 mục: App demo (`/app/?demo=1`) · Thiết kế hình (`/tt/`) · Bảng giá online (`/bg/?demo=1&xem=1`) · So sánh giá (`/so-sanh.html`). Commit 24/10, `bao-cao.html` nạp `bc-sale-app.js?v=20261024sg`.
- Sửa repo này theo skill `sua-trang-html-dashboard` (git trên Mac mini, dự phòng Chrome upload).

## 7. So sánh giá (`so-sanh.html`)
- Có: thanh giá 1 năm 5 bên · bảng giá Shop Gọn · "Một gói, đủ 3 việc" · bảng tính năng so gói thấp nhất KiotViet (Gói hỗ trợ) & Sapo (Start Up) · "Muốn có website 1 năm": Sapo 7.200.000đ (gói Advanced 600k/tháng), KiotViet 3.960.000đ (gói chuyên nghiệp 330k/tháng), Shop Gọn 1.000.000đ.
- Số KiotViet/Sapo lấy từ bảng giá chính thức ngày 24/10/2026. Nhanh.vn/MISA chưa kiểm bảng gốc → chỉ ở phần so giá, không ở bảng tính năng.

## 8. VIỆC TREO — làm đầu phiên sau
1. ⚠️ **GIÁ BÁN LỆCH:** trang so-sanh.html đang ghi 1 năm 1.000.000đ / 2 năm 1.500.000đ / 3 năm 2.000.000đ. Phiên khác anh Thái đã chốt giá **1.190.000đ / 1.990.000đ / 2.490.000đ, ưu đãi 990.000đ cho 100 shop đầu**. Hỏi anh xác nhận rồi sửa so-sanh.html (thanh giá, bảng giá, ô tiết kiệm, bảng "website 1 năm") + mọi chỗ khác ghi giá.
2. **Bộ test toàn bộ trước khi bán** (anh đã đồng ý hướng): em viết test tự động cho App · Bảng giá · Thiết kế hình · Robot kho · Trang chủ/So sánh; anh + 1–2 shop quen test tay phần camera IMEI, in hoá đơn, đăng nhập Google, mở Zalo trên điện thoại. Chưa bắt đầu.
3. Thẻ Shop Gọn trong App Sale chưa xem được trên màn hình thật (cần mã Sale) — nhờ anh mở tab Công cụ kiểm.
4. Dần thay 34 ảnh TGDD bằng ảnh hãng khi hãng đưa ảnh lên web (Motorola VN web đang lỗi 500 ngày 24/10).
5. Ảnh TGDD cũ vẫn nằm trong lịch sử git công khai — chỉ xoá nếu anh yêu cầu (phải viết lại lịch sử repo).

## 9. Bẫy đã gặp
- Shell của phiên cloud bị chặn mạng ra ngoài → **không tải ảnh trong phiên được**; mọi việc tải ảnh để robot GitHub Actions làm (push bo-sung.json).
- Lấy danh sách TGDD: mở thegioididong.com/dtdd bằng Chrome, bấm "Xem thêm" hết rồi đọc thẻ `a[title][href*="/dtdd/"]`; javascript_tool chỉ trả ~1.000 ký tự/lần → lọc máy chưa có trong kho ngay trên trang rồi đọc từng đoạn.
- Web Motorola/TECNO/Nubia render ảnh bằng JS → WebFetch không thấy ảnh; ảnh REDMI trên mi.com là ô màu 30×30 → robot từ chối.
- Bảng giá trên trình duyệt có thể còn bản lưu cũ (localStorage `sg_bg2`) → bấm "Lấy tồn kho" để làm mới.
- Push file workflow cần quyền workflow (đã có trong phiên có add_repo access push).

## 10. Luồng kích hoạt mới (25/10 — anh Thái chốt): XEM THỬ trước, kích hoạt sau
- Mở `app/` là vào **xem thử** ngay (dữ liệu mẫu `sampleDb()`, biến `XEM=true`, `save()`/`Store.save` không lưu). Không còn màn khóa bắt đăng nhập.
- Đăng nhập Gmail lúc nào cũng được (thanh vàng `#xbar`, ô **Kích hoạt Shop Gọn** đầu tab Thêm, hoặc bấm tính năng bị khóa).
- Chặn khi XEM: mọi submit form + nút bán/in/hủy/reset + Thêm › Bảng giá, Thiết kế hình, Gia hạn, CTV → `showKh()`.
- Đề nghị kích hoạt = tên shop + SĐT + **SĐT Sale/CTV** (gửi 1 lần, hoa hồng ghi luôn); mục Thêm › Cộng tác viên ẩn khi chưa kích hoạt.
- Chờ duyệt: app tự kiểm `license()` mỗi 45 giây → active thì tạo sổ Drive, `XEM=false`, nhãn "Đã kích hoạt". Lỗi Drive → vẫn xem thử + báo cho phép Drive.
- Hết hạn: báo gia hạn, cho "Xem thử tiếp" (sổ thật khóa). Đăng xuất → về xem thử. `?demo=1` của Sale không đổi.
- `ggErr()` báo rõ: bấm Hủy (access_denied), lỗi máy chủ, lỗi Drive, mã lỗi khác.
- Trang hướng dẫn cho Sale/shop: `setup/` (shopgon.vn/setup) — nút mở app, QR, 5 bước, 5 tính năng, lỗi thường gặp; `?ctv=SĐT` gắn số Sale vào nút + QR.
- Bộ test luồng (Playwright, máy chủ giả): 20 tình huống A–H đều đạt trước khi đẩy.

## 11. Tự duyệt bằng ủy nhiệm chi (25/10 — cách A anh chốt)
- Máy chủ Apps Script "Shop Gọn - Máy chủ bản quyền" thêm `tuDuyetUnc_` (v12): shop gửi UNC → Gemini (GEMINI_KEY) đọc → đủ 5 điều kiện (thành công · số tiền = đúng 1 gói · nội dung có SĐT shop · TK nhận khớp 4 số cuối hoặc tên chủ TK · ngày ≤3 ngày) → trạng thái **"Tạm duyệt"**, hạn +3 ngày, ghi chú `AI-TAM|tháng|tiền|ngày`, email báo anh. Sai → ghi lý do vào cột Ghi chú, anh duyệt tay.
- `doGet`: "Tạm duyệt" còn hạn = active (`tam:true`); quá 3 ngày → về chờ (tự khóa). `adminApprove` với Tạm duyệt tính hạn từ ngày kích hoạt tạm. Gia hạn không tự duyệt.
- quantri: shop tạm duyệt nằm nhóm Chờ duyệt, pill "⚡ Tạm kích hoạt", gói chọn sẵn, nút **Xác nhận đã nhận tiền / Hủy**; shop AI chưa khớp hiện lý do 🤖.
- app: gửi UNC trả `tam:true` → mở khóa ngay.
- Ưu đãi 100 shop đầu: gói 1 năm 990.000đ — máy chủ `goiNay_()` đếm shop "Kích hoạt" trong ThanhToan, còn suất thì trả giá ưu đãi + giaGoc + conLai (app hiện 🎁).
- Giá 25/10: chỉ 2 gói — 1 năm 1.190.000đ · 3 năm 2.490.000đ (bỏ 2 năm). Quyền lợi: app đủ tính năng, website mini, thiết kế hình, 12/36 bài truyền thông, Sale nhập tồn lần đầu ≤50 mã (>50 mã thương lượng gói full shop). Hiện ở màn thanh toán app (qlBlock), setup/, so-sanh.html.
- Cần tab **CauHinh** có số tài khoản nhận tiền (bank_), thiếu thì không tự duyệt.

## 11. Phiên 25/10 tối (đọc thêm bản đủ trong Project: `claude/BAN_GIAO_PHIEN_25-10_SHOP_GON_NHAN_VIEN_PHIEU_NHAP_DONG_BO_2_MAY.md`)
- Dự án Google Cloud Shop Gọn đã **bật Drive API + Sheets API** (thiếu là mọi shop không mở được sổ, lỗi 403).
- Bỏ gửi ảnh UNC trong app: shop gửi biên lai Zalo cho Sale, admin duyệt tay (quản trị có nút "＋ Gia hạn").
- Nhập hàng: 2 tab Nhập hôm nay / Đã nhập · **phiếu nhập** (bảng `Phieu`) · thu cũ đổi mới · sổ chi + chốt két (bảng `Chi`) · đổi máy / trả hàng.
- **Nhân viên cửa hàng đăng nhập SĐT**: máy chủ v14 `nvApi_` (nvSync/nvLogin/nvBan); chủ shop xác minh bằng token Google; NV chỉ Bán + tổng kết ngày; đơn NV về sổ khi app chủ mở. `localStorage shopgon_nv` có → app vào chế độ NV.
- **Đồng bộ gộp 3 chiều** (`GG.merge`, base `shopgon_base_<sheetId>`): 2 máy chủ shop không đè đơn nhau; phụ kiện cộng dồn chênh lệch.
- Sổ tay chào hàng & bảng giá (`/setup/`) KHÔNG còn link trong app chủ shop / trang chủ — chỉ ở App Sale (thẻ Shop Gọn).
- Việc tiếp: anh bán thử 1 ngày thật với Hồng Nhi → đóng băng tính năng.

## 12. Phiên 26/10 — QUAN TRỌNG khi đẩy code
- shopgon.vn chạy THẲNG từ repo này (GitHub Pages, CNAME) — push là lên web thật. Repo `shopgon-web` không tồn tại/không dùng.
- **Mỗi lần sửa app/: đổi `BUILD` trong app/index.html VÀ `app/ver.json` cùng 1 giá trị** (vd 20261026-1130) → điện thoại tự tải bản mới khi mở lại app (không đổi = máy shop giữ bản cũ tới ~10 phút).
- Thêm 26/10: KM cho khách (loai 'km'), Sửa/Xóa đơn, Xóa IMEI trong Kho, icon + manifest + nút Cài app + sw.js (không lưu đệm), Sửa phiếu nhập trực tiếp (PN.edit, Thôi = trả kho), Nhập máy chọn tên kèm MÀU từ kho-may.json (máy nhiều màu bắt chọn màu).
