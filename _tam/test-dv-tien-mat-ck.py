# 26/11: dịch vụ thu hộ / chuyển tiền chọn khách trả Tiền mặt / Chuyển khoản → chốt két + Tổng tiền thu tách đúng
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
      await E("db.don=db.don.filter(d=>d.ngay!==todayIso());save()")
      async def ghi(nhom,loai,tien,phi,tt):
        await E(f"sellMode='dv';pkNhom='{nhom}';pkPick=null;go('sell');render()"); await pg.wait_for_timeout(150)
        await E(f"$('dLoai').value='{loai}';$('dLoai').dispatchEvent(new Event('change',{{bubbles:true}}))")
        mac=await E("dvTtCur()")
        if tt: await E(f"document.querySelector('[data-dvtt=\"{tt}\"]').click()")
        await E(f"$('dTien').value='{tien}';$('pGia').value='{phi}';$('fPk').requestSubmit()"); await pg.wait_for_timeout(150)
        return mac
      m=await ghi('thuho','Tiền điện','1.000.000','10.000',None)
      ok(f'[{w}] Thu hộ mặc định Tiền mặt', m=='Tiền mặt', m)
      await E("sellMode='dv';pkNhom='thuho';go('sell');render()"); await pg.wait_for_timeout(100)
      ok(f'[{w}] Form có nút 💵 Tiền mặt / 🏦 Chuyển khoản', await E("document.querySelectorAll('[data-dvtt]').length")==2)
      await pg.screenshot(path=f'/tmp/dv_form_{w}.png')
      await ghi('ck','Chuyển khoản hộ','3.000.000','15.000','Chuyển khoản')
      m=await ghi('ck','Rút tiền mặt','2.000.000','20.000',None)
      ok(f'[{w}] Rút tiền mặt mặc định khách Chuyển khoản', m=='Chuyển khoản', m)
      D=json.loads(await E("JSON.stringify(db.don.filter(d=>d.ngay===todayIso()).map(d=>[d.ten,d.tt]))"))
      ok(f'[{w}] Lưu đúng cách trả từng đơn', D==[['Thu hộ tiền điện','Tiền mặt'],['Chuyển khoản hộ','Chuyển khoản'],['Rút tiền mặt','Chuyển khoản']], D)
      k=json.loads(await E("JSON.stringify(ketNgay(todayIso()))"))
      ok(f'[{w}] Két tiền mặt = 1.010.000 − 2.000.000 rút = −990.000', k['tm']==-990000, k)
      ok(f'[{w}] TK nhận = 3.015.000 + 2.020.000 = 5.035.000', k['ck']==5035000, k)
      r=json.loads(await E("JSON.stringify(sumRange(todayIso(),todayIso()))"))
      ok(f'[{w}] Tổng tiền thu = tiền mặt + TK (4.045.000)', r['dt']+r['th']==k['tm']+k['ck']==4045000, (r,k))
      ok(f'[{w}] Doanh thu/lời chỉ phí 45.000', r['dt']==45000 and r['loi']==45000, r)
      await E("homeD='today';go('home');render()"); await pg.wait_for_timeout(300)
      t=await E("(document.querySelector('.hmo .thl')||{}).innerText||''")
      ok(f'[{w}] Trang chủ tách Tiền mặt vào két / Chuyển khoản vào TK / Rút tiền mặt', 'Tiền mặt vào két' in t and '5.035.000' in t and 'Rút tiền mặt' in t and '4.045.000' in t, t)
      await pg.screenshot(path=f'/tmp/dv_home_{w}.png')
      # đơn rút cũ ghi Tiền mặt: giữ cách tính cũ
      await E("db.don.push({id:'old1',ngay:todayIso(),gio:'8:00',loai:'ck',ten:'Rút tiền mặt',soTien:500000,giaBan:5000,giaVon:0,tt:'Tiền mặt',huy:null})")
      k2=json.loads(await E("JSON.stringify(ketNgay(todayIso()))")); r2=json.loads(await E("JSON.stringify(sumRange(todayIso(),todayIso()))"))
      ok(f'[{w}] Đơn rút cũ (tiền mặt) vẫn tính như trước: két −495.000', k2['tm']-k['tm']==-495000 and k2['ck']==k['ck'], (k,k2))
      ok(f'[{w}] Vẫn khớp Tổng tiền thu', r2['dt']+r2['th']==k2['tm']+k2['ck'], (r2,k2))
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang', W<=w+2, W)
      ok(f'[{w}] Không lỗi console', not errs, errs); await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
asyncio.run(main())
