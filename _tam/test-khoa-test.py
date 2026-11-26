# 26/11: máy đã đăng nhập Gmail shop → khoá giao diện test (tab Tài khoản test, Xem thử tiếp, ?demo=1, NV test)
import asyncio
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def mo(b,w,q,gg):
    ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*',h)
    if gg: await ctx.add_init_script("localStorage.setItem('shopgon_gg',JSON.stringify({email:'xuanthanh@gmail.com'}));localStorage.setItem('shopgon_owner','xuanthanh@gmail.com')")
    await pg.goto(URL+'/app/'+q); await pg.wait_for_timeout(1300); return ctx,pg,errs
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      # chưa đăng nhập: test vẫn mở được
      ctx,pg,errs=await mo(b,w,'?demo=1&test=1',False)
      ok(f'[{w}] Máy CHƯA đăng nhập Gmail: shop test vẫn mở', await pg.evaluate("DEMO&&TEST"))
      await ctx.close()
      # đã đăng nhập: ?demo=1 bị chặn
      ctx,pg,errs=await mo(b,w,'?demo=1&test=1',True)
      ok(f'[{w}] Đã đăng nhập Gmail: ?demo=1 không vào demo', await pg.evaluate("!DEMO&&!TEST"))
      ok(f'[{w}] Link được xoá ?demo=1', 'demo=1' not in pg.url, pg.url)
      await pg.evaluate("showLogin('xuanthanh@gmail.com')"); await pg.wait_for_timeout(200)
      t=await pg.evaluate("$('welcome').innerText")
      ok(f'[{w}] Màn đăng nhập không còn tab Tài khoản test', 'Tài khoản test' not in t and 'Vào shop test' not in t, t[:300])
      await pg.evaluate("LGTAB='test';showLogin()"); t=await pg.evaluate("$('welcome').innerText")
      ok(f'[{w}] Ép LGTAB=test vẫn không hiện shop test', 'Vào shop test' not in t)
      await pg.evaluate("XEM=true;showPending({status:'pending'})"); t=await pg.evaluate("$('welcome').innerText")
      ok(f'[{w}] Chờ kích hoạt: không có nút Xem thử tiếp', 'Xem thử tiếp' not in t, t[-200:])
      await pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.gg='test';b.id='tt';$('welcome').appendChild(b)})()")
      await pg.evaluate("document.getElementById('tt').click()"); await pg.wait_for_timeout(400)
      ok(f'[{w}] Bấm nút test (nếu còn sót) bị chặn', 'demo=1' not in pg.url)
      ok(f'[{w}] Không lỗi console', not errs, errs)
      await ctx.close()
      # NV test cũ trên máy chủ shop bị gỡ
      ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page()
      await pg.route('**/*',lambda r:r.continue_() if 'localhost' in r.request.url and 'ver.json' not in r.request.url else r.abort())
      await ctx.add_init_script("if(!sessionStorage.getItem('x')){sessionStorage.setItem('x',1);localStorage.setItem('shopgon_owner','xuanthanh@gmail.com');localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0900000000',ten:'Nhân viên test',phien:'TEST',test:1}))}")
      await pg.goto(URL+'/app/'); await pg.wait_for_timeout(1200)
      ok(f'[{w}] NV test cũ bị gỡ trên máy đã đăng nhập', await pg.evaluate("localStorage.getItem('shopgon_nv')") is None)
      await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
