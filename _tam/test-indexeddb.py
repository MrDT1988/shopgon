# Test BỘ NHỚ MÁY → IndexedDB (09/11/2026). Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-indexeddb.py
import asyncio, json
from playwright.async_api import async_playwright

URL = 'http://localhost:8765'
KQ = []
def ok(ten, dk, ct=''):
    KQ.append((ten, bool(dk))); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:300]) if not dk else '')

IDB_GET = """k=>new Promise(r=>{const q=indexedDB.open('shopgon',1);q.onupgradeneeded=()=>q.result.createObjectStore('kv');q.onsuccess=()=>{const g=q.result.transaction('kv').objectStore('kv').get(k);g.onsuccess=()=>{r(g.result===undefined?null:g.result);q.result.close()};g.onerror=()=>r('ERR')}})"""
IDB_SET = """([k,v])=>new Promise(r=>{const q=indexedDB.open('shopgon',1);q.onupgradeneeded=()=>q.result.createObjectStore('kv');q.onsuccess=()=>{const t=q.result.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=()=>{q.result.close();r(1)}}})"""

def so(ten, imei, luu=0):
    return {'v': 1, 'sample': False, '_luu': luu, 'shop': {'ten': ten}, 'may': [{'imei': imei, 'ten': 'OPPO A6', 'tt': 'ton', 'giaBan': 5000000}], 'don': [], 'hang': [], 'pn': [], 'chi': []}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL + '/robots-khong-co'); E = pg.evaluate
        # 1. Máy cũ: sổ + bản gốc đang ở localStorage → lên bản mới
        await E("""([a,b])=>{localStorage.clear();localStorage.setItem('shopgon_v1',JSON.stringify(a));localStorage.setItem('shopgon_base_S1',JSON.stringify(b));localStorage.setItem('shopgon_gg',JSON.stringify({email:'x@gmail.com',sheetId:'S1'}))}""", [so('Shop A', '111', 0), {'may': [{'imei': '111'}], 'don': [], 'hang': [], 'pn': [], 'chi': [], 'shop': {}}])
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(1500)
        i1 = await E(IDB_GET, 'shopgon_v1'); b1 = await E(IDB_GET, 'shopgon_base_S1')
        ls = await E("()=>({v1:!!localStorage.getItem('shopgon_v1'),b:localStorage.getItem('shopgon_base_S1')})")
        ok('Lên bản mới: sổ chép sang IndexedDB', i1 and i1['may'][0]['imei'] == '111', i1)
        ok('Lên bản mới: bản gốc chuyển sang IndexedDB, xoá khỏi localStorage', b1 and b1['may'][0]['imei'] == '111' and ls['b'] is None, [b1, ls])
        ok('Sổ vẫn còn ở localStorage (mở nhanh + trang Bảng giá)', ls['v1'])
        gb = await E("()=>{GG.sheetId='S1';const a=GG.getBase();a.may.push({imei:'zz'});return [a.may.length,GG.getBase().may.length]}")
        ok('getBase trả bản chép (sửa không lan vào bản gốc)', gb == [2, 1], gb)
        # 2. Lưu: ghi cả 2 nơi, có dấu _luu
        await E("()=>{XEM=false;const d=Store.goc;d.may.push({imei:'222',ten:'OPPO A6',tt:'ton'});Store.save(d)}"); await pg.wait_for_timeout(300)
        i2 = await E(IDB_GET, 'shopgon_v1'); l2 = await E("()=>JSON.parse(localStorage.getItem('shopgon_v1'))")
        ok('Lưu: IndexedDB + localStorage cùng bản, có dấu _luu', len(i2['may']) == 2 and len(l2['may']) == 2 and i2['_luu'] == l2['_luu'] > 0, [i2.get('_luu'), l2.get('_luu')])
        # 3. setBase ghi IndexedDB, không ghi localStorage
        await E("()=>{GG.sheetId='S1';GG.setBase(Store.goc)}"); await pg.wait_for_timeout(300)
        b3 = await E(IDB_GET, 'shopgon_base_S1'); lb3 = await E("()=>localStorage.getItem('shopgon_base_S1')")
        ok('setBase: bản gốc chỉ nằm ở IndexedDB', b3 and len(b3['may']) == 2 and lb3 is None, [b3 and len(b3['may']), lb3])
        # 4. localStorage ĐẦY → sổ chạy bằng IndexedDB, bỏ bản cũ ở localStorage
        await E("""()=>{const o=Storage.prototype.setItem;window._o=o;Storage.prototype.setItem=function(k,v){if(k==='shopgon_v1')throw new DOMException('full','QuotaExceededError');return o.call(this,k,v)};
          const d=Store.goc;d.may.push({imei:'333',ten:'OPPO A6',tt:'ton'});Store.save(d)}"""); await pg.wait_for_timeout(300)
        i4 = await E(IDB_GET, 'shopgon_v1'); l4 = await E("()=>[localStorage.getItem('shopgon_v1'),Store.idb]")
        ok('localStorage đầy: IndexedDB vẫn có bản mới (3 máy), bỏ bản cũ ở localStorage', len(i4['may']) == 3 and l4[0] is None and l4[1] is True, [len(i4['may']), l4])
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(1500)
        n5 = await E("()=>[Store.goc.may.length,Store.goc.shop.ten,firstOpen]")
        ok('Mở lại khi localStorage không còn sổ: nạp từ IndexedDB (3 máy, không màn chào)', n5 == [3, 'Shop A', False], n5)
        # 5. IndexedDB mới hơn localStorage (localStorage còn bản cũ) → dùng IndexedDB
        await E("([a])=>localStorage.setItem('shopgon_v1',JSON.stringify(a))", [so('Shop A', '111', 1000)])
        await E(IDB_SET, ['shopgon_v1', {**so('Shop A', '111', 5000), 'may': [{'imei': str(i), 'tt': 'ton', 'ten': 'X'} for i in range(4)]}])
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(1500)
        dbg = await E("async()=>{const r=await IDBS.get(\"shopgon_v1\");return [Store.goc.may.length,Store.goc._luu,r&&r._luu,r&&r.may.length,JSON.parse(localStorage.getItem(\"shopgon_v1\")||\"null\")?._luu]}")
        ok("IndexedDB mới hơn → mở bản IndexedDB", dbg[0] == 4, dbg)
        # 6. localStorage mới hơn / bằng (bản app cũ ghi) → giữ localStorage, chép sang IndexedDB
        await E("([a])=>localStorage.setItem('shopgon_v1',JSON.stringify(a))", [{**so('Shop A', '111', 5000), 'may': [{'imei': str(i), 'tt': 'ton', 'ten': 'X'} for i in range(6)]}])
        await pg.goto(URL + '/app/'); await pg.wait_for_timeout(1500)
        i6 = await E(IDB_GET, 'shopgon_v1')
        ok('Dấu bằng nhau (app cũ ghi đè) → giữ localStorage, chép sang IndexedDB', await E("()=>Store.goc.may.length") == 6 and len(i6['may']) == 6, len(i6['may']))
        # 7. Trang Bảng giá đọc được tồn kho khi sổ chỉ còn ở IndexedDB
        await E("()=>localStorage.removeItem('shopgon_v1')")
        await pg.goto(URL + '/bg/?tu=app'); await pg.wait_for_timeout(2500)
        t7 = await E("()=>{const e=document.getElementById('laytonG');return e?e.textContent:''}")
        ok('Bảng giá: lấy tồn kho từ IndexedDB', 'app của shop' in t7, t7)
        ok('Không lỗi JavaScript', not errs, errs)
        await ctx.close()
        # 8. Demo + trình duyệt không có IndexedDB vẫn chạy
        ctx = await b.new_context(); await ctx.add_init_script("try{Object.defineProperty(window,'indexedDB',{get(){throw new Error('no idb')}})}catch(_){}")
        pg = await ctx.new_page(); er = []; pg.on('pageerror', lambda e: er.append(str(e)))
        await pg.goto(URL + '/app/?demo=1'); await pg.wait_for_timeout(3500)
        d8 = await pg.evaluate("()=>[db.may.length>0,!!localStorage.getItem('shopgon_demo3'),document.querySelectorAll('nav button,.tab').length>0]")
        ok('Không có IndexedDB: app demo vẫn chạy bằng localStorage', all(d8) and not er, [d8, er])
        await ctx.close(); await b.close()
    print('KẾT QUẢ', sum(1 for _, d in KQ if d), '/', len(KQ))

asyncio.run(main())
