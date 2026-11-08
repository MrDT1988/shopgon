const {Drive,device}=require('./sim.js');
const mk=()=>({v:1,sample:false,shop:{ten:'S'},may:[{imei:'111',ten:'Reno',giaNhap:5,giaBan:6,ngayNhap:'2026-11-01',tt:'ton'}],don:[{id:'d0',ngay:'2026-11-07',loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Tiền mặt',huy:null}],hang:[{id:'h1',ten:'Cap',nhom:'pk',sl:10,giaNhap:1,giaBan:2}],pn:[],chi:[],nk:[]});
(async()=>{
 // lost update: A read Drive, B pushes a cancel+stock change, A writes (stale T11/Hang), then B pushes again
 const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
 A.db.don.push({id:'a1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null});A.db.hang[0].sl=9; // A sells (T11 + Hang change)
 B.db.don[0].huy='khách trả';B.db.hang[0].giaBan=3; // B cancels d0 and changes price
 A.G.hook=async url=>{if(/values:batchUpdate/.test(url)){A.G.hook=null;await B.G.push();}};
 await A.G.push();
 await B.G.push();await A.G.push();
 console.log('B d0.huy',B.db.don[0].huy,'A d0.huy',A.db.don.find(x=>x.id==='d0').huy,'| B price',B.db.hang[0].giaBan,'A price',A.db.hang[0].giaBan,'| sl A',A.db.hang[0].sl,'B',B.db.hang[0].sl);
})();
