// Robot "Kho máy" Shop Gọn: lấy giá niêm yết + giá trên web hãng + ảnh chính hãng của OPPO, Samsung, Xiaomi, iPhone.
// Chạy: node kho/lay-kho.mjs  →  ghi kho/kho-may.json (hãng nào lỗi thì giữ dữ liệu cũ của hãng đó)
import { chromium } from 'playwright';
import fs from 'fs';

const FILE = new URL('./kho-may.json', import.meta.url);
const ngu = ms => new Promise(r => setTimeout(r, ms));
const tron = n => n ? Math.round(n / 1000) * 1000 : 0;
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

async function moTrang(ctx, url, cho = 3500) {
  const p = await ctx.newPage();
  await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await ngu(cho);
  return p;
}

// ---------- OPPO ----------
async function oppo(ctx) {
  const p = await moTrang(ctx, 'https://www.oppo.com/vn/smartphones/', 5000);
  for (let i = 0; i < 6; i++) { await p.mouse.wheel(0, 3000); await ngu(700); }
  const ds = await p.evaluate(() => {
    const so = s => +String(s).replace(/\.00$/, '').replace(/[^\d]/g, '');
    const m = new Map();
    for (const c of document.querySelectorAll('.item-container')) {
      const a = c.querySelector('a[data-product_name]'); if (!a) continue;
      const ten = a.dataset.product_name.trim(); if (m.has(ten)) continue;
      const anh = [...c.querySelectorAll('.swiper-slide img')].map(i => i.getAttribute('data-src') || i.src).filter(s => /^http/.test(s));
      const gia = (c.innerText.match(/₫\s?[\d,\.]+/g) || []).map(s => so(s.replace(/,/g, '')));
      m.set(ten, { ten, link: a.href, mua: a.dataset.buynowlink || '', anh, gia });
    }
    return [...m.values()];
  });
  await p.close();
  log('OPPO danh sách', ds.length);
  const out = [];
  for (const d of ds) {
    const sp = { hang: 'OPPO', ten: d.ten, link: d.link, mau: d.anh.map(a => ({ ten: '', anh: a })), bienThe: [] };
    const g = d.gia.filter(Boolean);
    if (/\/vn\/product\//.test(d.mua)) {
      try {
        const q = await moTrang(ctx, d.mua, 4500);
        const r = await q.evaluate(async () => {
          const ngu = ms => new Promise(r => setTimeout(r, ms)); const so = s => +String(s).replace(/[^\d]/g, '');
          const lb = re => [...document.querySelectorAll('.label__title')].filter(e => re.test(e.textContent.trim()));
          const box = document.querySelector('.product-information__price');
          const gia = () => { const m = (box ? box.innerText : '').match(/[\d\.]+\s?₫/g) || []; return { giaHang: so(m[0]), niemyet: m[1] ? so(m[1]) : so(m[0]) }; };
          const bt = []; for (const c of lb(/^\d+\s?\+\s?\d+\s?(G|GB|T|TB)$/i)) { c.click(); await ngu(1500); bt.push({ dl: c.textContent.trim().replace(/G$/, 'GB'), ...gia() }); }
          if (!bt.length && box) bt.push({ dl: '', ...gia() });
          const mau = lb(/[A-Za-zÀ-ỹ]/).filter(e => !/\+|\d+GB/i.test(e.textContent)).map(e => e.textContent.trim());
          return { bt, mau };
        });
        await q.close();
        sp.bienThe = r.bt.filter(b => b.niemyet);
        r.mau.forEach((t, i) => { if (sp.mau[i]) sp.mau[i].ten = t; else sp.mau.push({ ten: t, anh: sp.mau[0] ? sp.mau[0].anh : '' }); });
      } catch (e) { log('OPPO lỗi trang', d.ten, e.message); }
    }
    if (!sp.bienThe.length && g.length) sp.bienThe.push({ dl: '', giaHang: Math.min(...g), niemyet: Math.max(...g) });
    out.push(sp);
  }
  return out;
}

// ---------- Samsung ----------
async function samsung(ctx) {
  const p = await moTrang(ctx, 'https://www.samsung.com/vn/smartphones/all-smartphones/', 3000);
  const ds = await p.evaluate(async () => {
    const u = 'https://searchapi.samsung.com/v6/front/b2c/product/finder/global?type=01010000&siteCode=vn&start=1&num=200&sort=newest&onlyFilterInfoYN=N&keySummaryYN=Y';
    const j = await (await fetch(u)).json();
    return (j.response.resultData.productList || []).map(f => ({
      ten: f.fmyMarketingName,
      models: f.modelList.map(m => ({ link: m.pdpUrl || m.originPdpUrl, anh: m.thumbUrl, price: m.price, promo: m.promotionPrice, chips: (m.fmyChipList || []).map(c => [c.fmyChipType, c.fmyChipName]) }))
    }));
  });
  await p.close();
  return ds.map(f => {
    const ten = f.ten.replace(/\s*\(.*?\)\s*/g, ' ').trim();
    const mau = new Map(), bt = new Map(); let link = '';
    for (const m of f.models) {
      const ch = Object.fromEntries(m.chips.map(([k, v]) => [k.toUpperCase(), v]));
      const col = ch.COLOR || '';
      const rom = (ch['MOBILE MEMORY'] || '').replace(/\s/g, ''); const ram = (ch.OTHER || '').replace(/\s/g, '');
      const dl = ram && rom ? ram + '+' + rom : rom;
      if (!link && m.link) link = 'https://www.samsung.com' + m.link.replace(/^https?:\/\/www\.samsung\.com/, '');
      if (col && !mau.has(col)) mau.set(col, { ten: col, anh: m.anh ? 'https:' + m.anh.replace(/^https?:/, '') : '' });
      const ny = tron(m.price), gh = tron(m.promo || m.price);
      if (!bt.has(dl) || (!bt.get(dl).niemyet && ny)) bt.set(dl, { dl, niemyet: ny, giaHang: gh });
    }
    return { hang: 'Samsung', ten, link, mau: [...mau.values()], bienThe: [...bt.values()].sort((a, b) => (a.niemyet || 9e9) - (b.niemyet || 9e9)) };
  });
}

// ---------- Xiaomi ----------
async function xiaomi(ctx) {
  const p = await moTrang(ctx, 'https://www.mi.com/vn/product-list/phone/redmi/', 4000);
  const out = [];
  for (const nhom of ['xiaomi', 'redmi', 'poco']) {
    const ds = await p.evaluate(async nhom => {
      const r = await fetch('https://go.buy.mi.com/vn/search/product-list?version=v4&cacheable=1&page_size=60&type=2&category_tag=' + nhom + '&page_index=0&from=laptop', { credentials: 'include' });
      const j = await r.json();
      return ((((j.data || {}).data_provider || {}).data || {}).product_list || []).map(x => x.product);
    }, nhom);
    log('Xiaomi', nhom, ds.length);
    for (const x of ds) {
      if (!x || !x.name || out.find(o => o.ten === x.name)) continue;
      const ny = tron(x.market_price_min_num || x.price_min_num), gh = tron(x.price_min_num || ny);
      const dls = String(x.comb_sec_spec || '').split('|').map(t => t.replace(/\s/g, '')).filter(Boolean);
      const bt = dls.length ? dls.map((dl, i) => ({ dl, niemyet: i ? 0 : ny, giaHang: i ? 0 : gh })) : [{ dl: '', niemyet: ny, giaHang: gh }];
      out.push({ hang: 'Xiaomi', ten: x.name.trim(), link: x.item_link || '', mau: x.image ? [{ ten: '', anh: x.image }] : [], bienThe: bt });
    }
  }
  await p.close();
  return out;
}

// ---------- Apple ----------
async function apple(ctx) {
  const p = await moTrang(ctx, 'https://www.apple.com/vn/shop/buy-iphone', 3000);
  const links = await p.evaluate(() => [...new Set([...document.querySelectorAll('a[href*="/shop/buy-iphone/"]')].map(a => a.href.split('?')[0].split('#')[0]))]);
  await p.close();
  log('Apple trang', links.length);
  const out = [];
  for (const l of links) {
    try {
      const q = await moTrang(ctx, l, 3000);
      const r = await q.evaluate(() => {
        const h = document.documentElement.outerHTML;
        const lay = key => { let i = h.indexOf(key); if (i < 0) return null; i = h.indexOf('{', i); let d = 0, s = false, e = i;
          for (; e < h.length; e++) { const c = h[e]; if (s) { if (c == '\\') e++; else if (c == '"') s = false; continue; } if (c == '"') s = true; else if (c == '{') d++; else if (c == '}') { d--; if (!d) break; } }
          return JSON.parse(h.slice(i, e + 1)); };
        const d = lay('productSelectionData:'); if (!d) return [];
        const dv = d.displayValues, txt = s => String(s || '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
        const tenTrang = txt((document.querySelector('h1') || {}).textContent).replace(/^Mua\s+/i, '');
        const m = new Map();
        for (const p of d.products) {
          let ten = tenTrang;
          if (p.dimensionScreensize && dv.dimensionScreensize && dv.dimensionScreensize[p.dimensionScreensize])
            ten = txt(dv.dimensionScreensize[p.dimensionScreensize].value).split(' Màn hình')[0];
          ten = ten.replace(/\s+/g, ' ').trim();
          if (!m.has(ten)) m.set(ten, { ten, mau: new Map(), bt: new Map() });
          const o = m.get(ten);
          const col = dv.dimensionColor && dv.dimensionColor[p.dimensionColor] ? txt(dv.dimensionColor[p.dimensionColor].value) : p.dimensionColor;
          const img = d.imageDictionary && d.imageDictionary[p.imageKey] && d.imageDictionary[p.imageKey].sources ? d.imageDictionary[p.imageKey].sources[0].srcSet.split(' ')[0] : '';
          if (col && !o.mau.has(col)) o.mau.set(col, { ten: col, anh: img.replace(/&amp;/g, '&') });
          const dl = dv.dimensionCapacity && dv.dimensionCapacity[p.dimensionCapacity] ? txt(dv.dimensionCapacity[p.dimensionCapacity].value).match(/\d+\s*(GB|TB)/i)?.[0].replace(/\s/g, '') || p.dimensionCapacity : p.dimensionCapacity;
          const pr = dv.prices && dv.prices[p.fullPrice]; const gia = pr ? pr.amountBeforeTradeIn : 0;
          if (!o.bt.has(dl)) o.bt.set(dl, { dl, niemyet: gia, giaHang: gia });
        }
        return [...m.values()].map(o => ({ ten: o.ten, mau: [...o.mau.values()], bienThe: [...o.bt.values()].sort((a, b) => a.niemyet - b.niemyet) }));
      });
      await q.close();
      for (const sp of r) out.push({ hang: 'Apple', link: l, ...sp });
    } catch (e) { log('Apple lỗi', l, e.message); }
  }
  return out;
}

// ---------- chạy ----------
const cu = fs.existsSync(FILE) ? JSON.parse(fs.readFileSync(FILE, 'utf8')) : { hang: {} };
const moi = { capNhat: new Date().toISOString(), hang: {}, loi: {} };
const CHI_BO_SUNG = !!process.env.CHI_BO_SUNG;   // chạy nhanh: chỉ nạp bo-sung.json + tải ảnh, không quét web hãng
if (CHI_BO_SUNG) { moi.capNhat = cu.capNhat || moi.capNhat; log('Chế độ chỉ bổ sung'); }
const browser = CHI_BO_SUNG ? null : await chromium.launch();
const ctx = CHI_BO_SUNG ? null : await browser.newContext({ locale: 'vi-VN', viewport: { width: 1366, height: 900 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36' });
if (!CHI_BO_SUNG) for (const [ten, fn] of [['OPPO', oppo], ['Samsung', samsung], ['Xiaomi', xiaomi], ['Apple', apple]]) {
  try {
    const ds = (await fn(ctx)).filter(x => x.ten);
    log(ten, 'xong', ds.length, 'máy');
    if (ds.length) moi.hang[ten] = ds; else throw new Error('không lấy được máy nào');
  } catch (e) {
    log(ten, 'LỖI', e.message);
    moi.loi[ten] = e.message;
  }
}
if (browser) await browser.close();

// ---------- cộng dồn: máy hãng gỡ khỏi web vẫn giữ lại (shop còn bán) ----------
const khoa = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
const homNay = moi.capNhat.slice(0, 10);
for (const [h, ds] of Object.entries(cu.hang || {})) {
  if (!moi.hang[h]) { moi.hang[h] = ds; continue; }           // hãng quét lỗi / hãng bổ sung tay → giữ nguyên
  const co = new Set(moi.hang[h].map(s => khoa(s.ten)));
  let giu = 0;
  for (const s of ds) if (!co.has(khoa(s.ten))) { co.add(khoa(s.ten)); moi.hang[h].push(s.nguon === 'bo-sung' ? s : { ...s, ngung: s.ngung || homNay }); giu++; }
  if (giu) log(h, 'giữ lại', giu, 'máy không còn trên web hãng');
}

// ---------- bổ sung tay: kho/bo-sung.json (máy web hãng không có: hãng khác, đời cũ còn bán) ----------
const BO_SUNG = new URL('./bo-sung.json', import.meta.url);
if (fs.existsSync(BO_SUNG)) {
  let them = 0, va = 0;
  for (const sp of JSON.parse(fs.readFileSync(BO_SUNG, 'utf8'))) {
    if (!sp.hang || !sp.ten) continue;
    const ds = (moi.hang[sp.hang] = moi.hang[sp.hang] || []);
    const cu2 = ds.find(s => khoa(s.ten) === khoa(sp.ten));
    if (!cu2) { ds.push({ ...sp, nguon: 'bo-sung' }); them++; continue; }
    if (cu2.nguon === 'bo-sung') { const giuFile = new Map((cu2.mau || []).map(m => [m.anh, m.file])); Object.assign(cu2, sp, { mau: (sp.mau || []).map(m => ({ ...m, file: giuFile.get(m.anh) })) }); continue; }
    if (!(cu2.mau || []).some(m => m.anh)) { cu2.mau = sp.mau; va++; }   // máy web hãng thiếu ảnh → vá bằng ảnh bổ sung
  }
  log('Bổ sung tay: thêm', them, 'máy, vá ảnh', va, 'máy');
}

// ---------- lưu ảnh về repo (cùng tên miền shopgon.vn → app xuất hình PNG được) ----------
import crypto from 'crypto';
let sharp = null; try { sharp = (await import('sharp')).default; } catch (e) { log('Không có sharp, bỏ qua lưu ảnh'); }
const THU_MUC = new URL('./anh/', import.meta.url); fs.mkdirSync(THU_MUC, { recursive: true });
let moiTai = 0; moi.anhLoi = [];
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36';
async function taiAnh(url, ref) {
  let loi;
  for (const h of [{ 'User-Agent': UA, 'Referer': ref || '' }, { 'User-Agent': UA }, { 'User-Agent': 'Mozilla/5.0' }]) {
    try { const r = await fetch(url, { headers: h }); if (r.ok) return Buffer.from(await r.arrayBuffer()); loi = 'HTTP ' + r.status; } catch (e) { loi = e.message; }
  }
  throw new Error(loi);
}
if (sharp) for (const ds of Object.values(moi.hang)) for (const sp of ds) for (const m of sp.mau || []) {
  if (!m.anh) continue;
  const id = crypto.createHash('md5').update(m.anh).digest('hex').slice(0, 12);
  const f = new URL(id + 't.webp', THU_MUC);
  if (!fs.existsSync(f)) {
    try {
      const buf = await taiAnh(m.anh, sp.link);
      const md = await sharp(buf).metadata();
      if (Math.max(md.width || 0, md.height || 0) < 300) throw new Error('ảnh nhỏ ' + md.width + 'x' + md.height);
      await sharp(buf).trim({ threshold: 12 }).resize({ width: 700, height: 900, fit: 'inside', withoutEnlargement: true }).webp({ quality: 82 }).toFile(f.pathname);
      moiTai++;
    } catch (e) { log('Ảnh lỗi', sp.ten, e.message); moi.anhLoi.push(sp.hang + ' | ' + sp.ten + ' | ' + e.message); delete m.file; continue; }
  }
  m.file = 'kho/anh/' + id + 't.webp';
}
log('Ảnh mới tải', moiTai, '· ảnh lỗi', moi.anhLoi.length);
fs.writeFileSync(FILE, JSON.stringify(moi));
const tong = Object.values(moi.hang).reduce((s, a) => s + a.length, 0);
log('Tổng', tong, 'máy →', FILE.pathname);
