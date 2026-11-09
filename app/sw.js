// Shop Gọn — service worker.
// 09/11 anh Thái (LỚP 1 CHỐNG MẤT): có mạng thì LUÔN lấy bản mới nhất từ mạng (như cũ) và cất 1 bản vào máy;
// mất mạng thì mở bản đã cất → app vẫn mở được để bán, dữ liệu nằm trong IndexedDB của máy.
const KHO = 'shopgon-app-v1';
const GOC = ['/app/', '/app/manifest.json', '/app/icon-192.png', '/app/icon-512.png', '/mua.js',
  '/app/bd/ponyfill.js', '/app/bd/zxing_reader.wasm'];  // quét mã IMEI khi mất mạng

self.addEventListener('install', e => {
  e.waitUntil(caches.open(KHO).then(c => Promise.all(GOC.map(u =>
    fetch(u, { cache: 'no-store' }).then(r => r.ok ? c.put(u, r) : null).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('shopgon-app-') && k !== KHO).map(k => caches.delete(k))))
    .then(() => self.clients.claim())));

function cat(key, r) { if (r && r.ok && r.type !== 'opaque') { const c = r.clone(); caches.open(KHO).then(k => k.put(key, c)).catch(() => {}); } return r; }

self.addEventListener('fetch', e => {
  const q = e.request; if (q.method !== 'GET') return;
  const u = new URL(q.url);
  if (q.mode === 'navigate' && u.origin === location.origin && /^\/app(\/|\/index\.html)?$/.test(u.pathname)) {
    // trang app: mạng trước (bản mới nhất), mất mạng → bản đã cất (bỏ qua ?demo=…)
    e.respondWith(fetch(q, { cache: 'no-store' }).then(r => cat('/app/', r))
      .catch(() => caches.match('/app/', { ignoreSearch: true }).then(r => r || Response.error())));
    return;
  }
  if (u.origin === location.origin && GOC.includes(u.pathname)) {
    e.respondWith(fetch(q, { cache: 'no-store' }).then(r => cat(u.pathname, r)).catch(() => caches.match(u.pathname).then(r => r || Response.error())));
  }
  // còn lại (Google, Drive, máy chủ bản quyền, ver.json, ảnh kho…) đi mạng như cũ, không cất
});
