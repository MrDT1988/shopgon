const {Drive,device}=require('./sim.js');
const mk=()=>({v:1,sample:false,shop:{ten:'S'},may:[{imei:'111',ten:'Reno',giaNhap:5,giaBan:6,ngayNhap:'2026-11-01',tt:'ton'}],don:[],hang:[{id:'h1',ten:'Cap',nhom:'pk',sl:10,giaNhap:1,giaBan:2}],pn:[],chi:[],nk:[]});
const save=X=>{X.NK.ghi()};
(async()=>{
 // T2: 2 devices sell same qty of same accessory -> collapse
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
  A.db.hang[0].sl=9;A.db.don.push({id:'a1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null});
  B.db.hang[0].sl=9;B.db.don.push({id:'b1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null});
  await B.G.push();await A.G.push();await B.G.push();
  console.log('T2 two sales of 1 from 10: A sl',A.db.hang[0].sl,'B sl',B.db.hang[0].sl,'drive',D.f.S1['Hàng hóa'][1][4],'(expected 8)');}
 // T3: lost update interleave: A reads, B pushes full, A writes
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
  A.db.chi.push({id:'c1',ngay:'2026-11-08',loai:'Điện',tien:100});
  B.db.hang[0].sl=9;B.db.may[0].tt='ban';B.db.don.push({id:'b1',ngay:'2026-11-08',loai:'may',imei:'111',ten:'Reno',giaBan:6,giaVon:5,tt:'Tiền mặt',huy:null});
  A.G.hook=async url=>{if(/values:batchUpdate/.test(url)){A.G.hook=null;await B.G.push();}};
  await A.G.push();
  console.log('T3 after A write: drive T11 rows',D.f.S1['T11'].filter(r=>r[0]).length-1,'drive sl',D.f.S1['Hàng hóa'][1][4],'imei tt',D.f.S1['IMEI'][1][7]);
  await B.G.push();
  console.log('T3 after B push: B sl',B.db.hang[0].sl,'B imei tt',B.db.may[0].tt,'B don',B.db.don.map(x=>x.id).join(),'drive T11',D.f.S1['T11'].filter(r=>r[0]).map(r=>r[1]).join());}
 // T4: delete freshly synced row (no save between sync and delete) -> no tombstone -> resurrect
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();A.NK.chup();
  B.db.don.push({id:'x',ngay:'2026-11-08',loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null});await B.G.push();
  await A.G.push(); // periodic 90s sync brings x
  A.db.don=A.db.don.filter(o=>o.id!=='x');save(A); // user deletes x
  await A.G.push();
  console.log('T4 A deleted synced row x: tomb?',JSON.stringify((A.db.nk||[]).map(n=>n.xk)),'A don after push',A.db.don.map(x=>x.id).join()||'(none)');}
 // T5: mat() never fires even on mass tombstone deletions
 {const D=new Drive();const A=device(D,'A');A.db=mk();for(let i=0;i<50;i++)A.db.don.push({id:'o'+i,ngay:'2026-11-0'+(1+i%7),loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null});await A.G.push();
  const loc=JSON.parse(JSON.stringify(A.db));loc.don=[];loc.nk=[{id:'n1',t:'2026-11-08 10:00',xk:loc.may.length?A.db.don.map(o=>'Don|'+o.id):[]}];
  const rem=await A.G.readRemote();const m=A.G.merge(A.G.getBase(),loc,rem);console.log('T5 merge keeps',m.don.length,'of 50; mat=',JSON.stringify(A.G.mat(loc,rem,m)));
  // and without tombstones: merge keeps all, mat 0 -> mat can never be >0
  const loc2=JSON.parse(JSON.stringify(A.db));loc2.don=[];const m2=A.G.merge(A.G.getBase(),loc2,rem);console.log('T5b no tomb: merge keeps',m2.don.length,'mat=',JSON.stringify(A.G.mat(loc2,rem,m2)));}
})().catch(e=>console.error(e));
