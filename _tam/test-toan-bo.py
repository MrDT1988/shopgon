# Bộ test toàn bộ Shop Gọn (26/10/2026) — chạy: python3 _tam/test-toan-bo.py  (cần: cd repo && python3 -m http.server 8765)
import asyncio, json, sys
from playwright.async_api import async_playwright

URL = 'http://localhost:8765'
KQ = []
def ok(ten, dk, chi_tiet=''):
    KQ.append((ten, bool(dk), chi_tiet)); print(('✅' if dk else '❌'), ten, ('— ' + str(chi_tiet)) if chi_tiet and not dk else '')

async def trang(b, path, dev=None):
    ctx = await b.new_context(**(dev or {'viewport': {'width': 390, 'height': 844}}))
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    async def h(r):
        u = r.request.url
        if 'ver.json' in u: await r.fulfill(body='{}', content_type='application/json')
        elif 'localhost' in u: await r.continue_()
        else: await r.abort()
    await pg.route('**/*', h)
    await pg.goto(URL + path); await pg.wait_for_timeout(900)
    return ctx, pg, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx, pg, errs = await trang(b, '/app/?demo=1'); E = pg.evaluate
        S = lambda js: E('JSON.stringify(' + js + ')')

        # 1. Mở từng tab, không lỗi, không tràn ngang
        for v in ['home', 'sell', 'add', 'stock', 'more']:
            await E(f"go('{v}')"); await pg.wait_for_timeout(150)
            w = await E("document.documentElement.scrollWidth")
            ok(f'Tab {v} mở được, không tràn ngang', w <= 392 and not errs, f'width {w} {errs}')
        for m in ['look', 'hist', 'chi', 'set', 'tien', 'nvch']:
            await E(f"more='{m}';go('more')"); await pg.wait_for_timeout(120)
            ok(f'Thêm › {m} mở được', not errs, errs)

        # 2. Nhập phiếu: máy theo màu + phụ kiện
        await E("go('add');addTab='moi';addMode='may';render()")
        await pg.click('#aTen'); await pg.type('#aTen', 'a7 pro 5g', delay=10); await pg.wait_for_timeout(1200)
        sug = await E("[...document.querySelectorAll('#aSug b')].map(x=>x.textContent)")
        ok('Gợi ý tên máy có cấu hình + màu', any('8/128GB - ' in x for x in sug), sug[:3])
        await pg.fill('#aImei', '860000000001001\n860000000001019'); await pg.fill('#aGN', '10.000.000')
        await pg.click('#fAdd button[type=submit]'); await pg.wait_for_timeout(200)
        ok('Chặn nhập máy thiếu cấu hình/màu', 'cấu hình' in (await pg.text_content('#aErr') or ''))
        await pg.locator('[data-sug]').first.click(); await pg.click('#fAdd button[type=submit]'); await pg.wait_for_timeout(200)
        await E("addMode='hang';render()"); await pg.fill('#hTen', 'Ốp test'); await pg.fill('#hSl', '10'); await pg.fill('#hGN', '20.000')
        await pg.click('#fAddH button[type=submit]'); await pg.wait_for_timeout(200)
        await pg.click('[data-pnsave]'); await pg.wait_for_timeout(300)
        r = json.loads(await S("{may:db.may.filter(m=>m.imei.startsWith('8600000000010')).map(m=>m.ten+'|'+m.tt),op:(db.hang.find(h=>h.ten==='Ốp test')||{}).sl,pn:db.pn.length}"))
        ok('Lưu phiếu: 2 máy vào kho', len(r['may']) == 2 and all(x.endswith('|ton') for x in r['may']), r)
        ok('Lưu phiếu: phụ kiện vào kho đúng SL', r['op'] == 10, r)
        ten_may = r['may'][0].split('|')[0]
        ok('Nhập hàng có ô giá nhập + giá bán (máy, phụ kiện, dòng phiếu)', await E("go('add');addMode='may';render();const a=!!document.getElementById('aGB');addMode='hang';render();const b=!!document.getElementById('hGB');addMode='may';render();a&&b"))
        # 2b. Giá bán đặt 1 chỗ ở Kho
        hid = await E("db.hang.find(h=>h.ten==='Ốp test').id")
        await E("go('stock');khoTab='kho';stockMode='hang';render()"); await pg.fill(f'[data-kgh="{hid}"]', '50.000'); await pg.press(f'[data-kgh="{hid}"]', 'Tab'); await pg.wait_for_timeout(150)
        ok('Kho: sửa giá phụ kiện', await E(f"db.hang.find(h=>h.id==='{hid}').giaBan") == 50000)
        await E(f"stockMode='may';stockBrand=db.may.find(m=>m.ten==={ten_may!r}).hang;render()"); await pg.fill(f'[data-kgm="{ten_may}"]', '12.000.000'); await pg.press(f'[data-kgm="{ten_may}"]', 'Tab'); await pg.wait_for_timeout(150)
        ok('Kho: sửa giá mẫu máy áp mọi máy', await E(f"db.may.filter(m=>m.ten==={ten_may!r}&&m.tt==='ton').every(m=>m.giaBan===12000000)"))
        # 2c. Khuyến mãi tự gắn vào đơn
        await E("go('km')"); await pg.wait_for_timeout(300)
        g = await E(f"gk({ten_may!r})")
        await pg.click(f'[data-kmadd="g|{g}"]'); await pg.fill('#kmGt', '200.000'); await pg.click('#fKm button[type=submit]'); await pg.wait_for_timeout(150)
        ok('KM: thẻ web có chip KM vừa thêm', await E(f"[...document.querySelectorAll('.wchip')].some(c=>c.textContent.includes('200k'))"))
        await pg.click(f'[data-kmadd="g|{g}"]'); await pg.click('[data-kml=tg]'); await pg.click('#fKm button[type=submit]'); await pg.wait_for_timeout(150)
        ok('KM: trả góp 0% lưu, không đổi giá', await E("db.shop.km.some(k=>k.loai==='tg')"))
        im = await E(f"db.may.find(m=>m.ten==={ten_may!r}&&m.tt==='ton').imei")
        await E(f"cart=[];sellImei='{im}';sellMode='may';go('sell')"); await pg.click('#fSell button[type=submit]'); await pg.wait_for_timeout(150)
        ok('Bán: KM tự gắn vào đơn', await E("cartTotal()") == 11800000, await E("cartTotal()"))
        await E("cartOpen=true;render()"); await pg.click('[data-cartdel="0"]'); ok('Bỏ máy → bỏ luôn KM', await E("cart.length") == 0)
        await E("db.shop.km=[];khoTab='kho';save();go('add')")

        # 3. Sửa phiếu: +1 phụ kiện, bỏ 1 IMEI, Thôi giữ nguyên rồi sửa thật
        pid = await E("db.pn[db.pn.length-1].id")
        await E("addTab='da';render()"); await pg.click(f'[data-pnedit="{pid}"]'); await pg.wait_for_timeout(200)
        await pg.click('[data-pnclear]'); await pg.wait_for_timeout(200)
        r = json.loads(await S("{op:db.hang.find(h=>h.ten==='Ốp test').sl,n:db.may.filter(m=>m.imei.startsWith('8600000000010')).length,pn:db.pn.length}"))
        ok('Sửa phiếu › Thôi: kho giữ nguyên', r['op'] == 10 and r['n'] == 2, r)
        await E("addTab='da';render()"); await pg.click(f'[data-pnedit="{pid}"]'); await pg.wait_for_timeout(200)
        i_pk = await E("PN.dong.findIndex(d=>d.t==='hang')"); i_m = await E("PN.dong.findIndex(d=>d.t==='may')")
        await pg.click(f'[data-pnsl="{i_pk}"][data-dx="1"]'); await pg.click(f'[data-pnimx="{i_m}"][data-k="1"]'); await pg.click('[data-pnsave]'); await pg.wait_for_timeout(200)
        r = json.loads(await S("{op:db.hang.find(h=>h.ten==='Ốp test').sl,n:db.may.filter(m=>m.imei.startsWith('8600000000010')).length,id:db.pn[db.pn.length-1].id}"))
        ok('Sửa phiếu: +1 phụ kiện, bỏ 1 IMEI, giữ mã phiếu', r['op'] == 11 and r['n'] == 1 and r['id'] == pid, r)
        # 2a2. (04/11) Nhập kèm giá bán → áp mọi máy cùng mẫu + phụ kiện
        await E("PN={dong:[],ncc:'',ngay:''};pnSave();go('add');addTab='moi';addMode='may';render()")
        await pg.fill('#aTen', ten_may); await pg.dispatch_event('#aTen','input'); await E("$('aSug')&&($('aSug').hidden=true)")
        await pg.fill('#aImei', '860000000002009'); await pg.fill('#aGN', '9.000.000'); await pg.fill('#aGB', '13.500.000')
        await pg.click('#fAdd button[type=submit]'); await pg.wait_for_timeout(150)
        await E("addMode='hang';render()"); await pg.fill('#hTen', 'Kính test'); await pg.fill('#hSl', '2'); await pg.fill('#hGN', '20.000'); await pg.fill('#hGB', '45.000')
        await pg.click('#fAddH button[type=submit]'); await pg.wait_for_timeout(150)
        await pg.click('[data-pnsave]'); await pg.wait_for_timeout(300)
        r = json.loads(await S(f"{{may:db.may.filter(m=>m.ten==={ten_may!r}&&m.tt==='ton').map(m=>m.giaBan),op:db.hang.find(h=>h.ten==='Kính test').giaBan,tay:!!(db.shop.giaTay||{{}})[gk({ten_may!r})]}}"))
        ok('Nhập kèm giá bán: áp mọi máy cùng mẫu + phụ kiện, giữ giá shop', len(r['may']) >= 2 and all(x == 13500000 for x in r['may']) and r['op'] == 45000 and r['tay'], r)

        # 4. Bán: máy + 2 ốp + KM giảm + tặng
        await E("go('sell')"); await pg.fill('#sImei', '860000000001001'); await pg.wait_for_timeout(150)
        await pg.fill('#sGia', '12.000.000'); await pg.click('#fSell button[type=submit]'); await pg.wait_for_timeout(150)
        hid = await E("db.hang.find(h=>h.ten==='Ốp test').id")
        await E(f"cart.push({{type:'hang',hangId:'{hid}',ten:'Ốp test',nhom:'pk',gia:50000,von:20000,sl:2}});render()")
        await E("cartOpen=true;render()"); await pg.click('[data-kmo]'); await pg.click('[data-kmgiam="200000"]')
        await E("cartOpen=true;render()"); await pg.click('[data-kmo]'); await pg.click('[data-kmtab="qua"]'); await pg.fill('#kmQua', 'Dán màn'); await pg.fill('#kmVon', '15000'); await pg.click('[data-kmqua]')
        tong = await E("cartTotal()")
        ok('Giỏ hàng: tổng = 12tr + 100k − 200k', tong == 11900000, tong)
        dt0 = await E("live().filter(d=>d.ngay===todayIso()&&d.loai!=='thu').reduce((s,d)=>s+d.giaBan,0)")
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(300)
        bill = await E("rcId")
        ok('In hóa đơn hiện ra', await E("!$('rc').hidden"))
        r = json.loads(await S(f"{{may:db.may.find(m=>m.imei==='860000000001001').tt,op:db.hang.find(h=>h.id==='{hid}').sl,lines:db.don.filter(d=>d.bill==='{bill}').length,loi:db.don.filter(d=>d.bill==='{bill}').reduce((s,d)=>s+profitOf(d),0)}}"))
        ok('Bán: máy chuyển "đã bán", ốp trừ 2', r['may'] == 'ban' and r['op'] == 9, r)
        ok('Bán: lời = 12tr−10tr + 60k − 200k − 15k', r['loi'] == 2000000 + 60000 - 200000 - 15000, r)
        dt1 = await E("live().filter(d=>d.ngay===todayIso()&&d.loai!=='thu').reduce((s,d)=>s+d.giaBan,0)")
        ok('Doanh thu hôm nay cộng đúng', dt1 - dt0 == 11900000, dt1 - dt0)
        await E("$('rc').hidden=true")

        # 5. Trả hàng từ màn Bán: 1 ốp + máy
        await E("sellMode='tra';trQ='860000000001001';render()")
        oid = await E(f"db.don.find(d=>d.bill==='{bill}'&&d.hangId).id")
        await pg.click(f'[data-trpick="{oid}"]'); await pg.fill('#trSl', '1'); await pg.click(f'[data-trok="{oid}"]'); await pg.wait_for_timeout(250); await E("$('rc').hidden=true")
        mid = await E(f"db.don.find(d=>d.bill==='{bill}'&&d.loai==='may').id")
        await pg.click(f'[data-trpick="{mid}"]'); await pg.click(f'[data-trok="{mid}"]'); await pg.wait_for_timeout(250); await E("$('rc').hidden=true")
        r = json.loads(await S(f"{{may:db.may.find(m=>m.imei==='860000000001001').tt,op:db.hang.find(h=>h.id==='{hid}').sl,nhan:db.don.find(d=>d.id==='{oid}').traSl}}"))
        ok('Trả hàng: máy về kho, ốp +1, ghi "đã trả 1/2"', r['may'] == 'ton' and r['op'] == 10 and r['nhan'] == 1, r)
        await E("sellMode='may'")

        # 6. Sửa đơn / Hủy / Xóa đơn
        await E(f"cart=[{{type:'may',imei:'860000000001001',ten:'{ten_may}',hang:'OPPO',gia:11000000,von:10000000,bh:12,sl:1}}];render()")
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(250); b2 = await E("rcId"); await E("$('rc').hidden=true")
        await E(f"more='hist';histDays=1;histOpen='{b2}';go('more')")
        d2 = await E(f"db.don.find(d=>d.bill==='{b2}').id")
        await pg.click(f'[data-sua="{d2}"]'); await pg.fill('#eGia', '11.500.000'); await pg.click(f'[data-suaok="{d2}"]'); await pg.wait_for_timeout(150)
        ok('Sửa đơn: đổi giá bán', await E(f"db.don.find(d=>d.id==='{d2}').giaBan") == 11500000)
        await pg.click(f'[data-xoa="{b2}"]'); await pg.click(f'[data-xoaok="{b2}"]'); await pg.wait_for_timeout(150)
        r = json.loads(await S(f"{{n:db.don.filter(d=>d.bill==='{b2}').length,tt:db.may.find(m=>m.imei==='860000000001001').tt}}"))
        ok('Xóa đơn: mất đơn, máy về kho', r['n'] == 0 and r['tt'] == 'ton', r)

        # 7. Thu cũ đổi mới
        await E("go('sell');thuOpen=true;render()")
        await pg.fill('#tTen', 'iPhone 11 cũ'); await pg.fill('#tImei', '355555555555551'); await pg.fill('#tGia', '3.000.000'); await pg.click('#fThu button[type=submit]'); await pg.wait_for_timeout(150)
        ok('Thu cũ: trừ vào đơn', await E("cartTotal()") == -3000000)
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(250); await E("$('rc').hidden=true")
        ok('Thu cũ: máy cũ vào kho', await E("!!db.may.find(m=>m.imei==='355555555555551'&&m.tt==='ton')"))

        # 8. Đổi máy
        im_a = await E("stock().find(m=>m.imei!=='355555555555551').imei"); im_b = await E(f"stock().find(m=>m.imei!=='{im_a}'&&m.imei!=='355555555555551').imei")
        await E(f"cart=[{{type:'may',imei:'{im_a}',ten:'A',hang:'OPPO',gia:5000000,von:4000000,bh:12,sl:1}}];render()")
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(250); b3 = await E("rcId"); await E("$('rc').hidden=true")
        d3 = await E(f"db.don.find(d=>d.bill==='{b3}').id")
        await E(f"more='hist';histOpen='{b3}';go('more')"); await pg.click(f'[data-doi="{d3}"]'); await pg.fill('#dMoi', im_b); await pg.click(f'[data-doiok="{d3}"]'); await pg.wait_for_timeout(200)
        r = json.loads(await S(f"[db.may.find(m=>m.imei==='{im_a}').tt,db.may.find(m=>m.imei==='{im_b}').tt]"))
        ok('Đổi máy: máy cũ chờ BH, máy mới đã bán', r == ['loi', 'ban'], r)

        # 9. Xóa IMEI trong kho
        await E("go('stock')")
        n0 = await E("db.may.filter(m=>m.tt==='ton').length")
        await E("const x=document.createElement('button');x.dataset.delimeiok='355555555555551';document.getElementById('v-stock').appendChild(x);x.click()"); await pg.wait_for_timeout(150)
        ok('Kho: xóa 1 IMEI', await E("db.may.filter(m=>m.tt==='ton').length") == n0 - 1)

        # 10. Sổ chi + chốt két
        await E("more='chi';chiSub='chi';go('more')"); await pg.fill('#chiTien', '150.000'); await pg.click('#fChi button[type=submit]'); await pg.wait_for_timeout(150)
        ok('Sổ chi: ghi khoản chi', await E("(db.chi||[]).some(c=>c.tien===150000)"))

        # --- Giao diện mới 02/11 (học Sổ Bán Hàng): trang chủ gọn · báo cáo · kho danh sách · thu chi ---
        await E("go('home')")
        ok('Trang chủ gọn: 6 lối tắt, không còn biểu đồ báo cáo', await E("document.querySelectorAll('#v-home .qg button').length===6&&!$('v-home').innerText.includes('Tình hình kinh doanh')&&!document.querySelector('#v-home .ketcard')"))
        await E("go('rpt')")
        ok('Tab Báo cáo: có biểu đồ + 3 tab', await E("$('v-rpt').innerText.includes('Tình hình kinh doanh')&&document.querySelectorAll('#v-rpt [data-rt]').length===3"))
        await E("khoHub=true;go('stock')")
        ok('Kho hàng: danh sách ≥7 mục', await E("document.querySelectorAll('#v-stock .hubl button').length>=7"))
        await pg.click('[data-kh="may"]')
        ok('Kho › Tồn kho điện thoại: có nút ‹ Kho hàng', await E("!!document.querySelector('#v-stock [data-kh=hub]')"))
        await E("khoHub=false;more='chi';chiSub='list';go('more')")
        ok('Thu chi: thẻ tổng kết + 2 nút cố định dưới đáy', await E("!!document.querySelector('.tcsum')&&document.querySelectorAll('.tcbar button').length===2"))
        await E("go('home')")

        # 11. Khách nợ
        await E(f"cart=[{{type:'hang',hangId:'{hid}',ten:'Ốp test',nhom:'pk',gia:50000,von:20000,sl:1}}];cartKhach='Anh Nợ';go('sell')")
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(200); await pg.click('[data-rcpay="no"]'); await pg.fill('#rcTra', '10.000')
        await E("document.querySelector('[data-rcdone]')&&document.querySelector('[data-rcdone]').click()"); await pg.wait_for_timeout(200)
        ok('Ghi nợ: đơn còn nợ 40k', await E("db.don.some(d=>d.khach==='Anh Nợ'&&+d.no===40000)"))

        # 11b. Khách hàng
        await E("more='kh';khQ='Chị Mai';go('more')"); await pg.wait_for_timeout(100)
        await E(f"cart=[{{type:'hang',hangId:'{hid}',ten:'Ốp test',nhom:'pk',gia:50000,von:20000,sl:1}}];cartKhach='Chị Mai';cartSdt='0909 111 222';go('sell')")
        await E("cartOpen=true;render()"); await pg.click('[data-checkout]'); await pg.wait_for_timeout(200); await E("$('rc').hidden=true")
        await E("more='kh';khQ='0909111';go('more')"); await pg.wait_for_timeout(150)
        k = await E("khachDs().find(o=>o.sdt.replace(/\\D/g,'')==='0909111222')")
        ok('Khách hàng: tự lưu theo SĐT, có lịch sử', bool(k) and await E("document.querySelectorAll('[data-khopen]').length")>=1, k and k.get('ten'))
        await pg.locator('[data-khopen]').first.click(); await pg.wait_for_timeout(100)
        ok('Khách hàng: mở chi tiết có nút Gọi/Zalo', await E("!!document.querySelector('a[href^=\"https://zalo.me/0909111222\"]')"))
        await pg.locator('#v-more .mg:has(.imeis)').first.screenshot(path='/tmp/kh.png')

        # 11c. NCC: phiếu nợ → trả tiền → trả hàng trừ nợ
        await E("go('add');addTab='moi';addMode='may';render()")
        await pg.click('#aTen'); await pg.type('#aTen', 'reno15 5g', delay=5); await pg.wait_for_timeout(600)
        await pg.locator('[data-sug]').first.click()
        await pg.fill('#aImei', '860000000002001\n860000000002019'); await pg.fill('#aGN', '8.000.000'); await pg.click('#fAdd button[type=submit]'); await pg.wait_for_timeout(150)
        await pg.fill('#pnNcc', 'NPP Test'); await pg.fill('#pnNo', '10.000.000'); await pg.click('[data-pnsave]'); await pg.wait_for_timeout(200)
        no = await E("nccDs().find(o=>o.ten==='NPP Test').no")
        ok('NCC: phiếu nhập ghi nợ 10tr', no == 10000000, no)
        chi0 = await E("(db.chi||[]).length")
        await E("more='ncc';nccOpen='NPP Test';nccAct='tien';go('more')"); await pg.fill('#nTien', '3.000.000'); await pg.click('[data-nccpay="NPP Test"]'); await pg.wait_for_timeout(150)
        r = json.loads(await S("{no:nccDs().find(o=>o.ten==='NPP Test').no,chi:(db.chi||[]).length}"))
        ok('NCC: trả tiền mặt 3tr → nợ còn 7tr, ghi Sổ chi', r['no'] == 7000000 and r['chi'] == chi0 + 1, r)
        await E("nccAct='hang';nccTra=[];renderMore()"); await pg.fill('#ntIm', '860000000002001'); await pg.wait_for_timeout(150)
        await pg.locator('#v-more .confirm').first.screenshot(path='/tmp/ncc.png')
        await pg.click('[data-nttra="NPP Test"]'); await pg.wait_for_timeout(150)
        r = json.loads(await S("{no:nccDs().find(o=>o.ten==='NPP Test').no,tt:db.may.find(m=>m.imei==='860000000002001').tt,ton:stock().some(m=>m.imei==='860000000002001')}"))
        ok('NCC: trả 1 máy → rời kho, trừ nợ 8tr (còn −1tr = NCC nợ lại)', r['no'] == -1000000 and r['tt'] == 'ncc' and not r['ton'], r)

        # 11d. Kiểm kho
        await E("KK={q:[],luc:''};kkTab='may';more='kk';go('more')")
        ton = await E("stock().map(m=>m.imei)")
        for im in ton[:-1]: await E(f"kkAdd('{im}')")
        await E("kkAdd('999999999999999')"); await pg.wait_for_timeout(150)
        r = json.loads(await S("{thieu:document.body.innerText.includes('Thiếu 1 máy'),la:document.body.innerText.includes('1 IMEI lạ')}"))
        ok('Kiểm kho: quét thiếu 1 máy + 1 IMEI lạ → báo đúng', r['thieu'] and r['la'], r)
        await pg.locator('#v-more').screenshot(path='/tmp/kk.png')
        await E("kkTab='hang';renderMore()"); hh = await E("db.hang.find(h=>h.sl>0).id")
        await pg.fill(f'[data-kkh="{hh}"]', '3'); await pg.click('[data-kkhsave]'); await pg.wait_for_timeout(100)
        ok('Kiểm kho phụ kiện: lưu số đếm', await E(f"db.hang.find(h=>h.id==='{hh}').sl") == 3)

        # 11e. Dòng mới ghi được lên Sheet (cột traSl, no, loai)
        ok('Sổ Google: có cột traSl (trả 1 phần) và no/loai (công nợ NCC)', await E("GG.cols.Don.includes('traSl')&&GG.cols.Phieu.includes('no')&&GG.cols.Phieu.includes('loai')"))

        ok('Không có lỗi JavaScript suốt luồng chủ shop', not errs, errs)

        # 12. Nhân viên: bán + KM → đồng bộ về sổ chủ
        r = await E("""(async()=>{const OWNX=JSON.parse(JSON.stringify(db));const SENT=[];window.fetch=async(u,o)=>{if(o&&o.body)SENT.push(JSON.parse(o.body));return {ok:true,json:async()=>({ok:true})}};
          NV={sdt:'0900000000',ten:'Lan'};db=nvDb({shop:OWNX.shop,may:OWNX.may.filter(m=>m.tt==='ton').map(m=>({imei:m.imei,ten:m.ten,hang:m.hang,giaBan:m.giaBan||1})),hang:OWNX.hang.filter(h=>h.sl>0)});
          const m=db.may[0],h=db.hang.find(x=>x.sl>0);cart=[{type:'may',imei:m.imei,ten:m.ten,hang:m.hang,gia:3000000,von:0,bh:12,sl:1},{type:'free',nhom:'km',ten:'🎁 Giảm giá',gia:-100000,von:0,sl:1},{type:'hang',hangId:h.id,ten:'🎁 Tặng: '+h.ten,nhom:'km',gia:0,von:0,sl:1}];go('sell');
          cartOpen=true;render();document.querySelector('[data-checkout]').click();await new Promise(r=>setTimeout(r,200));nvClose();await new Promise(r=>setTimeout(r,400));
          const o=SENT.find(x=>x.act==='nvBan');if(!o)return 'không gửi';db=OWNX;NV=null;const sl0=db.hang.find(x=>x.id===h.id).sl;nvApply(o.don);
          const L=db.don.filter(d=>d.bill===o.don.id);return JSON.stringify({n:L.length,dt:L.reduce((s,d)=>s+d.giaBan,0),may:db.may.find(x=>x.imei===m.imei).tt,pk:sl0-db.hang.find(x=>x.id===h.id).sl,von:L.find(d=>d.hangId).giaVon>0})})()""")
        try: r = json.loads(r)
        except Exception: r = {'loi': r}
        ok('Nhân viên bán (có KM) → về sổ chủ đủ 3 dòng, đúng tiền', r.get('n') == 3 and r.get('dt') == 2900000, r)
        ok('Nhân viên bán → sổ chủ trừ máy + quà, có giá vốn quà', r.get('may') == 'ban' and r.get('pk') == 1 and r.get('von'), r)

        # 12b. (02/11) Mật khẩu nhân viên: chủ đặt MK → gửi lên máy chủ 1 lần rồi xóa khỏi máy; NV gửi phiên khi bán; bị đổi MK thì thoát
        r = await E("""(async()=>{const SENT=[];let RESP={ok:true,don:[],nv:[]};window.fetch=async(u,o)=>{const b=o&&o.body?JSON.parse(o.body):{};SENT.push(b);return {ok:true,json:async()=>RESP}};
          NV=null;db.sample=false;XEM=false;GG.token='t'.repeat(40);db.shop.nv=[];localStorage.removeItem('shopgon_nvmk');more='nvch';go('more');
          $('nvTen').value='Lan';$('nvSo').value='0911222333';$('nvMk').value='';document.querySelector('#fNvAdd button[type=submit]').click();await new Promise(r=>setTimeout(r,50));
          const thieuMk=!(db.shop.nv||[]).length&&/mật khẩu/i.test($('nvAddErr').textContent);
          $('nvMk').value='lan2468';document.querySelector('#fNvAdd button[type=submit]').click();await new Promise(r=>setTimeout(r,50));
          const cho=nvMkQ()['0911222333']==='lan2468'&&!JSON.stringify(db).includes('lan2468');
          RESP={ok:true,don:[],nv:[{sdt:'0911222333',ten:'Lan',coMk:true}]};nvBusy=false;await nvSync();
          const s1=SENT.filter(x=>x.act==='nvSync').pop();const guiMk=s1&&s1.nv[0].mk==='lan2468';const xoa=!nvMkQ()['0911222333'];
          nvBusy=false;await nvSync();const s2=SENT.filter(x=>x.act==='nvSync').pop();const khongGuiLai=!s2.nv[0].mk;
          render();const nhan=document.body.innerText.includes('Đã có mật khẩu');
          NV={sdt:'0911222333',ten:'Lan',phien:'P1'};nvQSet([{id:'X1',lines:[{loai:'pk',ten:'a',giaBan:1}]}]);RESP={ok:true};await nvFlush();
          const b1=SENT.filter(x=>x.act==='nvBan').pop();const coPhien=b1&&b1.phien==='P1';
          let thoat=0;const lo=window.nvLogout;window.nvLogout=()=>{thoat++};nvLogout=window.nvLogout;
          nvQSet([{id:'X2',lines:[{loai:'pk',ten:'a',giaBan:1}]}]);RESP={ok:false,dangXuat:true,msg:'Mật khẩu đã được chủ shop đổi. Đăng nhập lại.'};await nvFlush();await new Promise(r=>setTimeout(r,1700));
          const giuDon=nvQ().length===1;NV=null;nvQSet([]);db.shop.nv=[];
          return JSON.stringify({thieuMk,cho,guiMk,xoa,khongGuiLai,nhan,coPhien,thoat,giuDon})})()""")
        try: r = json.loads(r)
        except Exception: r = {'loi': r}
        ok('Mật khẩu NV: bắt buộc khi thêm, không lưu vào sổ, gửi lên máy chủ 1 lần rồi xóa', r.get('thieuMk') and r.get('cho') and r.get('guiMk') and r.get('xoa') and r.get('khongGuiLai') and r.get('nhan'), r)
        ok('Mật khẩu NV: bán gửi kèm phiên; bị đổi MK → thoát, giữ đơn chưa gửi', r.get('coPhien') and r.get('thoat') == 1 and r.get('giuDon'), r)
        r = await E("""(async()=>{window.fetch=async()=>({ok:true,json:async()=>({ok:true,don:[],nv:[]})});NV=null;db.shop.nv=[];more='nvch';go('more');
          for(const [n,s] of [['A','0911000001'],['B','0911000002'],['C','0911000003']]){$('nvTen').value=n;$('nvSo').value=s;$('nvMk').value='1234';document.querySelector('#fNvAdd button[type=submit]').click();await new Promise(r=>setTimeout(r,30))}
          const het=!$('fNvAdd')&&document.body.innerText.includes('Đã đủ 3/3');db.shop.nv=[];localStorage.removeItem('shopgon_nvmk');return JSON.stringify({n:3,het})})()""")
        r = json.loads(r)
        ok('Nhân viên: tối đa 3/shop, đủ 3 thì ẩn ô thêm', r.get('het'), r)
        await ctx.close()

        # 12c. (02/11) Nhân viên đã đăng nhập → mở lại app vào thẳng màn Bán, không lỗi, không bắt đăng nhập lại
        ctx, pg, errs = await trang(b, '/app/')
        await pg.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0911222333',ten:'Lan',phien:'P1'}))")
        for i in range(2):
            await pg.reload(); await pg.wait_for_timeout(900)
        r = json.loads(await pg.evaluate("JSON.stringify({nv:NV&&NV.sdt,ban:!$('v-sell').hidden,login:!$('welcome').hidden,ls:!!localStorage.getItem('shopgon_nv')})"))
        ok('Nhân viên: mở lại app vẫn đăng nhập, vào thẳng màn Bán, không lỗi', r['nv'] == '0911222333' and r['ban'] and not r['login'] and r['ls'] and not errs, (r, errs))
        await ctx.close()

        # 12d. (04/11) Tài khoản test nhân viên: vào thẳng màn Bán nhân viên bằng dữ liệu mẫu, bán được, không gọi máy chủ
        ctx, pg, errs = await trang(b, '/app/')
        await pg.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0900000000',ten:'Nhân viên test',phien:'TEST',test:1}))"); await pg.reload(); await pg.wait_for_timeout(900)
        r = json.loads(await pg.evaluate("JSON.stringify({nv:!!(NV&&NV.test),may:db.may.length,ban:!$('v-sell').hidden,vonAn:db.may.every(m=>!m.giaNhap)})"))
        n0 = r['may']
        await pg.evaluate("const m=db.may[0];cart=[{type:'may',imei:m.imei,ten:m.ten,hang:m.hang,gia:m.giaBan,von:0,bh:12,sl:1}];cartOpen=true;render();document.querySelector('[data-checkout]').click()"); await pg.wait_for_timeout(200)
        await pg.evaluate("nvClose()"); await pg.wait_for_timeout(300)
        r2 = await pg.evaluate("db.may.length")
        ok('Tài khoản test nhân viên: vào màn Bán, không thấy giá vốn, bán trừ kho trên máy', r['nv'] and r['ban'] and r['vonAn'] and n0 > 0 and r2 == n0 - 1 and not errs, (r, r2, errs))
        await ctx.close()

        # 12e. (04/11) Tờ rơi: tồn nhiều 9 máy · theo hãng 6 máy
        ctx, pg, errs = await trang(b, '/app/?demo=1&test=1')
        await pg.evaluate("more='ttq';go('more')"); await pg.wait_for_timeout(200); await pg.click('[data-trnew]'); await pg.wait_for_timeout(800)
        n9 = await pg.evaluate("document.querySelectorAll('#trPv .trc').length")
        await pg.evaluate("TR.kieu='hang';TR.hang='Samsung';TR.n=6;render()"); await pg.wait_for_timeout(300)
        n6 = await pg.evaluate("[...document.querySelectorAll('#trPv .trn')].map(x=>x.textContent)")
        ok('Tờ rơi: 9 máy theo tồn kho, 6 máy theo hãng đúng hãng', n9 == 9 and len(n6) == 6 and all('Samsung' in x for x in n6) and not errs, (n9, n6, errs))
        # 12f. (04/11) 5 mẫu tờ rơi: chọn mẫu đổi lớp, nhớ mẫu, mở lại vẫn mẫu đó
        mau = []
        for m in ['xanh', 'do', 'toi', 'trang', 'tim']:
            await pg.click(f'[data-trm="{m}"]'); await pg.wait_for_timeout(150)
            mau.append(await pg.evaluate("document.querySelector('#trPv .trp').classList.contains('m-'+TR.mau)&&document.querySelector('[data-trm][aria-pressed=true]').dataset.trm===TR.mau"))
        await pg.click('[data-trm="toi"]'); await pg.evaluate("TR=null;render()"); await pg.click('[data-trnew]'); await pg.wait_for_timeout(300)
        nho = await pg.evaluate("TR.mau==='toi'&&!!document.querySelector('#trPv .m-toi')")
        r = json.loads(await pg.evaluate("""JSON.stringify((()=>{TR.kieu='ton';TR.n=9;TR.oppo=true;render();const ds=trDs(),no=ds.filter(x=>trHang(x)==='OPPO').length,dau=ds.slice(0,no).every(x=>trHang(x)==='OPPO');
          const tong=ttqMau().filter(x=>x.gb>0&&trHang(x)==='OPPO').length;const tat=!document.querySelector('[data-tro]')&&!document.querySelector('.trbox').innerText.includes('Ưu tiên OPPO');
          return {no,tong,dau,tat}})())"""))
        ok('Tờ rơi: ưu tiên OPPO — máy OPPO đứng đầu, không hiện nút', r['no'] == min(9, r['tong']) and r['tong'] > 0 and r['dau'] and r['tat'] and not errs, r)
        ok('Tờ rơi: 5 mẫu chọn được, nhớ mẫu đã chọn', all(mau) and nho and not errs, (mau, nho, errs))
        await ctx.close()

        # 12g. (04/11) Nhân viên nhập hàng (không giá) → gửi phiếu (máy chủ giả) → chủ nhận → duyệt → kho tăng đúng, giá đúng; trả lại → nhapKq
        ctx, pg, errs = await trang(b, '/app/?demo=1&test=1')
        r = await pg.evaluate("""(async()=>{const OWNX=JSON.parse(JSON.stringify(db));const SENT=[];let RESP={ok:true};window.fetch=async(u,o)=>{const x=o&&o.body?JSON.parse(o.body):{};SENT.push(x);return {ok:true,json:async()=>RESP}};
          const w=ms=>new Promise(r=>setTimeout(r,ms));
          NV={sdt:'0911222333',ten:'Lan',phien:'P1'};db=nvDb({shop:OWNX.shop,may:OWNX.may.filter(m=>m.tt==='ton').map(m=>({imei:m.imei,ten:m.ten,hang:m.hang,giaBan:m.giaBan})),hang:OWNX.hang.filter(h=>h.sl>0)});
          localStorage.removeItem('shopgon_nvp');localStorage.removeItem('shopgon_nvpq');localStorage.removeItem('shopgon_nvpds');render();
          const nut=getComputedStyle(document.querySelector('nav.tabs button[data-v=stock]')).display!=='none'&&document.querySelector('nav.tabs button[data-v=stock]').textContent.includes('Nhập hàng');
          document.querySelector('nav.tabs button[data-v=stock]').click();await w(100);
          const tenMay=OWNX.may.find(m=>m.tt==='ton').ten;const a=$('aTen');a.value=tenMay;a.dispatchEvent(new Event('input',{bubbles:true}));
          $('aImei').value='356938035643809\\n490154203237518';document.querySelector('#fNvpMay button[type=submit]').click();await w(100);
          nvpMode='hang';render();const h0=OWNX.hang.find(x=>x.sl>0);$('hTen').value=h0.ten;$('hSl').value='4';document.querySelector('#fNvpHang button[type=submit]').click();await w(100);
          const chu=document.getElementById('v-add').innerText;const khongGia=!/giá nhập|giá bán|giá vốn/i.test(chu);
          $('nvpNcc').value='NPP Mekong';$('nvpNcc').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-nvpgui]').click();await w(300);
          const g=SENT.find(x=>x.act==='nvNhap');const daGui=g&&g.phien==='P1'&&g.phieu.kind==='nhap'&&g.phieu.lines.length===2&&!JSON.stringify(g.phieu).match(/"(giaNhap|giaBan|gn|gb)"/);
          const ds=nvpDs();const coDs=ds.length===1&&ds[0].tt==='moi'&&document.getElementById('v-add').innerText.includes('chờ chủ shop');
          /* chủ shop nhận qua nvSync */
          NV=null;db=JSON.parse(JSON.stringify(OWNX));db.sample=false;XEM=false;GG.token='t'.repeat(40);db.shop.nv=[{sdt:'0911222333',ten:'Lan'}];
          RESP={ok:true,don:[{...g.phieu,nv:'0911222333'}],nv:[]};nvBusy=false;await nvSync();
          const nhan=pnCho().length===1&&!db.don.some(d=>d.bill===g.phieu.id)&&nvAck.includes(g.phieu.id);
          go('home');const bar=!!document.querySelector('#v-home [data-pncho]');document.querySelector('#v-home [data-pncho]').click();await w(100);
          const gnMay=OWNX.may.filter(m=>m.ten===tenMay).pop().giaNhap,gnPk=h0.giaNhap;
          const dien=parseMoney(document.querySelector('[data-pcgn$="|0"]').value)===gnMay&&parseMoney(document.querySelector('[data-pcgn$="|1"]').value)===gnPk;
          document.querySelector('[data-pcgb$="|0"]').value='9.990.000';const ton0=stock().length,sl0=db.hang.find(x=>x.id===h0.id).sl,PN0=JSON.stringify(PN);
          document.querySelector('[data-pcok]').click();await w(150);
          const m1=db.may.find(m=>m.imei==='356938035643809');const vao=stock().length===ton0+2&&db.hang.find(x=>x.id===h0.id).sl===sl0+4&&m1&&m1.giaNhap===gnMay&&m1.giaBan===9990000&&/NV Lan/.test(m1.ncc);
          const giuPN=JSON.stringify(PN)===PN0;const kq=(db.shop.nhapKq||[])[0];const hetCho=!pnCho().length;
          RESP={ok:true,don:[],nv:[]};nvBusy=false;await nvSync();const gk2=SENT.filter(x=>x.act==='nvSync').pop().nhapKq;const daGuiKq=gk2.length===1&&gk2[0].kq==='ok'&&!(db.shop.nhapKq||[]).length;
          /* nhận lại lần 2 (máy chủ gửi trùng) không tạo phiếu chờ mới */
          RESP={ok:true,don:[{...g.phieu}],nv:[]};nvBusy=false;await nvSync();const khongTrung=!pnCho().length;
          /* trả lại */
          RESP={ok:true,don:[{...g.phieu,id:'P2'}],nv:[]};nvBusy=false;await nvSync();addTab='cho';go('add');window.confirm=()=>true;document.querySelector('[data-pctra]').click();await w(50);
          const tra=!pnCho().length&&(db.shop.nhapKq||[]).some(x=>x.id==='P2'&&x.kq==='tra');
          return JSON.stringify({nut,khongGia,daGui,coDs,nhan,bar,dien,vao,giuPN,kq:!!kq,hetCho,daGuiKq,khongTrung,tra})})()""")
        try: r = json.loads(r)
        except Exception: r = {'loi': r}
        ok('NV nhập hàng: nút Nhập hàng, KHÔNG thấy giá, gửi phiếu có phiên, không kèm giá', r.get('nut') and r.get('khongGia') and r.get('daGui') and r.get('coDs') and not errs, (r, errs))
        ok('Chủ duyệt phiếu NV: nhận qua nvSync, giá lần trước điền sẵn, vào kho đúng SL + giá, gửi kết quả', all(r.get(k) for k in ['nhan','bar','dien','vao','giuPN','kq','hetCho','daGuiKq','khongTrung','tra']) and not errs, (r, errs))
        await pg.screenshot(path='/tmp/pncho.png')
        await ctx.close()

        # 12h. NV test: nhập hàng giả lập gửi
        ctx, pg, errs = await trang(b, '/app/?demo=1')
        await pg.evaluate("localStorage.setItem('shopgon_nv',JSON.stringify({sdt:'0900000000',ten:'NV test',phien:'TEST',test:1}));['shopgon_nvp','shopgon_nvpq','shopgon_nvpds'].forEach(k=>localStorage.removeItem(k))")
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(1200)
        await pg.click('nav.tabs button[data-v=stock]'); await pg.wait_for_timeout(200)
        await pg.evaluate("nvpMode='hang';render()"); await pg.fill('#hTen', 'Cường lực test'); await pg.click('#fNvpHang button[type=submit]'); await pg.wait_for_timeout(150)
        await pg.click('[data-nvpgui]'); await pg.wait_for_timeout(300)
        t = await pg.evaluate("document.getElementById('v-add').innerText")
        ok('Tài khoản test NV: nhập hàng gửi phiếu giả lập, hiện trạng thái', 'chờ chủ shop' in t and 'giá nhập' not in t.lower() and 'giá bán' not in t.lower() and not errs, (t[:200], errs))
        await pg.screenshot(path='/tmp/nvnhap.png')
        await ctx.close()

        # 13. Các trang khác + cài app
        for path, ten in [('/', 'Trang chủ'), ('/so-sanh.html', 'So sánh giá'), ('/bg/?demo=1&xem=1', 'Bảng giá online (khách)'), ('/tt/', 'Thiết kế hình'), ('/setup/', 'Trang hướng dẫn Sale'), ('/quantri/', 'Trang quản trị')]:
            c2, p2, e2 = await trang(b, path); await p2.wait_for_timeout(600)
            w = await p2.evaluate("document.documentElement.scrollWidth")
            ok(f'{ten} mở được, không lỗi, không tràn', not e2 and w <= 392, f'{e2} w={w}'); await c2.close()
        c2, p2, e2 = await trang(b, '/app/'); await p2.wait_for_timeout(2000)
        cdp = await p2.context.new_cdp_session(p2)
        ie = (await cdp.send('Page.getInstallabilityErrors'))['installabilityErrors']
        mf = (await cdp.send('Page.getAppManifest'))
        ok('Cài app: Chrome nhận là app cài được', not ie and 'Shop Gọn' in mf.get('data', ''), ie)
        await c2.close()
        c2, p2, e2 = await trang(b, '/app/', p.devices['iPhone 13']); await p2.wait_for_timeout(1800)
        ok('iPhone: có thanh Cài app + icon apple-touch', await p2.evaluate("!document.getElementById('ibar').hidden&&!!document.head.querySelector('link[rel=apple-touch-icon]')"))
        await c2.close(); await b.close()

    dat = sum(1 for k in KQ if k[1]); print(f'\nKẾT QUẢ: {dat}/{len(KQ)} đạt')
    json.dump([{'ten': t, 'dat': d, 'ct': str(c)} for t, d, c in KQ], open(sys.argv[1] if len(sys.argv) > 1 else '/dev/null', 'w'), ensure_ascii=False)

asyncio.run(main())
