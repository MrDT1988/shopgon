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
| `tt/` | Thiết kế hình sản phẩm (ảnh máy + giá + KM → ảnh đăng Zalo/Facebook). Từ 28/10: 15 mẫu = 10 mẫu mới (mảng `MAU_MOI`: Khuyến mãi nổi bật, Trẻ trung, Tối giản, Chính hãng, Cao cấp, Pastel, Hot sale, Gradient, Đỏ vàng dịp lễ, Thẻ thông số — anh Thái duyệt thiết kế 28/10) + 5 mẫu cũ. Tên máy dài tự giảm cỡ chữ (`_tc`) |
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
- Tối 26/10: thêm Thêm › **Khách hàng** (gộp theo SĐT/tên từ db.don, BH còn/hết, Gọi/Zalo) · **Nhà cung cấp** (công nợ = Σ pn.no; phiếu nhập có ô 'Còn nợ NCC'; trả tiền = pn loai 'tt' no âm, tiền mặt ghi thêm Sổ chi; trả hàng NCC = pn loai 'tra', máy tt='ncc') · **Kiểm kho** (quét IMEI so tồn, lưu localStorage shopgon_kk; đếm phụ kiện). Sheet thêm cột Don.traSl/traTu, Phieu.no/loai/note. Bộ test `_tam/test-toan-bo.py` 50/50.
- ⚠ Repo shopgon đang CÔNG KHAI → chống copy (25/10) chưa hiệu lực; cần anh tạo repo riêng tư nếu muốn.

## 13. Phiên 28/10 — MÀN ĐĂNG NHẬP (anh Thái yêu cầu)
- Mở `shopgon.vn/app` / quét QR → vào **màn đăng nhập** trước (`showLogin()`), không còn vào thẳng shop mẫu.
- 2 mục (tab): **Đăng nhập** (Google · Nhân viên đăng nhập SĐT · dưới cùng "Đăng ký tài khoản mới") và **Tài khoản test** (nút "Vào shop test" = xem thử dữ liệu mẫu cũ).
- Đã đăng nhập rồi: có token → màn chờ "Đang mở sổ…" rồi vào thẳng sổ shop; điện thoại hết token → màn đăng nhập hiện "Tiếp tục với <gmail>" (1 chạm), không hiện shop test.
- Gmail chưa đăng ký / đang chờ duyệt → hiện ngay form đăng ký / màn chờ kích hoạt (có link "Xem thử tiếp").
- Đăng xuất, "Đăng nhập Gmail khác", nút Đăng nhập trên thanh vàng shop test → đều về màn đăng nhập.
- `?demo=1` (Sale) và `?nv=1` không đổi. Test: 50/50 + kiểm riêng màn đăng nhập.
- 28/10 16h30 anh chốt: CHỦ SHOP đăng nhập bằng Gmail, NHÂN VIÊN đăng nhập bằng SĐT (không làm đăng nhập SĐT cho chủ shop). Phần Gmail làm to rõ: thẻ "Gmail của shop" + nút Đăng nhập lớn; nhân viên là nút riêng.
- 28/10 16h40: nút 🚪 Đăng xuất (Gmail) cuối tab Thêm cho chủ shop (hỏi xác nhận → ggLogout → về màn đăng nhập); shop test có nút "Thoát shop test"; nhân viên giữ nút Đăng xuất trong màn NV.
- 28/10 16h50: Bán hàng — nhân viên KHÔNG sửa giá: ô giá = giá shop (readonly, class gialock, submit ép giaBan); cạnh nút "Thêm vào đơn" có nút "＋ Khuyến mãi" (data-addkm) = thêm món rồi mở bảng KM. Chủ shop vẫn sửa giá được, cũng có nút ＋ Khuyến mãi. Máy/phụ kiện chưa có giá shop thì nhân viên nhập tay.
- 28/10 17h05: tab Nhập hàng chia 3: Nhập hàng · Đã nhập · Kho hàng (addTab "kg", renderKhoGia). Kho hàng = website bảng giá theo tồn: shop thấy tồn từng mẫu + sửa giá bán (đổi giaBan mọi máy cùng tên / hang.giaBan), nút mở /bg/?tu=app để gửi link khách; khách chỉ thấy Còn/Hết hàng.

## 14. Phiên 28/10 tối — KHO = 1 chỗ đặt GIÁ + KHUYẾN MÃI (anh Thái chốt)
- Nhập hàng chỉ còn 2 tab (Nhập hàng · Đã nhập), bỏ tab Kho hàng; form nhập **bỏ ô giá bán** (máy/phụ kiện/phiếu) — chỉ sản phẩm + số lượng/IMEI + **giá nhập** (giữ để tính lời, công nợ NCC). Máy nhập thêm cùng mẫu tự lấy giá bán đang đặt (`giaMau`).
- Tab **Kho** dưới thanh menu có 2 tab con (`khoTab`): **📦 Kho** (tồn + ô Giá bán từng mẫu máy `data-kgm` / từng phụ kiện `data-kgh`, cảnh báo mẫu chưa có giá, thẻ Website bảng giá) · **🎁 Khuyến mãi** (`renderKmTab`, form `fKm`).
- Khuyến mãi lưu `db.shop.km` [{id, sp:'m|tên máy'|'h|id', ten, loai giam|pct|tang, gt, tang, tangTen, den}]; bán hàng `kmGan()` tự gắn dòng KM (kmOf ↔ kid; bỏ món là bỏ KM). Nhân viên nhận KM qua nvSync (shop.km). Nhân viên gặp máy chưa có giá → báo nhờ chủ shop đặt giá.
- Website `bg/` layTon: giá sau KM (gb) + giá gốc gạch (ny) + "Tặng …" (k).
- Bộ test cập nhật 55/55 (thêm: không còn ô giá bán, sửa giá ở Kho, KM tự gắn, bỏ máy bỏ KM).

## 15. Phiên 29/10 — KHUYẾN MÃI = GIAO DIỆN WEB KHÁCH + GIÁ NIÊM YẾT TGDD (anh Thái chốt)
- Tab **Kho › 🎁 Khuyến mãi** (`renderKmTab`) giờ là **giao diện web khách xem**: thẻ theo mẫu (gộp mọi màu, `gk()` bỏ " - Màu"), mỗi thẻ 2 trường: **Giá niêm yết** (TGDD, nhãn vàng "TGDD"; máy TGDD không có → ô trống shop tự điền, lưu `db.shop.ny[tên mẫu]`) + **Khuyến mãi** (chip + nút **＋ KM** mở bảng dưới `renderKmSheet`: giảm tiền · giảm % · tặng phụ kiện · trả góp 0% (`tg`) · khác (`txt`)). "Tồn N" chỉ shop thấy. Giá bán vẫn sửa ở tab 📦 Kho.
- KM mới lưu `sp:'g|<tên mẫu>'` (áp mọi màu); `kmCua()` vẫn nhận `m|` cũ. `kmGan` chỉ gắn dòng tiền cho giam/pct/tang; tg/txt chỉ hiện nhãn.
- **Robot giá TGDD**: `kho/gia-tgdd.mjs` + `.github/workflows/gia-tgdd.yml` (cron `0 23 * * *` = 06:00 VN). Playwright mở /dtdd bấm "Xem thêm" tới hết (173 máy 29/10) → fetch từng trang máy + các bản dung lượng → niêm yết = giá gạch `<del>` hoặc giá đang bán. 0đ, KHÔNG dùng Gemini (đọc thẳng HTML). Lấy < 60 mẫu thì giữ bản cũ. Ghi `kho/gia-tgdd.json` {capNhat, n, gia:{khóa:{t,ny,gb,u}}}.
- **Khóa khớp tên `tgKey()`** — giữ y hệt ở 3 nơi: kho/gia-tgdd.mjs · app/index.html · bg/index.html (bỏ "Điện thoại", "Samsung" trước Galaxy, "Xiaomi" trước Redmi/POCO, "Moto", màu, 5G/4G, "GB"; cắt sau dung lượng; "8+128"→"8/128", "S26+"→"s26plus"). Dự phòng khớp chỉ theo ROM khi duy nhất (TG2).
- Bản đầu `kho/gia-tgdd.json` (275 mẫu) dựng từ Chrome Mac mini 29/10 bằng đúng logic robot (tên = khóa, chưa có link) — robot 6h sáng 30/10 ghi lại đầy đủ. Demo khớp 35/38 mẫu; kho-may đang bán 275/459 (phần còn lại TGDD không bán → shop tự điền).
- **Trang khách `bg/` thiết kế lại** (`veXem`): header gradient + ô tìm, dải "🔥 Khuyến mãi hôm nay" cuộn ngang, tab dạng pill dính trên, thẻ máy bo 20px: badge −%, giá gạch niêm yết + giá sau KM + "Tiết kiệm", chip KM, chấm Còn hàng, nút "Hỏi giá qua Zalo"; phụ kiện dạng thẻ; thanh Gọi/Zalo/Gửi bạn nổi. Link `?d=` thêm `goc` (giá trước KM) + `km` (mảng chip); link cũ vẫn mở được.
- Test `_tam/test-toan-bo.py` 57/57.
- 29/10 17h45: nút "🌐 Xem website như khách" (Kho + Khuyến mãi) mở thẳng trang khách `/bg/?tu=app&xem=1` (không qua trang soạn có Copy link); trang khách khi mở từ app có thanh đen nhỏ "‹ Về app · 📤 Gửi link khách". **Tài khoản test FULL tính năng**: màn đăng nhập › Tài khoản test › "Vào shop test" = `/app/?demo=1&test=1` (biến `TEST`, cờ `localStorage shopgon_test`) — chạy như demo (dữ liệu mẫu lưu trên máy, mọi nút dùng được), ẩn thanh QR của Sale, thanh xanh "🧪 Tài khoản test · Thoát", nút "Thoát tài khoản test" cuối tab Thêm.
- 29/10 18h15 (anh chốt): **giá trên web = GIÁ NIÊM YẾT** (TGDD → shop tự điền → cuối cùng giá bán shop), KHÔNG trừ khuyến mãi; KM chỉ liệt kê dưới giá (🔻 giảm · 🎁 tặng · 💳 trả góp). Thẻ app Kho › Khuyến mãi hiện y vậy. Bán hàng trong app vẫn dùng giá bán shop + tự gắn KM như cũ.
- Trang khách bản 2: nền sáng kiểu sàn TMĐT (header trắng + logo chữ cái, tab viền, thẻ viền mảnh, ảnh vuông, chip cấu hình/màu, hộp KM, nút Zalo viền).
- Ảnh: 22 iPhone đời cũ (11 → 16 Pro Max) trong `kho/bo-sung.json` thêm ảnh TGDD (og:image) → robot kho-may tự tải. Robot giá TGDD lưu thêm `a` = ảnh TGDD từng máy; app/web dùng khi kho máy không có ảnh.
- 29/10 20h50: tab Khuyến mãi chia theo **hãng** (chip Tất cả/OPPO/Samsung/iPhone/Xiaomi… + tiêu đề từng hãng, `kmBrand`). Ảnh: `mKey()` khớp theo mẫu (bỏ hãng/5G/dung lượng/màu, "Xiaomi Redmi Note 17 5G 6/256" = "REDMI Note 17"), `kmLoad` lấy ảnh cả khi màu trong kho-may không có tên (Xiaomi) → demo 38/38 mẫu có ảnh.
- 29/10 21h: cỡ chữ app nhỏ lại ~8% (body 16→14,5px; mọi font-size ≥13px ×0,92, nhỏ hơn ×0,95); ô nhập giữ 16px để iPhone không tự phóng to khi gõ.
- 29/10 22h (anh chốt): giá niêm yết shop chỉnh được trên từng thẻ — nút − 100K / + 100K, bấm số để gõ, '↺ Về gốc' bỏ giá shop chỉnh. Ưu tiên: giá shop chỉnh (db.shop.ny) > giá tự cập nhật > giá bán. BỎ hết chữ TGDD / Thế Giới Di Động trên app + web (chỉ ghi 'tự cập nhật') — anh tự giải thích với shop.
- 29/10 22h15 (anh chốt, thay mục 22h): **1 GIÁ DUY NHẤT ở tab Kho** = giá bán = giá hiện trên web; sửa giá 1 máy là áp cho mọi màu của mẫu đó (`datGiaMau`). Tab Khuyến mãi bỏ nút −/+, chỉ hiện giá (đọc từ Kho) + thêm KM. Giá tự cập nhật mỗi sáng chỉ để GỢI Ý: nút 'Dùng giá gợi ý' ở Kho cho mẫu chưa có giá + tự điền giá khi nhập máy mẫu mới. db.shop.ny không còn dùng.
- 29/10 22h40 (anh chốt): giá niêm yết **tự cập nhật hằng ngày theo TGDĐ** cho mọi mẫu shop chưa tự sửa (`giaTuDong()` chạy mỗi render, ghi thẳng m.giaBan); mẫu shop sửa giá ở Kho → `db.shop.giaTay[mẫu]=1` giữ giá shop, nút "↺ Theo giá niêm yết" để bỏ. Lần đầu (`giaTayInit`) mẫu nào đang có giá khác giá niêm yết = coi là shop tự đặt (không đè giá cũ của shop).
- Tab Kho: thẻ Website có 2 lưu ý ① giá niêm yết tự cập nhật theo TGDĐ ② sửa giá ở Kho → web đổi theo (web chỉ thêm KM) + nút "Xem website như khách". Tab Khuyến mãi: bỏ dòng giá, thay nút xem web bằng **📋 Copy link gửi khách** (Android/iPhone mở bảng chia sẻ) + **📝 Copy bài đăng** (danh sách máy có KM + 📍📞 + câu chốt). Link dựng bằng bg chạy ẩn (`layLinkWeb`, iframe `/bg/?tu=app&nhung=1`), lưu `localStorage sg_web_link`.
- Mọi nội dung tạo cho shop kết thúc bằng "👉 Truy cập ngay để tham khảo giá và khuyến mãi: <link web shop>" (bài đăng app + 3 caption trang Thiết kế hình `tt/` qua `chot()`).
- ⚠ Link web shop dài ~2.000 ký tự (dữ liệu nén trong link). Đề xuất link ngắn (shopgon.vn/s/<mã>) cần lưu dữ liệu trên máy chủ Apps Script — chờ anh duyệt.
- 29/10 22h35 (anh duyệt): **LINK NGẮN `shopgon.vn/s/<mã 6 ký tự>`**. Máy chủ "Shop Gọn - Máy chủ bản quyền" **Phiên bản 15** (58 hàm): doPost `act:'web'` → `webLuu_` (tab **Web**: Ma · Khoa · DuLieu · CapNhat · Shop; mã cố định mỗi shop, chỉ máy có đúng khóa `k` mới cập nhật) · doGet `?web=<mã>` → `webDoc_` (chỉ đọc). App `layLinkWeb()` lấy link dài từ bg chạy ẩn → gửi z lên máy chủ khi giá/KM đổi → link ngắn (localStorage `sg_web_ma/_k/_z`, bản demo hậu tố `_demo`). Trang `s/index.html` + `404.html` đọc mã → mở `/bg/?d=…&s=<mã>`; nút Gửi bạn / Gửi link khách dùng link ngắn.
- 29/10 22h50: link ngắn **gắn mặc định** — app tự tạo khi mở (4s sau) và tự cập nhật ngầm 8s sau mỗi lần lưu (đổi giá/KM/kho) qua `linkHen()`; tab Khuyến mãi hiện sẵn '🔗 Link web của shop: shopgon.vn/s/<mã>'. Caption/bài đăng luôn có link ngắn mà shop không phải bấm gì.

## 16. Phiên 29/10 23h — TRUYỀN THÔNG QUA HÀNG CHỜ (anh Thái "làm đi")
- Luồng: app Thêm › **🖼 Ảnh truyền thông** (`renderTtq`, more='ttq') → "＋ Tạo bài mới" → chọn máy (từ Kho, gộp màu) → tick KM (+1 dòng ưu đãi) → Ảnh (Video "sắp có") → `hcGui` → hàng chờ. App hỏi `hcDs` (45s khi còn bài chờ, 10 phút khi không) → bài xong hiện 4 ảnh (lh3.googleusercontent.com/d/<id>) + 📤 Chia sẻ (navigator.share file) / ⬇ Tải (drive uc) + 📋 Copy caption (có câu chốt + link ngắn). Chấm đỏ ở tab Thêm + nhãn "Mới" trên thẻ menu khi có bài xong chưa xem (`sg_tt_seen`). Test/demo tính theo máy (`sg_tt_may`).
- Hạn mức **2 bài/tuần/shop** (T2→CN, giờ VN) — đếm ở máy chủ; bài lỗi không trừ lượt.
- Máy chủ: file **`HangCho.gs`** (bản lưu Project `claude/shopgon/HangCho_v16.gs`) + 1 dòng đầu doPost `var _hc = hcHook_(e); if (_hc) return _hc;`. Tab **HangCho**, thư mục Drive "Shop Gọn - Ảnh truyền thông", thuộc tính `HC_KEY` (chìa robot, tạo bằng hàm `hcCaiDat`), tự xoá ảnh/dòng > 60 ngày (1 lần/ngày khi robot gọi). Shop xác minh bằng token Google + hỏi chính máy chủ `?email=` phải active.
- Robot: `robot/hang-cho.mjs` (Node + Playwright, 0đ) — mỗi lượt lấy tối đa 10 bài, mở `shopgon.vn/tt/?robot=1`, `robotChon()` chọn 4 mẫu hợp nội dung (giảm → KM nổi bật; quà → Giá sốc; trả góp → Trả góp; mùa lễ → Đỏ vàng dịp lễ; còn lại xoay vòng theo mã đơn), `robotVe()` vẽ, chụp `#cho .k` JPEG → `hcTra`. Cài Mac mini: `zsh robot/cai-mac-mini.sh <HC_URL> <HC_KEY>` → launchd `vn.shopgon.hangcho` mỗi 2 phút, log `~/shopgon-robot/robot.log`, env `~/.shopgon-robot.env` (KHÔNG để trong repo).
- **Hiệu ứng mùa** `mua.js` (dùng chung app + tt + robot): 20/10, 20/11, Black Friday, **Noel 1–25/12 (đã vẽ: tuyết + mép tuyết + nhãn Merry Christmas)**, Năm mới, Tết (bảng ngày 2027–2031), 8/3, 30/4, Trung thu. Mùa chưa vẽ (`co:0`) thì ảnh không có hiệu ứng. Trang Thiết kế hình shop tự làm cũng tự gắn hiệu ứng mùa đang chạy.
- Test: máy chủ giả + robot 3 đơn cùng lúc ~6 giây · app tạo bài → robot → hiện ảnh · bộ test cũ 57/57.
- Việc tiếp: video (HyperFrames) 1–2 tuần sau · vẽ hiệu ứng mùa còn lại · sửa 12/36 → 96/288 bài khi anh duyệt gói.
- 30/10 06h50 (anh chốt): **bỏ mục "Thiết kế hình"** khỏi Thêm (trang `tt/` giữ lại làm khuôn cho robot) · robot ra **đủ 15 mẫu** mỗi bài (`robotChon` trả hết MAU5; mùa lễ đưa "Đỏ vàng dịp lễ" lên đầu), máy không có ý phụ thì dùng 3 dòng mặc định "Sẵn hàng, nhận máy ngay · Xem & trải nghiệm tại shop · Tư vấn tận tình" · **bài đăng viết sẵn** `ttqCap()` (4 kiểu mời mua + câu chốt link web), shop không phải viết; bỏ ô "Thêm 1 dòng ưu đãi" · bấm Chia sẻ tự copy bài đăng · **đếm mẫu được chọn**: Tải/Chia sẻ → `hcChon {ma, mau, kieu}` (mỗi bài + mẫu 1 lần/máy, `sg_tt_chon`) → máy chủ tab **MauChon** — để anh giữ mẫu chọn nhiều, thay mẫu ít.
- 30/10 11h10: máy chủ **Phiên bản 17** (74 hàm) — nhận 16 ảnh/bài + `hcChon_` ghi tab **MauChon** (Luc · Ma · Shop · TenShop · Mau · Kieu). Chạy thật: 15 ảnh, ~2,5 phút từ lúc gửi (chờ lượt robot ≤2 phút + đẩy 15 ảnh lên Drive).

## 17. Phiên 01/11 tối — HỌC GIAO DIỆN APP "SỔ BÁN HÀNG" (anh Thái muốn học cách trình bày/bố trí, GIỮ thế mạnh truyền thông + web)
- Phân tích Sổ Bán Hàng (video 11612.mp4): thanh dưới 5 mục · trang chủ có thanh tìm kiếm + quét · lưới "Truy cập nhanh" 6 nút · "Việc cần làm" dạng ô số · nút ＋ nổi · bán hàng dạng lưới ảnh sản phẩm · "Kho ứng dụng" chia nhóm · màn trống luôn có hình + 1 câu + nút. Sổ cũng có "Bán Online" (web) nhưng không có robot ảnh + bài đăng như Shop Gọn.
- Đã làm trong `app/index.html` (không đụng dữ liệu/Sheet): `homeSearch()` tìm máy (gộp theo tên, gõ 4+ số = tìm IMEI), khách, phụ kiện + nút quét IMEI (`data-scan="gsQ"`) · `homeStart()` thẻ "Bắt đầu với Shop Gọn" 4 bước (chỉ hiện shop thật còn trống, ẩn khi xem thử/dữ liệu mẫu) · `homeQuick()` 6 lối tắt · `homeWeb()` thẻ **Website & truyền thông** (link ngắn + Gửi link khách + Tạo ảnh/bài đăng, còn n/2 bài) · `homeTasks()` gom cảnh báo thành ô số (thay các alert cuối trang) · nút nổi `#fab` "＋ Bán hàng" (chỉ ở tab Hôm nay) · tab Bán › Phụ kiện thành lưới thẻ (`.pgrid`, bấm = +1 vào đơn, món chưa có giá thì mở form) · menu Thêm chia 5 nhóm `menuGroups()` (Truyền thông & Website đứng đầu) · `.empty` có icon + nút hành động (`.empty.sm` = không icon).
- Chưa làm (ý tưởng từ Sổ, chờ anh duyệt): chọn lối tắt tuỳ ý (nút bút) · In mã vạch · "Máy quét" (súng quét) bên cạnh camera · Danh thiếp shop · nút Khoản thu/Khoản chi cố định dưới đáy màn Sổ chi · hộp thư thông báo.
- Bẫy: `TTQ`, `linkNgan` khai báo SAU `renderHome` (let/const) → lần vẽ đầu bị TDZ; mọi chỗ trang chủ dùng chúng phải qua `sgTry(...)`.
- BUILD 20261102-0010. Test `_tam/test-toan-bo.py` 57/57.

## 18. Phiên 02/11 sáng sớm — GỌN LẠI THEO SỔ BÁN HÀNG (anh Thái: "trang Hôm nay đang nhồi quá nhiều")
- **Thanh dưới mới (5 mục):** Trang chủ · Bán · Kho hàng · Báo cáo · Thêm. Tab "Nhập hàng" bỏ khỏi thanh dưới, vào qua Kho hàng › Nhập hàng hoặc lối tắt trang chủ (view `add` vẫn còn, `go('add')` chạy như cũ; khi đang ở `add` thì tab Kho hàng sáng).
- **Trang chủ** (`renderHome`) chỉ còn: ô tìm kiếm + quét · thẻ doanh thu hôm nay (bấm → Báo cáo) · Truy cập nhanh 6 nút (Bán hàng, Nhập hàng, Đơn đã bán, Khách hàng, Thu chi, Báo cáo) · Việc cần làm (ô số) · Website & truyền thông. Shop thật còn trống: thẻ "Bắt đầu với Shop Gọn" thay cho thẻ doanh thu. Nút ＋ Bán hàng nổi.
- **Tab Báo cáo** (`renderRpt`, view `v-rpt`, `rptTab` ban|lai|kho): Bán hàng = biểu đồ/`reportPanel` + doanh thu theo người bán + đơn hôm nay · Lãi lỗ = lời hôm nay/thu hộ + lời tháng theo hãng + két · Kho hàng = tóm tắt tồn. (Nhân viên không thấy tab này.)
- **Kho hàng** = danh sách đơn giản (`renderKhoHub`, biến `khoHub`): 3 số (máy tồn/phụ kiện/vốn) + dòng Nhập hàng, Tồn kho điện thoại, Tồn kho phụ kiện, Phiếu đã nhập, Giá bán & khuyến mãi, Kiểm kho, Nhà cung cấp, Tra IMEI, Bảng giá online. Bấm tab Kho hàng ở thanh dưới → hub; mọi chỗ gọi `go('stock')` bằng code vẫn ra màn tồn kho cũ (khoHub mặc định false); màn con có nút "‹ Kho hàng". `renderStock0` = màn tồn kho cũ.
- **Thu chi** (`more==='chi'`, `renderThuChi`, `tcKy` ngay|thang, `chiSub` list|chi|ket): thẻ "Thu − chi trong kỳ" + Tổng thu/Tổng chi + lời ròng, danh sách giao dịch (thu = đơn bán, chi = sổ chi, xóa được), nút cố định dưới đáy "Khoản chi" (cam) và "Bán hàng" (xanh); form ghi chi và chốt két mở bằng `chiSub`.
- Test: `_tam/test-toan-bo.py` 62/62 (thêm 5 test giao diện mới). Sửa 2 chỗ test phụ thuộc giờ/giao diện: trả hàng tìm theo IMEI (không phụ thuộc giờ máy), ghi chi đặt `chiSub='chi'`. BUILD 20261102-0100.

## 19. (02/11) Làm lại màn Bán theo kiểu Sổ Bán Hàng
- Màn Bán: chip hãng/nhóm, lưới thẻ `.sgrid/.sc` (`sellGrid`), chọn model → chọn đơn vị (`sellGrp`), biến `sellBrand/sellOld`.
- Phụ kiện: ô `.pt` có ảnh/icon, bấm là thêm, có stepper −/+ (`cartStep`, `data-pkdec/pkadd`).
- Thanh xanh dưới "Số lượng ⓝ  tổng ›" (`cartBar`, `.cbar2`, `data-copen`) → màn "Xác nhận đơn" (`cartOpen`, `data-cclose`) chứa giỏ, KM, tên/SĐT khách, nút In hóa đơn.
- Test: các bước giỏ phải `cartOpen=true;render()` trước. BUILD 20261102-0200. Test 62/62.
- Chưa làm (gợi ý): Bán nhanh (máy tính), đọc đơn bằng giọng nói, giá lẻ/sỉ, in mã vạch, tab trạng thái đơn.

## 20. (02/11) Màn Bán giống Sổ + chọn màu theme
- Màn Bán: nền phẳng, chip chế độ `.smodes`, ô tìm xám, lưới 3 cột không viền, giá đỏ; phụ kiện 1 icon chung. CSS khối "02/11 (3)" nằm cuối `<style>` chính.
- Theme: biến `--pen/--pen-hi/--pen-dk/--pen-bg/--pen-line/--pen-rgb`; `THEMES` (8 màu) + `applyTheme(hex)`; lưu `db.shop.theme` + localStorage `sg_theme`. Menu Thêm → "Màu giao diện" (`more==='theme'`, `data-theme`). Mọi màu teal cứng trong CSS đã đổi sang biến. BUILD 20261102-0300.

## 21. (02/11) Gộp giao diện KM + gọn Trả hàng
- KM lên đơn (`renderKm`) dùng chung sheet `.wsheet/.wsbox` + `.wtypes` + `.wquick` với KM trên web; màu theo theme (không còn cam).
- Thẻ máy ở tab Web (`.wc2`) phẳng như lưới Bán.
- Chip "Trả hàng" bỏ khỏi màn Bán; vào bằng nút "Trả hàng" trong Lịch sử đơn (tự điền mã HĐ) hoặc Thêm → Khách trả hàng. Luồng trả inline cũ trong lịch sử không còn gọi (code `traId` chết).
- Ô tìm phụ kiện dạng pill; lịch sử đơn có nhãn Đã thanh toán / Còn nợ / Đã hủy. BUILD 20261102-0330.

## 22. (02/11) Hóa đơn sau bán: QR mặc định, bỏ "Tiền mặt"
- `openReceipt` mặc định `rcPay='ck'` (hiện QR VietQR khi shop có tài khoản); bỏ nút Tiền mặt/Chuyển khoản. Nút dưới: In hóa đơn · Ghi nợ (`data-rcpay="no"`, bấm lại "Bỏ ghi nợ") · Xong. Đơn lưu `tt='Đã thanh toán'` hoặc 'Ghi nợ'. Hóa đơn thêm địa chỉ/SĐT shop.
- Tài khoản test/demo (`sampleDb`): LK Mobile Store (mẫu), MB Bank STK 0123456789 (SỐ GIẢ để xem giao diện — shop thật nhập ở Thêm → Cài đặt). QR dùng CDN cdnjs nên môi trường không có mạng sẽ báo "không tải được".
BUILD 20261102-0400.

## 23. CHỐT PHIÊN 02/11/2026 — việc treo cho phiên sau
Đã xong phiên này: trang chủ gọn · Báo cáo · Kho hub · Thu chi · màn Bán kiểu Sổ (lưới 3 cột, stepper, thanh Số lượng, màn Xác nhận) · 8 màu theme (Thêm → Màu giao diện) · KM gộp 1 kiểu · Trả hàng gom 1 chỗ · hóa đơn có QR mặc định, Ghi nợ · tài khoản test = LK Mobile Store (mẫu).
Việc treo (theo thứ tự):
1. Anh Thái xem trên điện thoại thật: QR có hiện không (cdnjs), màu theme, màn Bán/Xác nhận; báo lỗi/ý chỉnh.
2. Số TK thật của LK thay số giả 0123456789 (MB Bank) trong `sampleDb`.
3. Chưa làm từ Sổ: "Bán nhanh" (máy tính bấm số) · lên đơn bằng giọng nói · giá lẻ/sỉ · tab trạng thái đơn có Xác nhận/Từ chối · in mã vạch · lối tắt tùy chỉnh. Chờ anh chọn.
4. Dọn code chết: luồng `traId` trong Lịch sử đơn; cân nhắc bỏ nút "Xóa đơn" (trùng Hủy).
5. Đồng bộ ô tìm các màn còn lại (Kho, Lịch sử) sang ô xám bo tròn; kiểm các màu theme còn sót hard-code.
6. Giá bán Shop Gọn trong so-sanh.html còn lệch (xem mục treo 24/10).
Quy tắc: sửa app thì đổi BUILD trong index.html và app/ver.json cùng giá trị (hiện 20261102-0400); chạy `python3 _tam/test-toan-bo.py` (cần `python3 -m http.server 8765` ở gốc repo) phải 62/62 trước khi đẩy.

## 24. (02/11 sáng) Website 1 khung hình · Bán 3 tab · đồng bộ giao diện Bán/Nhập
- **Trang chủ:** bỏ "Việc cần làm" (trùng Kho hàng). Thẻ Website & truyền thông có 4 nút: 👁 Xem website shop (`data-webview` → `/bg/?tu=app&xem=1`) · 📤 Gửi link khách · 📋 Copy link (`data-webcopy`, luôn copy) · 🖼 Sửa ảnh · bài đăng. Đã gỡ chỗ web trùng: dòng "Bảng giá online" ở Kho hàng, thẻ "Website bảng giá" ở Kho, mục "Bảng giá online" ở Thêm, hộp link + nút Copy link ở Kho › Khuyến mãi (giữ nút "Copy bài đăng khuyến mãi").
- **Website khách (`bg/index.html`, `veXem`):** lưới 3 cột (≥560px: 4 cột), thẻ gọn ảnh + tên + giá + niêm yết gạch ngang + nhãn −x%, 4 hàng vừa 1 màn hình 390×750. Bấm máy → bảng dưới (`.bs`, `moMay`) có giá niêm yết, tiết kiệm, danh sách khuyến mãi, nút Hỏi Zalo. Tab: Tất cả · 🎁 Khuyến mãi · 🔥 Bán chạy · hãng · Phụ kiện. Bỏ dải KM cuộn ngang và chip mức giá.
- **Màn Bán:** 3 tab Điện thoại · Phụ kiện (pk, sim) · Dịch vụ khác (sửa chữa, thu hộ, chuyển tiền, khác) — `sellMode` 'may'|'pk'|'dv', `nhomMode()`. Bỏ "Tồn N ngày" và chip "Tồn lâu" ở màn Bán, chỉ hiện "Trong kho: N".
- **Giao diện:** `.seg.top` gọn lại (cao 50px) dùng chung Bán/Nhập/Kho/Báo cáo; màn Bán không còn kiểu phẳng, lưới máy/phụ kiện nằm trong thẻ trắng bo góc; Nhập hàng dùng chip (Điện thoại · Hàng khác · Ảnh hóa đơn) trong thẻ như Bán. CSS khối "02/11 (4)" cuối `<style>`.
- BUILD 20261102-0830. Test 62/62.

## 25. (02/11 8h30) Tab Khuyến mãi thay Báo cáo · trang chủ mới
- Thanh dưới: Trang chủ · Bán · Kho hàng · **Khuyến mãi** · Thêm. View `km` = `renderKmTab` (ghi KM từng máy, Copy bài đăng). Đã bỏ tab KM trong Kho và dòng "Giá bán & khuyến mãi" ở Kho hàng (giá vẫn sửa ở Kho › tồn kho). View `rpt` (Báo cáo) còn, vào từ thẻ doanh thu/lối tắt trang chủ.
- Trang chủ từ trên xuống: Doanh thu tháng + Lợi nhuận tháng · tab Hôm nay/Hôm qua/7 ngày (`homeD`) · ô tìm IMEI · phần còn lại giữ nguyên. BUILD 20261102-0900. Test 62/62.

## 26. (02/11 9h30) Sửa lỗi giao diện trên máy thật (anh Thái báo: lợi nhuận tràn khung, chữ xuống dòng)
- Trang chủ: 1 thẻ tháng 2 cột (Doanh thu | Lợi nhuận, cỡ chữ co theo màn), thẻ ngày số lớn + 1 dòng phụ dưới. Bỏ thanh vàng "Đang xem dữ liệu mẫu" khi là demo/test (trùng thanh test). Bỏ nút nổi "＋ Bán hàng" (che nội dung, trùng tab Bán). Ô tìm rút gọn chữ gợi ý.
- Thanh dưới: chữ 11px không xuống dòng. Tab Khuyến mãi: đầu trang thành thẻ trắng gọn, thẻ máy trắng bo góc. Thêm: nhóm Truyền thông 1 cột. Giá trong lưới Bán co chữ, không tràn.
- **BẮT BUỘC trước khi báo anh:** chạy `python3 _tam/kiem-giao-dien.py` (kiểm 15 màn app + web ở 320/340/360/412px: tràn màn, tràn khung, nhãn thanh dưới 2 dòng) phải "TONG LOI: 0", rồi xem ảnh 360px bằng mắt. BUILD 20261102-0930. Test 62/62.

## 27. (02/11 13h) Nhân viên đăng nhập SĐT + MẬT KHẨU (anh Thái duyệt)
- Máy chủ "Shop Gọn - Máy chủ bản quyền" **Phiên bản 18** (76 hàm, thêm `nvHash_`, `nvRow_`): tab NhanVien thêm cột **MK** (SHA-256 của `shopgon-nv|sdt|mk`) + **Phien** (uuid, đổi mỗi lần đặt MK). `nvSync_` nhận `nv[].mk` (4–32 ký tự) → băm + phiên mới; trả `nv[].coMk`. `nvLogin_`: có `phien` → so phiên (sai → `dangXuat`); không có → so MK, sai 5 lần khóa 15 phút (Cache `nvsai_<sdt>`); chưa có MK → `canMk`. `nvBan_` bắt buộc đúng phiên.
- App: Thêm › Nhân viên cửa hàng — ô **Mật khẩu cho nhân viên** (bắt buộc), mỗi dòng có trạng thái 🔑/⚠ + nút **Đặt MK / Đổi MK**. MK chờ gửi nằm `localStorage shopgon_nvmk` (KHÔNG vào sổ Drive), gửi 1 lần qua nvSync rồi xóa. Nhân viên: màn đăng nhập có ô Mật khẩu; lưu `shopgon_nv.phien`; bị đổi MK → thoát, giữ đơn chưa gửi. Phiên cũ không có `phien` → tự thoát ra đăng nhập lại.
- Tài khoản test thấy cả "Nhân viên cửa hàng" (chủ) và "Nhân viên đăng nhập". Nhân viên cũ chưa có MK: chủ shop phải bấm Đặt MK.
- BUILD 20261102-1300. Test 64/64 (thêm 2 test MK). Kiểm giao diện 0 lỗi.

## 28. (02/11 14h) Quét IMEI trên iPhone (anh Thái: iPhone quét không ăn)
- Nguyên nhân: iPhone (Safari) không có BarcodeDetector → app dùng ZXing JS cũ (0.21.3) tải từ CDN, camera mặc định 640×480 → mã IMEI nhỏ đọc không ra.
- Đã thay: Chrome Android vẫn dùng BarcodeDetector có sẵn; máy không có (iPhone) dùng **ZXing-C++ WebAssembly** tự lưu trong repo `app/bd/ponyfill.js` (barcode-detector 3.2.2, IIFE) + `app/bd/zxing_reader.wasm` (zxing-wasm 3.1.3, 1,1 MB, chỉ tải khi bấm quét). Camera xin 1920×1080, lấy nét liên tục, zoom 2x nếu máy cho (iPhone Pro không lấy nét gần), đọc cả khung rồi dải giữa, **kiểm số Luhn** (bỏ mã đọc sai / mã không phải IMEI), hộp có IMEI1+IMEI2 → luôn lấy IMEI1 (trên cùng).
- Nhập hàng (ô IMEI) + Kiểm kho: **quét liên tục** từng hộp, rung + khung vàng mỗi máy, danh sách có ✕ bỏ, bấm "Xong" là đổ vào ô. Ô khác: quét 1 mã là đóng.
- Dự phòng **📷 Chụp ảnh** (camera gốc, ảnh nét cao) → đọc mã trong ảnh (thử cả xoay 90°). Đèn pin 🔦 khi máy hỗ trợ (Android).
- Thử bằng Playwright (Chromium không có BarcodeDetector = cùng đường iPhone): ảnh chụp mờ nghiêng → đúng IMEI1; camera giả quét liên tục → đúng IMEI1, bỏ IMEI2. CHƯA thử trên iPhone thật. BUILD 20261102-1400. Test 64/64.

## 29. (02/11 13h) Tối đa 3 nhân viên / shop (anh Thái chốt; cần thêm thì nâng gói — anh tính sau)
- App: hằng `NV_MAX=3`; Thêm › Nhân viên cửa hàng hiện "Đang có n/3", đủ 3 thì ẩn ô thêm + báo "xóa bớt hoặc liên hệ Shop Gọn để nâng gói".
- Máy chủ **Phiên bản 19**: `const NV_MAX = 3`, `nvSync_` chỉ nhận 3 nhân viên đầu (chặn gửi lách). Sau này nâng gói → đổi NV_MAX theo gói ở cả 2 nơi.
- BUILD 20261102-1430. Test 65/65.

## 30. (02/11 15h30) Nhân viên đăng nhập 1 lần là nhớ (anh Thái báo: mỗi lần vào phải đăng nhập lại)
- Lỗi gốc: chế độ nhân viên (`nvBoot`) chạy ngay trong khối script đầu → vẽ màn Bán khi `nv0`, `KM`… (khai báo ở khối script sau) chưa có → lỗi "nv0 is not defined", boot dừng giữa chừng, không tải lại tồn/phiên. Sửa: có `shopgon_nv` thì chờ `DOMContentLoaded` rồi mới `nvBoot()`; `nv0` chuyển lên đầu (cạnh `ageDays`).
- Lỗi phụ: ở màn đăng nhập (chế độ xem thử) bấm nút "Vào bán hàng" bị chặn bởi bộ chặn XEM → mở bảng Kích hoạt (chỉ bấm Enter trên bàn phím mới vào được). Đã cho `#fNvLogin` qua.
- Test mới: mở lại app 2 lần vẫn đăng nhập, vào thẳng màn Bán, không lỗi. BUILD 20261102-1530. Test 66/66.
- Lưu ý iPhone: Safari và app "Thêm vào MH chính" giữ đăng nhập RIÊNG — nhân viên đăng nhập trong cái nào thì dùng cái đó (cài app xong đăng nhập lại 1 lần trong app).

## 31. (04/11) Nhập hàng có lại ô GIÁ BÁN (anh Thái: nhập giá nhập + giá bán 1 lần cho dễ)
- Form máy: 2 ô **Giá nhập / máy** + **Giá bán / máy** (`aGB`); chọn máy đã có thì tự điền giá đang bán; máy mới thì gợi ý giá niêm yết (`aGBh`). Bỏ trống = giữ giá đang bán / lấy giá niêm yết tự cập nhật như cũ.
- Form phụ kiện: **Giá nhập / cái** + **Giá bán / cái** (`hGB`, món đã có thì điền sẵn). Dòng phiếu nhập: thêm ô Giá bán (`data-pngb`, sửa trước khi lưu).
- Lưu phiếu (`pnCommit`): dòng máy có giá bán → áp cho MỌI máy tồn cùng mẫu (mọi màu) + đánh dấu `db.shop.giaTay[mẫu]=1` (không bị giá niêm yết tự động đè). Phụ kiện → `h.giaBan`. Kho vẫn sửa giá được như cũ.
- Sửa kèm: trước đây chọn máy đã có trong ô tên bị lỗi ngầm (`$('aGB')` null) — nay hết.
- BUILD 20261104-0900. Test 67/67 (thay test "không còn ô giá bán" bằng test có ô + test nhập kèm giá bán). Kiểm giao diện 0 lỗi.

## 32. (04/11) Tài khoản test NHÂN VIÊN + TỜ RƠI theo tồn kho (anh Thái)
- Màn đăng nhập › Tài khoản test: thêm nút **"👤 Vào thử tài khoản nhân viên"** (`data-gg="testnv"`) → `shopgon_nv={…,test:1}` → `nvBoot` nhánh test: dữ liệu mẫu `sampleDb()` (không giá vốn), không gọi máy chủ (`nvLoad`/`nvFlush` bỏ qua), bán xong trừ kho trên máy; thanh "🧪 Nhân viên test · Thoát" (`thoatnv`).
- Ảnh truyền thông: 2 nút **🗞 Tạo tờ rơi** (mới) · 🖼 Ảnh 1 máy (robot cũ). Tờ rơi (`TR`, `renderTr`, `trHtml`, `trXuat`): kiểu **Tồn nhiều + KM** (máy có KM lên trước, rồi tồn nhiều) hoặc **Theo hãng** (chip hãng); **6 / 9 / 12 máy** lưới 3 cột; ảnh 1080×1350: tên shop + tiêu đề, mỗi máy ảnh + giá niêm yết gạch + giá bán + chip KM, chân: địa chỉ, SĐT, link web ngắn + mã QR. Dựng ngay trên máy bằng html-to-image (jsdelivr 1.11.11), KHÔNG qua robot, KHÔNG trừ lượt. Nút Chia sẻ (file ảnh + bài đăng) · Tải ảnh · Copy bài đăng (tự copy khi xuất).
- Chỉ dùng ảnh máy cùng nguồn shopgon.vn (ảnh TGDĐ ngoài miền bỏ để không lỗi xuất ảnh). Kho thiếu mẫu thì tờ rơi hiện ít hơn + ghi chú.
- BUILD 20261104-1000. Test 69/69 (thêm test NV test + tờ rơi). Kiểm giao diện 0 lỗi.
- Đề xuất đang chờ anh duyệt: nhân viên nhập hàng không thấy giá → gửi phiếu → chủ shop duyệt điền giá (đã gửi ảnh vẽ thử).

## 33. CHỐT PHIÊN 04/11 09h30 — việc tiếp (anh đã duyệt)
Bàn giao Project: `claude/BAN_GIAO_PHIEN_04-11_SHOP_GON_NHAN_VIEN_IMEI_TO_ROI.md` (thiết kế đủ 2 việc dưới).
1. **5 mẫu tờ rơi** (Xanh shop · Đỏ sale · Sang trọng · Tối giản · Cam tươi): code viết sẵn CHƯA test, lưu ở Project `claude/shopgon/patch_5_mau_to_roi_04-11.diff` → `git apply` → test + `_tam/kiem-giao-dien.py` → xuất 5 ảnh gửi anh chọn.
2. **Nhân viên nhập hàng chỉ số lượng (không giá) → chủ shop duyệt là tự vào kho:** máy chủ v20 (`nvNhap_`, trạng thái phiếu trong `nvLogin_`, `nhapKq` trong `nvSync_`) + app NV (tab Nhập hàng) + app chủ (Phiếu nhân viên chờ duyệt ở Kho hàng/trang chủ, Duyệt · vào kho / Trả lại).

## 34. (04/11 chiều–tối) Tờ rơi mới · Nhân viên Nhập hàng + Truyền thông · Máy chủ v20
- **Tờ rơi** làm lại theo mẫu tờ rơi điện thoại: tiêu đề lớn (SIÊU SALE / MÁY HOT / tên hãng), nhãn tròn "Đến dd/mm" theo hạn KM sớm nhất (không có hạn → "Giá SỐC", KHÔNG in ngày tạo), 1–2 máy nổi bật + lưới, nhãn −% (≥5%), dải Trả góp/Bảo hành/Thu cũ, QR. 5 mẫu `TR_MAU`: xanh · do · toi · trang (dạng danh sách) · tim; nhớ `sg_tr_mau`. Kiểu "Tồn nhiều + KM" **ưu tiên OPPO chạy ngầm** (anh Thái: không nút, không thông báo).
- **Nhân viên — thanh dưới:** Trang chủ · Bán · **Nhập hàng** (`renderNvNhap`, không có giá; phiếu nháp `shopgon_nvp`, chờ gửi `shopgon_nvpq`, đã gửi `shopgon_nvpds`) · **Truyền thông** (`renderNvTT`: link web của chủ `db.shop.web` — chủ gửi qua nvSync `ton.shop.web=linkNgan()`; Copy/Gửi/Xem/Copy bài đăng KM; xem KM đang chạy, không sửa) · Thêm.
- **Chủ shop:** "📥 Phiếu nhân viên chờ duyệt (n)" ở Trang chủ + Kho hàng → `renderPnCho` (addTab='cho'): giá nhập/bán điền sẵn lần trước, **Duyệt · vào kho** (PN tạm → `pnCommit`, NCC "(NV tên)", giữ phiếu dở của chủ) / **Trả lại** → `db.shop.nhapKq` gửi qua nvSync.
- **Máy chủ "Shop Gọn - Máy chủ bản quyền" Phiên bản 20 (04/11 21:19), 78 hàm:** `nvNhap_` (kiểm phiên, ghi NhanVienDon `kind:'nhap'` trạng thái `moi`, không trừ tồn, không giá) · `nvNhapDs_` (15 phiếu gần nhất) · `nvApi_` thêm `nvNhap` · `nvLogin_` trả `nhap` · `nvSync_` nhận `nhapKq` → cột 7 `ok`/`tra`. Trạng thái: moi → da (chủ nhận) → ok | tra. Đã gọi thử route sống.
- BUILD 20261104-2100. Test 75/75. Kiểm giao diện 0 lỗi.
- **Anh Thái cần thử máy thật:** NV gửi phiếu nhập → chủ duyệt → kho tăng; NV tab Truyền thông thấy link (chủ mở app 1 lần trước).

## 35. (05/11 đêm) SỔ THEO NĂM · SỐ DƯ · SAO LƯU/KHÔI PHỤC · TRA IMEI CÁC NĂM CŨ (anh Thái OK 5 điểm)
- **Mỗi năm 1 file Google** (`appProperties shopgon='2', nam='YYYY'`), trang: `Số dư` · `Cài đặt` · `Hàng hóa` · `IMEI` · `Năm trước` · `T01…T12` (đơn/phiếu nhập/chi theo tháng, cột `bang` = Đơn/Phiếu nhập/Chi, cột `them` = JSON trường phụ → không còn mất tgTT/cty… khi đồng bộ). Ghi chỉ trang thay đổi.
- **12 tháng liền kề:** app đọc sổ năm nay + các tháng của sổ năm trước còn trong 12 tháng (`GG.winStart()`); sổ năm cũ **đã chốt, chỉ đọc** — đơn năm cũ bị sửa sau khi chốt thì ghi bản mới vào trang `Năm trước` của sổ năm nay (đè lên bản cũ khi đọc).
- **01/01 (`GG.chuyenNam`):** gộp nốt dữ liệu máy này vào sổ năm cũ → tính số dư (máy tồn + chờ BH theo IMEI, phụ kiện, khách nợ, trả góp chờ giải ngân, nợ NCC) → tạo sổ năm mới, ghi `Số dư` + mang khoản còn mở sang `Năm trước` → đọc lại kiểm tra → dòng `KIỂM TRA | KHỚP 100%`, lưu `shop.soNam`; sao lưu sổ năm cũ 1 bản. 2 máy cùng chuyển → giữ file tạo trước, file sau tự vào thùng rác.
- **Sổ cũ 1 file (`GG.tachSoCu`):** tự tách 1 lần, kiểm không mất dòng nào rồi mới đổi tên file cũ "(sổ cũ – bản lưu dd/mm/yyyy)" + `shopgon='cu'`.
- **Sao lưu:** `GG.tuSaoLuu` sau mỗi lần đồng bộ nếu `shop.saoLuu` cũ ≥7 ngày → chép sổ năm nay vào thư mục "Shop Gọn – Sao lưu" (`shopgon='bk'`), giữ 8 bản. Thêm › Cài đặt › "Sổ dữ liệu · Sao lưu": Sao lưu ngay · Khôi phục… (tự sao lưu bản hiện tại trước, chỉ khôi phục bản cùng năm).
- **Tra IMEI:** đơn bán trong 12 tháng hiện từ đơn; không thấy → nút "🔎 Tìm trong sổ các năm trước" (`GG.timImei`).
- Test mới `_tam/test-luu-tru.py` (Drive/Sheets **giả lập**, có giả ngày 02/01/2027): 32/32. test-toan-bo 75/75. Kiểm giao diện 0 lỗi. BUILD 20261105-1200.
- **CHƯA chạy trên Google thật** — phiên sau: tài khoản test Google thật trước, rồi mới để shop thật mở app (shop thật mở bản mới là tự tách sổ).

## 36. (05/11 01h–02h) NHẬT KÝ THAY ĐỔI · IMEI BÁN 2 LẦN · TẢI EXCEL (anh Thái "làm đi"; sao lưu ngoài Gmail = chủ shop tự tải Excel)
- **Nhật ký (`NK`)**: `save()` → `NK.ghi()` so ảnh chụp trước (`NK.chup`, tự chụp lại ở mọi `Store.save`) → ghi Sửa/Hủy/Xóa đơn, Xóa IMEI, Sửa máy/hàng/phiếu/chi, Khách trả nợ, Trả hàng, Đổi máy, Khôi phục, Chốt sổ, Tải Excel: giờ · ai · máy (`sg_may`) · trước → sau. Bán/nhập bình thường không ghi. Đổi giá cả lô → gộp 1 dòng. `db.nk` → trang **"Nhật ký"** sổ năm; gộp đồng bộ chỉ CỘNG (không xóa theo máy khác); khôi phục không đụng nhật ký. Thêm › "Nhật ký thay đổi" (lọc Đơn/Kho/Khác). `var NK` (không `const` — Store.save chạy trước khi khai báo).
- **IMEI bán 2 lần**: `imeiTrung()` (đơn máy/đổi còn hiệu lực, chưa trả/đổi, ≥2 đơn cùng IMEI) → dải đỏ đầu Trang chủ, nút "Mở đơn" mở đúng đơn ở Đơn đã bán; hủy 1 đơn là hết báo. Chưa làm lớp giữ chỗ IMEI qua máy chủ khi có mạng.
- **Tải Excel**: Cài đặt › Sổ dữ liệu · Sao lưu › "⬇️ Excel" mỗi năm = Drive export .xlsx cả sổ (đồng bộ trước khi tải).
- Test `_tam/test-luu-tru.py` 45/45 (thêm nhật ký, 2 máy bán trùng, tải Excel), test-toan-bo 75/75, giao diện 0 lỗi. BUILD 20261105-0200.

## 37. (05/11 02h30) GIỮ CHỖ IMEI khi có mạng (lớp 2 chống bán trùng)
- App: thêm máy vào đơn → `giuImei([imei],'giu')` gửi `act:'nvGiu'` (chủ: `token`; NV: `sdt`+`phien`; kèm `may` = mã máy `sg_may`), chờ tối đa 4 giây; máy khác đang giữ / đã bán → hộp báo + dòng đỏ trên đơn ("NV Lan đang bán máy này từ 10:05"). Bỏ khỏi đơn → `bo`; bán xong (cả NV gửi đơn) → `ban`; hủy đơn / trả hàng → `mo`. Mất mạng hoặc máy chủ chưa có lệnh → bỏ qua êm (lớp 1 báo sau đồng bộ vẫn chạy).
- **Máy chủ v21 ĐÃ TRIỂN KHAI 05/11 01h40** (giữ URL /exec, `giuImei_` + route `nvGiu` trong `nvApi_`, 79 hàm). Gọi thử route sống: trả đúng "Phien dang nhap het han" với phiên giả.
- Test 49/49 (máy chủ giả lập), test toàn bộ 75/75, giao diện 0 lỗi. BUILD 20261105-0230.

## 38. (05/11 02h45) Gọn menu Thêm (anh Thái: trùng Kho + Truy cập nhanh)
- `MENU_TRUNG` = hist, kh, chi (đã ở Truy cập nhanh Trang chủ) · kk, ncc, look (đã ở Kho hàng) → không hiện ở Thêm. Nhóm mới "🗂 Dữ liệu & sao lưu": **Sổ dữ liệu · Sao lưu** (`more='solieu'`, chuyển khỏi Cài đặt — anh không tìm thấy khi để trong Cài đặt) + Nhật ký thay đổi. Chưa mở được sổ → nút "Mở lại sổ dữ liệu".
- Test 50/50, test toàn bộ 75/75, giao diện 0 lỗi. BUILD 20261105-0245.

## 39. (05/11 11h45) SỬA LỖI TẢI TỜ RƠI (anh Thái: "tờ rơi không download về được")
- Nguyên nhân: bấm Chia sẻ/Tải ảnh rồi mới dựng ảnh (vài giây) → điện thoại hết hiệu lực "lượt bấm" nên `navigator.share` bị chặn và bị nuốt lỗi im lặng; Tải ảnh dùng data-URL `<a download>` dễ bị app cài (PWA) / trình duyệt trong Zalo bỏ qua.
- Sửa: `trTruoc()` dựng sẵn ảnh (`TRB`, khóa `trKey()`) 0,7 giây sau khi xem trước vẽ xong (sau QR) → bấm là chia sẻ/tải liền trong lượt bấm. Tải bằng blob (`trTai`). Luôn mở khung **"✅ Tờ rơi đã xong"** (`trKq`, lớp `.trkq`) có ảnh để **nhấn giữ → Tải xuống/Lưu ảnh** + nút Chia sẻ / Tải lại (lượt bấm mới). Chia sẻ lỗi (không phải bấm Hủy) → tự tải về. Bỏ `cacheBust` cho nhanh.
- Test 75/75, lưu trữ 50/50, giao diện 0 lỗi; thử xuất thật bằng html-to-image: tải về file .jpg ~250KB, khung kết quả hiện đúng. BUILD 20261105-1150.

## 40. (05/11 12h) Tờ rơi: thông báo bị che · nút COPY ẢNH
- Video anh Thái (Xiaomi, app cài): bấm Tải ảnh không thấy gì → `.toast` z-index 9 nằm DƯỚI `.wsheet` (40) nên mọi thông báo/lỗi trong khung tờ rơi bị che. Đổi `.toast` z-index 10001; bấm là báo ngay. `toast(m,ms)` nhận thời gian hiện.
- Lỗi tạo ảnh hiện lý do trong ngoặc (8 giây) để anh chụp gửi.
- **📋 Copy ảnh** (nút chính, trên Chia sẻ/Tải ảnh; có cả trong khung "Tờ rơi đã xong"): `trCopyAnh` → `navigator.clipboard.write` với `ClipboardItem({'image/png': Promise})` (giữ lượt bấm khi ảnh chưa dựng xong; `trPng` đổi JPEG→PNG vì Android chỉ nhận PNG). Copy bài đăng đổi icon 📝.
- Test 75/75, giao diện 0 lỗi, test copy: bộ nhớ tạm có image/png. BUILD 20261105-1235.

## 41. (05/11 12h30) Tờ rơi: "Lỗi tạo ảnh (error)" trên Xiaomi → 3 cách dựng ảnh
- Máy Xiaomi anh Thái: html-to-image (vẽ qua SVG foreignObject) báo sự kiện `error`. `trTao` giờ thử lần lượt: **a** html-to-image đủ font → **b** bỏ nhúng font → **c** html2canvas 1.4.1 (cdnjs, vẽ thẳng canvas; bản sao đặt ngoài màn hình, lớp `.h2c` bỏ box-shadow/drop-shadow vì html2canvas vẽ xấu, chép lại canvas QR). Cách chạy được nhớ ở `sg_tr_cach`. Lỗi cả 3 → thông báo ghi lý do từng cách.
- Test giả lập html-to-image hỏng → tự sang cách c, ảnh đẹp, Copy ảnh ra image/png. Test 75/75, giao diện 0 lỗi. BUILD 20261105-1240.

## 42. (05/11 trưa) UI gọn toàn app + Khuyến mãi/Website dùng chung thẻ máy — anh Thái duyệt qua demo
- Làm theo skill `thiet-ke-giao-dien` (chữ ≥12px, nút ≥44px, icon nét, không emoji làm icon). Demo đã duyệt: `/app-moi/`, `/bg-moi/` (bản demo, có thể xoá).
- **app/index.html** (BUILD 20261105-1310): khối CSS "05/11/2026 UI gọn" ở cuối `<style>` lớn · `homeMonth()` thành 1 thẻ 4 tab Hôm nay/Hôm qua/7 ngày/Tháng (`homeD` thêm 'month'), `homeDay()` không còn gọi; chưa có đơn hôm nay → nút "Bán đơn đầu tiên" · `doiNgayMau(db)` ngay sau `let db=Store.load()…`: dữ liệu mẫu (db.sample) tự dời mọi trường `ngay*` để đơn mới nhất = hôm nay · tab Khuyến mãi: biến `kmF` (all/co/chua/sap), thẻ tóm tắt `.kmsum`, chip `data-kmf`, nút "＋ Thêm KM" · script cuối `<body>` đổi emoji ĐẦU nút/tiêu đề sang icon SVG (`.eic`, MutationObserver; bỏ qua textarea/.tr/.trc/.p/.no-eic — thêm class `no-eic` nếu chỗ nào cần giữ emoji).
- **bg/index.html**: lưới `.xem .luoi` 2 cột (3 cột ≥640px, 4 cột ≥960px), thẻ ảnh 1:1 · nhãn "-x%" hoặc "Quà tặng" · dòng KM đầu tiên + "+n ưu đãi" · "Còn hàng" · tab Tất cả có dải "Đang khuyến mãi" ở đầu (`kmTop` trong `ve()`) · chip lọc cao 44px · emoji ở tab/sheet đổi sang icon nét. Giá vẫn là GIÁ NIÊM YẾT, KM chỉ liệt kê (luật 29/10 giữ nguyên).
- Việc treo: nút "KM cho cả hãng" (anh đã duyệt ý tưởng, chưa làm) · xoá 2 thư mục demo `app-moi/`, `bg-moi/`.
