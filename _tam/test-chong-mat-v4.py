# Test chống mất v4 (09/11/2026): gộp từng ô khi 2 máy sửa cùng dòng + Nhật ký không sinh bia mộ/sửa giả sau đồng bộ.
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-chong-mat-v4.py
import asyncio, json
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
D = Drive(); GIO = {'v': ''}; HONG = {'clear': False}
_h0 = D.handle
def _h(method, url, body):
    if HONG['clear'] and ':batchClear' in url: raise KeyError('500 giả lập rớt mạng')
    r = _h0(method, url, body)
    if method == 'PATCH' and 'fields=modifiedTime' in url and GIO['v']: r = dict(r, modifiedTime=GIO['v'])
    return r
D.handle = _h
LOGIN = "()=>{localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}"
CHO = "while(GG.busy)await new Promise(r=>setTimeout(r,100));clearTimeout(GG.timer);"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def h(r):
            u = r.request.url
            if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
            if 'localhost' in u: return await r.continue_()
            if 'script.google.com' in u: return await r.fulfill(body='{"status":"active","shop":"Shop Test","ok":true}', content_type='application/json')
            if 'googleapis.com' in u:
                try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
                except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
            await r.abort()
        async def may():
            c = await b.new_context(); await c.route('**/*', h); pg = await c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL + '/khong-co'); await pg.evaluate(LOGIN); await pg.goto(URL + '/app/'); await pg.wait_for_timeout(4000); return c, pg
        # --- 1. gộp từng ô (gọi thẳng GG.merge) ---
        cA, A = await may()
        r = await A.evaluate("""()=>{const B={don:[{id:'d1',ngay:'2026-11-08',ten:'Ốp',giaBan:100000,note:'',huy:null}],may:[],hang:[{id:'h1',ten:'Cáp',sl:10,giaBan:50000}],pn:[],chi:[]};
          const L=JSON.parse(JSON.stringify(B)),R=JSON.parse(JSON.stringify(B));L.don[0].note='khách quen';R.don[0].huy='2026-11-08 10:00';
          L.hang[0].sl=8;R.hang[0].sl=9;R.hang[0].giaBan=60000;const m=GG.merge(B,L,R);return {d:m.don[0],h:m.hang[0]}}""")
        ok('2 máy sửa cùng 1 đơn (máy 1 ghi chú, máy 2 huỷ) → giữ CẢ HAI', r['d']['note'] == 'khách quen' and r['d']['huy'] == '2026-11-08 10:00', r['d'])
        ok('Phụ kiện: 2 máy cùng bán (10→8, 10→9) = 7, giữ giá máy 2 vừa đổi', r['h']['sl'] == 7 and r['h']['giaBan'] == 60000, r['h'])
        r = await A.evaluate("""()=>{const B={don:[],may:[],hang:[{id:'h1',ten:'Cáp',sl:10}],pn:[],chi:[]};
          const row={id:'nv-B9-0',bill:'B9',loai:'pk',hangId:'h1',sl:1,ngay:'2026-11-08',giaBan:50000,huy:null};
          const L={...B,don:[row],hang:[{id:'h1',ten:'Cáp',sl:8}]},R={...B,don:[{...row}],hang:[{id:'h1',ten:'Cáp',sl:9}]};
          const L1={...B,don:[{...row}],hang:[{id:'h1',ten:'Cáp',sl:9}]};
          const m2=GG.merge(B,L,R),m1=GG.merge(B,L1,B);return {n2:m2.don.length,s2:m2.hang[0].sl,n1:m1.don.length,s1:m1.hang[0].sl,goc:L.hang[0].sl}}""")
        ok('Đơn NV do 2 máy cùng nhận → 1 đơn, phụ kiện chỉ trừ 1 lần', r['n2'] == 1 and r['s2'] == 8 and r['goc'] == 8, r)  # máy 1: NV + tự bán 1 (10→8), máy 2: NV (10→9) → đúng = 8
        ok('Đơn NV chỉ 1 máy nhận → 1 đơn, 10→9', r['n1'] == 1 and r['s1'] == 9, r)
        r = await A.evaluate("()=>[GG.cuRa('Don',{ngay:'2024-01-05',no:500000}),GG.cuRa('Don',{ngay:'2024-01-05',tgTT:'Chờ duyệt'}),GG.cuRa('Phieu',{ngay:'2024-01-05',no:1}),GG.cuRa('Don',{ngay:'2024-01-05'})]")
        ok('Đơn cũ >12 tháng còn nợ / trả góp chờ / phiếu nợ NCC: KHÔNG bao giờ bị bỏ', r == [False, False, False, True], r)
        # --- xoá đơn rồi rớt mạng ngay sau khi ghi (bước xoá đuôi lỗi) → Drive không còn dòng đã xoá
        await A.evaluate("async()=>{" + CHO + "db.don.push({id:'z1',bill:'z1',ngay:todayIso(),gio:'8:00',loai:'pk',ten:'Ốp xoá',sl:1,giaBan:1,giaVon:1,tt:'Tiền mặt',huy:null});save();" + CHO + "await GG.push()}")
        HONG['clear'] = True
        await A.evaluate("async()=>{" + CHO + "db.don=db.don.filter(x=>x.id!=='z1');save();" + CHO + "await GG.push()}")
        HONG['clear'] = False
        ok('Xoá đơn + mạng rớt ở bước xoá đuôi: Drive không còn đơn đã xoá', 'z1' not in json.dumps([{k: v for k, v in f['sheets'].items() if k != 'Nhật ký'} for f in D.f.values() if f['ap'].get('nam')], ensure_ascii=False))
        # --- 2. Nhật ký không ghi nhầm thay đổi của máy khác ---
        await A.evaluate("async()=>{db.don.push({id:'x1',bill:'x1',ngay:todayIso(),gio:'9:00',loai:'pk',ten:'Ốp',sl:1,giaBan:100000,giaVon:30000,tt:'Tiền mặt',huy:null});save();" + CHO + "await GG.push()}")
        cB, B2 = await may()
        await B2.evaluate("async()=>{" + CHO + "const d=db.don.find(x=>x.id==='x1');d.giaBan=150000;save();" + CHO + "await GG.push()}")
        await cB.close()
        # máy 1 VẪN MỞ (không tải lại): bán 1 món → đồng bộ kéo sửa của máy 2 về → bán tiếp
        await A.evaluate("async()=>{" + CHO + "db.hang.push({id:'p1',ten:'Dán',nhom:'pk',sl:5,giaBan:50000});save();" + CHO + "await GG.push()}")
        n = await A.evaluate("async()=>{" + CHO + "const g=db.don.find(x=>x.id==='x1').giaBan;db.don.push({id:'x2',bill:'x2',ngay:todayIso(),gio:'9:30',loai:'pk',ten:'Sạc',sl:1,giaBan:200000,giaVon:80000,tt:'Tiền mặt',huy:null});save();return {g,nk:(db.nk||[]).map(x=>x.viec+'|'+(x.xk?'xk':''))}}")
        ok('Máy 1 (đang mở) nhận giá máy 2 đã sửa (150k)', n['g'] == 150000, n)
        ok('Máy 1 bán tiếp: Nhật ký KHÔNG ghi nhầm "Sửa đơn" của máy 2 lên máy 1', sum(1 for x in n['nk'] if x.startswith('Sửa đơn')) <= 1, n['nk'])
        ok('Không sinh bia mộ (xk) giả (chỉ 1 bia của đơn z1 đã xoá thật)', sum(1 for x in n['nk'] if x.endswith('|xk')) == 1, n['nk'])
        # --- máy khác ghi chen làm mất đơn của máy 1 trên Drive → 20 giây sau máy 1 tự ghi bù
        await A.evaluate("async()=>{" + CHO + "db.don.push({id:'w1',bill:'w1',ngay:todayIso(),gio:'10:00',loai:'pk',ten:'Ốp chen',sl:1,giaBan:1,giaVon:1,tt:'Tiền mặt',huy:null});save();" + CHO + "await GG.push()}")
        for f in D.f.values():
            if f['ap'].get('nam') == '2026':
                for k, rows in f['sheets'].items():
                    if k != 'Nhật ký': f['sheets'][k] = [r for r in rows if 'w1' not in r]
        thang = lambda x: x in json.dumps([{k: v for k, v in f['sheets'].items() if k != 'Nhật ký'} for f in D.f.values() if f['ap'].get('nam')], ensure_ascii=False)
        ok('(giả lập) máy khác ghi đè làm mất đơn w1 trên Drive', not thang('w1'))
        await A.wait_for_timeout(23000)
        await A.evaluate("async()=>{" + CHO + "}")
        ok('20 giây sau máy 1 tự đọc lại và ghi bù đơn w1 lên Drive', thang('w1'))
        # --- 2 tab cùng máy: tab cũ dừng ghi
        A2 = await cA.new_page(); await A2.goto(URL + '/app/'); await A2.wait_for_timeout(3000)
        t = await A.evaluate("()=>[TAB_DONG,document.body.innerText.slice(0,80)]")
        ok('Mở tab thứ 2: tab cũ tạm dừng, không ghi đè', t[0] is True and 'mở ở chỗ khác' in t[1], t)
        await A2.close(); await A.goto(URL + '/app/'); await A.wait_for_timeout(5000)
        # --- 3. Giờ máy nhảy sang năm sau, máy chủ Google vẫn 2026 → KHÔNG chốt sổ
        GIO['v'] = '2026-11-09T01:00:00.000Z'
        await A.evaluate("""(()=>{const _D=Date,off=new _D('2027-01-02T09:00:00').getTime()-_D.now();class FD extends _D{constructor(...a){super(...(a.length?a:[_D.now()+off]))}static now(){return _D.now()+off}};window.Date=FD})()""")
        r = await A.evaluate("async()=>{" + CHO + "GG._gio=null;await GG.push();return {nam:GG.nam,files:Object.keys(GG.files),sai:GG.gioSai||''}}")
        ok('Giờ máy sai (2027) nhưng Google báo 2026 → không mở sổ 2027, giữ sổ 2026', r['nam'] == 2026 and '2027' not in r['files'] and r['sai'], r)
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ))
asyncio.run(main())
