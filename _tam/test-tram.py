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
        await A.evaluate("async()=>{" + CHO + "db.hang.push({id:'h1',ten:'Ốp test',nhom:'pk',sl:10,giaNhap:10000,giaBan:50000,ngayNhap:todayIso()});db.may.push({imei:'351111111111111',ten:'OPPO Test',hang:'OPPO',giaNhap:1,giaBan:2,ngayNhap:todayIso(),tt:'ton'});save();" + CHO + "await GG.push()}")
        B = await mk('B')
        ok('B (trước khi bật trạm) thấy hàng của A qua Drive', await B.evaluate(SL) == 10, await B.evaluate(SL))
        # A bật trạm
        await A.evaluate("async()=>{await TRAM.batMoi()}")
        ok('A bật trạm: là máy chính, có chìa trong Drive shop, trạm nối', await A.evaluate("()=>TRAM.chinh()&&TRAM.ok&&!!TRAM.sid") and any(f['ap'].get('shopgon') == 'chia' for f in D.f.values()))
        await B.reload(); await B.wait_for_timeout(3500)
        ok('B mở lại: tự lấy chìa từ Drive, chạy trạm, là máy phụ', await doi(B, "()=>TRAM.ok&&!TRAM.chinh()&&TRAM.sid===%s" % json.dumps(await A.evaluate("()=>TRAM.sid"))))
        g0 = GHI_DRIVE.get('B', 0)
        # 1) 2 máy cùng bán 1 phụ kiện
        await asyncio.gather(A.evaluate(BAN, 'Ốp A1'), B.evaluate(BAN, 'Ốp B1'))
        t1 = time.time()
        ok('Tiêu chí 1: A và B cùng bán → cả 2 máy tồn = 8 (trừ đúng 2)', await doi(A, SL + "()===8".replace('()', '', 0) if False else "()=>(" + SL + ")()===8") and await doi(B, "()=>(" + SL + ")()===8"), [await A.evaluate(SL), await B.evaluate(SL)])
        ok('Đơn của B sang A trong ≤10 giây', await doi(A, "()=>db.don.some(x=>x.ten==='Ốp B1')", 10), round(time.time() - t1, 1))
        await A.evaluate("async()=>{" + CHO + "await GG.push()}"); await A.wait_for_timeout(500)
        r = drive_hang('Ốp test')
        ok('Drive (máy chính ghi): tồn Ốp test = 8, có cả 2 đơn', r is not None and '8' in r and drive_has('Ốp A1') and drive_has('Ốp B1'), r)
        # 2) B mất mạng bán 5 đơn, tắt app mở lại vẫn còn, có mạng → A thấy
        OFF.add('B')
        for i in range(5): await B.evaluate(BAN, 'Ốp OFF%d' % i)
        await B.wait_for_timeout(500)
        ok('B mất mạng: 5 lô nằm hàng chờ trên máy', await B.evaluate("()=>TRAM.choGui") >= 1, await B.evaluate("()=>TRAM.choGui"))
        await B.reload(); await B.wait_for_timeout(3000)
        ok('Tiêu chí 2a: tắt app mở lại (vẫn mất mạng) còn đủ 5 đơn', await B.evaluate("()=>db.don.filter(x=>/Ốp OFF/.test(x.ten)).length") == 5, await B.evaluate("()=>db.don.length"))
        OFF.discard('B'); t2 = time.time()
        await B.reload(); await B.wait_for_timeout(1000)
        ok('Tiêu chí 2b: có mạng → A nhận đủ 5 đơn ≤10 giây', await doi(A, "()=>db.don.filter(x=>/Ốp OFF/.test(x.ten)).length===5", 12), round(time.time() - t2, 1))
        ok('Tồn sau 7 lần bán = 3 trên cả 2 máy', await doi(A, "()=>(" + SL + ")()===3") and await doi(B, "()=>(" + SL + ")()===3"), [await A.evaluate(SL), await B.evaluate(SL)])
        ok('B hết hàng chờ sau khi có mạng', await doi(B, "()=>TRAM.choGui===0"), await B.evaluate("()=>TRAM.choGui"))
        # 3) B hết phiên Google cả ngày: mở app không cần đăng nhập, vẫn bán + đồng bộ
        await B.evaluate("()=>{localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()-1000}))}")
        await B.reload(); await B.wait_for_timeout(3500)
        ok('Tiêu chí 3a: hết phiên Google → B vẫn vào app (không màn đăng nhập), trạm chạy', await B.evaluate("()=>!GG.token&&TRAM.ok&&!document.body.classList.contains('locked')") , await B.evaluate("()=>({tk:!!GG.token,ok:TRAM.ok,loi:TRAM.loi})"))
        await B.evaluate(BAN, 'Ốp HETPHIEN')
        ok('Tiêu chí 3b: đơn bán lúc hết phiên sang A', await doi(A, "()=>db.don.some(x=>x.ten==='Ốp HETPHIEN')"))
        ok('B (máy phụ) KHÔNG ghi Drive lần nào sau khi bật trạm', GHI_DRIVE.get('B', 0) == g0, (g0, GHI_DRIVE.get('B', 0)))
        # 4) máy mới C: lấy Drive + phát lại lô sau mốc, không cộng trùng tồn
        await A.evaluate("async()=>{" + CHO + "await GG.push()}"); await A.wait_for_timeout(300)
        await B.evaluate(BAN, 'Ốp SAUMOC')   # lô sau mốc tramT (chưa vào Drive)
        await A.wait_for_timeout(300)
        C = await mk('C')
        ok('Tiêu chí 4a: máy mới C về đủ đơn (Drive + lô sau mốc)', await doi(C, "()=>TRAM.ok&&db.don.some(x=>x.ten==='Ốp SAUMOC')&&db.don.filter(x=>/Ốp OFF/.test(x.ten)).length===5"), await C.evaluate("()=>({ok:TRAM.ok,n:db.don.length,loi:TRAM.loi})"))
        ok('Tiêu chí 4b: C tồn = A = B (không cộng trùng)', await doi(C, "()=>(" + SL + ")()===%d" % (await A.evaluate(SL))) and await A.evaluate(SL) == await B.evaluate(SL) == 1, [await A.evaluate(SL), await B.evaluate(SL), await C.evaluate(SL)])
        # 5) trạm chỉ thấy chuỗi khoá
        raw = json.dumps(TRAM, ensure_ascii=False)
        ok('Tiêu chí 5: trên trạm không có chữ nào của shop (tên hàng, IMEI, giá)', 'Ốp' not in raw and '351111111111111' not in raw and '50000' not in raw and 'OPPO' not in raw)
        # 6) đối soát: Drive = mọi máy
        await A.evaluate("async()=>{" + CHO + "await GG.push()}"); await A.wait_for_timeout(500)
        nA = await A.evaluate("()=>db.don.length"); nB = await B.evaluate("()=>db.don.length"); nC = await C.evaluate("()=>db.don.length")
        ok('Tiêu chí 6: số đơn A = B = C và Drive có đủ', nA == nB == nC and all(drive_has(x) for x in ['Ốp A1', 'Ốp B1', 'Ốp OFF4', 'Ốp HETPHIEN', 'Ốp SAUMOC']), (nA, nB, nC))
        # 7) đổi máy chính sang B: A thôi ghi Drive, B ghi, không mất/không cộng trùng
        await B.evaluate("()=>{localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}));GG.token='t'}")
        await B.evaluate("async()=>{await TRAM.lamChinh()}")
        ok('Đổi máy chính: B là máy chính, A biết mình là máy phụ', await doi(A, "()=>!TRAM.chinh()") and await B.evaluate("()=>TRAM.chinh()"))
        gA = GHI_DRIVE.get('A', 0)
        await A.evaluate(BAN, 'Ốp SAUDOI')
        ok('Sau đổi: đơn A sang B, B lưu Drive, tồn Drive đúng', await doi(B, "()=>db.don.some(x=>x.ten==='Ốp SAUDOI')") and await doi(B, "async()=>{" + CHO + "await GG.push();return true}") and drive_has('Ốp SAUDOI'))
        await A.wait_for_timeout(3000)
        ok('Sau đổi: A không ghi Drive nữa', GHI_DRIVE.get('A', 0) == gA, (gA, GHI_DRIVE.get('A', 0)))
        r = drive_hang('Ốp test'); slA = await A.evaluate(SL)
        ok('Tồn trên Drive = tồn trên máy (%s)' % slA, r is not None and (r[4] or '0') == str(slA), r)
        # 8) MÁY PG: quét QR, bán → máy chính nhận qua trạm, trừ tồn 1 lần, máy phụ thấy; PG không có chìa shop
        await B.evaluate("()=>{db.shop.nv=[{sdt:'0901',ten:'PG A'}];save()}")
        await doi(A, "()=>(db.shop.nv||[]).length===1")
        qr = await B.evaluate("()=>TRAM.qrNv()")
        ok('Máy chính có mã QR cho PG (chỉ khoá công khai)', '#nvtram=' in qr and len(qr) < 1200, len(qr))
        N = await mk('N')
        await N.evaluate("()=>{localStorage.clear();localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0901',ten:'PG A',phien:'p1'}))}")
        await N.goto(URL + '/khong-co'); await N.goto(qr); await N.wait_for_timeout(3000)
        ok('PG quét QR: máy PG đã nối trạm, KHÔNG có chìa của shop', await N.evaluate("()=>NVT.coNoi()&&!localStorage.getItem('sg_tram_k')&&!!NV"), await N.evaluate("()=>({noi:NVT.coNoi(),nv:!!NV})"))
        s0 = await B.evaluate(SL)
        await N.evaluate("async()=>{await NVT.gui({id:'pgbill1',ngay:todayIso(),gio:'10:00',tt:'Tiền mặt',khach:'',lines:[{loai:'pk',hangId:'h1',ten:'Ốp PG1',sl:1,giaBan:50000,giaVon:0}],nv:'0901',nvTen:'PG A'})}")
        ok('Đơn PG đến máy chính ≤10 giây', await doi(B, "()=>db.don.some(x=>x.bill==='pgbill1')", 10))
        ok('Tồn trừ đúng 1 trên máy chính và máy phụ', await doi(B, "()=>(" + SL + ")()===%d" % (s0 - 1)) and await doi(A, "()=>(" + SL + ")()===%d" % (s0 - 1)), [await A.evaluate(SL), await B.evaluate(SL)])
        ok('PG hết hàng chờ (trạm đã nhận)', await doi(N, "()=>NVT.q().length===0"))
        await N.evaluate("async()=>{await NVT.gui({id:'pgbill1',ngay:todayIso(),gio:'10:00',tt:'Tiền mặt',lines:[{loai:'pk',hangId:'h1',ten:'Ốp PG1',sl:1,giaBan:50000}],nv:'0901'})}")
        await N.wait_for_timeout(2000)
        ok('Gửi lại cùng đơn PG không thành 2 đơn', await B.evaluate("()=>db.don.filter(x=>x.bill==='pgbill1').length") == 1 and await B.evaluate(SL) == s0 - 1)
        await N.evaluate("async()=>{await NVT.gui({id:'pgla',ngay:todayIso(),lines:[{loai:'pk',hangId:'h1',ten:'Ốp LA',sl:1,giaBan:1}],nv:'0999'})}")
        await N.wait_for_timeout(2500)
        ok('Đơn của số PG không có trong danh sách bị bỏ', not await B.evaluate("()=>db.don.some(x=>x.bill==='pgla')"))
        raw = json.dumps(TRAM, ensure_ascii=False)
        ok('Đơn PG trên trạm cũng chỉ là chuỗi khoá', 'Ốp PG1' not in raw and '0901' not in raw.replace('nv-0901', ''))
        N2 = await mk('N2')
        await N2.evaluate("()=>{localStorage.clear();localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0901',ten:'PG A',phien:'p1'}))}"); await N2.reload(); await N2.wait_for_timeout(2500)
        ok('PG chưa nối: Trang chủ PG có nút Quét mã QR trong app', await N2.evaluate("()=>!NVT.coNoi()&&NVT.the().includes('data-nvquet')"))
        ok('Đọc mã QR quét trong app → nối trạm', await N2.evaluate("(q)=>NVT.docChuoi(q)&&NVT.coNoi()", qr))
        # 9) iPhone mở bằng Safari: chặn bán
        ci = await b.new_context(user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')
        await ci.route('**/*', lambda r: r.continue_() if 'localhost' in r.request.url else r.abort())
        I = await ci.new_page(); await I.goto(URL + '/app/'); await I.wait_for_timeout(2000)
        ok('iPhone Safari chưa đăng nhập: chưa chặn (còn xem giới thiệu được)', await I.evaluate("()=>typeof iosChuaCai==='function'&&!iosChuaCai()&&INST.ios()"))
        await I.evaluate("()=>{GG.email='a@b.c'}")
        ok('iPhone Safari chưa cài, shop thật: chặn bán + hiện hướng dẫn cài', await I.evaluate("()=>iosChuaCai()&&iosBar().includes('Thêm vào MH chính')"))
        ok('Không lỗi JavaScript', not errs, errs[:5])
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ))
asyncio.run(main())
