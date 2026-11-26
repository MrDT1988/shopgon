# 26/11 anh Thái — 3 vấn đề vận hành: (1) thu hộ/chuyển tiền dòng riêng + Tổng tiền thu khớp két · (2) phiếu sửa trừ kho linh kiện, 1 hóa đơn · (3) shop mẹ: Trang chủ tổng chuỗi + từng cửa hàng → chi tiết ngày + nhân viên
# Chạy: python3 -m http.server 8765 ở gốc repo
import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765'; KQ=[]
def ok(t,d,x=''): KQ.append(bool(d)); print(('✅' if d else '❌'),t,'' if d else x)
async def trang(b,w,q='?demo=1'):
    ctx=await b.new_context(viewport={'width':w,'height':844}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
    async def h(r):
        u=r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}',content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*',h); await pg.goto(URL+'/app/'+q); await pg.wait_for_timeout(1200); return ctx,pg,errs
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,1280):
      ctx,pg,errs=await trang(b,w); E=pg.evaluate
      # ---- (1) thu hộ ----
      await E("""(()=>{const t=todayIso();db.don=db.don.filter(d=>d.ngay!==t);const n=(o)=>db.don.push({id:uid(),ngay:t,gio:'9:00',huy:null,tt:'Tiền mặt',khach:'',...o});
        n({loai:'may',ten:'OPPO A6',imei:'111',giaBan:5000000,giaVon:4500000});
        n({loai:'thuho',ten:'Thu hộ Tiền điện',soTien:1250000,giaBan:10000,giaVon:0});
        n({loai:'ck',ten:'Chuyển khoản hộ',soTien:3000000,giaBan:15000,giaVon:0});
        n({loai:'ck',ten:'Rút tiền mặt',soTien:2000000,giaBan:20000,giaVon:0});homeD='today';go('home');render()})()""")
      await pg.wait_for_timeout(300)
      r=json.loads(await E("JSON.stringify(sumRange(todayIso(),todayIso()))"))
      ok(f'[{w}] Doanh thu giữ nguyên (bán + phí) = 5.045.000', r['dt']==5045000, r)
      ok(f'[{w}] Thu hộ/CK ròng = 1,25tr + 3tr − 2tr rút = 2.250.000, 3 lần', r['th']==2250000 and r['nth']==3, r)
      k=json.loads(await E("JSON.stringify(ketNgay(todayIso()))"))
      ok(f'[{w}] Tổng tiền thu = tiền mặt vào két + CK (khớp chốt két)', r['dt']+r['th']==k['tm']+k['ck']+k['no'], (r,k))
      t=await E("(document.querySelector('.hmo .thl')||{}).innerText||''")
      ok(f'[{w}] Trang chủ: dòng Thu hộ + Tổng tiền thu 7.295.000', 'Thu hộ' in t and '7.295.000' in t, t)
      ok(f'[{w}] Lời không cộng tiền thu hộ (chỉ phí)', r['loi']==500000+45000, r)
      await E("go('rpt');rptTab='ban';rptMode='ngay';render()"); await pg.wait_for_timeout(300)
      t=await E("document.getElementById('v-rpt')?document.getElementById('v-rpt').innerText:document.body.innerText")
      ok(f'[{w}] Báo cáo: có Tổng tiền thu', 'Tổng tiền thu' in t)
      # ---- (2) linh kiện ----
      await E("""(()=>{db.shop.mod=Object.assign({},db.shop.mod||{},{sua:true});db.hang=db.hang.filter(h=>h.id!=='lk1'&&h.id!=='lk2');
        db.hang.push({id:'lk1',ten:'Màn hình OPPO A78',nhom:'sua',loai:'Màn hình',giaNhap:450000,giaBan:0,sl:3,min:1},{id:'lk2',ten:'Pin OPPO A78',nhom:'sua',loai:'Pin thay thế',giaNhap:150000,giaBan:0,sl:1,min:1});
        khoHub=true;go('stock');render()})()""")
      await pg.wait_for_timeout(300)
      t=await E("document.getElementById('v-stock').innerText")
      ok(f'[{w}] Kho: có mục Tồn kho linh kiện riêng', 'Tồn kho linh kiện' in t and 'Tồn kho phụ kiện' in t, t[:300])
      await E("document.querySelector('[data-kh=\"lk\"]').click()"); await pg.wait_for_timeout(300)
      ok(f'[{w}] Bấm Tồn kho linh kiện → lọc nhóm Linh kiện', await E("hangNhom")=='sua')
      await E("more='sc';scSub='list';scL=null;go('more')"); await pg.wait_for_timeout(500)
      await E("scCur='demo3xyz12ab';scSub='xem';render()"); await pg.wait_for_timeout(300)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Phiếu Sửa xong: có ô Linh kiện đã thay', 'Linh kiện đã thay' in t and 'Màn hình OPPO A78' in t, t[-500:])
      await E("$('scThu').value='1.050.000';$('scVon').value='50.000'")
      await E("document.querySelector('[data-sclkadd=\"lk1\"]').click()"); await pg.wait_for_timeout(200)
      await E("document.querySelector('[data-sclk=\"lk1|1\"]').click()"); await pg.wait_for_timeout(200)
      await E("$('scLkQ').value='pin';$('scLkQ').dispatchEvent(new Event('input',{bubbles:true}))"); await pg.wait_for_timeout(100)
      await E("document.querySelector('[data-sclkadd=\"lk2\"]').click()"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Giữ số Thu khách sau khi chọn linh kiện', await E("$('scThu').value")=='1.050.000')
      await E("document.querySelector('[data-sclk=\"lk2|1\"]').click()"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Không cho chọn quá tồn (pin còn 1)', await E("scLkDs('demo3xyz12ab').find(x=>x.id==='lk2').sl")==1)
      n0=await E("db.don.length")
      await E("document.querySelector('[data-sctra]').click()"); await pg.wait_for_timeout(700)
      D=json.loads(await E("JSON.stringify(db.don.filter(d=>d.scMa&&d.ngay===todayIso()))"))
      bills={d.get('bill') for d in D}
      ok(f'[{w}] Trả máy ra 1 hóa đơn (3 dòng: dịch vụ + 2 linh kiện)', len(D)==3 and len(bills)==1, D)
      sl=json.loads(await E("JSON.stringify(db.hang.filter(h=>h.nhom==='sua').map(h=>[h.id,h.sl]))"))
      ok(f'[{w}] Trừ kho: màn hình 3→1, pin 1→0', ['lk1',1] in sl and ['lk2',0] in sl, sl)
      von=sum(d['giaVon'] for d in D); ban=sum(d['giaBan'] for d in D)
      ok(f'[{w}] Giá vốn = 2×450k + 150k + 50k khác = 1.100.000; thu 1.050.000', von==1100000 and ban==1050000, (von,ban))
      rc=await E("document.getElementById('rc')&&!document.getElementById('rc').hidden?document.getElementById('rc').innerText:''")
      ok(f'[{w}] Hóa đơn mở, dòng linh kiện không ghi giá', 'Linh kiện: Màn hình OPPO A78 ×2' in rc, rc[:400])
      await pg.screenshot(path=f'/tmp/vh_rc_{w}.png')
      # hủy đơn → hoàn kho
      bid=list(bills)[0]
      await E(f"""(()=>{{db.don.filter(x=>x.bill==='{bid}').forEach(x=>{{x.huy='test';if(x.hangId){{const h=db.hang.find(o=>o.id===x.hangId);if(h)h.sl+=x.sl||1}}}})}})()""")
      r2=json.loads(await E("JSON.stringify(sumRange(todayIso(),todayIso()))"))
      ok(f'[{w}] Đếm đơn: dòng linh kiện không thành "đơn khác"', r2['n']==r['n'], (r2,r))
      ok(f'[{w}] Không lỗi console (1+2)', not errs, errs)
      await E("$('rc').hidden=true")
      # ---- (3) chuỗi ----
      await E("CS.ky='hn';go('home');render()"); await pg.wait_for_timeout(300)
      t=await E("(document.querySelector('.cshp')||{}).innerText||''")
      ok(f'[{w}] Trang chủ shop mẹ: Tổng doanh thu + 3 cửa hàng', 'Tổng doanh thu' in t and 'LK Mobile Chợ Gạo' in t and 'Gò Đen' in t and 'shop mẹ' in t, t)
      await pg.screenshot(path=f'/tmp/vh_home_{w}.png',full_page=True)
      await E("document.querySelector('[data-cshky=\"th\"]').click()"); await pg.wait_for_timeout(200)
      ok(f'[{w}] Đổi kỳ Tháng ngay trên Trang chủ', await E("CS.ky")=='th')
      await E("document.querySelector('[data-cshsel=\"lk.chogao@gmail.com\"]').click()"); await pg.wait_for_timeout(400)
      t=await E("document.getElementById('v-more').innerText")
      ok(f'[{w}] Bấm Chợ Gạo → chi tiết: nhân viên + từng ngày', 'Nhân viên' in t and 'Ngọc Hân' in t and 'Doanh thu từng ngày' in t and dmy_today(t), t[:500])
      W=await E("document.documentElement.scrollWidth"); ok(f'[{w}] Không tràn ngang', W<=w+2, W)
      await pg.screenshot(path=f'/tmp/vh_ct_{w}.png',full_page=True)
      so=json.loads(await E("JSON.stringify(csTom())"))
      ok(f'[{w}] Shop con gửi số theo NV (không IMEI/khách), ngày có ô thu hộ', 'nv' in so and len(json.dumps(so))<45000 and 'imei' not in json.dumps(so).lower() and len(so['ngay'][await E('todayIso()')])==5, len(json.dumps(so)))
      ok(f'[{w}] Không lỗi console (3)', not errs, errs)
      await ctx.close()
    print(f'{sum(KQ)}/{len(KQ)}')
def dmy_today(t): return 'hôm nay' in t
asyncio.run(main())
