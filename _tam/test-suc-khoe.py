# Test bộ đếm sức khoẻ đồng bộ (09/11/2026): đếm ghi bù / lỗi / đối soát lệch, gửi 1 lần/ngày, KHÔNG gửi nội dung đơn.
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-suc-khoe.py
import asyncio, json
from playwright.async_api import async_playwright
src = open('_tam/test-luu-tru.py', encoding='utf-8').read()
exec(src[:src.index('D = Drive()')])
URL = 'http://localhost:8765'; KQ = []
def ok(ten, dk, ct=''):
    KQ.append(bool(dk)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')
D = Drive(); HONG = {'loi': False}; GUI = []
_h0 = D.handle
def _h(method, url, body):
    if HONG['loi'] and 'values:batchUpdate' in url: raise KeyError('500 giả lập')
    return _h0(method, url, body)
D.handle = _h
LOGIN = "()=>{localStorage.setItem('shopgon_gg',JSON.stringify({email:'test@shopgon.vn'}));localStorage.setItem('shopgon_tk',JSON.stringify({t:'t',e:'test@shopgon.vn',x:Date.now()+3e6}))}"
CHO = "while(GG.busy)await new Promise(r=>setTimeout(r,100));clearTimeout(GG.timer);"
def tren_drive(x):
    return x in json.dumps([{k: v for k, v in f['sheets'].items() if k != 'Nhật ký'} for f in D.f.values() if f['ap'].get('nam')], ensure_ascii=False)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def h(r):
            u = r.request.url
            if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
            if 'localhost' in u: return await r.continue_()
            if 'script.google.com' in u:
                try:
                    o = json.loads(r.request.post_data or '{}')
                    if o.get('act') == 'sk': GUI.append(o)
                except Exception: pass
                return await r.fulfill(body='{"status":"active","shop":"Shop Test","ok":true}', content_type='application/json')
            if 'googleapis.com' in u:
                try: return await r.fulfill(body=json.dumps(D.handle(r.request.method, u, json.loads(r.request.post_data or '{}'))), content_type='application/json')
                except Exception as e: return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
            await r.abort()
        c = await b.new_context(); await c.route('**/*', h); A = await c.new_page(); A.on('pageerror', lambda e: errs.append(str(e)))
        await A.goto(URL + '/khong-co'); await A.evaluate(LOGIN); await A.goto(URL + '/app/'); await A.wait_for_timeout(4000)
        # bán 1 đơn (id kiểu thật: thời gian base36, lùi 2 giờ để không bị coi là đơn mới)
        await A.evaluate("async()=>{" + CHO + "const id=(Date.now()-72e5).toString(36)+'ab';db.don.push({id,bill:id,ngay:todayIso(),gio:'8:00',loai:'pk',ten:'Ốp BÍ MẬT',sl:1,giaBan:123456,giaVon:1,tt:'Tiền mặt',huy:null,khach:'Nguyễn Văn Khách'});save();" + CHO + "await GG.push()}")
        s = await A.evaluate("()=>SK.get()")
        ok('Lưu Drive xong: đếm 1 lần lên, không còn đơn chờ', s['len'] >= 1 and s['cho'] == 0, s)
        # lỗi ghi Drive → đếm lỗi, đơn còn chờ
        HONG['loi'] = True
        await A.evaluate("async()=>{" + CHO + "db.don.push({id:(Date.now()-72e5).toString(36)+'cd',bill:'b2',ngay:todayIso(),gio:'8:10',loai:'pk',ten:'Sạc',sl:1,giaBan:1,giaVon:1,tt:'Tiền mặt',huy:null});save();" + CHO + "await GG.push()}")
        s = await A.evaluate("()=>SK.get()")
        ok('Ghi Drive lỗi → đếm lỗi, đơn vẫn đánh dấu chờ', s['loi'] >= 1 and s['cho'] > 0, s)
        HONG['loi'] = False
        await A.evaluate("async()=>{" + CHO + "await GG.push()}")
        s = await A.evaluate("()=>SK.get()")
        ok('Mạng lại → lên Drive, hết chờ', s['cho'] == 0, s)
        # đối soát: xoá 1 đơn khỏi Drive → lệch 1
        ids = await A.evaluate("()=>db.don.map(x=>x.id)")
        for f in D.f.values():
            if f['ap'].get('nam'):
                for k, rows in f['sheets'].items():
                    if k != 'Nhật ký': f['sheets'][k] = [r for r in rows if ids[0] not in r]
        ds = await A.evaluate("async()=>await SK.doiSoat()")
        ok('Đối soát: Drive thiếu 1 đơn → lệch 1', ds['lechDon'] == 1 and ds['lechImei'] == 0, ds)
        ok('Đối soát không đụng khoá rev (GG._rev giữ nguyên)', await A.evaluate("async()=>{const r=GG._rev;await SK.doiSoat();return GG._rev===r}"))
        # kiểm lại 20s → ghi bù + gửi sức khoẻ
        await A.wait_for_timeout(1000)
        await A.evaluate("async()=>{" + CHO + "GG._laKiem=true;await GG.push()}")
        await A.wait_for_timeout(6000)
        s = await A.evaluate("()=>SK.get()")
        ok('Kiểm lại thấy Drive thiếu → đếm ghi bù', s['bu'] >= 1, s)
        ok('Đơn đã được ghi bù lên Drive', tren_drive(ids[0]))
        ok('Gửi sức khoẻ đúng 1 lần, đánh dấu đã gửi', len(GUI) == 1 and s['gui'] == 1, len(GUI))
        g = json.dumps(GUI, ensure_ascii=False) if GUI else ''
        ok('Gói gửi KHÔNG có nội dung đơn (tên hàng, giá, khách)', GUI and 'BÍ MẬT' not in g and '123456' not in g and 'Khách' not in g, g[:300])
        d = GUI[0]['d'] if GUI else {}
        ok('Gói gửi có đủ số đếm + đối soát + máy', all(k in d for k in ['len','loi','bu','chen','choMax','lechDon','lechImei','may','build','app']), d)
        ok('Lúc gửi Drive đã đủ đơn → lệch 0', d.get('lechDon') == 0, d)
        await A.evaluate("async()=>{" + CHO + "GG._laKiem=true;await GG.push()}"); await A.wait_for_timeout(5000)
        ok('Lần kiểm lại sau cùng ngày KHÔNG gửi thêm', len(GUI) == 1, len(GUI))
        # sang ngày mới → số hôm qua chưa gửi thì kèm theo
        r = await A.evaluate("()=>{const o=SK.get();o.ngay='2000-01-01';o.gui=0;SK.luu();SK.d=null;const n=SK.get();return {ngay:n.ngay,hq:!!n.homQua,len:n.len}}")
        ok('Qua ngày: bộ đếm về 0, giữ số hôm qua chưa gửi', r['len'] == 0 and r['hq'], r)
        ok('Không lỗi JavaScript', not errs, errs)
        await b.close()
    print('KẾT QUẢ', sum(KQ), '/', len(KQ))
asyncio.run(main())
