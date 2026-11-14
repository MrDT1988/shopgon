# Test Chuỗi cửa hàng + điều chuyển qua máy chủ (giả lập fetch). Chạy: python3 -m http.server 8765 ở gốc repo
import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
MOCK = r"""
window.SV={ph:{},log:[]};
const f0=window.fetch;window.fetch=async(u,o)=>{if(String(u)!==GG.LICENSE_URL)return f0(u,o);const d=JSON.parse(o.body);SV.log.push(d.act);let r={ok:false};
 const ch={ma:'',ten:'Chuoi LK',laChu:false,tt:'ok',chu:'me@x.com',shops:[{email:'me@x.com',ten:'LK me',tt:'ok',chu:true},{email:'con@x.com',ten:'LK con',tt:'ok'}]};
 if(d.act==='chuoiXem')r={ok:true,chuoi:ch};
 if(d.act==='ckGui'){SV.ph[JSON.parse(d.phieu).id]={tt:'cho',json:d.phieu,toi:d.toi};r={ok:true}}
 if(d.act==='ckHop')r={ok:true,den:Object.entries(SV.ph).filter(([k,v])=>v.tt==='cho'&&SV.toi===v.toi).map(([k,v])=>({id:k,tu:'me@x.com',tuTen:'LK me',luc:'2026-11-14 16:00',json:v.json})),di:Object.fromEntries(Object.entries(SV.ph).map(([k,v])=>[k,{tt:v.tt}]))};
 if(d.act==='ckNhan'){const p=SV.ph[d.id];if(p.tt==='huy')r={ok:false,huy:true,msg:'huy'};else{p.tt='nhan';r={ok:true}}}
 if(d.act==='ckHuy'){const p=SV.ph[d.id];if(p&&p.tt==='nhan')r={ok:false,daNhan:true};else{if(p)p.tt='huy';r={ok:true}}}
 return new Response(JSON.stringify(r),{headers:{'Content-Type':'application/json'}})};
window.chMau=()=>false;GG.token='t'.repeat(30);GG.email='me@x.com';
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
      # 1. Trang Chuỗi (tài khoản demo = chuỗi mẫu)
      await E("more='chuoi';go('more')"); await pg.wait_for_timeout(200)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Trang Chuỗi mẫu: mã + shop + chờ duyệt', 'CGLK8M2' in t and 'Chờ duyệt' in t and 'LK Mobile Gò Đen' in t, t[:200])
      await pg.screenshot(path=f'/tmp/chuoi_{w}.png',full_page=True)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang (chuỗi)', W<=w+2, W)
      ok(f'[{w}] Menu Thêm có Chuỗi cửa hàng', await E("more='menu';renderMore();document.getElementById('v-more').innerText.includes('Chuỗi cửa hàng')"))
      # 2. Chế độ máy chủ (giả lập)
      await E(MOCK); await E("CH.d=null;CH.luc=0;more='chuoi';renderMore()"); await pg.wait_for_timeout(500)
      ok(f'[{w}] Tải chuỗi từ máy chủ', await E("!!CH.d&&CH.d.shops.length===2"), await E("JSON.stringify([CH.d,SV.log])"))
      await E("more='dck';DC.tab='di';DC.toiE='';DC.ngoai=false;go('more')"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Điều chuyển: chip shop trong chuỗi, chọn sẵn shop con', await pg.locator('[data-dctoie="con@x.com"][aria-pressed="true"]').count()==1)
      ims=await E("stock().slice(0,2).map(x=>x.imei)")
      for i in ims: await E(f"dcAdd('{i}')")
      await pg.screenshot(path=f'/tmp/chuoi_dck_{w}.png',full_page=True)
      await E("document.querySelector('[data-dctao]').click()"); await pg.wait_for_timeout(800)
      pn=json.loads(await E("JSON.stringify(dcDi()[0])"))
      ok(f'[{w}] Phiếu gửi qua máy chủ tới con@x.com', pn.get("toiEmail")=="con@x.com" and await E("DC.gui.startsWith('ok:')"), await E("DC.gui"))
      await pg.screenshot(path=f'/tmp/chuoi_gui_{w}.png',full_page=True)
      # 3. Shop con nhận: đổi vai sang con@x.com, máy chưa có IMEI
      await E(f"SV.toi='con@x.com';GG.email='con@x.com';db.pn=db.pn.filter(p=>p.id!=='{pn['id']}');db.may=db.may.filter(m=>!{json.dumps(ims)}.includes(m.imei));CH.den=[];DC.tab='nhan';renderMore()")
      await E("chHop().then(()=>renderMore())"); await pg.wait_for_timeout(400)
      ok(f'[{w}] Shop con thấy 1 phiếu đến', await pg.locator('[data-dchop]').count()==1, await E("JSON.stringify(CH.den.length)"))
      await E("document.querySelector('[data-dchop]').click()"); await pg.wait_for_timeout(200)
      await pg.screenshot(path=f'/tmp/chuoi_nhan_{w}.png',full_page=True)
      await E("document.querySelector('[data-dcnhan]').click()"); await pg.wait_for_timeout(500)
      st=json.loads(await E(f"JSON.stringify({json.dumps(ims)}.map(i=>(db.may.find(m=>m.imei===i)||{{}}).tt))"))
      ok(f'[{w}] Nhận: máy vào kho + máy chủ ghi đã nhận', st==['ton','ton'] and await E(f"SV.ph['{pn['id']}'].tt==='nhan'"), st)
      ok(f'[{w}] Hộp phiếu trống sau khi nhận', await E("CH.den.length===0"))
      # 4. Shop mẹ hủy phiếu đã nhận → bị chặn
      await E(f"GG.email='me@x.com';db.pn.push({json.dumps(pn)});{json.dumps(ims)}.forEach(i=>{{const m=db.may.find(x=>x.imei===i);if(m)m.tt='chuyen'}});DC.tab='ls';renderMore()")
      await E("document.querySelector('[data-dchuy]')&&document.querySelector('[data-dchuy]').click()"); await pg.wait_for_timeout(500)
      ok(f'[{w}] Hủy phiếu shop con đã nhận → bị chặn', await E(f"!dcDi().find(p=>p.id==='{pn['id']}').huy"))
      ok(f'[{w}] Lịch sử hiện "Đã nhận"', 'Đã nhận' in await E("document.getElementById('v-more').innerText"))
      ok(f'[{w}] Không lỗi console', not errs, errs)
      await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
