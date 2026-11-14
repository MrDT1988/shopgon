# Test đợt 2: shop mẹ xem doanh thu shop con (giả lập máy chủ). Chạy: python3 -m http.server 8765 ở gốc repo
import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
MOCK = r"""
window.SV={log:[],so:null};const f0=window.fetch;window.fetch=async(u,o)=>{if(String(u)!==GG.LICENSE_URL)return f0(u,o);const d=JSON.parse(o.body);SV.log.push(d.act);let r={ok:false};
 const t=todayIso();
 if(d.act==='chuoiXem')r={ok:true,chuoi:{ma:'CGTEST1',ten:'Chuoi',laChu:true,tt:'ok',chu:'me@x.com',shops:[{email:'me@x.com',ten:'Me',tt:'ok',chu:true},{email:'con@x.com',ten:'Shop Con A',tt:'ok'},{email:'con2@x.com',ten:'Shop Con B',tt:'ok'}]}};
 if(d.act==='ckSo'){SV.so=d.so;r={ok:true}}
 if(d.act==='chuoiSo')r={ok:true,shops:[{email:'me@x.com',ten:'Me',chu:true,so:null,luc:'',nvCho:{}},{email:'con@x.com',ten:'Shop Con A',so:{ngay:{[t]:[10000000,1000000,2,2]},ton:{may:5,von:30000000,no:0},top:[['OPPO A6',2]]},luc:t+' 16:30',nvCho:{[t]:{dt:3000000,don:1,may:1}}},{email:'con2@x.com',ten:'Shop Con B',so:{ngay:{}},luc:'2026-11-01 09:00',nvCho:{}}]};
 if(d.act==='ckHop')r={ok:true,den:[],di:{}};
 return new Response(JSON.stringify(r),{headers:{'Content-Type':'application/json'}})};
window.chMau=()=>false;GG.token='t'.repeat(30);GG.email='me@x.com';CH.d=null;CH.luc=0;CS.ds=null;CS.luc=0;CS.guiLuc=0;
"""
async def trang(b,w):
    ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
    async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*',h); await pg.goto(URL+'/app/?demo=1'); await pg.wait_for_timeout(1200); return ctx,pg,errs
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      ctx,pg,errs=await trang(b,w); E=pg.evaluate
      await E("go('home')"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Trang chủ shop mẹ có thẻ Chuỗi hôm nay (mẫu)', await pg.locator('.cshome').count()==1)
      await pg.screenshot(path=f'/tmp/cs_home_{w}.png')
      await E("document.querySelector('.cshome').click()"); await pg.wait_for_timeout(300)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Bấm thẻ → tab Doanh thu, 3 shop xếp hạng', 'Doanh thu chuỗi' in t and 'LK Mobile Chợ Gạo' in t and 'Gò Đen' in t, t[:300])
      ok(f'[{w}] Nhắc shop chưa bán hôm nay', 'Chưa bán đơn nào hôm nay' in t)
      await pg.screenshot(path=f'/tmp/cs_dt_{w}.png',full_page=True)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang', W<=w+2, W)
      for k in ['hq','7n','th']:
        await E(f"document.querySelector('[data-csky=\"{k}\"]').click()"); await pg.wait_for_timeout(100)
      ok(f'[{w}] Kỳ Tháng có so cùng kỳ', 'cùng kỳ tháng trước' in await E("document.getElementById('v-more').innerText"))
      await E("document.querySelector('[data-cssel=\"lk.chogao@gmail.com\"]').click()"); await pg.wait_for_timeout(150)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Chi tiết shop: 7 ngày, tồn, mẫu bán chạy', 'Doanh thu 7 ngày' in t and 'Máy tồn' in t and 'Mẫu bán chạy' in t, t[:200])
      await pg.screenshot(path=f'/tmp/cs_ct_{w}.png',full_page=True)
      # chế độ máy chủ giả lập
      await E(MOCK); await E("csGui(1)"); await pg.wait_for_timeout(400)
      so=json.loads(await E("JSON.stringify(SV.so)"))
      ok(f'[{w}] Shop gửi số tóm tắt (có ngày, tồn, không có IMEI)', so and 'ngay' in so and 'ton' in so and 'imei' not in json.dumps(so).lower(), so and list(so.keys()))
      await E("CH.d=null;CS.ds=null;CS.sel='';CS.ky='hn';CS.tab='dt';more='chuoi';go('more')"); await pg.wait_for_timeout(300)
      await E("chTai().then(()=>renderMore())"); await pg.wait_for_timeout(300); await E("renderMore()"); await pg.wait_for_timeout(600)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Máy chủ: Shop Con A = 10tr + 3tr đơn NV chờ', '13.000.000' in t and 'đơn NV chờ về sổ' in t, t[:400])
      ok(f'[{w}] Máy chủ: Shop Con B cũ → nhắc chưa mở app', 'chưa mở app hôm nay' in t)
      ok(f'[{w}] Không lỗi console', not errs, errs)
      await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
