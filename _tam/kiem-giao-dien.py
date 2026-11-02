# Kiểm giao diện: chữ tràn khung / tràn màn hình / nhãn thanh dưới xuống dòng, ở nhiều độ rộng
import asyncio, sys
from playwright.async_api import async_playwright
OUT='/tmp/'
tag=sys.argv[1] if len(sys.argv)>1 else 'x'
VIEWS=[('home',"go('home')"),('sell',"sellMode='may';go('sell')"),('sellpk',"sellMode='pk';go('sell')"),('selldv',"sellMode='dv';go('sell')"),
 ('add',"addTab='moi';addMode='may';go('add')"),('addh',"addTab='moi';addMode='hang';go('add')"),('da',"addTab='da';go('add')"),
 ('khohub',"khoHub=true;go('stock')"),('kho',"khoHub=false;stockMode='may';go('stock')"),('khoh',"khoHub=false;stockMode='hang';go('stock')"),
 ('km',"go('km')"),('rpt',"go('rpt')"),('more',"more='menu';go('more')"),('chi',"more='chi';chiSub='list';go('more')"),('hist',"more='hist';go('more')")]
JS="""()=>{const W=innerWidth,bad=[];const box=e=>e.closest('.panel,.kpi,.wc2,.sc,.pt,.row,.gsb,button,nav,header,.alert,.wtop');
const scr=e=>{for(let a=e.parentElement;a;a=a.parentElement){const o=getComputedStyle(a).overflowX;if(o==='auto'||o==='scroll')return true}return false};
for(const e of document.querySelectorAll('body *')){if(e.closest('[hidden]')||e.tagName==='IFRAME'||e.closest('.bar,.bars')||scr(e)||!e.offsetParent&&getComputedStyle(e).position!=='fixed')continue;
 const r=e.getBoundingClientRect();if(!r.width||!r.height)continue;
 const hasText=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
 if(r.right>W+1||r.left<-1){bad.push('TRAN MAN: '+(e.className||e.tagName)+' «'+(e.innerText||'').slice(0,30)+'» '+Math.round(r.left)+'..'+Math.round(r.right));continue}
 if(hasText&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflow!=='visible'&&getComputedStyle(e).textOverflow!=='ellipsis'&&e.tagName!=='INPUT'&&e.tagName!=='SELECT'&&e.tagName!=='TEXTAREA')bad.push('CAT CHU: '+(e.className||e.tagName)+' «'+e.innerText.slice(0,30)+'»');
 const p=box(e.parentElement||e);if(hasText&&p&&p!==e){const q=p.getBoundingClientRect();if(r.right>q.right+0.5)bad.push('TRAN KHUNG: «'+(e.innerText||'').slice(0,30)+'» trong '+p.className)}}
for(const b of document.querySelectorAll('nav.tabs button')){const t=[...b.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();const rg=document.createRange();const tn=[...b.childNodes].find(n=>n.nodeType===3&&n.textContent.trim());if(tn){rg.selectNodeContents(tn);if(rg.getClientRects().length>1)bad.push('NAV 2 DONG: '+t)}}
return [...new Set(bad)]}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); tong=0
        for w in [320,340,360,412]:
            ctx=await b.new_context(viewport={'width':w,'height':780},device_scale_factor=2); pg=await ctx.new_page(); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)))
            async def h(r):
                u=r.request.url
                if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
                elif 'localhost' in u: await r.continue_()
                else: await r.abort()
            await pg.route('**/*',h)
            await pg.goto('http://localhost:8765/app/?demo=1&test=1'); await pg.wait_for_timeout(1200)
            for n,js in VIEWS:
                await pg.evaluate(js); await pg.wait_for_timeout(250)
                bad=await pg.evaluate(JS)
                if bad: tong+=len(bad); print(f'[{w}] {n}:',*bad[:8],sep='\n   ')
                if w==360: await pg.screenshot(path=OUT+f'{tag}-{n}.png')
            if errs: print('JS ERR',w,errs)
            await ctx.close()
        # web khách
        for w in [320,360,412]:
            ctx=await b.new_context(viewport={'width':w,'height':780}); pg=await ctx.new_page()
            async def h2(r):
                if 'localhost' in r.request.url: await r.continue_()
                else: await r.abort()
            await pg.route('**/*',h2)
            await pg.goto('http://localhost:8765/bg/?demo=1&xem=1'); await pg.wait_for_timeout(1500)
            bad=await pg.evaluate(JS)
            if bad: tong+=len(bad); print(f'[{w}] web:',*bad[:8],sep='\n   ')
            if w==360: await pg.screenshot(path=OUT+f'{tag}-web.png')
            await ctx.close()
        print('TONG LOI:',tong); await b.close()
asyncio.run(main())
