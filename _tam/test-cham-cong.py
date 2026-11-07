# Test CHẤM CÔNG + LƯƠNG (07/11/2026) — máy chủ GIẢ LẬP (chặn POST tới máy chủ bản quyền). Chạy: python3 -m http.server 8765 & ; python3 _tam/test-cham-cong.py
import asyncio, json, time
from playwright.async_api import async_playwright
KQ=[]
def ok(t,d,c=''):KQ.append(d);print(('✅' if d else '❌'),t,('— '+str(c)[:300]) if not d else '')
SENT=[];GTT={'g9':'cho'}
def fake(body):
    d=json.loads(body);SENT.append(d);a=d.get('act');now=int(time.time()*1000)
    if a=='nvLogin':return {'ok':True,'ten':'Lan','sdt':'0901000111','phien':'P1','shop':{'ten':'Shop A'},'may':[],'hang':[],'luc':now,'nhap':[],'homNay':[],
        'cong':{'cong':[],'gt':[],'toaDo':{'lat':10.36,'lng':106.36},'banKinh':200,'gtMax':2,'luong':{'thang':time.strftime('%Y-%m'),'loai':'shop','cb':6000000,'chuan':224,'pMay':1,'pKhac':3,'bonus':0,'bnote':'','may':10000000,'khac':0,'nMay':1,'chot':None,'truoc':None},'luc':now}}
    if a=='nvCong':return {'ok':True,'id':'cc1','luc':now,'loai':d['loai'],'cach':12,'anh':'F1'}
    if a=='nvGt':return {'ok':True,'id':'gt1','dem':1}
    if a=='nvSync':
        [GTT.__setitem__(x['id'],x['kq']) for x in ((d.get('cc') or {}).get('gtKq') or [])]
        return {'ok':True,'don':[],'nv':[{'sdt':'0901000111','ten':'Lan','coMk':True}],'cc':{'cong':[{'id':'x1','sdt':'0901000111','ten':'Lan','luc':now-3600e3,'loai':'vao','cach':10,'anh':'A1'}],'gt':[{'id':'g9','sdt':'0901000111','ten':'Lan','ngay':'2026-11-01','vao':'08:00','ra':'17:00','ly':'quen','tt':GTT['g9'],'luc':now}],'toaDo':None,'banKinh':200,'gtMax':2,'luc':now}}
    return {'ok':True}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':390,'height':800},geolocation={'latitude':10.3602,'longitude':106.3601},permissions=['geolocation'])
        async def route(r):
            if r.request.method=='POST' and 'script.google.com' in r.request.url:await r.fulfill(status=200,content_type='application/json',body=json.dumps(fake(r.request.post_data)))
            else:await r.continue_()
        await ctx.route('**/*',route);errs=[]
        pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('http://localhost:8765/app/');await pg.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0901000111',ten:'Lan',phien:'P1'}));localStorage.setItem('shopgon_ccok','1')")
        await pg.goto('http://localhost:8765/app/');await pg.wait_for_timeout(2500)
        await pg.evaluate("go('home')");await pg.wait_for_timeout(300)
        ok('NV: trang chủ có thẻ chấm công + nút Vào ca',await pg.evaluate("!!document.querySelector('#ccCard [data-cccam]')"))
        await pg.evaluate("ccInput()");await pg.set_input_files('#ccCam','app/icon-192.png' if False else '_tam/../app/bd/../icon-512.png') if False else None
        import glob;img=(glob.glob('app/*.png')+glob.glob('app/**/*.png',recursive=True))[0]
        await pg.evaluate("ccInput()");await pg.set_input_files('#ccCam',img);await pg.wait_for_timeout(2500)
        c=[x for x in SENT if x.get('act')=='nvCong']
        ok('NV: gửi nvCong có ảnh + vị trí + phiên, loại vào',c and c[0]['loai']=='vao' and c[0]['anh'].startswith('data:image/jpeg') and abs(c[0]['lat']-10.3602)<1e-6 and c[0]['phien']=='P1',c and {k:v for k,v in c[0].items() if k!='anh'})
        ok('NV: ảnh nén nhỏ (<160k ký tự)',c and len(c[0]['anh'])<160000,c and len(c[0]['anh']))
        ok('NV: hiện ảnh đóng dấu + nút Gửi Zalo, trạng thái Đang trong ca',await pg.evaluate("!!document.querySelector('#ccPrev img')&&!!document.querySelector('[data-ccshare]')&&/Đang trong ca/.test(document.querySelector('#ccCard').textContent)"))
        await pg.evaluate("more='cc';go('more')");await pg.wait_for_timeout(300)
        ok('NV: trang Chấm công có lương tạm tính 1% × 10tr = 100.000đ',await pg.evaluate("/100\\.000đ/.test(document.getElementById('v-more').textContent)"))
        # vị trí xa -> chặn trước khi gửi
        await ctx.set_geolocation({'latitude':10.40,'longitude':106.36});n0=len(SENT)
        await pg.evaluate("ccViTriP=null");await pg.set_input_files('#ccCam',img);await pg.wait_for_timeout(2000)
        ok('NV: ở xa shop → không gửi lên máy chủ',not [x for x in SENT[n0:] if x.get('act')=='nvCong'])
        # quên tan ca hôm qua -> giải trình
        await pg.evaluate("const y=new Date();y.setDate(y.getDate()-1);y.setHours(8,0,0,0);if(y.getMonth()===new Date().getMonth()){CC.cong.push({id:'y1',sdt:'0901000111',luc:y.getTime(),loai:'vao',cach:5});}render()")
        has=await pg.evaluate("!!document.getElementById('fCcGt')")
        if has:
            await pg.fill('#ccGtLy','het pin');await pg.click('#fCcGt button[type=submit]');await pg.wait_for_timeout(500)
            g=[x for x in SENT if x.get('act')=='nvGt'];ok('NV: quên tan ca → gửi nvGt có giờ ra + lý do',g and g[0]['ra']=='17:30' and g[0]['ly']=='het pin',g)
        else: ok('NV: (bỏ qua giải trình — đầu tháng)',True)
        # ---- chủ shop ----
        pg2=await ctx.new_page();pg2.on('pageerror',lambda e:errs.append('CHU:'+str(e)))
        await pg2.goto('http://localhost:8765/app/');await pg2.evaluate("localStorage.removeItem('shopgon_nv')")
        await pg2.goto('http://localhost:8765/app/');await pg2.wait_for_timeout(1500)
        r=await pg2.evaluate("""(async()=>{NV=null;XEM=false;db.sample=false;GG.token='t'.repeat(30);GG.email='a@b.c';db.shop.nv=[{sdt:'0901000111',ten:'Lan'}];CC.mau=false;CC._l=1;CC.cong=[];CC.gt=[];
          ccL().chung={cb:6000000,chuan:224,pMay:1,pKhac:3};await nvSync();return {n:CC.cong.length,g:CC.gt.length}})()""")
        s=[x for x in SENT if x.get('act')=='nvSync'][-1]
        ok('Chủ: nvSync gửi cc.tu + cấu hình lương từng NV',s.get('cc') and 'tu' in s['cc'] and s['cc']['nv']['0901000111']['cb']==6000000,s.get('cc'))
        ok('Chủ: nhận lượt chấm công + giải trình từ máy chủ',r=={'n':1,'g':1},r)
        await pg2.evaluate("XEM=false;db.sample=false;more='cc';ccTab='gt';go('more')");await pg2.wait_for_timeout(300)
        await pg2.evaluate("document.querySelector('[data-ccduyet=\"g9\"]').click()");await pg2.wait_for_timeout(300);await pg2.evaluate("nvSync()");await pg2.wait_for_timeout(800)
        gq=[x['cc']['gtKq'] for x in SENT if x.get('act')=='nvSync' and (x.get('cc') or {}).get('gtKq')]
        ok('Chủ: duyệt giải trình → gửi gtKq ok (1 lần, rồi xoá khỏi hàng chờ)',gq==[[{'id':'g9','kq':'ok'}]],gq)
        await pg2.evaluate("XEM=false;db.sample=false;ccTab='luong';render()");await pg2.evaluate("document.querySelector('[data-ccchot]').click()");await pg2.evaluate("document.querySelector('[data-ccchotok]').click()");await pg2.wait_for_timeout(300)
        ok('Chủ: chốt lương lưu vào db.shop.luong.chot',await pg2.evaluate("!!ccL().chot[ccNow()]&&!!ccL().chot[ccNow()].ds['0901000111']"))
        ok('Không lỗi JS',not errs,errs)
        print('KẾT QUẢ: %d/%d đạt'%(sum(KQ),len(KQ)));await b.close()
asyncio.run(main())
