# 07/11 22h anh Thái: Báo cáo › Lãi lỗ — bấm hãng ra máy + IMEI + lãi từng IMEI
import asyncio,sys,os
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp';W=int(sys.argv[2]) if len(sys.argv)>2 else 390
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':W,'height':844},device_scale_factor=2);errs=[];ok=0
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1800)
    await pg.evaluate("go('rpt');rptTab='lai';render();scrollTo(0,0)");await pg.wait_for_timeout(300)
    n=await pg.evaluate("document.querySelectorAll('[data-lhg]').length");print('số hãng',n);ok+=n>0
    k=await pg.evaluate("document.querySelector('[data-lhg]').dataset.lhg")
    await pg.locator('[data-lhg]').first.click();await pg.wait_for_timeout(300)
    r=await pg.evaluate("""k=>{const rm=todayIso().slice(0,7),L=live().filter(d=>d.ngay.startsWith(rm)&&d.loai==='may'&&(d.hang||'Khác')===k);
      const imeis=[...document.querySelectorAll('.lhct .lhi .lt b')].map(e=>e.textContent),btn=[...document.querySelectorAll('[data-lhg]')].find(e=>e.dataset.lhg===k);
      return [document.querySelectorAll('.lhct .lhi').length,L.length,L.every(d=>!d.imei||imeis.includes(String(d.imei))),document.querySelector('.lhct .hlsum b:last-child').textContent,money(L.reduce((a,d)=>a+profitOf(d),0)),btn.querySelector('.l b').textContent]}""",k)
    print('bấm',k,r);ok+= r[0]==r[1] and r[2] and r[3]==r[4] and r[3] in r[5]
    await pg.evaluate("document.querySelectorAll('body *').forEach(e=>{const c=getComputedStyle(e);if(c.position==='fixed'||c.position==='sticky')e.style.display='none'})")
    await pg.locator('#v-rpt .panel.own:has(.lhct)').screenshot(path=os.path.join(OUT,f'lai_imei_{W}.png'))
    await pg.locator('[data-lhg]').first.click();await pg.wait_for_timeout(200)
    c=await pg.evaluate("document.querySelectorAll('.lhct').length");print('đóng lại',c==0);ok+=c==0
    tr=await pg.evaluate('document.documentElement.scrollWidth>innerWidth');print('tràn',tr);ok+=not tr
    print('KẾT QUẢ',f'{ok}/4','errs',errs);await b.close()
asyncio.run(main())
