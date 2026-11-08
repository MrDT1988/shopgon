const {Drive,device}=require('./sim.js');
const D=new Drive();const A=device(D,'A');const G=A.G;
const loc={shop:{},may:[],don:[{id:'d',ngay:'2026-11-07',loai:'pk',ten:'Op',giaBan:9,giaVon:1,tt:'Ghi nợ',no:500,huy:null}],hang:[{id:'h1',ten:'Cap',sl:10}],pn:[],chi:[],nk:[]};
const rem=JSON.parse(JSON.stringify(loc));rem.hang[0].sl=7;rem.don[0].no=0;rem.don[0].huy='hủy';
const m=G.merge(null,loc,rem);console.log('merge(null): sl',m.hang[0].sl,'(Drive 7) no',m.don[0].no,'huy',m.don[0].huy);
