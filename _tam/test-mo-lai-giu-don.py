# Test 09/11: MỞ LẠI APP không mất đơn chưa kịp lên Drive (Drive giả lập, không đụng tài khoản thật).
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-mo-lai-giu-don.py
import asyncio, json, re, sys
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])   # lấy lớp Drive giả lập dùng chung
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
D = Drive(); LOG = []
def tren_drive(x): return x in json.dumps([f['sheets'] for f in D.f.values()], ensure_ascii=False)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        async def h(r):
            u = r.request.url
            if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
            if 'localhost' in u: return await r.continue_()
            if 'script.google.com' in u: return await r.fulfill(body='{"status":"active","shop":"Shop Test","ok":true}', content_type='application/json')
            if 'googleapis.com' in u:
                LOG.append(r.request.method+' '+u.split('?')[0][-70:])
                try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
                except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
            await r.abort()
        await ctx.route('**/*', h)
        await pg.goto(URL + '/khong-co'); E = pg.evaluate
        await E("()=>{localStorage.clear();localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}")
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(4000)
        st = await E("()=>[XEM,!!GG.sheetId,GG.email]")
        ok('Lần đầu: đăng nhập + tạo sổ trên Drive', st[0] is False and st[1], st)
        # bán đơn 1 → lên Drive
        await E("async()=>{db.don.push({id:'da-len',bill:'da-len',ngay:todayIso(),gio:'9:00',loai:'pk',ten:'Ốp',sl:1,giaBan:100000,giaVon:30000,tt:'Tiền mặt',huy:null});save();while(GG.busy)await new Promise(r=>setTimeout(r,100));clearTimeout(GG.timer);await GG.push()}")
        await pg.wait_for_timeout(800)
        ok('Đơn 1 đã lên Drive', tren_drive('da-len'))
        # bán đơn 2 rồi TẮT APP trước khi kịp lên Drive (chưa hết 2,5 giây / mất mạng)
        await E("()=>{db.don.push({id:'chua-len',bill:'chua-len',ngay:todayIso(),gio:'9:05',loai:'pk',ten:'Sạc',sl:1,giaBan:200000,giaVon:80000,tt:'Tiền mặt',huy:null});save();clearTimeout(GG.timer)}")
        ok('Đơn 2 chưa lên Drive (giả lập tắt app)', not tren_drive('chua-len'))
        # máy khác (máy 2, cùng Gmail) bán đơn 3 lên Drive trong lúc máy 1 tắt
        ctx2 = await b.new_context(); await ctx2.route('**/*', h); p2 = await ctx2.new_page()
        await p2.goto(URL + '/khong-co')
        await p2.evaluate("()=>{localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}")
        await p2.goto(URL + '/app/'); await p2.wait_for_timeout(4000)
        await p2.evaluate("async()=>{while(GG.busy)await new Promise(r=>setTimeout(r,100));db.don.push({id:'may-khac',bill:'may-khac',ngay:todayIso(),gio:'9:10',loai:'pk',ten:'Cáp',sl:1,giaBan:50000,giaVon:20000,tt:'Tiền mặt',huy:null});save();clearTimeout(GG.timer);await GG.push()}")
        ok('Máy 2 bán đơn 3 lên Drive', tren_drive('may-khac'))
        await ctx2.close()
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(5000)
        ds = await E("()=>[XEM,db.don.map(x=>x.id)]")
        ok('Mở lại app: đơn 2 (chưa lên Drive) vẫn còn trên máy', 'chua-len' in ds[1] and 'da-len' in ds[1], ds)
        await E("async()=>{while(GG.busy)await new Promise(r=>setTimeout(r,100));clearTimeout(GG.timer);await GG.push()}"); await pg.wait_for_timeout(800)
        ok('Mở lại app: đơn 2 được gộp và ghi lên Drive, giữ đơn máy 2', tren_drive('chua-len') and tren_drive('da-len') and tren_drive('may-khac'))
        ds2 = await E("()=>db.don.map(x=>x.id).sort()")
        ok('Máy 1 sau gộp có đủ 3 đơn, không trùng', ds2 == ['chua-len', 'da-len', 'may-khac'], ds2)
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ))
asyncio.run(main())
