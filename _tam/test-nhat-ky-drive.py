# 27/11 NHẬT KÝ TỪNG MÁY TRÊN DRIVE — không mất đơn khi trạm hỏng / khác chìa / máy chính tắt / sổ trên máy mất. Dựa trên khung test TRẠM
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
D = Drive(); FILES = {}; TRAM = {}; OFF = set(); GHI_DRIVE = {}; TDOWN = set()
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
                    if ten in TDOWN: return await r.abort()
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
        def dem(pg, ten): return pg.evaluate("(t)=>db.don.filter(x=>x.ten===t).length", ten)
        def nk_tabs():
            out = {}
            for f in D.f.values():
                if f['ap'].get('nam') and f['sheets']:
                    for k, rows in f['sheets'].items():
                        if k.startswith('NK máy '): out[k] = len(rows)
            return out
        def drive_dem(ten):
            n = 0
            for f in D.f.values():
                if f['ap'].get('nam') and f['sheets']:
                    for k, rows in f['sheets'].items():
                        if k.startswith('NK'): continue
                        for r in rows:
                            if ten in r: n += 1
            return n
        GOP = "async()=>{for(let i=0;i<50&&NKD._g;i++)await new Promise(r=>setTimeout(r,100));return await NKD.gop()}"
        DAY = "async()=>{for(let i=0;i<50&&NKD._b;i++)await new Promise(r=>setTimeout(r,100));await NKD.day();return NKD.q().length}"
        A = await mk('A')
        await A.evaluate("async()=>{" + CHO + "db.hang.push({id:'h1',ten:'Ốp test',nhom:'pk',sl:20,giaNhap:10000,giaBan:50000,ngayNhap:todayIso()});save();" + CHO + "await GG.push();await TRAM.batMoi()}")
        B = await mk('B')
        ok('B nối máy phụ', await doi(B, "()=>TRAM.ok&&!TRAM.chinh()"))
        # 1) bình thường: B bán → nhật ký B trên Drive + A nhận
        await B.evaluate(BAN, 'N1'); await B.evaluate(DAY)
        ok('Bán ở B → trang "NK máy …" của B có trên Drive', any(v > 1 for v in nk_tabs().values()), nk_tabs())
        ok('A nhận N1 (trạm)', await doi(A, "()=>db.don.some(x=>x.ten==='N1')"))
        await A.evaluate(GOP); await A.evaluate(GOP)
        ok('Trạm + nhật ký cùng đưa N1: A chỉ 1 đơn, tồn 19', await dem(A,'N1') == 1 and await A.evaluate(SL) == 19, (await dem(A,'N1'), await A.evaluate(SL)))
        # 2) TRẠM HỎNG ở B: B bán 2 đơn → không lên trạm, vẫn lên nhật ký Drive → A gộp được
        TDOWN.add('B')
        await B.evaluate(BAN, 'N2'); await B.evaluate(BAN, 'N3'); await B.evaluate(DAY)
        await A.wait_for_timeout(1500)
        ok('Trạm hỏng: A chưa thấy N2 qua trạm', await dem(A,'N2') == 0)
        await A.evaluate(GOP)
        ok('A gộp nhật ký Drive → có N2, N3', await dem(A,'N2') == 1 and await dem(A,'N3') == 1)
        ok('Tồn A trừ đúng: 17', await A.evaluate(SL) == 17, await A.evaluate(SL))
        await A.evaluate("async()=>{" + CHO + "await GG.push()}")
        ok('A (máy chính) lưu N2 vào sổ chính trên Drive', drive_dem('N2') >= 1)
        TDOWN.discard('B')
        await A.wait_for_timeout(3000); await A.evaluate(GOP)
        ok('Trạm B sống lại, lô cũ lên trạm: A vẫn 1 đơn N2, tồn 17', await dem(A,'N2') == 1 and await A.evaluate(SL) == 17, (await dem(A,'N2'), await A.evaluate(SL)))
        # 3) KHÁC CHÌA: C dùng chìa riêng (không thấy trạm của A) → bán vẫn về A qua nhật ký
        C = await mk('C')
        await doi(C, "()=>TRAM.ok")
        await C.evaluate("async()=>{TRAM.dung();TRAM.k=null;await TRAM.datChia(TRAM.b64(crypto.getRandomValues(new Uint8Array(32))));TRAM.da=new Set();TRAM.lastT=Date.now();TRAM.san=TRAM.napFB().then(()=>TRAM.FB().dangNhap());await TRAM.san;TRAM.ok=true;TRAM.un=TRAM.FB().nghe(TRAM.sid,TRAM.lastT,(d,p,c)=>TRAM.nhan(d,p,c),()=>{})}")
        ok('C khác mã trạm với A', await C.evaluate("()=>TRAM.sid") != await A.evaluate("()=>TRAM.sid"))
        await C.evaluate(BAN, 'N4'); await C.evaluate(DAY)
        await A.wait_for_timeout(1500)
        ok('Khác chìa: A không thấy N4 qua trạm', await dem(A,'N4') == 0)
        await A.evaluate(GOP)
        ok('A gộp nhật ký → có N4, tồn 16', await dem(A,'N4') == 1 and await A.evaluate(SL) == 16, (await dem(A,'N4'), await A.evaluate(SL)))
        # 4) MÁY CHÍNH TẮT: A đóng app, B bán N5 → máy mới D mở thấy N5 (không cần A)
        await A.context.close()
        await B.evaluate(BAN, 'N5'); await B.evaluate(DAY)
        Dm = await mk('D')
        await Dm.evaluate(GOP)
        ok('Máy chính tắt: máy mới D vẫn thấy N5 (gộp nhật ký)', await doi(Dm, "()=>db.don.some(x=>x.ten==='N5')"))
        ok('D thấy đủ N1..N5, mỗi đơn 1 lần', all([await dem(Dm, 'N%d' % i) == 1 for i in range(1,6)]), [await dem(Dm, 'N%d' % i) for i in range(1,6)])
        ok('D tồn đúng 15', await Dm.evaluate(SL) == 15, await Dm.evaluate(SL))
        # 5) ĐƠN KẸT TRÊN MÁY (bán bản cũ, chưa từng gửi đi): E có đơn N6 nằm riêng trên máy → bản kê lần đầu đưa lên
        E = await mk('E')
        await doi(E, "()=>TRAM.ok")
        await E.evaluate("()=>{const h=db.hang.find(x=>x.ten==='Ốp test');h.sl-=1;db.don.push({id:'ket6',bill:'ket6',ngay:todayIso(),gio:'8:00',loai:'pk',hangId:h.id,ten:'N6',sl:1,giaBan:50000,giaVon:10000,tt:'Tiền mặt',huy:null});Store.save(db);localStorage.removeItem(NKD.kBF);TRAM.S=TRAM.anh()}")
        await E.evaluate("()=>{NKD.keBan()}"); await E.evaluate(DAY)
        await Dm.evaluate(GOP); await Dm.evaluate(GOP)
        ok('Đơn kẹt N6 trên E về D qua bản kê', await dem(Dm,'N6') == 1)
        ok('Bản kê trừ tồn đúng 1 lần: D tồn 14', await Dm.evaluate(SL) == 14, await Dm.evaluate(SL))
        # 6) SỔ TRÊN MÁY B MẤT SẠCH: mở lại → gộp nhật ký lấy lại cả đơn của chính B
        await B.evaluate("()=>{localStorage.removeItem(KEY);try{IDBS.del&&IDBS.del(KEY)}catch(_){}}")
        await B.reload(); await B.wait_for_timeout(4000); await B.evaluate(GOP)
        ok('B mất sổ trên máy: gộp lại đủ N1..N6', all([await dem(B, 'N%d' % i) >= 1 for i in range(1,7)]), [await dem(B, 'N%d' % i) for i in range(1,7)])
        # 7) gộp nhiều lần không đổi
        a = (await Dm.evaluate("()=>db.don.length"), await Dm.evaluate(SL)); await Dm.evaluate(GOP); await Dm.evaluate(GOP)
        ok('Gộp lặp lại không đổi gì', a == (await Dm.evaluate("()=>db.don.length"), await Dm.evaluate(SL)))
        # 8) thẻ ⚡ có dòng Drive + các máy
        t = await B.evaluate("()=>tramBar()")
        ok('Thẻ ⚡ hiện "📒 Drive" + các máy ghi nhật ký', '📒 Drive' in t or 'chờ lên Drive' in t, t[:300])
        ok('Không lỗi console', not errs, errs[:3])
        print(f'{sum(KQ)}/{len(KQ)}')

asyncio.run(main())
