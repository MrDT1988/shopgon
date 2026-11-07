# Quét lỗi hiển thị: chữ đè nhau, tràn ngang, chữ bị cắt — mọi màn chủ shop (test) + nhân viên (test), 2 khổ
# Dùng: python3 -m http.server 8765 & ; python3 _tam/quet-hien-thi.py 320 360 412  → ❌ = chữ đè nhau / bị cắt / tràn ngang
import asyncio,json,sys
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/ce0826dd-72f1-5e32-9809-e704164ebeef/scratchpad/sweep/'
DET=r"""(()=>{const fx=e=>{for(let x=e;x&&x!==document.body;x=x.parentElement){const p=getComputedStyle(x).position;if(p==='fixed'||p==='sticky')return true}return false};
const vis=e=>{const dd=e.closest('details:not([open])');if(dd&&!e.closest('summary'))return false;const r=e.getBoundingClientRect();if(!r.width||!r.height)return false;const c=getComputedStyle(e);return c.visibility!=='hidden'&&c.display!=='none'&&+c.opacity>0.05};
const R=[];document.querySelectorAll('#app *, main *, body > div *').forEach(e=>{if(fx(e)||!vis(e))return;const tn=[...e.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim());if(!tn.length)return;const r=document.createRange();tn.forEach(n=>{r.selectNodeContents(n);const cs=getComputedStyle(e),eb=e.getBoundingClientRect(),clip=cs.overflow!=='visible'||cs.overflowX!=='visible';[...r.getClientRects()].forEach(b0=>{let b={left:b0.left,right:b0.right,top:b0.top,bottom:b0.bottom};if(clip){b.left=Math.max(b.left,eb.left);b.right=Math.min(b.right,eb.right);b.top=Math.max(b.top,eb.top);b.bottom=Math.min(b.bottom,eb.bottom)}b.width=b.right-b.left;b.height=b.bottom-b.top;if(b.width>2&&b.height>2)R.push({e,b,t:n.textContent.trim().slice(0,40)})})})});
const ov=[];for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const a=R[i],b=R[j];if(a.e===b.e||a.e.contains(b.e)||b.e.contains(a.e))continue;const x=Math.min(a.b.right,b.b.right)-Math.max(a.b.left,b.b.left),y=Math.min(a.b.bottom,b.b.bottom)-Math.max(a.b.top,b.b.top);if(x>3&&y>3&&x*y>40)ov.push(a.t+' ⟂ '+b.t)}
const cut=[];document.querySelectorAll('body *').forEach(e=>{if(fx(e)||!vis(e))return;const c=getComputedStyle(e);if(e.scrollWidth>e.clientWidth+3&&(c.overflowX==='hidden'||c.overflow==='hidden')&&c.textOverflow!=='ellipsis'&&e.textContent.trim()&&!['SVG','svg','CANVAS','IMG'].includes(e.tagName))cut.push((e.className||e.tagName)+': '+e.textContent.trim().slice(0,40))});
return {ov:[...new Set(ov)].slice(0,15),cut:[...new Set(cut)].slice(0,10),hscroll:document.documentElement.scrollWidth>innerWidth+1}})()"""
async def scan(pg,name,shot=True):
    await pg.wait_for_timeout(350)
    r=await pg.evaluate(DET)
    if shot: await pg.screenshot(path=S+name+'.png',full_page=True)
    bad=r['ov'] or r['cut'] or r['hscroll']
    print(('❌ ' if bad else '✅ ')+name, json.dumps(r,ensure_ascii=False) if bad else '')
    return bad
async def main(w):
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':w,'height':800},device_scale_factor=1);errs=[]
        pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('http://localhost:8765/app/?demo=1&test=1');await pg.wait_for_timeout(1500)
        await pg.evaluate("db.shop.nv=db.shop.nv&&db.shop.nv.length?db.shop.nv:[]")
        for k in ['today','yest','week','month']:
            await pg.evaluate(f"homeD='{k}';go('home')");await scan(pg,f'{w}_home_{k}')
        for v in ['sell','add','stock','rpt','km']:
            try:
                await pg.evaluate(f"go('{v}')");await scan(pg,f'{w}_{v}')
            except Exception as e: print('skip',v,str(e)[:80])
        await pg.evaluate("more='menu';go('more')");await pg.wait_for_timeout(300)
        keys=await pg.evaluate("[...new Set([...document.querySelectorAll('#v-more [data-more]')].map(b=>b.dataset.more))].filter(k=>k!=='menu')")
        await scan(pg,f'{w}_more_menu')
        for k in keys:
            try:
                await pg.evaluate(f"more='{k}';go('more')");await scan(pg,f'{w}_more_{k}')
            except Exception as e: print('skip',k,str(e)[:80])
        for t in ['nay','thang','gt','luong']:
            await pg.evaluate(f"more='cc';ccTab='{t}';go('more')");await scan(pg,f'{w}_cc_{t}')
        # NV test
        pg2=await ctx.new_page();pg2.on('pageerror',lambda e:errs.append('NV '+str(e)))
        await pg2.goto('http://localhost:8765/app/');await pg2.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0900000099',ten:'Nhân viên test',phien:'TEST',test:1}));localStorage.setItem('shopgon_ccok','1')")
        await pg2.goto('http://localhost:8765/app/');await pg2.wait_for_timeout(1800)
        for v in ['home','sell','add']:
            await pg2.evaluate(f"go('{v}')");await scan(pg2,f'{w}_nv_{v}')
        nk=await pg2.evaluate("more='nvme';go('more');[...new Set([...document.querySelectorAll('nav [data-v],#tb [data-v],.tabbar [data-v]')].map(b=>b.dataset.v))]")
        for v in nk:
            if v in ('home','sell','add'):continue
            try:
                await pg2.evaluate(f"go('{v}')");await scan(pg2,f'{w}_nv_tab_{v}')
            except Exception as e: print('skip',v)
        for k in ['nvme','cc']:
            await pg2.evaluate(f"more='{k}';go('more')");await scan(pg2,f'{w}_nv_more_{k}')
        print('JS errors:',errs[:5]);await b.close()
for w in [int(x) for x in sys.argv[1:]] or [360]:
    asyncio.run(main(w))
