# Đưa Shop Gọn lên bản chống sao chép (chuẩn bị 26/10/2026)

Mục tiêu: repo nguồn `MrDT1988/shopgon` → RIÊNG TƯ; shopgon.vn chạy từ repo CÔNG KHAI `MrDT1988/shopgon-web` chứa bản đã nén + làm rối.

## Đã kiểm (26/10 tối)
- `node build/build.mjs <thư mục>` (cần javascript-obfuscator@4.1.1 + html-minifier-terser@7.2.0) chạy OK.
- Bản build: 9 trang không lỗi, không file thiếu; chạy `_tam/test-toan-bo.py` trên bản build = **50/50 đạt**.

## Anh Thái bấm (máy chỉ được làm trong GitHub của anh)
1. github.com/new → tên `shopgon-web` → Public → KHÔNG tick README → Create.
2. Báo Claude → Claude `add_repo shopgon-web (push)`, build, push bản build (có CNAME shopgon.vn, kho/, robot đã làm rối, workflow kho-may.yml).
3. Repo `shopgon` → Settings → Pages → Custom domain: Remove.
4. Repo `shopgon-web` → Settings → Pages → Deploy from branch `main` / root → Custom domain `shopgon.vn` → Save → tick Enforce HTTPS (khi hiện).
5. Claude kiểm shopgon.vn chạy bản mới (BUILD trong ver.json khớp) → anh: repo `shopgon` → Settings → Danger zone → Change visibility → Private.

## Từ đó về sau (mỗi lần sửa)
Sửa ở `shopgon` → đổi BUILD + app/ver.json → build → push sang `shopgon-web`. Robot kho chạy ở cả 2 repo (vô hại); kho thật = repo web.
