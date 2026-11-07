# 07/11 21h22: Báo cáo › Bán hàng — Lợi nhuận theo ngày (tổng tháng trên đầu, mỗi ngày 1 hàng, bấm ra chi tiết)
import asyncio,sys,os
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp';W=int(sys.argv[2]) if len(sys.argv)>2 else 390
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':W,'height':844},device_scale_factor=2);errs=[];ok=0
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1800)
    await pg.evaluate("go('rpt');scrollTo(0,0)");await pg.wait_for_timeout(300)
    r=await pg.evaluate("""(()=>{const t=todayIso(),m=t.slice(0,8)+'01',T=sumRange(m,t);return [!!document.querySelector('.lnp'),document.querySelectorAll('.lnr').length,+t.slice(8),document.querySelector('.lnh b').textContent,money(T.loi),/Đơn hôm nay/.test(document.getElementById('v-rpt').textContent)]})()""")
    print('panel',r); ok+= r[0] and r[1]==r[2] and r[3]==r[4] and not r[5]
    k=await pg.evaluate("document.querySelector('.lnr:not(:disabled)').dataset.lno")
    await pg.click(f'[data-lno="{k}"]');await pg.wait_for_timeout(300)
    d=await pg.evaluate(f"[document.querySelectorAll('.lnp .rdon .hld').length,document.querySelector('.lnp .hl3 b:last-child').textContent,money(sumRange('{k}','{k}').loi)]")
    print('bấm ngày',k,d); ok+= d[0]>0 and d[1]==d[2]
    await pg.evaluate("document.querySelectorAll('body *').forEach(e=>{const c=getComputedStyle(e);if(c.position==='fixed'||c.position==='sticky')e.style.display='none'})")
    await pg.locator('.lnp').screenshot(path=os.path.join(OUT,f'ln_ngay_{W}.png'))
    await pg.click(f'[data-lno="{k}"]');await pg.wait_for_timeout(200)
    c=await pg.evaluate("document.querySelectorAll('.lnp .rdon').length"); print('đóng lại',c==0); ok+= c==0
    tr=await pg.evaluate('document.documentElement.scrollWidth>innerWidth'); print('tràn',tr); ok+= not tr
    print('KẾT QUẢ',f'{ok}/4','errs',errs); await b.close()
asyncio.run(main())
