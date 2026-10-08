import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('dist');
let files=0,bytes=0,largest={name:'',bytes:0};
function inspect(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
 const file=path.join(dir,entry.name);
 if(entry.isSymbolicLink())throw Error('El paquete no admite enlaces simbólicos: '+file);
 if(entry.isDirectory()){inspect(file);continue;}
 const relative=path.relative(root,file).replaceAll('\\','/');
 if(/(?:^|\/)(?:audit|node_modules|\.git)(?:\/|$)/.test(relative)||/\.docx?$/.test(relative)||entry.name==='ASIS_RIS_SAN_MIGUEL_2025.pdf')throw Error('Archivo privado o de desarrollo en el paquete: '+relative);
 const size=fs.statSync(file).size;files++;bytes+=size;
 if(size>largest.bytes)largest={name:relative,bytes:size};
 if(size>25*1024*1024)throw Error('Archivo superior a 25 MiB: '+relative);
}}
inspect(root);
if(files>20000)throw Error('Se supera el límite de 20.000 archivos de Pages Free.');
for(const name of ['index.html','404.html','_headers','data/asis.json','documents/ASIS_SAN_MIGUEL_2025_PUBLICO.pdf'])if(!fs.existsSync(path.join(root,name)))throw Error('Falta recurso requerido: '+name);
console.log(JSON.stringify({files,totalMiB:Number((bytes/1024/1024).toFixed(2)),largest,freeLimits:{files:20000,fileMiB:25}},null,2));
