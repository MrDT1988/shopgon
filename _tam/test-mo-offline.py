# Test 09/11 — LỚP 1: mất mạng vẫn MỞ được app, bán trên máy, có mạng lại tự lên Drive (Drive giả lập).
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-mo-offline.py
import asyncio, json, sys
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
D = Drive()
def tren_drive(x): return x in json.dumps([f['sheets'] for f in D.f.values()], ensure_ascii=False)
CHO = "async()=>{for(let i=0;i<60&&GG.busy;i++)await new Promise(r=>setTimeout(r,100))}"

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
        for ca, hetPhien in (('còn phiên Google', False), ('hết phiên Google', True)):
            ctx = await b.new_context(); await ctx.route('**/*', h); pg = await ctx.new_page(); E = pg.evaluate
            pg.on('pageerror', lambda e: errs.append(str(e)))
            MM = 'mat-mang-%d' % (2 if hetPhien else 1)
            mail = 'off%d@shopgon.vn' % (1 if not hetPhien else 2)
            await pg.goto(URL + '/khong-co')
            await E("m=>{localStorage.clear();localStorage.setItem('shopgon_gg',JSON.stringify({email:m}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:m,x:Date.now()+3e6}))}", mail)
            await pg.goto(URL + '/app/'); await pg.wait_for_timeout(4000)
            await E("async()=>{db.don.push({id:'co-mang',bill:'co-mang',ngay:todayIso(),gio:'9:00',loai:'pk',ten:'Ốp',sl:1,giaBan:100000,giaVon:30000,tt:'Tiền mặt',huy:null});save();clearTimeout(GG.timer)}")
            await E(CHO); await E("async()=>{clearTimeout(GG.timer);await GG.push()}"); await pg.wait_for_timeout(500)
            ok(f'[{ca}] Có mạng: đơn lên Drive', tren_drive('co-mang'))
            await E("()=>navigator.serviceWorker.ready.then(()=>1)"); await pg.reload(); await pg.wait_for_timeout(3500)
            ok(f'[{ca}] Service worker đang điều khiển trang', await E("()=>!!navigator.serviceWorker.controller"))
            # MẤT MẠNG — đóng app, mở lại
            await ctx.set_offline(True)
            if hetPhien: await E("m=>localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:m,x:Date.now()-1000}))", mail)
            try: await pg.goto(URL + '/app/'); mo = True
            except Exception as e: mo = False; print(e)
            await pg.wait_for_timeout(2500)
            ok(f'[{ca}] Mất mạng: app vẫn mở được', mo and await E("()=>typeof GG!=='undefined'"))
            st = await E("()=>({off:!!GG.OFF,xem:XEM,don:db.don.map(x=>x.id),khoa:document.body.classList.contains('locked'),the:!!document.querySelector('.chanb')&&document.querySelector('.chanb').textContent.includes('mất mạng')})")
            ok(f'[{ca}] Mở sổ trên máy (không khoá, không phải dữ liệu mẫu), thấy đơn cũ', st['off'] and not st['xem'] and not st['khoa'] and 'co-mang' in st['don'], st)
            ok(f'[{ca}] Trang chủ hiện thẻ "Đang mất mạng"', st['the'], st)
            await E("mm=>{db.don.push({id:mm,bill:mm,ngay:todayIso(),gio:'9:30',loai:'pk',ten:'Sạc',sl:1,giaBan:200000,giaVon:80000,tt:'Tiền mặt',huy:null});save()}", MM)
            await pg.wait_for_timeout(500)
            ok(f'[{ca}] Bán lúc mất mạng: đơn lưu trên máy, chưa lên Drive', not tren_drive(MM) and await E("mm=>Store.goc.don.some(x=>x.id===mm)", MM))
            # CÓ MẠNG LẠI
            await ctx.set_offline(False); await pg.wait_for_timeout(4000); await E(CHO)
            if not hetPhien:
                await E("async()=>{clearTimeout(GG.timer);if(GG.token)await GG.push()}"); await pg.wait_for_timeout(500)
                ok(f'[{ca}] Có mạng lại: tự đồng bộ, đơn mất mạng lên Drive', tren_drive(MM) and tren_drive('co-mang') and not await E("()=>GG.OFF"), await E("()=>[GG.OFF,!!GG.token]"))
            else:
                st2 = await E("()=>({off:!!GG.OFF,het:!!GG.het,don:db.don.map(x=>x.id)})")
                ok(f'[{ca}] Có mạng lại: hiện thẻ đỏ Đăng nhập lại, đơn vẫn trên máy', st2['het'] and not st2['off'] and MM in st2['don'], st2)
            await ctx.close()
        # máy CHƯA từng mở sổ (máy mới) mất mạng → không mở sổ giả, về màn đăng nhập
        ctx = await b.new_context(); await ctx.route('**/*', h); pg = await ctx.new_page()
        await pg.goto(URL + '/khong-co'); await pg.evaluate("()=>{localStorage.clear();localStorage.setItem('shopgon_gg',JSON.stringify({email:'moi@shopgon.vn'}))}")
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(2500); await ctx.set_offline(True)
        await pg.evaluate("()=>{GG.OFF=false;return moOffline({email:'moi@shopgon.vn'})}")
        ok('Máy chưa từng kích hoạt: không mở sổ offline', not await pg.evaluate("()=>!!GG.OFF"))
        await ctx.close()
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ)); sys.exit(0 if all(KQ) else 1)
asyncio.run(main())
