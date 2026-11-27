# Test TRẠM TRUNG CHUYỂN MÃ HOÁ (21/11/2026): 3 máy cùng 1 shop (A máy chính, B máy phụ, C máy mới), trạm giả lập + Drive giả lập.
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-tram.py
import asyncio, json, re, time
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:400]) if not dk else '')
D = Drive(); FILES = {}; TRAM = {}; OFF = set(); GHI_DRIVE = {}
T0 = [int(time.time() * 1000)]
def tnow():
    T0[0] = max(T0[0] + 1, int(time.time() * 1000)); return T0[0]
LOGIN = "()=>{localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}"
FAKE = r"""window.TRAM_FB=(()=>{const U='https://tram.test',sl=ms=>new Promise(r=>setTimeout(r,ms));
 async function ghi(sid,id,o){for(;;){let j;try{const r=await fetch(U+'/ghi',{method:'POST',body:JSON.stringify({sid,id,...o})});j=await r.json()}catch(e){await sl(400);continue}if(j.err)throw {code:j.err};return}}
 function nghe(sid,tu,cb){let last=tu,stop=false;(async()=>{while(!stop){try{const r=await fetch(U+'/nghe?sid='+sid+'&tu='+last);const j=await r.json();if(j.ds.length)last=Math.max(last,...j.ds.map(d=>d.t));await cb(j.ds,false,false)}catch(e){try{await cb([],false,true)}catch(_){}}await sl(300)}})();return()=>{stop=true}}
 return {dangNhap:async()=>'u',ghi,nghe,don:async()=>0,cho:async()=>{}}})();"""
CHO = "while(GG.busy)await new Promise(r=>setTimeout(r,100));"
def drive_hang(ten):
    for f in D.f.values():
        if f['ap'].get('nam') and f['sheets']:
            for k, rows in f['sheets'].items():
                for r in rows:
                    if ten in r: return r
    return None
def drive_has(x):
    return x in json.dumps([f['sheets'] for f in D.f.values() if f['ap'].get('nam') and f['sheets']], ensure_ascii=False)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def mk(ten):
            async def h(r):
                u = r.request.url
                if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
                if 'localhost' in u: return await r.continue_()
                if ten in OFF: return await r.abort()
                if u.startswith('https://tram.test/'):
                    q = urlparse(u); a = parse_qs(q.query)
                    if q.path == '/ghi':
                        o = json.loads(r.request.post_data); L = TRAM.setdefault(o['sid'], [])
                        if any(x['id'] == o['id'] for x in L): return await r.fulfill(body='{"err":"permission-denied"}', content_type='application/json')
                        L.append({'id': o['id'], 'c': o['c'], 'iv': o['iv'], 'd': o['d'], 't': tnow()}); return await r.fulfill(body='{}', content_type='application/json')
                    ds = [x for x in TRAM.get(a['sid'][0], []) if x['t'] > int(a['tu'][0])]
                    return await r.fulfill(body=json.dumps({'ds': ds}), content_type='application/json')
                if 'script.google.com' in u: return await r.fulfill(body='{"status":"active","shop":"Shop Test","ok":true}', content_type='application/json')
                if '/upload/drive/v3/files' in u:
                    body = r.request.post_data; parts = [x for x in re.split(r'--sgb\d+', body) if '{' in x]
                    meta = json.loads(parts[0][parts[0].index('{'):].strip()); cont = parts[1][parts[1].index('{'):].strip()
                    i = D.new_id(); D.f[i] = {'id': i, 'name': meta['name'], 'ap': meta.get('appProperties', {}), 'ct': D.ts(), 'trashed': False, 'sheets': None, 'parents': []}; FILES[i] = cont
                    return await r.fulfill(body=json.dumps({'id': i}), content_type='application/json')
                m = re.search(r'/drive/v3/files/(\w+)\?alt=media', u)
                if m: return await r.fulfill(body=FILES.get(m.group(1), '{}'), content_type='application/json')
                if 'googleapis.com' in u:
                    if 'values:batchUpdate' in u: GHI_DRIVE[ten] = GHI_DRIVE.get(ten, 0) + 1
                    try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
                    except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
                await r.abort()
            c = await b.new_context(); await c.route('**/*', h); await c.add_init_script(FAKE)
            pg = await c.new_page(); pg.on('pageerror', lambda e: errs.append(ten + ': ' + str(e)))
            await pg.goto(URL + '/khong-co'); await pg.evaluate(LOGIN); await pg.goto(URL + '/app/'); await pg.wait_for_timeout(3500)
            return pg
        async def doi(pg, js, giay=12):
            for _ in range(int(giay * 5)):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(200)
            return False
        BAN = "async(a)=>{const h=db.hang.find(x=>x.ten==='Ốp test');h.sl-=1;const id=Date.now().toString(36)+Math.random().toString(36).slice(2,6);db.don.push({id,bill:id,ngay:todayIso(),gio:'9:00',loai:'pk',hangId:h.id,ten:a,sl:1,giaBan:50000,giaVon:10000,tt:'Tiền mặt',huy:null});save();return id}"
        SL = "()=>{const h=db.hang.find(x=>x.ten==='Ốp test');return h?h.sl:null}"
        A = await mk('A')
        await A.evaluate("async()=>{" + CHO + "db.hang.push({id:'h1',ten:'Ốp test',nhom:'pk',sl:10,giaNhap:10000,giaBan:50000,ngayNhap:todayIso()});save();await GG.push();await TRAM.batMoi()}")
        B = await mk('B')
        ok('B nối máy phụ', await doi(B, "()=>TRAM.ok&&!TRAM.chinh()"))
        BAN1 = "async(a)=>{const h=db.hang.find(x=>x.ten==='Ốp test');h.sl-=1;const id=Date.now().toString(36)+Math.random().toString(36).slice(2,5);db.don.push({id,bill:id,ngay:todayIso(),gio:'9:00',loai:'pk',hangId:h.id,ten:a,sl:1,giaBan:50000,giaVon:10000,tt:'Tiền mặt',huy:null});save()}"
        # B chụp sổ TRƯỚC khi nhận đơn (giả: lần lưu sau bị mất do máy chưa kịp ghi)
        await B.evaluate("()=>{window._cu=JSON.stringify(db)}")
        await A.evaluate(BAN1, 'Đơn X1'); await A.evaluate(BAN1, 'Đơn X2')
        ok('B thấy 2 đơn X1, X2', await doi(B, "()=>db.don.filter(x=>/^Đơn X/.test(x.ten)).length===2"))
        tonB = await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")
        # mất lần lưu: sổ trên máy quay về bản cũ, nhưng mốc rời (localStorage) đã tiến
        await B.evaluate("()=>{const o=JSON.parse(window._cu);localStorage.setItem(KEY,JSON.stringify(o));try{IDBS.set(KEY,o)}catch(_){}}")
        await B.evaluate("()=>{Store.save=()=>{};}")
        await B.reload(); await B.wait_for_timeout(4000)
        ok('Tải lại: 2 đơn X1, X2 quay về (không mất)', await doi(B, "()=>db.don.filter(x=>/^Đơn X/.test(x.ten)).length===2"), await B.evaluate("()=>db.don.map(x=>x.ten).join(',')"))
        ok('Tồn không cộng/trừ trùng', await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl") == tonB, (tonB, await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")))
        # tải lại lần nữa (sổ đã lưu đủ) → vẫn 2 đơn, không nhân đôi
        await B.reload(); await B.wait_for_timeout(3500)
        ok('Tải lại lần 2: vẫn đúng 2 đơn', await B.evaluate("()=>db.don.filter(x=>/^Đơn X/.test(x.ten)).length")==2)
        ok('Tồn vẫn đúng', await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl") == tonB)
        ok('Không lỗi console', not errs, errs[:3])
        print(f'{sum(KQ)}/{len(KQ)}')

asyncio.run(main())
