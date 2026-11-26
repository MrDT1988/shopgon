# 26/11: shop mẹ xem tồn kho chi tiết từng shop con + cả chuỗi
import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e)))
      async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
      await pg.route('**/*',h); await pg.goto(URL+'/app/?demo=1'); await pg.wait_for_timeout(1200); E=pg.evaluate
      so=json.loads(await E("JSON.stringify(csTom())"))
      st=await E("stock().length")
      ok(f'[{w}] Gói tồn kho: tổng máy = máy tồn thật ({st})', sum(x[1] for x in so['kho']['m'])==st)
      s=json.dumps(so,ensure_ascii=False)
      ok(f'[{w}] Không gửi IMEI / NCC', all(m not in s for m in ['imei','ncc']) and not any(len(str(x))>=15 and str(x).isdigit() for r in so['kho']['m'] for x in r), s[:200])
      big=json.loads(await E("JSON.stringify(csKho(Array.from({length:900},(_,i)=>({ten:'Mẫu '+(i%120),giaNhap:5e6,ngayNhap:'2026-10-01'})),Array.from({length:3000},(_,i)=>({ten:'Phụ kiện số '+i+' loại dài dài',nhom:'pk',sl:3,giaNhap:1000*i,min:1}))))"))
      ok(f'[{w}] Shop rất lớn: gói ≤22KB, bớt phụ kiện vốn thấp', len(json.dumps(big,ensure_ascii=False,separators=(',',':')))<=22000 and big['cat']>0 and big['h'][0][3]>=big['h'][-1][3], (len(json.dumps(big)),big['cat']))
      await E("go('home');render()"); await pg.wait_for_timeout(300)
      await E("document.querySelector('[data-cskho=\"\"]').click()"); await pg.wait_for_timeout(500)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Trang chủ → 📦 Tồn kho cả chuỗi', 'Cả chuỗi' in t and 'Máy tồn' in t and 'LK Mobile Chợ Gạo' in t, t[:300])
      tong=await E("CS.ds.reduce((a,s)=>a+s.so.kho.m.reduce((x,r)=>x+r[1],0),0)")
      ok(f'[{w}] KPI máy tồn = tổng các shop ({tong})', await E("csKhoGop().tong[0]")==tong)
      ok(f'[{w}] Mỗi mẫu ghi shop nào còn bao nhiêu', await E("document.querySelectorAll('.cskr').length")>0 and ('Gò Đen' in t or 'Chợ Gạo' in t))
      await pg.screenshot(path=f'/tmp/tk_chuoi_{w}.png',full_page=True)
      ten=await E("CS.ds[1].so.kho.m[0][0]")
      await E(f"$('csKq').value={json.dumps(ten[:6])};$('csKq').dispatchEvent(new Event('input',{{bubbles:true}}))"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Tìm tên lọc danh sách (không vẽ lại cả trang)', await E("document.activeElement&&document.activeElement.id")!='x' and ten[:6].lower() in (await E("$('csKhoL').innerText")).lower())
      await E("document.querySelector('[data-cskn=\"pk\"]').click()"); await pg.wait_for_timeout(200)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Nhóm Phụ kiện: có Sắp hết', 'Sắp hết' in t)
      await E("CS.kq='';document.querySelector('[data-csks=\"lk.goden@gmail.com\"]').click()"); await pg.wait_for_timeout(200)
      g=await E("csKhoGop().L.every(x=>x.sh.every(y=>y[0]==='LK Mobile Gò Đen'))")
      ok(f'[{w}] Lọc 1 shop chỉ còn hàng của shop đó', g)
      await E("CS.tab='dt';CS.sel='lk.chogao@gmail.com';renderMore()"); await pg.wait_for_timeout(200)
      await E("document.querySelector('[data-cskho=\"lk.chogao@gmail.com\"]').click()"); await pg.wait_for_timeout(300)
      ok(f'[{w}] Chi tiết shop → Xem tồn kho của shop đó', await E("CS.tab==='kho'&&CS.ks==='lk.chogao@gmail.com'&&CS.kn==='may'"))
      await E("CS.ds[2].so.kho=undefined;renderMore()"); t=await E("document.getElementById('v-more').innerText")
      await E("CS.ks='';renderMore()"); t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Shop con bản cũ: báo "Chưa gửi tồn kho"', 'Chưa gửi tồn kho' in t)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang', W<=w+2, W)
      ok(f'[{w}] Không lỗi console', not errs, errs); await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
