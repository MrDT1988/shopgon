// H2: in-place mutation during ghiFile -> base polluted -> edit reverted on next push
const {Drive,device}=require('./sim.js');
(async()=>{const D=new Drive();const A=device(D,'A');
 A.db={v:1,sample:false,shop:{ten:'S'},may:[{imei:'111',ten:'Reno',giaNhap:5,giaBan:6,ngayNhap:'2026-11-01',tt:'ton'}],don:[],hang:[{id:'h1',ten:'Cap',nhom:'pk',sl:10,giaNhap:1,giaBan:2}],pn:[],chi:[],nk:[]};
 await A.G.push(); console.log('drive sl after push1', D.f.S1['Hàng hóa'][1][4]);
 // sale happens WHILE ghiFile is in flight (in-place, like line ~2214)
 A.G.hook=async(url)=>{if(/values:batchUpdate/.test(url)){A.G.hook=null;const h=A.db.hang.find(x=>x.id==='h1');h.sl-=1;const m=A.db.may.find(x=>x.imei==='111');m.tt='ban';A.db.don.push({id:'d1',ngay:'2026-11-08',loai:'may',imei:'111',ten:'Reno',giaBan:6,giaVon:5,tt:'Tiền mặt',huy:null},{id:'d2',ngay:'2026-11-08',loai:'pk',hangId:'h1',ten:'Cap',sl:1,giaBan:2,giaVon:1,tt:'Tiền mặt',huy:null})}};
 A.db.chi.push({id:'c1',ngay:'2026-11-08',loai:'Điện',tien:100}); // something to make push write
 await A.G.push(); console.log('after push2 local sl',A.db.hang[0].sl,'tt',A.db.may[0].tt,'base sl',A.G.getBase().hang[0].sl,'drive sl',D.f.S1['Hàng hóa'][1][4]);
 await A.G.push(); console.log('after push3 local sl',A.db.hang[0].sl,'tt',A.db.may[0].tt,'drive sl',D.f.S1['Hàng hóa'][1][4],'drive imei tt',D.f.S1['IMEI'][1][7],'don',A.db.don.map(x=>x.id).join());
})();
