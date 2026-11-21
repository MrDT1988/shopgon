# Test thanh '⏳ đơn chưa lên Drive' (21/11/2026): Drive lỗi → thanh hiện ở Bán + Trang chủ, đếm đúng đơn; bấm Lưu ngay → lên Drive, thanh tắt.
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-cho-drive.py
import asyncio, json
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
D = Drive(); HONG = {'loi': False}; GUI = []
_h0 = D.handle
def _h(method, url, body):
    if HONG['loi'] and 'values:batchUpdate' in url: raise KeyError('500 giả lập')
    return _h0(method, url, body)
D.handle = _h
LOGIN = "()=>{localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}"
CHO = "while(GG.busy)await new Promise(r=>setTimeout(r,100));clearTimeout(GG.timer);"
def tren_drive(x):
    return x in json.dumps([{k: v for k, v in f['sheets'].items() if k != 'Nhật ký'} for f in D.f.values() if f['ap'].get('nam')], ensure_ascii=False)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def h(r):
            u = r.request.url
            if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
            if 'localhost' in u: return await r.continue_()
            if 'script.google.com' in u:
                try:
                    o = json.loads(r.request.post_data or '{}')
                    if o.get('act') == 'sk': GUI.append(o)
                except Exception: pass
                return await r.fulfill(body='{"status":"active","shop":"Shop Test","ok":true}', content_type='application/json')
            if 'googleapis.com' in u:
                try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
                except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
            await r.abort()
        c = await b.new_context(); await c.route('**/*', h); A = await c.new_page(); A.on('pageerror', lambda e: errs.append(str(e)))
        await A.goto(URL + '/khong-co'); await A.evaluate(LOGIN); await A.goto(URL + '/app/'); await A.wait_for_timeout(4000)
        await A.evaluate("async()=>{" + CHO + "await GG.push()}")
        ok('Bình thường: không có thanh chờ', await A.evaluate("()=>choBar()===''"))
        HONG['loi'] = True
        await A.evaluate("async()=>{" + CHO + "for(const k of ['x1','x2']){const id=Date.now().toString(36)+k;db.don.push({id,bill:id,ngay:todayIso(),gio:'21:00',loai:'pk',ten:'Ốp '+k,sl:1,giaBan:1,giaVon:1,tt:'Tiền mặt',huy:null})}save();" + CHO + "await GG.push();clearTimeout(GG.timer)}")
        ok('Mới chờ <1 phút: chưa hiện (tránh nháy mỗi lần bán)', await A.evaluate("()=>choBar()===''"))
        await A.evaluate("()=>{const o=SK.get();o.cho=Date.now()-75*6e4;SK.luu();view='sell';render()}")
        t = await A.evaluate("()=>[...document.querySelectorAll('#v-sell .choBar')].map(e=>e.innerText).join('|')")
        ok('Màn Bán hiện thanh: 2 đơn chưa lên Drive, 1 giờ 15 phút, màu đỏ', 'Còn 2 đơn chưa lên Google Drive' in t and '1 giờ 15 phút' in t and await A.evaluate("()=>!!document.querySelector('#v-sell .choBar .alert.red')"), t)
        await A.evaluate("()=>{view='home';render()}")
        t2 = await A.evaluate("()=>[...document.querySelectorAll('#v-home .choBar')].map(e=>e.innerText).join('|')")
        ok('Trang chủ cũng hiện thanh', 'chưa lên Google Drive' in t2, t2)
        await A.evaluate("()=>{GG.het=true;choVe()}")
        ok('Hết phiên Google → thanh có nút Đăng nhập lại', await A.evaluate("()=>!!document.querySelector('#v-home .choBar [data-gg=login]')"))
        await A.evaluate("()=>{GG.het=false;choVe()}")
        HONG['loi'] = False
        await A.click('#v-home .choBar [data-choluu]'); await A.wait_for_timeout(2500)
        await A.evaluate("async()=>{" + CHO + "}")
        ok('Bấm Lưu ngay → đơn lên Drive', tren_drive('Ốp x1') and tren_drive('Ốp x2'))
        ok('Lưu xong → thanh tự tắt, không cần mở lại app', await A.evaluate("()=>SK.get().cho===0&&[...document.querySelectorAll('.choBar')].every(e=>e.innerHTML==='')"))
        await A.evaluate("()=>{NV={ten:'NV',sdt:'1'};const o=SK.get();o.cho=Date.now()-9e6}")
        ok('Máy nhân viên không hiện thanh', await A.evaluate("()=>choBar()===''"))
        await A.evaluate("()=>{NV=null;SK.get().cho=0}")
        for w in (320, 360, 412):
            await A.set_viewport_size({'width': w, 'height': 800})
            await A.evaluate("()=>{const o=SK.get();o.cho=Date.now()-5*6e4;view='sell';render()}")
            ok(f'{w}px: thanh không tràn ngang', await A.evaluate("()=>document.documentElement.scrollWidth<=innerWidth+1"))
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ))
asyncio.run(main())
