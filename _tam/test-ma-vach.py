# Test mã vạch phụ kiện. Chạy: python3 -m http.server 8765 ở gốc repo (cần pip zxing-cpp pillow)
import asyncio, json, io
from playwright.async_api import async_playwright
import zxingcpp
from PIL import Image
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
      async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
      await pg.route('**/*',h); await pg.goto(URL+'/app/?demo=1'); await pg.wait_for_timeout(1200); E=pg.evaluate
      await E("khoHub=true;go('stock')"); await pg.wait_for_timeout(150)
      ok(f'[{w}] Kho hàng có mục Mã vạch phụ kiện', await pg.locator('[data-more="mv"]').count()==1)
      await E("document.querySelector('[data-more=\"mv\"]').click()"); await pg.wait_for_timeout(200)
      await E("document.querySelector('[data-mvtao]').click()"); await pg.wait_for_timeout(150)
      ok(f'[{w}] Tạo mã: mọi món có mã SG, không trùng', await E("(()=>{const L=db.hang.filter(h=>h.nhom!=='km');return L.every(h=>/^SG\\d{6}$/.test(h.ma))&&new Set(L.map(h=>h.ma)).size===L.length})()"))
      hid,ma=json.loads(await E("JSON.stringify((h=>[h.id,h.ma])(db.hang.find(h=>h.sl>2&&h.giaBan&&h.nhom!=='km')))"))
      for _ in range(3): await E(f"document.querySelector('[data-mvinc=\"{hid}\"]').click()")
      await pg.wait_for_timeout(100)
      ok(f'[{w}] Nút In 3 tem', '3 tem' in await E("document.querySelector('[data-mvin]').textContent"))
      await pg.screenshot(path=f'/tmp/mv_{w}.png',full_page=True)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang', W<=w+2, W)
      # giải mã mã vạch bằng zxing
      await E(f"document.body.insertAdjacentHTML('beforeend','<div id=\"bct\" style=\"position:fixed;left:0;top:0;width:360px;height:110px;background:#fff;z-index:99999;padding:10px\">'+mvSvg('{ma}',50).replace('<svg','<svg style=\"width:340px;height:90px\"')+'</div>')")
      img=Image.open(io.BytesIO(await pg.locator('#bct').screenshot()))
      res=zxingcpp.read_barcodes(img); got=[r.text for r in res]
      ok(f'[{w}] Mã vạch in ra đọc lại đúng {ma} (Code128)', ma in got, got)
      await E("document.getElementById('bct').remove()")
      # in tem: iframe có 3 tem
      await E("window.print=()=>{};document.querySelector('[data-mvin]').click()"); await pg.wait_for_timeout(500)
      n=await E("(f=>f?f.contentWindow.document.querySelectorAll('.t').length:0)(document.getElementById('mvFrame'))")
      ok(f'[{w}] Trang in có 3 tem', n==3, n)
      # bán: gõ/quét mã ở ô phụ kiện → vào đơn
      await E("go('sell');sellMode='pk';cart=[];render()"); await pg.wait_for_timeout(150)
      await pg.fill('#pQ', ma); await pg.wait_for_timeout(200)
      q=await E(f"cart.filter(c=>c.hangId==='{hid}').reduce((s,c)=>s+c.sl,0)")
      ok(f'[{w}] Quét mã ở ô phụ kiện → món vào đơn', q==1, q)
      # máy quét cầm tay ở ô tìm máy: gõ mã + Enter
      await E("sellMode='may';render()"); await pg.wait_for_timeout(100)
      await pg.fill('#sImei', ma); await pg.wait_for_timeout(200)
      q=await E(f"cart.filter(c=>c.hangId==='{hid}').reduce((s,c)=>s+c.sl,0)")
      ok(f'[{w}] Quét mã ở ô tìm máy → cộng thêm 1', q==2, q)
      ok(f'[{w}] Ô tìm được xoá sau khi quét', await E("($('sImei')||{value:''}).value===''"))
      # mã trùng bị chặn khi sửa mã
      h2=await E(f"db.hang.find(h=>h.id!=='{hid}'&&h.nhom!=='km').id")
      await E(f"more='mv';MV.sua='{h2}';go('more')"); await pg.wait_for_timeout(150)
      await pg.fill('#mvMa', ma); await E(f"document.querySelector('[data-mvluu=\"{h2}\"]').click()"); await pg.wait_for_timeout(150)
      ok(f'[{w}] Sửa mã trùng món khác → bị chặn', await E(f"db.hang.find(h=>h.id==='{h2}').ma")!=ma)
      # gửi NV: tồn có mã
      ok(f'[{w}] Không lỗi console', not errs, errs)
      await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
