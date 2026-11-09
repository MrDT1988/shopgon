# Test 09/11 — LỚP 6: sao lưu mã hoá ngoài Gmail shop (máy chủ + Drive giả lập, không đụng tài khoản thật).
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-sao-luu-ma-hoa.py
import asyncio, json, sys, hashlib
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
SV = {}   # máy chủ giả: ma -> {xac, ban:{id:(ngay,nam,d)}}
GUI = []
def may_chu(body):
    d = json.loads(body or '{}'); a = d.get('act')
    if a == 'bk':
        GUI.append(d); bam = hashlib.sha256(('shopgon|' + d['xac']).encode()).hexdigest(); x = SV.get(d['ma'])
        if x and x['xac'] != bam: return {'ok': False, 'msg': 'Mã shop này đã có Mã khôi phục khác'}
        x = x or {'xac': bam, 'ban': {}}; SV[d['ma']] = x; x['ban'][d['ngay'] + '_' + str(d['nam'])] = (d['ngay'], str(d['nam']), d['d']); return {'ok': True}
    if a in ('bkds', 'bklay'):
        x = SV.get(d.get('ma'))
        if not x: return {'ok': False, 'msg': 'Không thấy bản sao nào của mã shop này'}
        if x['xac'] != hashlib.sha256(('shopgon|' + d['xac']).encode()).hexdigest(): return {'ok': False, 'msg': 'Sai Mã khôi phục'}
        if a == 'bkds': return {'ok': True, 'ds': [{'id': k, 'ngay': v[0], 'nam': v[1], 'kb': len(v[2]) // 1365} for k, v in x['ban'].items()]}
        return {'ok': True, 'd': x['ban'][d['id']][2]}
    return {'status': 'active', 'shop': 'Shop Test', 'ok': True}

def lam_h(D):
    async def h(r):
        u = r.request.url
        if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
        if 'localhost' in u: return await r.continue_()
        if 'script.google.com' in u: return await r.fulfill(body=json.dumps(may_chu(r.request.post_data)), content_type='application/json')
        if 'googleapis.com' in u:
            try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
            except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
        await r.abort()
    return h
CHO = "async()=>{for(let i=0;i<80&&GG.busy;i++)await new Promise(r=>setTimeout(r,100))}"

async def mo(b, D, mail, w=390):
    ctx = await b.new_context(viewport={'width': w, 'height': 800}); await ctx.route('**/*', lam_h(D)); pg = await ctx.new_page()
    await pg.goto(URL + '/khong-co')
    await pg.evaluate("m=>{localStorage.clear();localStorage.setItem('shopgon_gg',JSON.stringify({email:m}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:m,x:Date.now()+3e6}))}", mail)
    await pg.goto(URL + '/app/'); await pg.wait_for_timeout(4000); return ctx, pg

async def main():
    errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        D1 = Drive(); ctx, pg = await mo(b, D1, 'cu@shopgon.vn'); E = pg.evaluate; pg.on('pageerror', lambda e: errs.append(str(e)))
        await E("async()=>{for(let i=0;i<30;i++)db.don.push({id:'don-'+i,bill:'don-'+i,ngay:todayIso(),gio:'9:00',loai:'pk',ten:'Ốp '+i,sl:1,giaBan:100000+i,giaVon:30000,tt:'Tiền mặt',huy:null});save();clearTimeout(GG.timer)}")
        await E(CHO); await E("async()=>{clearTimeout(GG.timer);await GG.push()}")
        # mở panel Sổ dữ liệu · Sao lưu
        await E("()=>{more='solieu';go('more')}"); await pg.wait_for_timeout(300)
        ok('Panel có mục Sao lưu ngoài Gmail', await pg.locator('[data-bk="bat"]').count() == 1)
        await pg.click('[data-bk="bat"]'); await pg.wait_for_timeout(200)
        mc = await E("()=>BK.moi")
        ok('Tạo Mã shop SG+6 và Mã khôi phục 16 ký tự', mc and len(mc['ma']) == 8 and len(mc['code']) == 16 and mc['ma'].startswith('SG'), mc)
        await pg.click('[data-bk="luu"]'); await pg.wait_for_timeout(300)
        ok('Chưa tích "đã cất mã" thì không bật', not await E("()=>!!(db.shop.bk&&db.shop.bk.ma)"))
        await pg.check('#bkDaCat'); await pg.click('[data-bk="luu"]')
        for _ in range(60):
            await pg.wait_for_timeout(200)
            if GUI: break
        await pg.wait_for_timeout(500)
        ok('Bật xong: gửi bản sao đầu tiên lên máy chủ', len(GUI) == 1 and GUI[0]['ma'] == mc['ma'], len(GUI))
        g = GUI[0] if GUI else {}
        ok('Máy chủ KHÔNG thấy nội dung (không có tên hàng, không có mã khôi phục)', g and 'Ốp' not in g['d'] and mc['code'] not in json.dumps(g) and 'don-1' not in g['d'])
        ok('Ghi ngày gửi, mã lưu trong sổ shop', await E("()=>db.shop.bk.ngay===todayIso()&&db.shop.bk.code.length===16"))
        n0 = len(GUI); await E("()=>BK.gui()"); await pg.wait_for_timeout(500)
        ok('Mỗi ngày chỉ gửi tự động 1 lần', len(GUI) == n0)
        w = await E("()=>document.documentElement.scrollWidth<=innerWidth+1"); ok('Panel 390px không tràn ngang', w)
        ma, code = mc['ma'], mc['code']
        await ctx.close()
        # MẤT GMAIL: shop đăng nhập Gmail MỚI, Drive mới trống
        D2 = Drive(); ctx2, p2 = await mo(b, D2, 'moi@shopgon.vn', 1280); E2 = p2.evaluate; p2.on('pageerror', lambda e: errs.append(str(e)))
        ok('Gmail mới: sổ trống', await E2("()=>db.don.length") == 0)
        r = await E2("async c=>{try{await BK.ds(c[0],'AAAABBBBCCCCDDDD');return 'khong-loi'}catch(e){return e.message}}", [ma, code])
        ok('Sai Mã khôi phục → báo sai, không lấy được', 'Sai' in r, r)
        r = await E2("async c=>{try{await BK.khoa(c[0],c[1]);const L=await BK.ds(c[0],c[1].toLowerCase().replace(/(.{4})/g,'$1-'));return L}catch(e){return e.message}}", [ma, code])
        ok('Đúng mã (gõ thường, có gạch) → thấy bản sao', isinstance(r, list) and len(r) == 1, r)
        await E2(CHO)
        kq = await E2("async c=>{try{const L=await BK.ds(c[0],c[1]);await BK.khoiPhuc(c[0],c[1],L[0].id);return db.don.map(x=>x.id).length}catch(e){return e.message}}", [ma, code])
        ok('Khôi phục: đủ 30 đơn về máy', kq == 30, kq)
        await E2(CHO); await E2("async()=>{clearTimeout(GG.timer);await GG.push()}"); await p2.wait_for_timeout(500)
        tren = json.dumps([f['sheets'] for f in D2.f.values()], ensure_ascii=False)
        ok('Khôi phục: dữ liệu lên Drive của Gmail mới', 'don-29' in tren and 'don-0' in tren)
        ok('Sau khôi phục: tiếp tục sao lưu bằng mã cũ', await E2("c=>db.shop.bk&&db.shop.bk.ma===c", ma))
        n1 = len(GUI); r = await E2("async()=>{try{return await BK.gui(true)}catch(e){return e.message}}")
        ok('Gmail mới gửi tiếp được vào mã cũ', r is True and len(GUI) == n1 + 1, r)
        r = await E2("async c=>{try{db.shop.bk={ma:c,code:'ZZZZZZZZZZZZZZZZ'};return await BK.gui(true)}catch(e){return e.message}}", ma)
        ok('Mã khôi phục khác không ghi đè được mã shop', 'khác' in str(r), r)
        await ctx2.close()
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ)); sys.exit(0 if all(KQ) else 1)
asyncio.run(main())
