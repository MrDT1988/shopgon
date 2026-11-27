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
        await B.evaluate("()=>{window._cu=JSON.parse(JSON.stringify(db));delete window._cu._tram}")
        await A.evaluate(BAN1, 'Đơn Y1'); await A.evaluate(BAN1, 'Đơn Y2')
        ok('B thấy 2 đơn Y', await doi(B, "()=>db.don.filter(x=>/^Đơn Y/.test(x.ten)).length===2"))
        tonB = await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")
        # mất kiểu bản CŨ: sổ quay về bản trước, KHÔNG có mốc trong sổ, mốc rời đã tiến
        await B.evaluate("()=>{const o=window._cu;localStorage.setItem(KEY,JSON.stringify(o));try{IDBS.set(KEY,o)}catch(_){}Store.save=()=>{}}")
        await B.reload(); await B.wait_for_timeout(4000)
        mat = await B.evaluate("()=>db.don.filter(x=>/^Đơn Y/.test(x.ten)).length")
        ok('Giả lập mất đơn (kiểu trước 18h00): B còn 0 đơn Y', mat==0, mat)
        r = await B.evaluate("async()=>{await doiTram();return await TRAM.layLai()}".replace('await doiTram();','for(let i=0;i<40&&!TRAM.ok;i++)await new Promise(r=>setTimeout(r,200));'))
        ok('Bấm Lấy lại đơn từ trạm: về đủ 2 đơn Y', await B.evaluate("()=>db.don.filter(x=>/^Đơn Y/.test(x.ten)).length")==2, r)
        ok('Tồn trừ đúng như lúc chưa mất', await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")==tonB, (tonB, await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")))
        r2 = await B.evaluate("async()=>await TRAM.layLai()")
        ok('Bấm lần 2: không áp gì thêm (không trùng)', r2['lo']==0 and await B.evaluate("()=>db.don.filter(x=>/^Đơn Y/.test(x.ten)).length")==2 and await B.evaluate("()=>db.hang.find(x=>x.id==='h1').sl")==tonB, r2)
        n0 = await A.evaluate("()=>db.don.length"); rA = await A.evaluate("async()=>await TRAM.layLai()")
        ok('Máy chính A đủ đơn: Lấy lại không đổi gì', rA['lo']==0 and await A.evaluate("()=>db.don.length")==n0, rA)
        ok('Thẻ ⚡ có nút Lấy lại đơn', 'data-tram="laylai"' in await B.evaluate("()=>tramBar()"))
        ok('Không lỗi console', not errs, errs[:3])
        print(f'{sum(KQ)}/{len(KQ)}')

asyncio.run(main())
