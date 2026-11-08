const {Drive,device,setClock}=require('./sim.js');
const mk=()=>({v:1,sample:false,shop:{ten:'S'},may:[],don:[{id:'d0',ngay:'2026-11-07',loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null},{id:'d1',ngay:'2026-11-07',loai:'pk',ten:'Op2',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null}],hang:[],pn:[],chi:[],nk:[]});
(async()=>{
 // pnCho lost via whole-key shop merge
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
  A.db.shop.pnCho=[{id:'p1',kind:'nhap'}];B.db.shop.pnCho=[{id:'p2',kind:'nhap'}];await B.G.push();await A.G.push();await B.G.push();
  console.log('pnCho A',JSON.stringify(A.db.shop.pnCho.map(x=>x.id)),'B',JSON.stringify(B.db.shop.pnCho.map(x=>x.id)));}
 // stale snapshot after push -> remote edit logged as local "Sửa đơn"
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();A.NK.chup();
  B.db.don[0].giaBan=99;await B.G.push();await A.G.push();A.db.chi.push({id:'c',ngay:'2026-11-08',loai:'x',tien:1});A.NK.ghi();
  console.log('fake journal on A:',JSON.stringify(A.db.nk.map(n=>n.viec+' '+n.ct)));}
 // device clock in past year: tombstone not written to Drive -> resurrect
 {const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();B.NK.chup();
  setClock('2025-12-30T10:00:00');B.db.don=B.db.don.filter(x=>x.id!=='d0');B.NK.ghi();await B.G.push();setClock('2026-11-08T10:00:00');
  console.log('Drive Nhật ký rows',D.f.S1['Nhật ký'].length-1,'Drive T11 ids',D.f.S1['T11'].slice(1).map(r=>r[1]).join());
  await A.G.push();await B.G.push();console.log('after A,B push: B don',B.db.don.map(x=>x.id).join(),'A don',A.db.don.map(x=>x.id).join());}
})().catch(e=>console.error(e));
