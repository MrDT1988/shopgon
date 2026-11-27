# 27/11: giờ cập nhật shop con dạng "Fri Nov 27 2026 13:11:00 GMT+0700" → hiện "13:11"/"26/11 07:19"; gói số dạng chuỗi vẫn đọc được
import asyncio
from playwright.async_api import async_playwright
KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('**/*',lambda r:r.continue_() if 'localhost' in r.request.url and 'ver.json' not in r.request.url else r.abort())
    await pg.goto('http://localhost:8765/app/?demo=1'); await pg.wait_for_timeout(1000); E=pg.evaluate
    t=await E("(()=>{const d=new Date();d.setHours(13,11,0,0);return csLuc({luc:d.toString()})})()")
    ok('Giờ hôm nay dạng Date → "13:11"', t=='13:11', t)
    t=await E("(()=>{const d=new Date(Date.now()-86400000);d.setHours(7,19,0,0);return [csLuc({luc:d.toString()}),csCu({luc:d.toString()})]})()")
    ok('Hôm qua → "dd/mm 07:19" + báo chưa mở app hôm nay', t[0].endswith('07:19') and '/' in t[0] and t[1], t)
    ok('Dạng cũ "YYYY-MM-DD HH:mm" vẫn đúng', await E("csLuc({luc:todayIso()+' 09:05'})")=='09:05')
    ok('Chưa gửi', await E("csLuc({})")=='chưa gửi số')
    await E("""window.chMau=()=>false;GG.token='t'.repeat(30);GG.email='me@x.com';const f0=window.fetch;window.fetch=async(u,o)=>{if(String(u)!==GG.LICENSE_URL)return f0(u,o);const d=JSON.parse(o.body);let r={ok:false};
      if(d.act==='chuoiSo')r={ok:true,shops:[{email:'me@x.com',ten:'Mẹ',chu:true},{email:'c@x.com',ten:'Con',luc:new Date().toString(),so:JSON.stringify({v:3,ngay:{[todayIso()]:[5000000,500000,2,1,0]},kho:{m:[['OPPO A6',3,15000000,0,'']],h:[]}})}]};
      if(d.act==='ckSo'||d.act==='ckHop')r={ok:true,den:[],di:{}};return new Response(JSON.stringify(r),{headers:{'Content-Type':'application/json'}})};""")
    await E("CS.ds=null;csTai()"); await pg.wait_for_timeout(500)
    ok('Gói số dạng chuỗi: đọc được doanh thu 5tr', await E("csTong(CS.ds[1],todayIso(),todayIso()).dt")==5000000)
    ok('… và tồn kho 3 máy', await E("CS.kn='may';CS.ks='c@x.com';csKhoGop().tong[0]")==3)
    ok('Không lỗi console', not errs, errs)
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
