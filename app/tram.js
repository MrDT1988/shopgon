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
  async datChia(raw){const u=this.ub64(raw);this.k=await crypto.subtle.importKey('raw',u,'AES-GCM',false,['encrypt','decrypt']);this.raw=raw;
    const h=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('shopgon|'+raw));this.sid=[...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,'0')).join('');
    this.ghiLS(this.kK(),{raw,e:(typeof GG!=='undefined'&&GG.email)||''})},
  async maHoa(o){const iv=crypto.getRandomValues(new Uint8Array(12));const c=await crypto.subtle.encrypt({name:'AES-GCM',iv},this.k,new TextEncoder().encode(JSON.stringify(o)));return {c:this.b64(c),iv:this.b64(iv)}},
  async giaiMa(c,iv){const p=await crypto.subtle.decrypt({name:'AES-GCM',iv:this.ub64(iv)},this.k,this.ub64(c));return JSON.parse(new TextDecoder().decode(p))},
  /* ---- chìa trong Drive shop ---- */
  async timChiaDrive(){const q=encodeURIComponent("appProperties has { key='shopgon' and value='chia' } and trashed=false");
    const f=await GG.api('https://www.googleapis.com/drive/v3/files?q='+q+'&orderBy=createdTime&fields=files(id,name)');const x=f.files&&f.files[0];if(!x)return '';
    const r=await fetch('https://www.googleapis.com/drive/v3/files/'+x.id+'?alt=media',{headers:{Authorization:'Bearer '+GG.token}});if(!r.ok)throw new Error('chia '+r.status);const o=await r.json();return o&&o.k||''},
  async luuChiaDrive(raw){const tm=await GG.thuMuc();const meta={name:'Shop Gọn – chìa đồng bộ (KHÔNG xoá, KHÔNG gửi ai).json',parents:[tm],mimeType:'application/json',appProperties:{shopgon:'chia'}};
    const b='sgb'+Date.now(),body='--'+b+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(meta)+'\r\n--'+b+'\r\nContent-Type: application/json\r\n\r\n'+JSON.stringify({k:raw,ghiChu:'Chìa mở dữ liệu đồng bộ Shop Gọn của shop. Mất file này thì máy mới phải đăng nhập máy chính để lấy lại.'})+'\r\n--'+b+'--';
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
    for(const d of ds){if(!this.da.has(d.id)&&d.d!==this.me()){try{const o=await this.giaiMa(d.c,d.iv);doi+=this.apDung(o.ops||[])}catch(e){this.loi='Không mở được 1 lô (sai chìa?)'}}
      this.da.add(d.id);if(d.t>this.lastT)this.lastT=d.t}
    this.ghiLS(this.kT(),this.lastT);this.luuDa();
    if(doi){this.S=this.anh();Store.save(db);try{render()}catch(_){}
      if(this.chinh()&&typeof GG!=='undefined'&&GG.token&&GG.sheetId){SK.doi();GG.queue(1500)}
      if(cu&&!this.chinh())ggStatus('Máy khác đã làm máy chính — máy này chỉ gửi qua trạm')}
    this.ve()},
  luuDa(){const a=[...this.da];if(a.length>4000)this.da=new Set(a.slice(-3000));this.ghiLS(this.kD(),[...this.da])},
  /* ---- khởi động: có chìa trên máy thì chạy luôn, không cần Google ---- */
  async batDau(){if(!this.bat()||this.un||this._dang)return;this._dang=true;try{
      if(!this.k){const c=this.docLS(this.kK(),null);if(c&&c.raw)await this.datChia(c.raw);else if(typeof GG!=='undefined'&&GG.token){const raw=await this.timChiaDrive();if(!raw){this.loi='Chưa có chìa trong Drive — mở máy chính';this.ve();return}await this.datChia(raw)}else{this.loi='Cần đăng nhập Google 1 lần để lấy chìa';this.ve();return}}
      this.lastT=Math.max(+this.docLS(this.kT(),0)||0,+(db.shop&&db.shop.tramT)||0);this.da=new Set(this.docLS(this.kD(),[]));this.S=this.anh();this.ghiLS('sg_tram_on',1);
      const q0=this.docQ();if(q0.length&&!this.choTu)this.choTu=q0[0].luc||Date.now();
      this.san=this.napFB().then(()=>this.FB().dangNhap());await this.san;this.ok=true;this.loi='';
      q0.forEach(x=>this.gui(x,true));
      this.un=this.FB().nghe(this.sid,this.lastT,(ds,p,c)=>this.nhan(ds,p,c),e=>{this.loi='Mất kết nối trạm: '+String(e&&e.code||e).slice(0,60);this.ve()});
      if(this.chinh()&&Date.now()-this._don>864e5){this._don=Date.now();setTimeout(()=>this.FB().don(this.sid,Date.now()-31*864e5).catch(()=>{}),30000)}
      this.ve()}catch(e){this.loi='Chưa nối được trạm: '+String(e&&e.message||e).slice(0,80);this.ve()}finally{this._dang=false}},
  dung(){if(this.un){try{this.un()}catch(_){}}this.un=null;this.ok=false;this.san=null},
  /* ---- bật lần đầu (chủ shop, đang có Google): máy này làm máy chính ---- */
  async batMoi(){if(!GG.token||!GG.sheetId)throw new Error('Đăng nhập Google trước');let raw=await this.timChiaDrive();
    if(!raw){raw=this.b64(crypto.getRandomValues(new Uint8Array(32)));await this.luuChiaDrive(raw)}
    await this.datChia(raw);db.shop.tram=1;db.shop.tramW=this.me();db.shop.tramT=+db.shop.tramT||0;this.ghiLS(this.kT(),Math.max(+this.docLS(this.kT(),0)||0,db.shop.tramT));
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
