# 07/11 22h anh Thái: gói rời 10 nhân viên 500k/năm (tổng 10 NV, hạn 1 năm từ ngày mua, anh duyệt tay)
import asyncio,sys,os
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp';W=int(sys.argv[2]) if len(sys.argv)>2 else 390;QR=sys.argv[3] if len(sys.argv)>3 else ''
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':W,'height':900},device_scale_factor=2);errs=[];ok=0
    pg.on('pageerror',lambda e:errs.append(str(e)))
    async def h(r):
      u=r.request.url
      if 'qrcode' in u.lower() and QR: await r.fulfill(path=QR,content_type='application/javascript')
      elif 'localhost' in u: await r.continue_()
      else: await r.abort()
    await pg.route('**/*',h)
    await pg.goto('http://localhost:8765/app/?demo=1');await pg.wait_for_timeout(1500)
    E=pg.evaluate
    base="NV=null;db.sample=false;XEM=false;GG.token='t'.repeat(40);nvGoiMo=false;"
    nv=lambda n:"db.shop.nv=["+",".join(f"{{sdt:'09000000{i:02d}',ten:'NV {i}',coMk:1}}" for i in range(n))+"];"
    shot=lambda t:pg.locator('.nvgoi').screenshot(path=os.path.join(OUT,f'goi_nv_{t}_{W}.png'))
    hide="document.querySelectorAll('body *').forEach(e=>{const c=getComputedStyle(e);if(c.position==='fixed'||c.position==='sticky')e.style.display='none'})"
    # 1. chưa có gói: tối đa 3
    r=await E(base+"XLIC=null;"+nv(3)+"more='nvch';go('more');[nvMax(),!!document.getElementById('fNvAdd'),document.querySelector('.nvgoi button').textContent,document.getElementById('v-more').textContent.includes('Đã đủ 3/3')]")
    print('chưa gói',r);ok+=r[0]==3 and not r[1] and 'Mua' in r[2] and r[3]
    # 2. bấm Mua: QR 500k, nội dung SG NV <sdt>
    await E("GG.email='lkmobile.store@gmail.com';XLIC={status:'active',sdt:'0909123456',bank:{nh:'MB Bank',acc:'0123456789',bin:'970422',name:'SHOP TEST'}};render()")
    await pg.click('[data-nvgoi]');await pg.wait_for_timeout(900)
    r=await E("[document.querySelector('.nvgoi .qri').textContent,!!document.querySelector('#nvQr canvas,#nvQr img')]")
    print('QR',r);ok+='500.000' in r[0] and 'GOI 10 NV' in r[0]
    await E(hide);await shot('mua')
    # 3. gói còn hạn: tổng 10
    await E(base+"XLIC={status:'active',nvMax:10,nvHan:'2027-11-07'};"+nv(3)+"render()")
    r=await E("[nvMax(),!!document.getElementById('fNvAdd'),document.getElementById('v-more').textContent.includes('Đang có 3/10'),document.querySelector('.nvgoi').classList.contains('on')]")
    print('còn hạn',r);ok+=r[0]==10 and r[1] and r[2] and r[3]
    await E(hide);await shot('con')
    # 4. hết hạn: về 3, báo khoá NV thứ 4+
    await E(base+"XLIC={status:'active',nvMax:3,nvHan:'2026-01-01'};"+nv(5)+"render()")
    r=await E("[nvMax(),document.querySelector('.nvgoi').textContent]")
    print('hết hạn',r[0]);ok+=r[0]==3 and 'thứ 4' in r[1] and 'Hết hạn' in r[1]
    await E(hide);await shot('het')
    tr=await E('document.documentElement.scrollWidth>innerWidth');print('tràn',tr);ok+=not tr
    print('KẾT QUẢ',f'{ok}/5','errs',errs);await b.close()
asyncio.run(main())
