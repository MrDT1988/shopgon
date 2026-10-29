// Robot GIÁ NIÊM YẾT TGDD — 29/10/2026 anh Thái: "giá niêm yết lấy theo Thế Giới Di Động, 6h sáng quét 1 lần".
// Chạy: node kho/gia-tgdd.mjs  (GitHub Actions .github/workflows/gia-tgdd.yml, 06:00 giờ VN mỗi ngày)
// Cách lấy (0đ, không cần AI): mở thegioididong.com/dtdd bằng Playwright, bấm "Xem thêm" tới hết → đọc từng thẻ máy
// (tên + giá) → mở trang từng máy lấy thêm các bản dung lượng khác. Giá niêm yết = giá gạch (giá gốc) nếu có, không thì giá đang bán.
// Ghi kho/gia-tgdd.json: { capNhat, n, gia: { <khóa>: { t, ny, gb, u } } } — khóa = tgKey(tên) (app + bảng giá dùng cùng hàm).
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const GOC = 'https://www.thegioididong.com';
const RA = 'kho/gia-tgdd.json';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';

/* KHÓA KHỚP TÊN — giữ y hệt bản trong app/index.html và bg/index.html */
export function tgKey(s) {
  s = String(s || '').toLowerCase().replace(/^điện thoại\s+/, '').replace(/^samsung\s+(?=galaxy)/, '').replace(/^xiaomi\s+(?=redmi|poco)/, '').replace(/\bmoto\s+/g, '').replace(/\s+-\s+.*$/, '').replace(/(\d)\+(\d)/g, '$1/$2').replace(/\+/g, 'plus');
  const m = s.match(/\d+\s*(?:gb|tb)?\s*\/\s*\d+\s*(?:gb|tb)?|\d+\s*(?:gb|tb)/);
  if (m) s = s.slice(0, m.index + m[0].length);
  return s.replace(/\b[45]g\b/g, '').replace(/gb/g, '').replace(/[^a-z0-9/]/g, '');
}
const so = s => +String(s || '').replace(/\D/g, '') || 0;
const ngu = ms => new Promise(r => setTimeout(r, ms));

function docTrang(h) {
  let ten = ((h.match(/<h1[^>]*>([^<]+)<\/h1>/) || [])[1] || '').trim();
  if (!ten) ten = ((h.match(/<title>([^<]+)/) || [])[1] || '').split(/\s+(?:giá|\||-)\s+/i)[0].trim();
  ten = ten.replace(/^Điện thoại\s+/i, '').replace(/&amp;/g, '&');
  const gach = so((h.match(/<del[^>]*>([\d.]{6,})<!-- -->đ/) || [])[1]);
  const ban = so((h.match(/text-red-5">([\d.]{6,})<!-- -->đ/) || [])[1]) || so((h.match(/Giá bán:\s*<b>([\d.]{6,})₫/) || [])[1]);
  const bienThe = [...new Set((h.match(/href="\/dtdd\/[a-z0-9-]+"/g) || []).map(x => x.slice(6, -1)))];
  return { ten, ny: Math.max(gach, ban), gb: ban || gach, bienThe };
}

async function layHtml(p) {
  for (let lan = 0; lan < 3; lan++) {
    try {
      const r = await fetch(GOC + p, { headers: { 'user-agent': UA, 'accept-language': 'vi-VN,vi;q=0.9' } });
      if (r.ok) return await r.text();
    } catch (e) { }
    await ngu(1500 * (lan + 1));
  }
  return '';
}

const tb = await chromium.launch();
const pg = await (await tb.newContext({ userAgent: UA, locale: 'vi-VN', viewport: { width: 1280, height: 900 } })).newPage();
await pg.goto(GOC + '/dtdd', { waitUntil: 'domcontentloaded', timeout: 90000 });
await pg.waitForTimeout(3000);
const dem = () => pg.evaluate(() => new Set([...document.querySelectorAll('a[href*="/dtdd/"][title]')].map(a => a.pathname)).size);
for (let i = 0; i < 25; i++) {
  const n0 = await dem();
  const bam = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('a,button,div,span')].filter(e => /^Xem thêm/.test((e.innerText || '').trim()) && e.innerText.length < 60 && e.offsetParent).pop();
    if (!b) return false; b.scrollIntoView({ block: 'center' }); b.click(); return true;
  });
  if (!bam) break;
  for (let t = 0; t < 24 && (await dem()) <= n0; t++) await pg.waitForTimeout(500);
}
const the = await pg.evaluate(() => [...document.querySelectorAll('a[href*="/dtdd/"][title]')].map(a => {
  let c = a; for (let i = 0; i < 6 && c.parentElement && !/\d\.\d{3}\.\d{3}đ/.test(c.innerText); i++) c = c.parentElement;
  // chỉ tin giá trên thẻ khi khung chứa đúng 1 máy (tránh lẫn giá thẻ bên cạnh)
  const mot = new Set([...c.querySelectorAll('a[href*="/dtdd/"][title]')].map(x => x.pathname)).size === 1;
  const gia = mot ? (c.innerText.match(/\d{1,3}(?:\.\d{3}){2,}đ/g) || []).map(x => +x.replace(/\D/g, '')).filter(x => x >= 100000) : [];
  return { p: a.pathname, t: a.getAttribute('title') || '', gia };
}));
await tb.close();

const daXem = new Set(), gia = {};
const ghi = (ten, ny, gb, u) => { const k = tgKey(ten); if (!k || !ny || gia[k]) return; gia[k] = { t: ten, ny, gb: gb || ny, u }; };
const cho = [...new Map(the.map(x => [x.p, x])).values()];
console.log('Thẻ máy trên trang danh sách:', cho.length);
// thẻ danh sách: giá gạch (lớn nhất) = niêm yết, giá nhỏ nhất = giá đang bán
const hang = cho.map(x => x.p);
for (const x of cho) if (x.gia.length && x.gia.length <= 2 && Math.max(...x.gia) <= Math.min(...x.gia) * 1.6) ghi(x.t, Math.max(...x.gia), Math.min(...x.gia), x.p);
// mở từng trang: tên chuẩn + các bản dung lượng khác
async function tho() {
  while (hang.length) {
    const p = hang.shift(); if (daXem.has(p)) continue; daXem.add(p);
    const h = await layHtml(p); if (!h) continue;
    const d = docTrang(h);
    if (d.ten && d.ny) { const k = tgKey(d.ten); gia[k] = { t: d.ten, ny: d.ny, gb: d.gb, u: p }; }
    d.bienThe.forEach(b => { if (!daXem.has(b) && !hang.includes(b)) hang.push(b); });
    await ngu(250);
  }
}
await Promise.all([1, 2, 3, 4, 5].map(tho));

const n = Object.keys(gia).length;
console.log('Đã mở', daXem.size, 'trang · lấy được giá', n, 'mẫu');
if (n < 60) {
  console.log('Lấy được quá ít (<60) — giữ nguyên bản cũ, không ghi đè.');
  process.exit(existsSync(RA) ? 0 : 1);
}
const cu = existsSync(RA) ? JSON.parse(readFileSync(RA, 'utf8')) : { gia: {} };
const doi = Object.keys(gia).filter(k => !cu.gia[k] || cu.gia[k].ny !== gia[k].ny).length;
const sap = {}; Object.keys(gia).sort().forEach(k => { sap[k] = gia[k]; });
writeFileSync(RA, JSON.stringify({ capNhat: new Date().toISOString(), nguon: 'thegioididong.com', n, gia: sap }));
console.log('Ghi', RA, '·', doi, 'mẫu đổi giá so với lần trước');
