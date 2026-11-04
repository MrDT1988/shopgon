# Test SỔ THEO NĂM + SAO LƯU (05/11/2026) — Google Drive/Sheets GIẢ LẬP trong máy, không đụng tài khoản thật.
# Chạy: cd repo && python3 -m http.server 8765 & ; python3 _tam/test-luu-tru.py
import asyncio, json, sys, re, copy, itertools
from urllib.parse import urlparse, parse_qs, unquote
from playwright.async_api import async_playwright

URL = 'http://localhost:8765'
KQ = []
def ok(ten, dk, ct=''):
    KQ.append((ten, bool(dk), ct)); print(('✅' if dk else '❌'), ten, ('— ' + str(ct)[:400]) if ct and not dk else '')

class Drive:
    """Giả lập đủ các lệnh app dùng: drive/v3 files (list/create/patch/copy), sheets v4 (create/get/batchGet/batchClear/batchUpdate)."""
    def __init__(s): s.f = {}; s.n = itertools.count(1)
    def new_id(s): return 'F%03d' % next(s.n)
    def ts(s):
        import datetime; return (datetime.datetime.utcnow() + datetime.timedelta(seconds=next(s.n))).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    def lst(s, q, order):
        m = re.search(r"key='(\w+)' and value='(\w+)'", q or '')
        out = [x for x in s.f.values() if not x['trashed'] and (not m or x['ap'].get(m.group(1)) == m.group(2))]
        out.sort(key=lambda x: x['ct'], reverse='desc' in (order or ''))
        return [{'id': x['id'], 'name': x['name'], 'createdTime': x['ct'], 'appProperties': dict(x['ap'])} for x in out]
    def sheet_name(s, r): r = unquote(r); r = r.split('!')[0]; return r[1:-1] if r.startswith("'") else r
    def handle(s, method, url, body):
        u = urlparse(url); p = u.path; qs = parse_qs(u.query)
        if 'oauth2/v3/userinfo' in p: return {'email': 'test@shopgon.vn'}
        if p == '/drive/v3/files' and method == 'GET': return {'files': s.lst(qs.get('q', [''])[0], qs.get('orderBy', [''])[0])}
        if p == '/drive/v3/files' and method == 'POST':
            i = s.new_id(); s.f[i] = {'id': i, 'name': body.get('name'), 'ap': body.get('appProperties', {}), 'ct': s.ts(), 'trashed': False, 'sheets': None, 'parents': body.get('parents', [])}; return {'id': i}
        m = re.match(r'/drive/v3/files/(\w+)/copy$', p)
        if m:
            src = s.f[m.group(1)]; i = s.new_id(); ap = dict(src['ap']); ap.update(body.get('appProperties', {}))
            s.f[i] = {'id': i, 'name': body.get('name'), 'ap': ap, 'ct': s.ts(), 'trashed': False, 'sheets': copy.deepcopy(src['sheets']), 'parents': body.get('parents', [])}; return {'id': i}
        m = re.match(r'/drive/v3/files/(\w+)$', p)
        if m and method == 'PATCH':
            x = s.f[m.group(1)]
            if 'appProperties' in body: x['ap'].update(body['appProperties'])
            if 'name' in body: x['name'] = body['name']
            if 'trashed' in body: x['trashed'] = body['trashed']
            return {'id': x['id']}
        if p == '/v4/spreadsheets' and method == 'POST':
            i = s.new_id(); s.f[i] = {'id': i, 'name': body['properties']['title'], 'ap': {}, 'ct': s.ts(), 'trashed': False, 'sheets': {t['properties']['title']: [] for t in body.get('sheets', [])}, 'parents': []}
            return {'spreadsheetId': i}
        m = re.match(r'/v4/spreadsheets/(\w+)$', p)
        if m and method == 'GET': return {'sheets': [{'properties': {'title': t}} for t in s.f[m.group(1)]['sheets']]}
        m = re.match(r'/v4/spreadsheets/(\w+):batchUpdate$', p)
        if m:
            for rq in body.get('requests', []): s.f[m.group(1)]['sheets'][rq['addSheet']['properties']['title']] = []
            return {}
        m = re.match(r'/v4/spreadsheets/(\w+)/values:(\w+)$', p)
        if m:
            sh = s.f[m.group(1)]['sheets']; act = m.group(2)
            if act == 'batchGet':
                vr = []
                for r in qs.get('ranges', []):
                    n = s.sheet_name(r)
                    if n not in sh: raise KeyError('Unable to parse range: ' + n)
                    vals = [[str(v) for v in row] for row in sh[n]]
                    vals = [row[:max([i + 1 for i, v in enumerate(row) if v != ''] or [0])] for row in vals]
                    while vals and not vals[-1]: vals.pop()
                    vr.append({'range': r, 'values': vals} if vals else {'range': r})
                return {'valueRanges': vr}
            if act == 'batchClear':
                for r in body['ranges']:
                    n = s.sheet_name(r)
                    if n not in sh: raise KeyError(n)
                    sh[n] = []
                return {}
            if act == 'batchUpdate':
                for d in body['data']:
                    n = s.sheet_name(d['range'])
                    if n not in sh: raise KeyError(n)
                    sh[n] = [['' if v is None else str(v) for v in row] for row in d['values']]
                return {}
        raise KeyError('Chưa giả lập: ' + method + ' ' + url)

D = Drive()
GIU = {}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 360, 'height': 780}, device_scale_factor=2)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        async def h(r):
            u = r.request.url
            if 'ver.json' in u: return await r.fulfill(body='{}', content_type='application/json')
            if 'localhost' in u: return await r.continue_()
            if 'script.google.com' in u:
                bd = json.loads(r.request.post_data or '{}') if r.request.method == 'POST' else {}
                if bd.get('act') == 'nvGiu':   # giả lập máy chủ v21 giuImei_
                    ai = 'Chủ shop' if bd.get('token') else 'NV ' + str(bd.get('sdt')); may = bd.get('may'); out = []
                    for im in bd.get('imei', []):
                        o = GIU.get(im); lo = bd.get('loai')
                        if lo == 'mo': GIU.pop(im, None); continue
                        if lo == 'bo':
                            if o and o['may'] == may and not o['ban']: GIU.pop(im, None)
                            continue
                        if o and o['may'] != may: out.append({'imei': im, 'ai': o['ai'], 'luc': o['luc'], 'ban': o['ban']}); continue
                        GIU[im] = {'ai': ai, 'may': may, 'luc': '10:05', 'ban': lo == 'ban'}
                    return await r.fulfill(body=json.dumps({'ok': True, 'trung': out}), content_type='application/json')
                return await r.fulfill(body='{"status":"active","shop":"Shop Test"}', content_type='application/json')
            if 'googleapis.com' in u and '/export' in u:
                return await r.fulfill(body=b'PK\x03\x04 gia-lap-xlsx', content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            if 'googleapis.com' in u:
                try:
                    body = json.loads(r.request.post_data or '{}')
                    res = D.handle(r.request.method, u, body)
                    return await r.fulfill(body=json.dumps(res), content_type='application/json')
                except Exception as e:
                    return await r.fulfill(status=400, body=json.dumps({'error': str(e)}), content_type='application/json')
            await r.abort()
        await pg.route('**/*', h)
        await pg.goto(URL + '/app/?demo=1'); await pg.wait_for_timeout(1000)
        E = pg.evaluate
        async def J(js): return json.loads(await E('(async()=>JSON.stringify(await (async()=>{' + js + '})()))()'))
        def sheets(fid): return D.f[fid]['sheets']

        # ---------- 0. Sổ cũ 1 file (định dạng trước 05/11) có dữ liệu thật: mẫu + đơn năm 2025 + bán tháng 1/2026 + nợ + trả góp ----------
        seed = await J("""
          db=sampleDb();db.sample=false;db.shop.ten='Shop Test';
          db.don.push({id:'cu1',bill:'cu1',ngay:'2025-11-10',gio:'9:00',loai:'pk',ten:'Ốp năm cũ',giaBan:100000,giaVon:30000,tt:'Tiền mặt',huy:null});
          db.don.push({id:'cu2',bill:'cu2',ngay:'2025-12-20',gio:'10:00',loai:'pk',ten:'Sạc năm cũ nợ',giaBan:500000,giaVon:200000,tt:'Ghi nợ',no:300000,khach:'Chú Tư',huy:null});
          db.may.push({imei:'351111111111111',ten:'OPPO A18 4/64GB - Đen',hang:'OPPO',giaNhap:2800000,giaBan:3290000,ngayNhap:'2026-01-05',ncc:'NPP',tt:'ban'});
          db.don.push({id:'t1',bill:'t1',ngay:'2026-01-15',gio:'9:00',loai:'may',imei:'351111111111111',ten:'OPPO A18 4/64GB - Đen',giaBan:3290000,giaVon:2800000,tt:'Tiền mặt',khach:'Anh Ba',sdt:'0909',bh:12,huy:null});
          db.don.push({id:'n1',bill:'n1',ngay:'2026-10-02',gio:'9:00',loai:'pk',ten:'Tai nghe',giaBan:400000,giaVon:150000,tt:'Ghi nợ',no:400000,khach:'Cô Năm',huy:null});
          (db.pn=db.pn||[]).push({id:'pn1',ngay:'2026-10-20',gio:'8:00',ncc:'NPP Mekong',tong:20000000,nMay:2,no:5000000,dong:[{t:'pk',ten:'x',sl:1}]});
          db.chi=db.chi||[];db.chi.push({id:'c1',ngay:'2026-09-01',gio:'8:00',loai:'Điện',tien:800000,note:''});
          GG.token='t';GG.email='test@shopgon.vn';
          const sh=await GG.api('https://sheets.googleapis.com/v4/spreadsheets',{method:'POST',body:JSON.stringify({properties:{title:'Shop Gọn - Shop Test'},sheets:['May','Don','Hang','CaiDat','Phieu','Chi'].map(t=>({properties:{title:t}}))})});
          const id=sh.spreadsheetId;await GG.api('https://www.googleapis.com/drive/v3/files/'+id,{method:'PATCH',body:JSON.stringify({appProperties:{shopgon:'1'}})});
          const tbl={May:db.may,Don:db.don,Hang:db.hang,Phieu:db.pn,Chi:db.chi};const data=[];
          for(const [t,c] of Object.entries(GG.cols)){if(!tbl[t])continue;data.push({range:t+'!A1',values:[c,...tbl[t].map(o=>{const x=t==='Phieu'?{...o,dong:JSON.stringify(o.dong||[])}:o;return c.map(k=>x[k]??'')})]})}
          data.push({range:'CaiDat!A1',values:[['shop'],[JSON.stringify(db.shop)]]});
          await GG.api('https://sheets.googleapis.com/v4/spreadsheets/'+id+'/values:batchUpdate',{method:'POST',body:JSON.stringify({valueInputOption:'RAW',data})});
          const n={may:db.may.length,don:db.don.length,hang:db.hang.length,pn:db.pn.length,chi:db.chi.length};
          /* máy MỚI: chưa có dữ liệu, chưa có bản gốc */
          db=emptyDb();Object.keys(localStorage).filter(k=>k.startsWith('shopgon_base')).forEach(k=>localStorage.removeItem(k));
          return {id,n}""")
        leg = seed['id']

        # ---------- 1. Tự tách sổ cũ 1 lần ----------
        r = await J("const c=await GG.moSo();return {c,nam:GG.nam,kq:GG.kq,files:GG.files,n:{may:db.may.length,don:db.don.length,hang:db.hang.length,pn:db.pn.length,chi:db.chi.length}}")
        ok('Tách sổ cũ: tạo sổ năm 2026', r['nam'] == 2026 and '2026' in r['files'], r)
        ok('Tách sổ cũ: không mất dòng nào (đơn, IMEI, hàng, phiếu, chi)', r['kq']['khop'] and r['n'] == seed['n'], (r['kq'], r['n'], seed['n']))
        ok('Tách sổ cũ: giữ file cũ làm bản lưu (đổi tên, không còn là sổ đang ghi)', D.f[leg]['ap'].get('shopgon') == 'cu' and 'bản lưu' in D.f[leg]['name'] and len(D.f[leg]['sheets']['Don']) == seed['n']['don'] + 1, D.f[leg]['name'])
        f26 = r['files']['2026']; S = sheets(f26)
        ok('Sổ năm có đủ trang: Số dư, Cài đặt, Hàng hóa, IMEI, Năm trước, T01…T12', all(n in S for n in ['Số dư', 'Cài đặt', 'Hàng hóa', 'IMEI', 'Năm trước'] + ['T%02d' % i for i in range(1, 13)]), list(S))
        ok('Đơn chia đúng tháng: T01 có đơn bán 15/01, T10 có đơn nợ, T09 có chi', any(x[1] == 't1' for x in S['T01'][1:]) and any(x[1] == 'n1' for x in S['T10'][1:]) and any(x[0] == 'Chi' for x in S['T09'][1:]))
        ok('Đơn năm 2025 nằm ở trang "Năm trước"', sorted(x[1] for x in S['Năm trước'][1:]) == ['cu1', 'cu2'], S['Năm trước'][1:])
        ok('Trang tháng đọc được bằng mắt (cột Bảng: Đơn/Phiếu nhập/Chi)', S['T10'][0][0] == 'bang' and {x[0] for x in S['T10'][1:]} <= {'Đơn', 'Phiếu nhập', 'Chi'})

        # ---------- 2. Đồng bộ thường ngày ghi đúng tháng ----------
        r = await J("""db.don.push({id:'moi1',bill:'moi1',ngay:todayIso(),gio:'10:00',loai:'pk',ten:'Cường lực',giaBan:100000,giaVon:20000,tt:'Tiền mặt',huy:null,cty:'X',tgTT:'Chờ duyệt'});
          await GG.push();return GG.thang(+todayIso().slice(5,7))""")
        row = [x for x in sheets(f26)[r][1:] if x[1] == 'moi1']
        ok('Bán mới → ghi vào trang tháng hiện tại, giữ cả trường phụ (trả góp…)', row and 'tgTT' in row[0][-1], row)
        r = await J("db=emptyDb();Object.keys(localStorage).filter(k=>k.startsWith('shopgon_base')).forEach(k=>localStorage.removeItem(k));await GG.pull();const d=db.don.find(x=>x.id==='moi1');return {n:db.don.length,tg:d&&d.tgTT,cty:d&&d.cty}")
        ok('Máy thứ 2 mở sổ: đọc đủ, không mất trường phụ', r['tg'] == 'Chờ duyệt' and r['cty'] == 'X' and r['n'] == seed['n']['don'] + 1, r)

        # ---------- 2b. Nhật ký thay đổi ----------
        r = await J("""NV=null;XEM=false;NK.chup();const n0=(db.nk||[]).length;const d=db.don.find(x=>x.id==='n1');d.giaBan=450000;save();
          const m=db.may.find(x=>x.tt==='ton');const im=m.imei;db.may=db.may.filter(x=>x.imei!==im);save();
          const m2=db.may.find(x=>x.tt==='ton');m2.tt='ban';db.don.push({id:'bt1',bill:'bt1',ngay:todayIso(),gio:'12:00',loai:'may',imei:m2.imei,ten:m2.ten,giaBan:5000000,giaVon:4000000,tt:'Tiền mặt',huy:null});save();
          const t3=db.may.filter(x=>x.tt==='ton'&&x.ten===db.may.find(y=>y.tt==='ton').ten);t3.forEach(x=>x.giaBan=9990000);save();
          await GG.push();return {nk:db.nk.slice(n0).map(x=>x.viec+'|'+x.ma+'|'+x.ct+'|'+x.ai+'|'+x.may),nlo:t3.length}""")
        nk = r['nk']
        ok('Nhật ký: sửa giá đơn → "Sửa đơn", ghi giá trước → sau, ai, máy nào', any(x.startswith('Sửa đơn|') and 'Giá bán' in x and '→' in x and '|Chủ shop|' in x for x in nk), nk)
        ok('Nhật ký: xóa IMEI khỏi kho có ghi', any(x.startswith('Xóa IMEI khỏi kho|') for x in nk), nk)
        ok('Nhật ký: bán hàng bình thường KHÔNG sinh dòng (không rác)', not any('bt1' in x or (x.startswith('Sửa máy') and 'Trạng thái' in x) for x in nk), nk)
        ok('Nhật ký: đổi giá cả lô máy cùng tên → gộp 1 dòng', r['nlo'] < 2 or sum(1 for x in nk if x.startswith('Sửa máy trong kho|')) == 1, nk)
        nks = sheets(f26)['Nhật ký']
        ok('Nhật ký lên trang "Nhật ký" của sổ năm', len(nks) - 1 >= len(nk) and nks[0][:3] == ['id', 't', 'ai'], len(nks))
        r = await J("const keep=db.nk.length;db=emptyDb();Object.keys(localStorage).filter(k=>k.startsWith('shopgon_base')).forEach(k=>localStorage.removeItem(k));await GG.pull();return {a:keep,b:db.nk.length}")
        ok('Máy thứ 2 mở sổ: thấy đủ nhật ký', r['a'] == r['b'] and r['b'] > 0, r)

        # ---------- 2c. IMEI bán 2 lần khi 2 máy cùng mất mạng ----------
        r = await J("""NK.chup();const X=db.may.find(x=>x.tt==='ton');const im=X.imei;
          /* máy B (mất mạng) bán X rồi có mạng đẩy lên sổ */
          const B=JSON.parse(JSON.stringify(db));B.may.find(x=>x.imei===im).tt='ban';B.don.push({id:'b2',bill:'b2',ngay:todayIso(),gio:'10:05',loai:'may',imei:im,ten:X.ten,giaBan:5100000,giaVon:4000000,tt:'Tiền mặt',khach:'Khách máy B',nvTen:'Lan',huy:null});
          await GG.readRemote();await GG.ghiFile(GG.sheetId,GG.dungSheet(B,GG.nam));
          /* máy A (cũng mất mạng) bán đúng máy đó */
          X.tt='ban';db.don.push({id:'a2',bill:'a2',ngay:todayIso(),gio:'10:07',loai:'may',imei:im,ten:X.ten,giaBan:5200000,giaVon:4000000,tt:'Tiền mặt',khach:'Khách máy A',huy:null});save();
          await GG.push();const T=imeiTrung();return {im,n:T.length,ids:T.length?T[0].L.map(d=>d.id):[]}""")
        ok('Gộp đồng bộ phát hiện IMEI bán 2 lần (giữ cả 2 đơn, không mất)', r['n'] == 1 and sorted(r['ids']) == ['a2', 'b2'], r)
        await E("closeWelcome&&closeWelcome();go('home')"); await pg.wait_for_timeout(250)
        t = await pg.inner_text('#v-home')
        ok('Trang chủ báo đỏ "máy đang bị bán 2 lần" kèm 2 đơn', 'bán 2 lần' in t and 'Khách máy A' in t and 'Khách máy B' in t, t[:300])
        await pg.screenshot(path='/tmp/sg_trung_imei.png')
        await pg.click('[data-trung="b2"]'); await pg.wait_for_timeout(250)
        ok('Bấm "Mở đơn" → mở đúng đơn trong Đơn đã bán', await E("more==='hist'&&histOpen==='b2'"))
        r = await J("NK.chup();db.don.find(x=>x.id==='b2').huy='Bán trùng máy B';save();await GG.push();return {n:imeiTrung().length,nk:db.nk.at(-1).viec}")
        ok('Hủy đơn bán nhầm → hết báo đỏ, nhật ký ghi "Hủy đơn"', r['n'] == 0 and r['nk'] == 'Hủy đơn', r)

        # ---------- 2d. Giữ chỗ IMEI khi có mạng (máy chủ giả lập) ----------
        r = await J("""cart=[];const X=db.may.find(x=>x.tt==='ton');window.__X=X.imei;
          /* máy khác (NV Lan) đang giữ máy này */
          await nvPost({act:'nvGiu',sdt:'0911',phien:'p',imei:[X.imei],loai:'giu',may:'NVLAN'});
          window.alert=m=>{window.__al=m};go('sell');sellMode='may';sellImei=X.imei;render();return X.imei""")
        await pg.fill('#sGia', '5.000.000'); await pg.click('#fSell button[type=submit]'); await pg.wait_for_timeout(600)
        r = await J("cartOpen=true;render();await new Promise(r=>setTimeout(r,200));return {al:window.__al||'',tr:!!(cart[0]&&cart[0].trung),txt:document.body.innerText}")
        ok('Giữ chỗ IMEI: máy khác đang bán → báo ngay khi thêm vào đơn (hộp báo + dòng đỏ)', 'NV 0911' in r['al'] and r['tr'] and 'đang bán máy này' in r['txt'], (r['al'], r['tr']))
        await pg.screenshot(path='/tmp/sg_giu_imei.png')
        r = await J("const im=window.__X;cart=[];cartOpen=false;render();await nvPost({act:'nvGiu',sdt:'0911',phien:'p',imei:[im],loai:'bo',may:'NVLAN'});cart=[];const Y=db.may.find(x=>x.tt==='ton'&&x.imei!==im);sellImei=Y.imei;render();return Y.imei")
        await pg.fill('#sGia', '5.000.000'); await pg.click('#fSell button[type=submit]'); await pg.wait_for_timeout(500)
        r2 = await J("cartOpen=true;render();await new Promise(r=>setTimeout(r,200));window.__al='';const im=cart[0].imei;document.querySelector('[data-checkout]').click();await new Promise(r=>setTimeout(r,600));const t=await nvPost({act:'nvGiu',sdt:'0911',phien:'p',imei:[im],loai:'giu',may:'NVLAN'});document.getElementById('rc').hidden=true;return {t:t.trung,al:window.__al}")
        ok('Bán xong → máy chủ ghi "đã bán": máy khác quét lại được báo "đã bán lúc …"', r2['t'] and r2['t'][0]['ban'] and r2['t'][0]['ai'] == 'Chủ shop', r2)
        ok('Máy không bị ai giữ → thêm vào đơn bình thường, không báo', r2['al'] == '', r2)
        r = await J("const im=db.don.at(-1).imei;cancelId=null;const d=db.don.at(-1);d.huy='thu';await giuImei([im],'mo');const t=await nvPost({act:'nvGiu',sdt:'0911',phien:'p',imei:[im],loai:'giu',may:'NVLAN'});return t.trung.length")
        ok('Hủy/trả máy → mở lại, máy khác bán được', r == 0, r)

        # ---------- 3. Sao lưu + Khôi phục thật ----------
        r = await J("const id=await GG.saoLuu('Test');const L=await GG.dsSaoLuu();return {id,L:L.map(x=>x.name),tm:GG._tm}")
        bk1 = r['id']
        ok('Sao lưu: tạo thư mục "Shop Gọn – Sao lưu" + bản sao trong đó', D.f[r['tm']]['name'] == 'Shop Gọn – Sao lưu' and D.f[bk1]['parents'] == [r['tm']] and D.f[bk1]['ap'].get('shopgon') == 'bk', r)
        ok('Bản sao lưu KHÔNG bị nhận nhầm là sổ đang ghi', (await J("const F=await GG.dsNam();return F[2026]")) == f26)
        snap_bk = json.dumps(sheets(bk1), sort_keys=True)
        await J("db.don.push({id:'sau1',bill:'sau1',ngay:todayIso(),gio:'11:00',loai:'pk',ten:'Bán sau sao lưu',giaBan:99000,giaVon:1,tt:'Tiền mặt',huy:null});db.don=db.don.filter(x=>x.id!=='n1');await GG.push();return 1")
        ok('Sau sao lưu: sổ đã thay đổi (thêm 1 đơn, xóa 1 đơn)', json.dumps(sheets(f26), sort_keys=True) != snap_bk)
        r = await J(f"await GG.khoiPhuc('{bk1}');const L=await GG.dsSaoLuu();return {{sau:!!db.don.find(x=>x.id==='sau1'),n1:!!db.don.find(x=>x.id==='n1'),L:L.map(x=>x.appProperties.ly)}}")
        tw = lambda V: [r[:max([i + 1 for i, v in enumerate(r) if v != ''] or [0])] for r in V if any(v != '' for v in r)]
        same = all(tw(sheets(f26)[n]) == tw(sheets(bk1)[n]) for n in sheets(bk1) if n != 'Nhật ký')
        ok('KHÔI PHỤC THẬT: sổ năm nay trở về đúng bản sao lưu (từng trang giống hệt)', same, [(n, sheets(f26)[n][:3], sheets(bk1)[n][:3]) for n in sheets(bk1) if n != 'Nhật ký' and tw(sheets(f26)[n]) != tw(sheets(bk1)[n])][:2])
        ok('Khôi phục KHÔNG xóa nhật ký, ghi thêm dòng "Khôi phục dữ liệu"', await E("db.nk.some(x=>x.viec==='Hủy đơn')&&db.nk.at(-1).viec==='Khôi phục dữ liệu'"))
        ok('Khôi phục: app bỏ đơn sau sao lưu, có lại đơn đã xóa', not r['sau'] and r['n1'], r)
        tr = [x for x in D.f.values() if x['ap'].get('ly') == 'Trước khi khôi phục']
        ok('Trước khi khôi phục tự sao lưu bản hiện tại (không mất gì)', tr and any(len(row) > 1 and row[1] == 'sau1' for n in tr[0]['sheets'] for row in tr[0]['sheets'][n]))
        await J("for(let i=0;i<9;i++)await GG.saoLuu('Hằng tuần');return 1")
        con = [x for x in D.f.values() if x['ap'].get('shopgon') == 'bk' and not x['trashed']]
        ok('Giữ 8 bản sao lưu gần nhất, bản cũ hơn vào thùng rác', len(con) == 8, len(con))
        r = await J("db.shop.saoLuu='';await GG.tuSaoLuu();const a=db.shop.saoLuu;const n0=(await GG.dsSaoLuu()).length;await GG.tuSaoLuu();return {a,same:db.shop.saoLuu===a,n0}")
        ok('Tự sao lưu hằng tuần: chưa có → sao lưu; trong 7 ngày → không sao lưu lại', r['a'] and r['same'], r)

        # ---------- 4. SANG NĂM MỚI: chốt sổ 2026, chép số dư sang 2027 ----------
        await J("""const m=db.may.find(x=>x.tt==='ton');db.don.push({id:'tg9',bill:'tg9',ngay:'2026-12-28',gio:'9:00',loai:'may',imei:m.imei,ten:m.ten,giaBan:5000000,giaVon:4000000,tt:'Trả góp',tgTT:'Chờ duyệt',traTruoc:1000000,cty:'HD',khach:'Chị Sáu',bh:12,huy:null});m.tt='ban';
          const l=db.may.find(x=>x.tt==='ton');l.tt='loi';await GG.push();return 1""")
        truoc = await J("const s=GG.soDu(db,2027);return s.t")
        f26_raw = json.dumps(sheets(f26), sort_keys=True)
        await E("""(()=>{const _D=Date,off=new _D('2027-01-02T09:00:00').getTime()-_D.now();class FD extends _D{constructor(...a){super(...(a.length?a:[_D.now()+off]))}static now(){return _D.now()+off}};window.Date=FD})()""")
        r = await J("await GG.pull();return {nam:GG.nam,kq:GG.kq,files:GG.files,sau:GG.soDu(db,2027).t,today:todayIso()}")
        f27 = r['files'].get('2027')
        ok('01/01/2027: tự mở sổ năm 2027', r['nam'] == 2027 and f27 and r['today'].startswith('2027'), r)
        ok('SỐ DƯ CUỐI NĂM 2026 = ĐẦU NĂM 2027 (khớp 100%)', r['kq'] and r['kq']['khop'] and r['sau'] == truoc, (r['kq'], truoc, r['sau']))
        sd = sheets(f27)['Số dư']
        ok('Trang "Số dư" có máy tồn, máy chờ BH, khách nợ, trả góp chờ, nợ NCC, phụ kiện + dòng KIỂM TRA KHỚP 100%',
           {'Máy tồn', 'Máy chờ bảo hành', 'Khách nợ', 'Trả góp chờ giải ngân', 'Nợ nhà cung cấp', 'Phụ kiện'} <= {x[0] for x in sd} and any(x[0] == 'KIỂM TRA' and x[1] == 'KHỚP 100%' for x in sd), [x[:2] for x in sd[-7:]])
        ok('Số dư: tổng khách nợ / nợ NCC / máy tồn đúng số', [x[4] for x in sd if x[0] == 'TỔNG khách nợ'] == [str(truoc['khachNo'])] and [x[4] for x in sd if x[0] == 'TỔNG nợ nhà cung cấp'] == [str(truoc['nccNo'])] and truoc['khachNo'] == 700000 and truoc['nccNo'] == 5000000, truoc)
        nt = [x[1] for x in sheets(f27)['Năm trước'][1:]]
        ok('Đơn còn nợ / trả góp chờ / phiếu nợ NCC năm cũ chuyển sang trang "Năm trước"', {'cu2', 'n1', 'tg9', 'pn1'} <= set(nt) and 'cu1' not in nt and 't1' not in nt, nt)
        ok('IMEI năm 2027 = đúng máy tồn + chờ BH chuyển sang', len(sheets(f27)['IMEI']) - 1 == truoc['mayN'])
        r = await J("return {min:db.don.filter(x=>!['cu2','n1','tg9'].includes(x.id)&&x.bill!=='cu2').reduce((m,x)=>x.ngay<m?x.ngay:m,'9999'),cu1:!!db.don.find(x=>x.id==='cu1'),t1:!!db.don.find(x=>x.id==='t1'),ws:GG.winStart()}")
        ok('App chỉ giữ 12 tháng liền kề (từ 01/02/2026) + khoản còn mở', r['min'] >= '2026-02-01' and not r['cu1'] and not r['t1'] and r['ws'] == '2026-02-01', r)
        # ghi tiếp năm 2027: sổ 2026 KHÔNG bị ghi đè
        ino = await E("GG.tcols().indexOf('no')")
        f26_sau_chuyen = json.dumps(sheets(f26), sort_keys=True)
        await J("db.don.push({id:'y27',bill:'y27',ngay:todayIso(),gio:'9:00',loai:'pk',ten:'Bán đầu năm',giaBan:150000,giaVon:50000,tt:'Tiền mặt',huy:null});const b=db.don.find(x=>x.id==='n1');b.no=0;await GG.push();await GG.push();return 1")
        ok('Bán đầu năm 2027 → trang T01 sổ 2027', any(x[1] == 'y27' for x in sheets(f27)['T01'][1:]))
        ok('Khách trả nợ năm cũ → cập nhật ở sổ 2027 (trang Năm trước), sổ 2026 đã chốt không bị ghi', json.dumps(sheets(f26), sort_keys=True) == f26_sau_chuyen and any(x[1] == 'n1' and (len(x) <= ino or x[ino] == '') for x in sheets(f27)['Năm trước'][1:]))
        r = await J("const t0=JSON.stringify(Object.fromEntries(GG.dsSheet().map(n=>[n,1])));const id=GG.files[2026];await GG.push();return 1")
        ok('Đồng bộ lặp lại không phát sinh ghi thừa vào "Năm trước"', len(sheets(f27)['Năm trước']) - 1 == len(nt))
        # máy 2 mở sổ năm 2027 từ đầu
        r = await J("db=emptyDb();Object.keys(localStorage).filter(k=>k.startsWith('shopgon_base')).forEach(k=>localStorage.removeItem(k));GG._cu=null;await GG.moSo();await GG.pull();return {nam:GG.nam,t:GG.soDu(db,2027).t,y27:!!db.don.find(x=>x.id==='y27'),dec:db.don.filter(x=>x.ngay.startsWith('2026-12')).length}")
        ok('Máy 2 mở sổ 2027: thấy đủ 12 tháng (cả tháng 12/2026) + đơn mới', r['nam'] == 2027 and r['y27'] and r['dec'] > 0, r)

        # ---------- 5. Tra IMEI / bảo hành không giới hạn 12 tháng ----------
        r = await J("const k=await GG.timImei('351111111111111');return k.map(x=>({nam:x.nam,ten:x.may.ten,ban:x.don&&x.don.ngay}))")
        ok('Tra IMEI bán 15/01/2026 (ngoài 12 tháng) → tìm thấy ở sổ 2026, có ngày bán', r and r[0]['nam'] == 2026 and r[0]['ban'] == '2026-01-15', r)
        await E("NV=null;XEM=false;db.sample=false;closeWelcome&&closeWelcome();more='look';lookQ='351111111111111';go('more')"); await pg.wait_for_timeout(200)
        await pg.click('[data-imeicu]'); await pg.wait_for_timeout(600)
        t = await pg.inner_text('#v-more')
        ok('Màn Tra IMEI: nút "Tìm trong sổ các năm trước" ra kết quả + bảo hành', 'sổ năm 2026' in t and ('Còn BH' in t or 'Hết BH' in t), t[-300:])
        await pg.screenshot(path='/tmp/sg_tra_imei.png')
        await E("more='set';slOpen=true;slDs=null;go('more');GG.dsSaoLuu().then(L=>{slDs=L;renderMore()})"); await pg.wait_for_timeout(500)
        el = await pg.query_selector('#pSoNam'); await el.scroll_into_view_if_needed()
        t = await pg.inner_text('#pSoNam')
        ok('Cài đặt: khung "Sổ dữ liệu · Sao lưu" hiện sổ 2026/2027, kết quả chốt số dư, danh sách khôi phục', 'Sổ năm 2027' in t and 'Sổ năm 2026' in t and 'khớp 100%' in t and 'Năm 2026' in t and 'Đã chốt' in t, t)
        await pg.evaluate("document.getElementById('pSoNam').scrollIntoView({block:'start'});scrollBy(0,-130)"); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/sg_so_nam.png')
        async with pg.expect_download() as dl:
            await pg.click('[data-xls="2027"]')
        fn = (await dl.value).suggested_filename; await pg.wait_for_timeout(300)
        ok('Nút ⬇️ Excel tải cả sổ năm về máy (.xlsx) + ghi nhật ký', fn.endswith('.xlsx') and 'nam2027' in fn and await E("db.nk.at(-1).viec==='Tải dữ liệu Excel'"), fn)
        await E("more='nk';go('more')"); await pg.wait_for_timeout(200)
        t = await pg.inner_text('#v-more')
        ok('Màn Nhật ký thay đổi hiện đủ dòng (Tải Excel, Chốt sổ…)', 'Tải dữ liệu Excel' in t and 'Chốt sổ năm 2026' in t, t[:300])
        await pg.screenshot(path='/tmp/sg_nhat_ky.png')
        ok('Không lỗi JS', not errs, errs)
        await b.close()
    dat = sum(1 for k in KQ if k[1]); print(f'\nKẾT QUẢ: {dat}/{len(KQ)} đạt')

asyncio.run(main())
