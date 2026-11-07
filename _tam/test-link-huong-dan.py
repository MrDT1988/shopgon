import asyncio
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/912e7d6c-97d1-5634-b470-4e79346b25d7/scratchpad/'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2);errs=[]
    pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1800)
    await pg.evaluate("more='menu';go('more')");await pg.wait_for_timeout(300)
    async with ctx.expect_page() as np: await pg.click('[data-more=hdsd]')
    n=await np.value;await n.wait_for_load_state();print('menu ->',n.url)
    await pg.evaluate("document.querySelector('.mh:last-of-type')?.scrollIntoView()");await pg.wait_for_timeout(200)
    await pg.screenshot(path=S+'menu_hd.png')
    await pg.evaluate("more='cc';ccTab='nay';go('more')");await pg.wait_for_timeout(300)
    async with ctx.expect_page() as np: await pg.click('#v-more [data-hdan]')
    n=await np.value;print('cc ->',n.url)
    await pg.evaluate("go('rpt')");await pg.wait_for_timeout(300)
    async with ctx.expect_page() as np: await pg.click('#v-rpt [data-hdan]')
    n=await np.value;print('rpt ->',n.url)
    pg2=await ctx.new_page()
    await pg2.goto('http://localhost:8765/app/');await pg2.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0900000099',ten:'Nhân viên test',phien:'TEST',test:1}));localStorage.setItem('shopgon_ccok','1')")
    await pg2.goto('http://localhost:8765/app/');await pg2.wait_for_timeout(2000)
    await pg2.evaluate("more='nvme';go('more')");await pg2.wait_for_timeout(300)
    async with ctx.expect_page() as np: await pg2.click('[data-hdan=cham-cong]')
    n=await np.value;print('nv ->',n.url)
    print('errs',errs);await b.close()
asyncio.run(main())
