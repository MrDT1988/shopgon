// Shop Gọn — đóng gói bản công khai (25/10/2026, anh Thái duyệt việc chống sao chép).
// Mã nguồn đọc được nằm ở repo RIÊNG TƯ MrDT1988/shopgon. Bản chạy trên shopgon.vn nằm ở repo CÔNG KHAI MrDT1988/shopgon-web:
//   - HTML/CSS nén, JS trong trang được làm rối (javascript-obfuscator) → copy về cũng khó đọc, khó sửa.
//   - KHÔNG đưa sang: BAN_GIAO.md, _tam/, build/, .github của repo nguồn.
//   - kho/ (kho máy + ảnh + robot) do robot chạy ở repo web cập nhật → build KHÔNG ghi đè kho-may.json / anh / demo-ton.json.
// Cách dùng (trong máy có node):  node build/build.mjs <thư mục repo shopgon-web>
//   cần: npm i javascript-obfuscator@4.1.1 html-minifier-terser@7.2.0
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join, dirname, extname } from 'path';
import { createRequire } from 'module';
const require = createRequire(process.env.NODE_MODS ? join(process.env.NODE_MODS, 'x.js') : import.meta.url);
const JO = require('javascript-obfuscator');
const { minify } = require('html-minifier-terser');

const SRC = join(dirname(new URL(import.meta.url).pathname), '..');
const OUT = process.argv[2];
if (!OUT) { console.error('Thiếu thư mục đích (repo shopgon-web)'); process.exit(1); }

const TRANG = ['index.html', 'so-sanh.html', 'privacy.html', 'terms.html', 'app/index.html', 'quantri/index.html', 'bg/index.html', 'tt/index.html', 'setup/index.html'];
const TINH = ['style.css', 'CNAME', 'quantri/manifest.json', 'quantri/icon-192.png', 'quantri/icon-512.png', 'app/manifest.json', 'app/icon-180.png', 'app/icon-192.png', 'app/icon-512.png'];
const THU_MUC_TINH = ['setup/img'];
const KHO_CHI_CHEP_NEU_CHUA_CO = ['kho/kho-may.json', 'kho/demo-ton.json'];   // robot ở repo web tự cập nhật
const KHO_LUON_CHEP = ['kho/bo-sung.json'];
const ROBOT = ['kho/lay-kho.mjs'];

const roi = js => JO.obfuscate(js, {
  compact: true, simplify: true, target: 'browser',
  stringArray: true, stringArrayEncoding: ['base64'], stringArrayThreshold: 0.75, splitStrings: true, splitStringsChunkLength: 8,
  identifierNamesGenerator: 'hexadecimal', renameGlobals: false, selfDefending: false,
  controlFlowFlattening: false, deadCodeInjection: false, numbersToExpressions: false, unicodeEscapeSequence: false
}).getObfuscatedCode();

const ghi = (p, s) => { mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, s); };
const chep = (a, b) => { mkdirSync(dirname(b), { recursive: true }); copyFileSync(a, b); };

for (const t of TRANG) {
  let h = readFileSync(join(SRC, t), 'utf8');
  h = h.replace(/<script(?![^>]*\bsrc=)([^>]*)>([\s\S]*?)<\/script>/g, (m, at, code) => /type=["']?(application\/ld\+json|text\/template)/.test(at) || !code.trim() ? m : `<script${at}>${roi(code)}</script>`);
  h = await minify(h, { collapseWhitespace: true, conservativeCollapse: true, removeComments: true, minifyCSS: true, minifyJS: false, keepClosingSlash: true });
  ghi(join(OUT, t), h);
  console.log('trang', t, h.length);
}
for (const f of TINH) if (existsSync(join(SRC, f))) chep(join(SRC, f), join(OUT, f));
for (const d of THU_MUC_TINH) for (const f of readdirSync(join(SRC, d))) chep(join(SRC, d, f), join(OUT, d, f));
for (const f of KHO_LUON_CHEP) chep(join(SRC, f), join(OUT, f));
for (const f of KHO_CHI_CHEP_NEU_CHUA_CO) if (!existsSync(join(OUT, f))) chep(join(SRC, f), join(OUT, f));
if (!existsSync(join(OUT, 'kho/anh'))) for (const f of readdirSync(join(SRC, 'kho/anh'))) chep(join(SRC, 'kho/anh', f), join(OUT, 'kho/anh', f));
for (const f of ROBOT) ghi(join(OUT, f), JO.obfuscate(readFileSync(join(SRC, f), 'utf8'), { compact: true, target: 'node', stringArray: true, stringArrayEncoding: ['base64'], renameGlobals: false, identifierNamesGenerator: 'hexadecimal' }).getObfuscatedCode());
chep(join(SRC, '.github/workflows/kho-may.yml'), join(OUT, '.github/workflows/kho-may.yml'));
ghi(join(OUT, 'README.md'), '# shopgon.vn\nBản chạy của Shop Gọn. © Shop Gọn — mọi quyền được bảo lưu. Không sao chép, phân phối lại.\n');
console.log('xong →', OUT);
