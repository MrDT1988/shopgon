import asyncio,sys,os
from playwright.async_api import async_playwright
W=int(sys.argv[1]) if len(sys.argv)>1 else 390
S=f'/tmp/claude-0/-home-claude/912e7d6c-97d1-5634-b470-4e79346b25d7/scratchpad/bc4_{W}/';os.makedirs(S,exist_ok=True)
HIDE="document.querySelectorAll('body *').forEach(e=>{const c=getComputedStyle(e);if(c.position==='fixed'||c.position==='sticky')e.style.display='none'})"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':W,'height':844},device_scale_factor=2);errs=[]
    pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(2000)
    await pg.evaluate("go('rpt');scrollTo(0,0)");await pg.wait_for_timeout(400)
    print('tabs',await pg.evaluate("[...document.querySelectorAll('#v-rpt [data-rt]')].map(b=>b.textContent)"))
    await pg.fill('#rDay','2026-11-05');await pg.dispatch_event('#rDay','change');await pg.wait_for_timeout(500)
    print('ngay',await pg.evaluate("[rptSel,document.querySelectorAll('.rdon .hld').length,document.querySelector('.rdh b').textContent]"))
    await pg.evaluate("scrollTo(0,0)");await pg.evaluate(HIDE);await pg.locator('#v-rpt .panel.own').first.screenshot(path=S+'rpt_lich.png')
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1500)
    await pg.evaluate("go('rpt')");await pg.click('[data-rm=thang]');await pg.wait_for_timeout(300)
    await pg.select_option('#rThang',await pg.evaluate("monthsList()[0]"));await pg.wait_for_timeout(500)
    print('thang hlp',await pg.evaluate("!!document.querySelector('#v-rpt .hlp')"))
    await pg.evaluate(HIDE);await pg.screenshot(path=S+'rpt_thang.png',full_page=True)
    # Lãi lỗ: két + chi phí
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1500)
    await pg.evaluate("go('rpt')");await pg.click('[data-rt=lai]');await pg.wait_for_timeout(300)
    await pg.evaluate(HIDE);await pg.locator('.rket').screenshot(path=S+'rket.png')
    await pg.click('[data-rchi=list]');await pg.wait_for_timeout(400)
    print('vao thu chi',await pg.evaluate("[view,more,document.querySelector('#v-more .back').textContent]"))
    await pg.click('#v-more .back');await pg.wait_for_timeout(400)
    print('quay lai',await pg.evaluate("[view,rptTab]"))
    await pg.click('[data-rchi=chi]');await pg.wait_for_timeout(400)
    print('ghi chi',await pg.evaluate("[view,chiSub,!!document.getElementById('fChi'),document.querySelector('#v-more .back').textContent]"))
    await pg.fill('#chiTien','150000');await pg.click('#fChi button[type=submit]');await pg.wait_for_timeout(500)
    print('sau luu',await pg.evaluate("[view,rptTab,document.querySelector('.rket .rchi b').textContent]"))
    # Thêm › Thu chi bình thường vẫn về menu
    await pg.evaluate("more='menu';go('more')");await pg.wait_for_timeout(200)
    await pg.evaluate("document.querySelector('[data-more=chi]').click()");await pg.wait_for_timeout(300)
    print('tu Them',await pg.evaluate("document.querySelector('#v-more .back').dataset.more"))
    print('tran',await pg.evaluate('document.documentElement.scrollWidth>innerWidth'),'errs',errs)
    await b.close()
asyncio.run(main())
