const {Drive,device}=require('./sim.js');
const mk=()=>({v:1,sample:false,shop:{ten:'S'},may:[],don:[{id:'d0',ngay:'2026-11-07',loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null}],hang:[{id:'h1',ten:'Cap',nhom:'pk',sl:10,giaNhap:1,giaBan:2}],pn:[],chi:[],nk:[]});
(async()=>{
 // (a) both owner devices apply same NV order (deterministic id) -> _nv2 correction
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
  for(const X of [A,B]){X.db.hang[0].sl=9;X.db.don.push({id:'nv-o1-0',bill:'o1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null})}
  await A.G.push();await B.G.push();await A.G.push();console.log('(a) same NV order on 2 owner devices, stock 10 sell 1 => A',A.db.hang[0].sl,'B',B.db.hang[0].sl,'drive',D.f.S1['Hàng hóa'][1][4],'(expect 9)');}
 // (c) tombstoned delete resurrected by a concurrent stale write
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();B.NK.chup();
  A.db.chi.push({id:'c1',ngay:'2026-11-08',loai:'Điện',tien:100});
  B.db.don=[];B.NK.ghi(); // B deletes d0 with tombstone
  A.G.hook=async url=>{if(/values:batchUpdate/.test(url)){A.G.hook=null;await B.G.push();}};
  await A.G.push();await B.G.push();await A.G.push();
  console.log('(c) B deleted d0 (tomb',JSON.stringify(B.db.nk.map(n=>n.xk)),') -> B don',B.db.don.map(x=>x.id).join()||'-','A don',A.db.don.map(x=>x.id).join()||'-');}
 // (d) chuyenNam-style db replacement then a save -> bogus tombstones / journal
 {const D=new Drive();const A=device(D,'A');A.db=mk();for(let i=0;i<30;i++)A.db.don.push({id:'o'+i,ngay:'2026-10-1'+(i%9),loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null});await A.G.push();A.NK.chup();
  // simulate push merge dropping rows (e.g. db replaced by khoiPhuc/chuyenNam with fewer rows)
  A.db={...A.db,don:A.db.don.slice(0,5)};A.db.chi=[{id:'c9',ngay:'2026-11-08',loai:'x',tien:1}];A.NK.ghi();
  const x=A.db.nk.filter(n=>n.xk);console.log('(d) after db replaced, first save emits',x.length,'journal rows with tombstones covering',x.reduce((a,n)=>a+n.xk.length,0),'keys, viec=',x.map(n=>n.viec).slice(0,3).join('|'));}
})().catch(e=>console.error(e));
