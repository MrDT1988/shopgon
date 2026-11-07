# 07/11 21h: Trang chủ chủ shop — Nhân viên + Tổng kết lãi mặc định thu gọn, bấm mới mở
import asyncio,sys,os
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2);errs=[];ok=0
    pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1800)
    await pg.evaluate("homeD='today';go('home');scrollTo(0,0)");await pg.wait_for_timeout(300)
    g=await pg.evaluate("[document.querySelectorAll('.hgon').length,document.querySelectorAll('.hnvr,.hlr').length,/lãi \\d|Lãi cửa hàng/.test(document.querySelector('.hnv').textContent+document.querySelector('.hlp').textContent)]")
    print('gọn mặc định',g); ok+= g[0]==2 and g[1]==0 and not g[2]
    await pg.screenshot(path=os.path.join(OUT,'home_gon.png'),full_page=True)
    await pg.click('[data-hshow=nv]');await pg.click('[data-hshow=lai]');await pg.wait_for_timeout(300)
    m=await pg.evaluate("[document.querySelectorAll('.hnvr').length>0,document.querySelectorAll('.hlr').length>0]")
    print('bấm mở',m); ok+=all(m)
    await pg.click('.hnv button.hnvr:not(:disabled)');await pg.wait_for_timeout(200)
    print('bấm NV ra chi tiết',await pg.evaluate("document.querySelectorAll('.hnv .hld').length>0"))
    await pg.screenshot(path=os.path.join(OUT,'home_mo.png'),full_page=True)
    await pg.click('[data-hshow=nv]');await pg.wait_for_timeout(200)
    c=await pg.evaluate("document.querySelectorAll('.hnvr').length"); print('thu gọn lại',c==0); ok+= c==0
    await pg.evaluate("go('rpt')");await pg.click('[data-rm=thang]');await pg.select_option('#rThang',await pg.evaluate("monthsList()[0]"));await pg.wait_for_timeout(300)
    r=await pg.evaluate("document.querySelectorAll('#v-rpt .hlr').length>0"); print('Báo cáo tháng vẫn mở sẵn',r); ok+=r
    print('KẾT QUẢ',f'{ok}/4','errs',errs); await b.close()
asyncio.run(main())
