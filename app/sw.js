// Shop Gọn — service worker tối giản để điện thoại cho "Cài app". KHÔNG lưu đệm: luôn lấy bản mới nhất từ mạng.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(fetch(e.request,{cache:'no-store'}).catch(()=>fetch(e.request)))});
