#!/usr/bin/env node
/**
 * Shop Gọn — ROBOT HÀNG CHỜ TRUYỀN THÔNG (chạy trên Mac mini, 0đ, không AI)
 * 29/10/2026 anh Thái: shop bấm Tạo bài → hàng chờ trên máy chủ → robot này lấy đơn → dựng 4 ảnh từ
 * 15 mẫu của trang Thiết kế hình (shopgon.vn/tt) + hiệu ứng mùa → gửi ảnh về máy chủ (lưu Drive) → app hiện cho shop.
 *
 * Chạy 1 lượt rồi thoát (launchd gọi lại mỗi 2 phút):   node robot/hang-cho.mjs
 * Cấu hình: file ~/.shopgon-robot.env (KHÔNG để trong repo vì repo công khai)
 *   HC_URL=https://script.google.com/macros/s/…/exec
 *   HC_KEY=<chìa robot, lấy từ hàm hcCaiDat>
 *   TT_URL=https://shopgon.vn/tt/?robot=1        (không bắt buộc)
 */
import { readFileSync, existsSync, writeFileSync, unlinkSync, statSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const env = { ...process.env };
const envFile = env.HC_ENV || join(homedir(), '.shopgon-robot.env');
if (existsSync(envFile)) for (const l of readFileSync(envFile, 'utf8').split('\n')) {
  const m = l.match(/^\s*([A-Z_]+)\s*=\s*(.*?)\s*$/); if (m && !env[m[1]]) env[m[1]] = m[2].replace(/^["']|["']$/g, '');
}
const HC_URL = env.HC_URL, HC_KEY = env.HC_KEY, TT_URL = env.TT_URL || 'https://shopgon.vn/tt/?robot=1';
const MAX = +env.HC_MAX || 10;                       // tối đa 10 bài mỗi lượt
if (!HC_URL || !HC_KEY) { console.error('Thiếu HC_URL / HC_KEY trong', envFile); process.exit(2); }

/* chống chạy chồng 2 lượt */
const LOCK = join(tmpdir(), 'shopgon-hang-cho.lock');
if (existsSync(LOCK) && Date.now() - statSync(LOCK).mtimeMs < 20 * 60000) { console.log('Lượt trước còn chạy'); process.exit(0); }
writeFileSync(LOCK, String(process.pid));
const xong = c => { try { unlinkSync(LOCK); } catch (_) {} process.exit(c); };

async function goi(o) {
  const r = await fetch(HC_URL, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify({ ...o, key: HC_KEY }), redirect: 'follow' });
  const t = await r.text();
  try { return JSON.parse(t); } catch (_) { throw new Error('Máy chủ trả lạ: ' + t.slice(0, 160)); }
}
const gio = () => new Date().toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

let chromium;
try { ({ chromium } = await import('playwright')); }
catch (_) { const req = createRequire(import.meta.url); ({ chromium } = req(env.PW_PATH || 'playwright')); }

let browser = null, page = null, n = 0;
try {
  for (; n < MAX; n++) {
    const r = await goi({ act: 'hcLay' });
    if (!r.ok) throw new Error(r.msg || 'hcLay lỗi');
    if (!r.job) break;
    const { ma, du } = r.job;
    console.log(gio(), 'Nhận', ma, du.may && du.may.ten, du.mua ? '· mùa ' + du.mua : '');
    try {
      if (!browser) {
        browser = await chromium.launch({ headless: true });
        page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
      }
      await page.goto(TT_URL + (TT_URL.includes('?') ? '&' : '?') + 'v=' + Date.now(), { waitUntil: 'networkidle', timeout: 60000 });
      await page.waitForFunction(() => typeof window.robotVe === 'function', null, { timeout: 30000 });
      const chon = await page.evaluate(([du, ma]) => window.robotChon(du, ma), [du, ma]);
      const anh = [], ten = [];
      for (const c of chon) {
        await page.evaluate(([du, i, ma]) => window.robotVe(du, i, ma), [du, c.i, ma]);
        await page.evaluate(async () => {                      // chờ font + ảnh máy tải xong
          await document.fonts.ready;
          await Promise.all([...document.querySelectorAll('#cho img')].map(im => im.complete ? 0 : new Promise(ok => { im.onload = im.onerror = ok; setTimeout(ok, 15000); })));
        });
        const buf = await page.locator('#cho .k').first().screenshot({ type: 'jpeg', quality: 86 });
        anh.push(buf.toString('base64')); ten.push(c.ten);
      }
      const t = await goi({ act: 'hcTra', ma, anh, ten });
      if (!t.ok) throw new Error(t.msg || 'hcTra lỗi');
      console.log(gio(), 'Xong', ma, anh.length, 'ảnh');
    } catch (e) {
      console.error(gio(), 'Lỗi', ma, e.message);
      try { await goi({ act: 'hcTra', ma, loi: 'Robot: ' + String(e.message).slice(0, 200) }); } catch (_) {}
    }
  }
} catch (e) { console.error(gio(), e.message); if (browser) await browser.close(); xong(1); }
if (browser) await browser.close();
if (n) console.log(gio(), 'Lượt này làm', n, 'bài');
xong(0);
