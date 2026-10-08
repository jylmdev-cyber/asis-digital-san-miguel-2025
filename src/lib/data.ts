import raw from '../data/asis.json';
export type Row = Record<string,string|number>;
export type Column = {key:string;label:string;unit:string;numeric:boolean};
export type Dataset = {id:string;title:string;module:string;period:number|number[];unit:string;source:{document:string;page:number;printedPage:number;table:string;institution:string};columns:Column[];rows:Row[];note:string;status:string};
export const data=raw;
export const datasets=raw.datasets as Dataset[];
export const dataset=(id:string)=>datasets.find(d=>d.id===id)!;
export const nf=new Intl.NumberFormat('es-PE',{maximumFractionDigits:2});
export const fmt=(n:string|number)=>typeof n==='number'?nf.format(n):n;
export const norm=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export const isTotal=(r:Row)=>['total','provincial','total provincial'].includes(norm(String(Object.values(r)[0])));
export const detail=(d:Dataset)=>d.rows.filter(r=>!isTotal(r));
export const total=(id:string,key='total')=>Number(dataset(id).rows.find(isTotal)?.[key]??0);
export const sourceUrl=(page:number)=>`${import.meta.env.BASE_URL}documents/ASIS_SAN_MIGUEL_2025_PUBLICO.pdf#page=${page}`;
export function exportCsv(d:Dataset,rows:Row[]) {
 const cols=[...d.columns.map(c=>c.key),'source_document','source_page','source_table','source_period','source_note'];
 const quote=(x:unknown)=>{let s=String(x??''); if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
 const csv='\ufeff'+[cols.map(quote).join(','),...rows.map(r=>cols.map(k=>quote(k==='source_document'?d.source.document:k==='source_page'?r.page??d.source.page:k==='source_table'?d.source.table:k==='source_period'?r.year??(Array.isArray(d.period)?d.period.join('/'):d.period):k==='source_note'?d.note:r[k])).join(','))].join('\r\n');
 download(new Blob([csv],{type:'text/csv;charset=utf-8'}),`${d.id}.csv`);
}
export function download(blob:Blob,name:string){const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
export const routes=[{id:'inicio',label:'Panorama general',icon:'LayoutDashboard'},{id:'territorio',label:'Territorio',icon:'Map'},{id:'demografia',label:'Demografía',icon:'Users'},{id:'epidemiologia',label:'Situación epidemiológica',icon:'Activity'},{id:'determinantes',label:'Determinantes sociales',icon:'Sprout'},{id:'servicios',label:'Servicios de salud',icon:'Hospital'},{id:'prioridades',label:'Prioridades y acciones',icon:'Target'},{id:'biblioteca',label:'Biblioteca y fuentes',icon:'Library'}];
export const href=(id:string)=>import.meta.env.BASE_URL+(id==='inicio'?'':id+'/');
