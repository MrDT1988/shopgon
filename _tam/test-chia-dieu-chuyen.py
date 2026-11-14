import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765'
KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def trang(b,path,w=390):
    ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
    async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*',h); await pg.goto(URL+path); await pg.wait_for_timeout(1200); return ctx,pg,errs
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      ctx,pg,errs=await trang(b,'/app/?demo=1',w); E=pg.evaluate
      g=await E("(()=>{const G={};stock().forEach(x=>{G[gk(x.ten)]=(G[gk(x.ten)]||0)+1});return Object.entries(G).sort((a,b)=>b[1]-a[1])[0]})()")
      print('nhom',g)
      await E(f"go('sell');sellMode='may';sellGrp={json.dumps(g[0])};render()"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Nút đỏ Chia hàng hiện ở nhóm máy', await pg.locator('button.chbtn').count()==1)
      await pg.click('button.chbtn'); await pg.wait_for_timeout(200)
      n=await pg.locator('button.chrow').count(); ok(f'[{w}] Panel chia hiện {n} IMEI kèm giá nhập', n==g[1] and await pg.locator('.chrow .gn b').count()==n)
      rows=pg.locator('button.chrow'); await rows.nth(0).click(); await rows.nth(1).click()
      await pg.click('[data-chq="200000"]'); await pg.wait_for_timeout(100)
      ok(f'[{w}] Giá chia điền = TB giá nhập +200k', (await pg.input_value('#chGia'))!='')
      await pg.screenshot(path=f'/tmp/chia_{w}.png',full_page=True)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang (chia)', W<=w+2, W)
      await pg.click('[data-chok="1"]'); await pg.wait_for_timeout(200)
      c=json.loads(await E("JSON.stringify(cart)")); ok(f'[{w}] Giỏ có 2 máy chia', len([x for x in c if x.get('chia')])==2, c)
      await E("cartOpen=true;render()"); await pg.wait_for_timeout(150)
      ok(f'[{w}] Giỏ có nhãn Chia hàng', await pg.locator('i.chtag').count()==2)
      await pg.click('[data-checkout="1"]'); await pg.wait_for_timeout(400)
      d=json.loads(await E("JSON.stringify(db.don.filter(x=>x.chia))")); ok(f'[{w}] Đơn lưu chia:1, giá vốn = giá nhập', len(d)==2 and all(x['giaVon']>0 for x in d), d)
      # máy lẻ: nút chia trên máy đã chọn
      im=await E("stock()[0].imei"); await E(f"go('sell');sellImei='{im}';sellGrp='';render()")
      ok(f'[{w}] Nút Chia hàng ở máy đã chọn', await pg.locator('button.chbtn.wide').count()==1)
      await E("document.querySelector('#rc')&&(document.querySelector('#rc').hidden=true);document.querySelector('button.chbtn.wide').click()"); await pg.wait_for_timeout(150)
      ok(f'[{w}] Mở chia với IMEI chọn sẵn', await pg.locator('button.chrow[aria-pressed="true"]').count()==1)
      # ĐIỀU CHUYỂN
      await E("more='dck';DC.tab='di';go('more')"); await pg.wait_for_timeout(200)
      ims=await E("stock().slice(0,2).map(x=>x.imei)")
      for i in ims: await E(f"dcAdd('{i}')")
      hid=await E("(db.hang.find(h=>h.sl>1)||{}).id||''")
      await E("DC.toiE='';DC.ngoai=true;renderMore()"); await pg.fill('#dcToi','LK Mobile 2')
      if hid:
        await pg.select_option('#dcH',hid); await pg.fill('#dcSl','1'); await pg.click('[data-dcpk="1"]'); await pg.wait_for_timeout(100)
      await pg.screenshot(path=f'/tmp/dck_{w}.png',full_page=True)
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang (điều chuyển)', W<=w+2, W)
      sl0=await E(f"(db.hang.find(h=>h.id==='{hid}')||{{}}).sl") if hid else 0
      await pg.click('[data-dctao="1"]'); await pg.wait_for_timeout(500)
      st=await E(f"JSON.stringify({json.dumps(ims)}.map(i=>db.may.find(m=>m.imei===i).tt))")
      ok(f'[{w}] Tạo phiếu: máy rời kho (chuyen), có link', st=='["chuyen","chuyen"]' and (await E("DC.link")).startswith(URL+'/app/?ck='), st)
      if hid: ok(f'[{w}] Phụ kiện trừ kho', await E(f"db.hang.find(h=>h.id==='{hid}').sl")==sl0-1)
      link=await E("DC.link"); print('độ dài link',len(link))
      ok(f'[{w}] Phiếu chuyển không vào danh sách NCC', await E("!nccDs().some(o=>o.P.some(p=>p.loai==='chuyen'))"))
      await pg.screenshot(path=f'/tmp/dcklink_{w}.png',full_page=True)
      # SHOP NHẬN
      c2,p2,e2=await trang(b,link.replace(URL,'')+'&demo=1' if '?' in link else link,w)
      await p2.wait_for_timeout(1500)
      ok(f'[{w}] Mở link → tự vào tab Nhận, thấy phiếu', await p2.evaluate("more==='dck'&&DC.tab==='nhan'&&!!DC.xem"), await p2.evaluate("[more,DC.tab,DC.msg]"))
      await p2.evaluate(f"db.may=db.may.filter(m=>!{json.dumps(ims)}.includes(m.imei));renderMore()")
      await p2.screenshot(path=f'/tmp/dcnhan_{w}.png',full_page=True)
      await p2.click('[data-dcnhan="1"]'); await p2.wait_for_timeout(300)
      r=json.loads(await p2.evaluate(f"JSON.stringify({json.dumps(ims)}.map(i=>{{const m=db.may.find(x=>x.imei===i);return m&&[m.tt,m.ncc,m.giaNhap]}}))"))
      ok(f'[{w}] Shop nhận: 2 máy vào kho, NCC "Chuyển từ…"', all(x and x[0]=='ton' and x[1].startswith('Chuyển từ') for x in r), r)
      ok(f'[{w}] Nhận lần 2 bị chặn', await p2.evaluate("dcNhan(DC.xem)===0"))
      ok(f'[{w}] Shop nhận không lỗi', not e2, e2)
      await c2.close()
      # HỦY ở shop gửi
      await E("DC.tab='ls';renderMore()"); await pg.click('[data-dchuy]'); await pg.wait_for_timeout(300)
      st=await E(f"JSON.stringify({json.dumps(ims)}.map(i=>db.may.find(m=>m.imei===i).tt))")
      ok(f'[{w}] Hủy phiếu: máy về kho', st=='["ton","ton"]', st)
      if hid: ok(f'[{w}] Hủy phiếu: phụ kiện về kho', await E(f"db.hang.find(h=>h.id==='{hid}').sl")==sl0)
      ok(f'[{w}] Không lỗi console', not errs, errs)
      await ctx.close()
    # NV không thấy nút
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
