const fs=require('fs'),vm=require('vm');const src=fs.readFileSync(process.env.SRC||(__dirname+'/../../app/index.html'),'utf8');
const a=src.indexOf('const GG={'),b=src.indexOf('async function license');
const c=src.indexOf('var NK={'),d=src.indexOf('setTimeout(()=>{try{NK.chup()}catch(_){}},0);');
const body=`var XEM=false,NV=null,db=null,TAB_DONG=false;const DAY=86400000;
const iso=d=>{const x=new Date(d);return x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0')};
const todayIso=()=>iso(NOW());const dmy=s=>s;const money=n=>n+'d';const uid=()=>'u'+(++CNT.u);
const localStorage={_:{},getItem(k){return this._[k]??null},setItem(k,v){this._[k]=String(v)},removeItem(k){delete this._[k]},key(){return null},length:0};
const IDBS={ok:false};const navigator={userAgent:'Android'};const Store={saves:0,save(x){this.saves++;try{if(typeof NK!=='undefined'&&NK&&NK.snap!==undefined)NK.chup()}catch(_){}}};
function ggStatus(){};function render(){};const document={querySelector(){return null}};
`+src.slice(a,b)+'\n'+src.slice(c,d)+'\n;this.GG=GG;this.NK=NK;this.getDb=()=>db;this.setDb=v=>{db=v};';
const SHARED={u:0};let clock=Date.parse('2026-11-08T10:00:00');
// ---- mock Google Sheets: sheets[name] = array of rows
function Drive(){this.f={}}
Drive.prototype.handle=function(url,opt){const id=(url.match(/spreadsheets\/([^/?:]+)/)||[])[1];const S=this.f[id]=this.f[id]||{};const body=opt&&opt.body?JSON.parse(opt.body):null;const un=s=>decodeURIComponent(s).replace(/^'|'$/g,'').replace(/'!.*$/,'').replace(/^'/,'');
  if(/values:batchGet/.test(url)){const rs=[...url.matchAll(/ranges=([^&]+)/g)].map(m=>un(m[1]));return {valueRanges:rs.map(n=>({values:(S[n]||[]).map(r=>r.slice())}))}}
  if(/values:batchUpdate/.test(url)){body.data.forEach(x=>{const n=x.range.replace(/^'/,'').replace(/'!A1$/,'');const cur=S[n]=S[n]||[];x.values.forEach((r,i)=>cur[i]=r.slice())});return {}}
  if(/values:batchClear/.test(url)){body.ranges.forEach(rg=>{const m=rg.match(/^'(.+)'!([A-Z]+)(\d+):([A-Z]+)(\d+)$/);const n=m[1];const r0=+m[3];if(m[2]==='A'){S[n]=(S[n]||[]).slice(0,r0-1)}});return {}}
  if(/:batchUpdate/.test(url))return {};
  if(/fields=sheets/.test(url)){return {sheets:Object.keys(GGNAMES).map((t,i)=>({properties:{title:t,sheetId:i,gridProperties:{rowCount:1000,columnCount:40}}}))}}
  throw new Error('unhandled '+url)};
let GGNAMES={};
function device(D,name,opts={}){const ctx={NOW:()=>clock,CNT:SHARED,console,setTimeout:()=>0,clearTimeout:()=>0,JSON,Math,Date,Object,Array,String,Number,Set,Map,Promise,Error,encodeURIComponent,decodeURIComponent,Boolean,RegExp,isNaN};vm.createContext(ctx);vm.runInContext(body,ctx);
  const G=ctx.GG;G.token='t';G.email='a@x';G.sheetId='S1';G.nam=2026;G.files={2026:'S1'};G._ens='S1';G.tuSaoLuu=()=>{};G.saoLuu=async()=>'bk';G.queued=0;G.queue=function(){this.queued++};
  G.api=async function(url,opt){ if(this.hook)await this.hook(url,opt); return D.handle(url,opt)};
  if(!Object.keys(GGNAMES).length)G.dsSheet().forEach(n=>GGNAMES[n]=1);
  return {ctx,G,NK:ctx.NK,get db(){return ctx.getDb()},set db(v){ctx.setDb(v)},name}}
module.exports={Drive,device,setClock:t=>clock=Date.parse(t)};
