# 25/11: mở xem thử (chuỗi mẫu) rồi vào shop thật → thẻ "Chuỗi hôm nay" KHÔNG còn số mẫu "LK Mobile Chợ Gạo". Chạy: python3 -m http.server 8765 ở gốc repo
import asyncio
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
def MOCK(chuoi):
    return r"""window.SV={log:[]};const f0=window.fetch;window.fetch=async(u,o)=>{if(String(u)!==GG.LICENSE_URL)return f0(u,o);const d=JSON.parse(o.body);SV.log.push(d.act);let r={ok:false,msg:'khong'};const t=todayIso();
 if(d.act==='chuoiXem')r={ok:true,chuoi:CHUOI};
 if(d.act==='chuoiSo'&&CHUOI)r={ok:true,shops:[{email:'xt@x.com',ten:'Xuân Thành',chu:true,so:null,luc:'',nvCho:{}},{email:'xt2@x.com',ten:'Xuân Thành 2',so:{ngay:{[t]:[7000000,700000,1,1]}},luc:t+' 11:00',nvCho:{}}]};
 if(d.act==='ckHop')r={ok:true,den:[],di:{}};if(d.act==='ckSo')r={ok:true};
 return new Response(JSON.stringify(r),{headers:{'Content-Type':'application/json'}})};
window.chMau=()=>false;GG.token='t'.repeat(30);GG.email='xt@x.com';""".replace('CHUOI',chuoi)
THAT="{ma:'CGXT1',ten:'Chuoi XT',laChu:true,tt:'ok',chu:'xt@x.com',shops:[{email:'xt@x.com',ten:'Xuân Thành',tt:'ok',chu:true},{email:'xt2@x.com',ten:'Xuân Thành 2',tt:'ok'}]}"
async def trang(b,w):
    ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*',h); await pg.goto(URL+'/app/?demo=1'); await pg.wait_for_timeout(1200); return ctx,pg,errs
async def home(pg):
    await pg.evaluate("go('home');render()"); await pg.wait_for_timeout(400)
    return await pg.evaluate("(document.querySelector('.cshome')||{}).innerText||''")
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      # 1) xem thử → shop thật KHÔNG có chuỗi
      ctx,pg,errs=await trang(b,w)
      t=await home(pg); ok(f'[{w}] Xem thử: thẻ chuỗi mẫu có Chợ Gạo', 'Chợ Gạo' in t, t)
      await pg.evaluate(MOCK('null')); await pg.evaluate("localStorage.removeItem(chKey())")
      t=await home(pg); ok(f'[{w}] Vào shop thật không chuỗi: hết thẻ chuỗi mẫu', t=='', t)
      await pg.evaluate("more='chuoi';go('more')"); await pg.wait_for_timeout(500)
      v=await pg.evaluate("document.getElementById('v-more').innerText")
      ok(f'[{w}] Trang Chuỗi shop thật không còn LK Mobile / Tài khoản test', 'LK Mobile' not in v and 'Tài khoản test' not in v, v[:200])
      ok(f'[{w}] Không lỗi console', not errs, errs); await ctx.close()
      # 2) xem thử → shop thật CÓ chuỗi thật
      ctx,pg,errs=await trang(b,w); await home(pg)
      await pg.evaluate(MOCK(THAT)); await pg.evaluate("localStorage.setItem(chKey(),JSON.stringify("+THAT+"))")
      await home(pg); await pg.wait_for_timeout(600); t=await home(pg)
      ok(f'[{w}] Shop thật có chuỗi: thẻ hiện shop thật, không Chợ Gạo', 'Chợ Gạo' not in t and 'Xuân Thành' in t and '2 shop' in t, t)
      # 3) shop thật → quay lại xem thử: hiện lại chuỗi mẫu, không lẫn số thật
      await pg.evaluate("window.chMau=()=>true"); t=await home(pg)
      ok(f'[{w}] Quay lại xem thử: chuỗi mẫu 3 shop', 'Chợ Gạo' in t and '3 shop' in t, t)
      ok(f'[{w}] Không lỗi console (2)', not errs, errs); await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
