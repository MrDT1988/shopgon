const {Drive,device}=require('./sim.js');
const mk=()=>({v:1,sample:false,shop:{ten:'S'},may:[],don:[],hang:[{id:'h1',ten:'Cap',nhom:'pk',sl:10,giaNhap:1,giaBan:2}],pn:[],chi:[],nk:[]});
(async()=>{const D=new Drive();const A=device(D,'A'),B=device(D,'B');A.db=mk();await A.G.push();B.db=mk();await B.G.pull();
 A.db.hang[0].sl=9;A.db.don.push({id:'a1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null});
 A.G.hook=async url=>{if(/batchClear/.test(url)){A.G.hook=null;throw new Error('429 rate')}};
 const ok=await A.G.push();console.log('A push ok?',ok,'drive sl',D.f.S1['Hàng hóa'][1][4],'A base sl',A.G.getBase().hang[0].sl);
 B.db.hang[0].sl=8;B.db.don.push({id:'b1',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:2,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null});await B.G.push();
 await A.G.push();await B.G.push();console.log('sold 1+2 from 10 => expect 7; A',A.db.hang[0].sl,'B',B.db.hang[0].sl,'drive',D.f.S1['Hàng hóa'][1][4]);
})();
