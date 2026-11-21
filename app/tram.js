/* Shop Gọn — TRẠM TRUNG CHUYỂN MÃ HOÁ (21/11/2026, anh Thái chốt sau khi hỏi chéo Gemini + ChatGPT)
   - Drive của shop vẫn là KHO CHÍNH. Trạm (Firebase shopgon-vn) chỉ chở "lô thay đổi" đã khoá AES-GCM 256 trên máy shop.
   - Chìa nằm trong Drive shop (file "Shop Gọn – chìa đồng bộ") + bộ nhớ máy. Shop Gọn không có chìa → không đọc được.
   - Đường trạm /t/{sid}/ev/{lô}: sid = SHA-256(chìa) → không có chìa thì không biết đường.
   - MỘT máy chính (db.shop.tramW) ghi Drive. Máy khác KHÔNG ghi/gộp Drive nữa → hết cộng trùng tồn phụ kiện, hết ghi đè.
   - Tồn phụ kiện gửi dạng chênh lệch (dl) → 2 máy cùng bán trừ đúng 2.
   - db.shop.tramT = mốc lô cuối máy chính đã lưu vào Drive → máy mới lấy Drive rồi chỉ phát lại lô sau mốc. */
const TRAM={
  BANG:{may:'imei',don:'id',hang:'id',pn:'id',chi:'id',nk:'id'},
  BO_SHOP:new Set(['tramT']),            /* khoá shop không gửi qua trạm */
  k:null,raw:'',sid:'',S:null,lastT:0,da:null,un:null,ok:false,loi:'',choTu:0,fromCache:true,_nap:null,_don:0,san:null,
  FB(){return window.TRAM_FB||window.FB},
  bat(){try{return !!(db&&db.shop&&db.shop.tram)&&!db.sample&&typeof NV!=='undefined'&&!NV&&!XEM&&!DEMO}catch(_){return false}},
  me(){return SK.may()},
  chinh(){return !!(db&&db.shop&&db.shop.tramW===this.me())},
  /* ---- bộ nhớ máy ---- */
  kK(){return 'sg_tram_k'},kT(){return 'sg_tram_t_'+this.sid},kD(){return 'sg_tram_da_'+this.sid},
  docLS(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(_){return d}},
  ghiLS(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}},
  /* ---- mã hoá ---- */
  b64(u){let s='';const a=new Uint8Array(u);for(let i=0;i<a.length;i+=8192)s+=String.fromCharCode.apply(null,a.subarray(i,i+8192));return btoa(s)},
  ub64(s){const b=atob(s),a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a},
  /* 21/11 đợt 2: cặp khoá RSA cho máy PG — PG chỉ có khoá CÔNG KHAI (khoá được, không mở được); máy chủ shop có khoá riêng để mở đơn PG */
  async datNv(pub,priv){this.nvPub=pub||null;this.nvPriv=null;if(priv)try{this.nvPriv=await crypto.subtle.importKey('jwk',priv,{name:'RSA-OAEP',hash:'SHA-256'},false,['unwrapKey'])}catch(_){}this._nvPrivJ=priv||null},
  async taoNv(){const kp=await crypto.subtle.generateKey({name:'RSA-OAEP',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['wrapKey','unwrapKey']);
    return {pub:await crypto.subtle.exportKey('jwk',kp.publicKey),priv:await crypto.subtle.exportKey('jwk',kp.privateKey)}},
  async giaiMaNv(c,iv){const all=this.ub64(c),w=all.slice(0,256),ct=all.slice(256);const k=await crypto.subtle.unwrapKey('raw',w,this.nvPriv,{name:'RSA-OAEP'},'AES-GCM',false,['decrypt']);
    const p=await crypto.subtle.decrypt({name:'AES-GCM',iv:this.ub64(iv)},k,ct);return JSON.parse(new TextDecoder().decode(p))},
  async datChia(raw,nv){const u=this.ub64(raw);if(nv)await this.datNv(nv.pub,nv.priv);this.k=await crypto.subtle.importKey('raw',u,'AES-GCM',false,['encrypt','decrypt']);this.raw=raw;
    const h=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('shopgon|'+raw));this.sid=[...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,'0')).join('');
    this.ghiLS(this.kK(),{raw,e:(typeof GG!=='undefined'&&GG.email)||'',nvPub:this.nvPub||null,nvPriv:this._nvPrivJ||null})},
  async maHoa(o){const iv=crypto.getRandomValues(new Uint8Array(12));const c=await crypto.subtle.encrypt({name:'AES-GCM',iv},this.k,new TextEncoder().encode(JSON.stringify(o)));return {c:this.b64(c),iv:this.b64(iv)}},
  async giaiMa(c,iv){const p=await crypto.subtle.decrypt({name:'AES-GCM',iv:this.ub64(iv)},this.k,this.ub64(c));return JSON.parse(new TextDecoder().decode(p))},
  /* ---- chìa trong Drive shop ---- */
  async timChiaDrive(){const q=encodeURIComponent("appProperties has { key='shopgon' and value='chia' } and trashed=false");
    const f=await GG.api('https://www.googleapis.com/drive/v3/files?q='+q+'&orderBy=createdTime desc&fields=files(id,name)');const x=f.files&&f.files[0];if(!x)return null;
    const r=await fetch('https://www.googleapis.com/drive/v3/files/'+x.id+'?alt=media',{headers:{Authorization:'Bearer '+GG.token}});if(!r.ok)throw new Error('chia '+r.status);const o=await r.json();return o&&o.k?o:null},
  async luuChiaDrive(raw,nv){const tm=await GG.thuMuc();const meta={name:'Shop Gọn – chìa đồng bộ (KHÔNG xoá, KHÔNG gửi ai).json',parents:[tm],mimeType:'application/json',appProperties:{shopgon:'chia'}};
    const b='sgb'+Date.now(),body='--'+b+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(meta)+'\r\n--'+b+'\r\nContent-Type: application/json\r\n\r\n'+JSON.stringify({k:raw,nvPub:nv&&nv.pub||null,nvPriv:nv&&nv.priv||null,ghiChu:'Chìa mở dữ liệu đồng bộ Shop Gọn của shop. Mất file này thì máy mới phải đăng nhập máy chính để lấy lại.'})+'\r\n--'+b+'--';
    const r=await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',{method:'POST',headers:{Authorization:'Bearer '+GG.token,'Content-Type':'multipart/related; boundary='+b},body});if(!r.ok)throw new Error('luu chia '+r.status)},
  /* ---- nạp gói Firebase tự host (chỉ shop bật trạm mới tải) ---- */
  napFB(){if(this.FB())return Promise.resolve();if(this._nap)return this._nap;this._nap=new Promise((ok,bad)=>{const s=document.createElement('script');s.src='/app/fb.js?v=1';s.onload=ok;s.onerror=e=>{this._nap=null;bad(e)};document.head.appendChild(s)});return this._nap},
  /* ---- ảnh chụp để so thay đổi ---- */
  anh(){const S={shop:{}};const sh=(db&&db.shop)||{};for(const k in sh)if(!this.BO_SHOP.has(k))S.shop[k]=JSON.stringify(sh[k]);
    for(const t in this.BANG){const f=this.BANG[t],m=new Map();(db[t]||[]).forEach(o=>{if(o&&o[f]!=null)m.set(String(o[f]),JSON.stringify(o))});S[t]=m}return S},
  khac(){const S=this.S,N=this.anh(),ops=[];const sh={},bo=[];
    for(const k in N.shop)if(N.shop[k]!==S.shop[k])sh[k]=JSON.parse(N.shop[k]);for(const k in S.shop)if(!(k in N.shop))bo.push(k);
    if(Object.keys(sh).length||bo.length)ops.push({k:'shop',v:sh,x:bo});
    for(const t in this.BANG){const a=S[t]||new Map(),b=N[t];
      b.forEach((j,id)=>{const cu=a.get(id);if(cu===j)return;const v=JSON.parse(j);
        if(t==='hang'&&cu!=null){const o=JSON.parse(cu),dl=(+v.sl||0)-(+o.sl||0);const v2={...v};delete v2.sl;ops.push({k:t,id,v:v2,dl})}
        else ops.push({k:t,id,v})});
      a.forEach((_,id)=>{if(!b.has(id))ops.push({k:t,id,x:1})})}
    return {ops,N}},
  /* ---- gửi: gọi trong save() ---- */
  /* hàng chờ lô chưa được trạm xác nhận: cất ở máy (localStorage) — tắt app giữa chừng, mở lại gửi tiếp */
  kQ(){return 'sg_tram_q_'+this.sid},docQ(){return this.docLS(this.kQ(),[])},
  ghi(){if(!this.k||!this.S||!this.bat())return;const {ops,N}=this.khac();if(!ops.length)return;this.S=N;
    const id=Date.now().toString(36)+'-'+this.me().slice(0,8)+'-'+Math.random().toString(36).slice(2,8);this.da.add(id);this.luuDa();
    if(!this.choTu)this.choTu=Date.now();if(!this.chinh())SK.doi();
    this.maHoa({v:1,ops,ts:Date.now()}).then(e=>{const q=this.docQ();q.push({id,c:e.c,iv:e.iv,luc:Date.now()});this.ghiLS(this.kQ(),q);this.gui({id,c:e.c,iv:e.iv})});this.ve()},
  get choGui(){return this.sid?this.docQ().length:0},set choGui(_){},
  gui(x,laiLan){(this.san||Promise.reject(new Error('chưa nối trạm'))).then(()=>this.FB().ghi(this.sid,x.id,{c:x.c,iv:x.iv,d:this.me()})).then(()=>this.xong(x.id),er=>{
      const m=String(er&&(er.code||er.message)||er);if(laiLan&&/permission/i.test(m)){this.xong(x.id);return}   /* gửi lại lô đã có trên trạm → coi như xong */
      this.loi='Chưa gửi được lên trạm: '+m.slice(0,80);this.ve()})},
  xong(id){const q=this.docQ().filter(o=>o.id!==id);this.ghiLS(this.kQ(),q);if(!q.length){this.choTu=0;if(!this.chinh())SK.len()}if(/Chưa gửi/.test(this.loi))this.loi='';this.ve()},
  /* ---- nhận lô của máy khác ---- */
  apDung(ops){let doi=0;for(const op of ops){
      if(op.k==='shop'){db.shop=db.shop||{};for(const k in op.v||{}){if(this.BO_SHOP.has(k))continue;db.shop[k]=op.v[k];doi++}(op.x||[]).forEach(k=>{if(!this.BO_SHOP.has(k)){delete db.shop[k];doi++}});continue}
      const f=this.BANG[op.k];if(!f)continue;const A=db[op.k]=db[op.k]||[];const i=A.findIndex(o=>o&&String(o[f])===op.id);
      if(op.x){if(i>=0){A.splice(i,1);doi++}continue}
      if(op.k==='hang'&&op.dl!==undefined){if(i>=0){const sl=(+A[i].sl||0)+(+op.dl||0);A[i]={...A[i],...op.v,sl}}else A.push({...op.v,sl:+op.dl||0});doi++;continue}
      if(i>=0)A[i]=op.v;else A.push(op.v);doi++}
    return doi},
  async nhan(ds,pend,cache){this.fromCache=!!cache;ds.sort((a,b)=>a.t-b.t);let doi=0,cu=this.chinh();
    if(ds.some(d=>!this.da.has(d.id)&&d.d!==this.me()))this.ghi();          /* đẩy thay đổi trên máy trước khi nhận, ảnh chụp không nuốt thay đổi chưa gửi */
    const nvDon=[];
    for(const d of ds){if(!this.da.has(d.id)&&d.d!==this.me()){
        if(String(d.d||'').startsWith('nv-')){/* đơn PG: CHỈ máy chính áp (máy khác nhận kết quả qua lô của máy chính) */if(this.chinh()&&this.nvPriv){try{nvDon.push(await this.giaiMaNv(d.c,d.iv))}catch(e){this.loi='Không mở được 1 đơn PG'}}}
        else{try{const o=await this.giaiMa(d.c,d.iv);doi+=this.apDung(o.ops||[])}catch(e){this.loi='Không mở được 1 lô (sai chìa?)'}}}
      this.da.add(d.id);if(d.t>this.lastT)this.lastT=d.t}
    this.ghiLS(this.kT(),this.lastT);this.luuDa();
    if(doi){this.S=this.anh();Store.save(db);try{render()}catch(_){}
      if(this.chinh()&&typeof GG!=='undefined'&&GG.token&&GG.sheetId){SK.doi();GG.queue(1500)}
      if(cu&&!this.chinh())ggStatus('Máy khác đã làm máy chính — máy này chỉ gửi qua trạm')}
    if(nvDon.length&&typeof nvApply==='function'){const dang=new Set(((db.shop&&db.shop.nv)||[]).map(x=>String(x.sdt)));let n=0;
      nvDon.forEach(o=>{if(o&&o.id&&(!o.nv||dang.has(String(o.nv))))n+=nvApply(o)});   /* PG đã bị xoá khỏi danh sách thì bỏ đơn */
      if(n){db.shop.nvCo=1;save();try{render()}catch(_){}try{toast('Nhận '+n+' đơn PG qua trạm')}catch(_){}}}
    this.ve()},
  luuDa(){const a=[...this.da];if(a.length>4000)this.da=new Set(a.slice(-3000));this.ghiLS(this.kD(),[...this.da])},
  /* ---- khởi động: có chìa trên máy thì chạy luôn, không cần Google ---- */
  async batDau(){if(!this.bat()||this.un||this._dang)return;this._dang=true;try{
      if(!this.k){const c=this.docLS(this.kK(),null);if(c&&c.raw&&(c.nvPriv||!(typeof GG!=='undefined'&&GG.token)))await this.datChia(c.raw,{pub:c.nvPub,priv:c.nvPriv});else if(typeof GG!=='undefined'&&GG.token){const o=await this.timChiaDrive();if(!o){this.loi='Chưa có chìa trong Drive — mở máy chính';this.ve();return}await this.datChia(o.k,{pub:o.nvPub,priv:o.nvPriv})}else{this.loi='Cần đăng nhập Google 1 lần để lấy chìa';this.ve();return}}
      /* máy chính chưa có cặp khoá PG (shop bật trạm trước đợt 2) → tạo, cất bản chìa mới nhất vào Drive */
      if(!this.nvPriv&&this.chinh()&&typeof GG!=='undefined'&&GG.token){try{const nv=await this.taoNv();await this.luuChiaDrive(this.raw,nv);await this.datChia(this.raw,nv)}catch(_){}}
      this.lastT=Math.max(+this.docLS(this.kT(),0)||0,+(db.shop&&db.shop.tramT)||0);this.da=new Set(this.docLS(this.kD(),[]));this.S=this.anh();this.ghiLS('sg_tram_on',1);
      const q0=this.docQ();if(q0.length&&!this.choTu)this.choTu=q0[0].luc||Date.now();
      this.san=this.napFB().then(()=>this.FB().dangNhap());await this.san;this.ok=true;this.loi='';
      q0.forEach(x=>this.gui(x,true));
      this.un=this.FB().nghe(this.sid,this.lastT,(ds,p,c)=>this.nhan(ds,p,c),e=>{this.loi='Mất kết nối trạm: '+String(e&&e.code||e).slice(0,60);this.ve()});
      if(this.chinh()&&Date.now()-this._don>864e5){this._don=Date.now();setTimeout(()=>this.FB().don(this.sid,Date.now()-31*864e5).catch(()=>{}),30000)}
      this.ve()}catch(e){this.loi='Chưa nối được trạm: '+String(e&&e.message||e).slice(0,80);this.ve()}finally{this._dang=false}},
  dung(){if(this.un){try{this.un()}catch(_){}}this.un=null;this.ok=false;this.san=null},
  /* ---- bật lần đầu (chủ shop, đang có Google): máy này làm máy chính ---- */
  async batMoi(){if(!GG.token||!GG.sheetId)throw new Error('Đăng nhập Google trước');
    let o=await this.timChiaDrive(),raw,nv;
    if(o&&o.nvPriv){raw=o.k;nv={pub:o.nvPub,priv:o.nvPriv}}else{raw=o&&o.k||this.b64(crypto.getRandomValues(new Uint8Array(32)));nv=await this.taoNv();await this.luuChiaDrive(raw,nv)}
    await this.datChia(raw,nv);db.shop.tram=1;db.shop.tramW=this.me();db.shop.tramT=+db.shop.tramT||0;this.ghiLS(this.kT(),Math.max(+this.docLS(this.kT(),0)||0,db.shop.tramT));
    this.dung();this.S=null;this.k=null;save();await GG.push();await this.batDau()},
  /* ---- nhận làm máy chính: lấy nguyên Drive làm gốc, giữ mọi dòng Drive có mà máy này thiếu (không xoá theo bàn giao) ---- */
  async lamChinh(){if(!GG.token||!GG.sheetId)throw new Error('Đăng nhập Google trước');if(this.choGui)throw new Error('Còn lô chưa lên trạm, chờ có mạng');
    const rem=await GG.readRemote();if(!rem.empty){for(const [t,[f,key]] of Object.entries(GG.T)){const L=db[f]=db[f]||[];const co=new Set(L.map(o=>String(o[key])));(rem[f]||[]).forEach(o=>{if(!co.has(String(o[key])))L.push(o)})}GG.setBase(rem)}
    db.shop.tramW=this.me();save();await GG.push()},
  pending(){return this.choGui},
  coChia(){const c=this.docLS(this.kK(),null);return !!(c&&c.raw)},
  daChay(){return !!this.docLS('sg_tram_on',0)},
  /* có được ghi Drive không: máy phụ thì không; máy chính chờ lô của mình lên trạm (tối đa 10 phút) để mốc tramT phủ hết */
  choPhepDrive(){if(!this.bat())return 'ok';if(!this.chinh())return 'phu';if(this.k&&this.choGui&&Date.now()-(this.choTu||Date.now())<6e5)return 'cho';return 'ok'},
  /* mã QR cho máy PG: đường trạm + khoá CÔNG KHAI (không có chìa mở dữ liệu) */
  qrNv(){if(!this.sid||!this.nvPub)return '';const o={s:this.sid,p:this.nvPub,t:String((db.shop&&db.shop.ten)||'').slice(0,40)};return location.origin+'/app/#nvtram='+btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')},
  ve(){try{document.querySelectorAll('.tramBar').forEach(el=>{const h=tramBar();if(el.innerHTML!==h)el.innerHTML=h})}catch(_){}}
};
function tramBar(){if(typeof NV!=='undefined'&&NV||XEM||DEMO||!db||db.sample)return '';const on=!!(db.shop&&db.shop.tram);
  if(!on){if(!GG.token||!GG.sheetId)return '';return `<div class="alert chanb tramb"><b>⚡ Đồng bộ tức thì giữa các máy</b><span>Bán ở máy nào, máy khác thấy ngay trong vài giây. Dữ liệu vẫn nằm trong Drive của shop; đồng bộ qua trạm đã khoá — Shop Gọn không đọc được. Máy đang mở sẽ làm máy chính lưu Drive.</span><div class="inrow" style="margin-top:8px"><button class="btn" data-tram="bat">Bật đồng bộ tức thì</button></div></div>`}
  const T=TRAM,ch=T.chinh();let tt,mau='';
  if(T.loi)tt='🔴 '+esc(T.loi),mau='red';else if(!T.ok)tt='⏳ Đang nối trạm…';else if(T.choGui)tt='🟡 '+T.choGui+' lô chưa lên trạm (mất mạng?) — đừng xoá app';else tt=T.fromCache?'🟡 Chưa thấy trạm (mất mạng?) — vẫn bán bình thường':'🟢 Đã đồng bộ với các máy';
  return `<div class="alert ${mau} chanb tramb"><b>⚡ Đồng bộ tức thì · ${ch?'Máy chính (lưu Drive)':'Máy phụ'}</b><span>${tt}${ch?'':'<br>Máy chính lưu vào Drive. Máy chính hỏng/mất → bấm nút dưới ở máy khác.'}</span>${!ch&&GG.token?`<div class="inrow" style="margin-top:8px"><button class="ghost" data-tram="chinh">Đặt máy này làm máy chính</button></div>`:''}</div>`}
document.addEventListener('click',async e=>{const b=e.target.closest('[data-tram]');if(!b)return;b.disabled=true;
  try{if(b.dataset.tram==='bat'){toast('Đang bật đồng bộ tức thì…');await TRAM.batMoi();toast('Đã bật — máy này là máy chính')}
    else if(b.dataset.tram==='chinh'){toast('Đang nhận làm máy chính…');await TRAM.lamChinh();toast('Máy này đã là máy chính')}}
  catch(er){toast('Chưa xong: '+String(er&&er.message||er).slice(0,80))}finally{b.disabled=false;TRAM.ve();try{render()}catch(_){}}});
/* ===== 21/11 đợt 2: MÁY PG (nhân viên bán trên điện thoại riêng) =====
   PG quét mã QR ở máy chủ shop → máy PG nhớ đường trạm + khoá CÔNG KHAI. Bán xong: đơn khoá bằng khoá công khai → trạm → máy chính mở bằng khoá riêng.
   PG KHÔNG có chìa của shop → không đọc được dữ liệu shop (giá vốn, lời) dù có mở bộ nhớ máy. Đường máy chủ cũ (nvBan) vẫn chạy song song: đơn đến đường nào trước thì nhận, mã đơn trùng thì bỏ. */
const NVT={K:'sg_nvtram',KQ:'sg_nvtram_q',san:null,ok:false,loi:'',
  cfg(){return TRAM.docLS(this.K,null)},
  coNoi(){const c=this.cfg();return !!(c&&c.s&&c.p)},
  docHash(){const ok=this.docChuoi(location.hash||'');if(/nvtram=/.test(location.hash||''))try{history.replaceState(null,'',location.pathname+location.search)}catch(_){}return ok},
  docChuoi(t){const m=/[#&]nvtram=([A-Za-z0-9_-]+)/.exec(t||'');if(!m)return false;
    try{const s=m[1].replace(/-/g,'+').replace(/_/g,'/');const o=JSON.parse(decodeURIComponent(escape(atob(s+'==='.slice((s.length+3)%4)))));if(o&&/^[0-9a-f]{64}$/.test(o.s)&&o.p&&o.p.n){TRAM.ghiLS(this.K,{s:o.s,p:o.p,t:o.t||'',luc:Date.now()});this._moi=1;return true}}catch(_){}return false},
  /* quét QR NGAY TRONG APP — iPhone: app cài ngoài màn hình chính có bộ nhớ riêng, quét bằng camera iPhone sẽ mở Safari (bộ nhớ khác) → phải quét trong app */
  async quet(){const box=$('scan'),msg=$('scanMsg');scanTarget='nvtram';scanGot=[];box.hidden=false;try{drawScanList()}catch(_){}$('scanClose').textContent='Đóng';$('scanTorch').hidden=true;msg.textContent='Đang mở camera…';
    let det;try{if('BarcodeDetector' in window&&(await BarcodeDetector.getSupportedFormats()).includes('qr_code'))det=new BarcodeDetector({formats:['qr_code']});
      else{await loadBd();const A=window.BarcodeDetectionAPI;A.setZXingModuleOverrides({locateFile:(p,pre)=>p.endsWith('.wasm')?'/app/bd/zxing_reader.wasm':pre+p});det=new A.BarcodeDetector({formats:['qr_code']})}}
    catch(e){msg.textContent='Chưa tải được bộ đọc mã, kiểm tra mạng.';return}
    try{stream=await navigator.mediaDevices.getUserMedia({audio:false,video:{facingMode:{ideal:'environment'}}});const v=$('cam');v.srcObject=stream;await v.play();msg.textContent='Đưa mã QR trên máy chủ shop vào khung';
      scanTimer=setInterval(async()=>{if(scanBusy||!v.videoWidth)return;scanBusy=true;try{const r=await det.detect(v);const t=(r||[]).map(x=>x.rawValue).find(x=>/nvtram=/.test(x||''));
        if(t){closeScan();if(this.docChuoi(t)){toast('⚡ Đã nối đồng bộ tức thì với shop');this.day();try{render()}catch(_){}}else toast('Mã QR không đúng, nhờ chủ shop mở lại mã')}}catch(_){}finally{scanBusy=false}},300)}
    catch(e){msg.textContent='Không mở được camera. Cho phép camera cho Shop Gọn trong Cài đặt.'}},
  q(){return TRAM.docLS(this.KQ,[])},
  async khoa(o){const c=this.cfg();const pub=await crypto.subtle.importKey('jwk',c.p,{name:'RSA-OAEP',hash:'SHA-256'},false,['wrapKey']);
    const k=await crypto.subtle.generateKey({name:'AES-GCM',length:256},true,['encrypt']);const iv=crypto.getRandomValues(new Uint8Array(12));
    const ct=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv},k,new TextEncoder().encode(JSON.stringify(o))));const w=new Uint8Array(await crypto.subtle.wrapKey('raw',k,pub,{name:'RSA-OAEP'}));
    const all=new Uint8Array(w.length+ct.length);all.set(w,0);all.set(ct,w.length);return {c:TRAM.b64(all),iv:TRAM.b64(iv)}},
  /* gửi 1 đơn: khoá → cất hàng chờ trên máy → trạm (mã lô = 'nv-'+mã đơn: gửi lại không thành 2 đơn) */
  async gui(o){if(!this.coNoi()||!o||!o.id)return;try{const e=await this.khoa(o);const id='nv-'+String(o.id).replace(/[^A-Za-z0-9_-]/g,'').slice(0,80);
      const q=this.q().filter(x=>x.id!==id);q.push({id,c:e.c,iv:e.iv,d:'nv-'+String(o.nv||'').slice(0,20)});TRAM.ghiLS(this.KQ,q);this.day()}catch(er){this.loi='Chưa khoá được đơn: '+String(er&&er.message||er).slice(0,60)}},
  day(){const c=this.cfg();if(!c)return;const q=this.q();if(!q.length)return;
    (this.san||(this.san=TRAM.napFB().then(()=>TRAM.FB().dangNhap()))).then(()=>{this.ok=true;q.forEach(x=>TRAM.FB().ghi(c.s,x.id,{c:x.c,iv:x.iv,d:x.d}).then(()=>this.xong(x.id),er=>{if(/permission/i.test(String(er&&(er.code||er.message)||er)))this.xong(x.id);else this.loi='Chưa gửi được lên trạm'}))},er=>{this.san=null;this.loi='Chưa nối được trạm'})},
  xong(id){TRAM.ghiLS(this.KQ,this.q().filter(x=>x.id!==id));this.loi='';try{if(typeof view!=='undefined'&&view==='home')render()}catch(_){}},
  the(){if(!this.coNoi())return `<div class="alert amber"><b>⚡ Chưa nối đồng bộ tức thì</b><span>Nhờ chủ shop mở <b>Thêm › Quản lý nhân viên › Hiện mã QR</b>, rồi bấm nút dưới để quét <b>ngay trong app</b>. Chưa quét vẫn bán được (đơn đi đường cũ).</span><div class="inrow" style="margin-top:8px"><button class="btn" data-nvquet="1">📷 Quét mã QR đồng bộ</button></div></div>`;
    const n=this.q().length;return n?`<div class="alert amber"><b>⚡ ${n} đơn chưa lên trạm</b><span>Mất mạng? Có mạng app tự gửi. Đừng xoá app.</span></div>`:`<div class="alert chanb tramb"><b>⚡ Đồng bộ tức thì: đã nối</b><span>Bán xong, chủ shop thấy đơn trong vài giây.</span></div>`}};
NVT.docHash();
setInterval(()=>{try{if(NVT.coNoi()&&NVT.q().length)NVT.day()}catch(_){}},20000);
window.addEventListener('online',()=>{try{NVT.day()}catch(_){}});
document.addEventListener('click',e=>{const b=e.target.closest('[data-nvquet]');if(b)NVT.quet()});
