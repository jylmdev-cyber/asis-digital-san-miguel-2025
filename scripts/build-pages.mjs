import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const destination=process.env.SITE_URL||process.env.CF_PAGES_URL;
if(!destination)throw Error('Define SITE_URL con la URL HTTPS de tu proyecto. Cloudflare también proporciona CF_PAGES_URL durante la compilación.');
const site=new URL(destination);
if(site.protocol!=='https:'||site.username||site.password||site.pathname!=='/'||site.search||site.hash)throw Error('SITE_URL debe ser un origen HTTPS sin credenciales, ruta, consulta ni fragmento.');
const env={...process.env,SITE_URL:site.origin,BASE_PATH:'/'};
function run(file,args=[],extra={}){const r=spawnSync(process.execPath,[file,...args],{env:{...env,...extra},stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status||1);}
const astro=JSON.parse(fs.readFileSync('node_modules/astro/package.json','utf8'));
run(path.resolve('node_modules/astro',astro.bin.astro),['build']);
// Los recursos generados se escriben en dist; la copia de Sites en public no se altera.
run(path.resolve('scripts/generate-qr.mjs'),[],{QR_OUTPUT_DIR:path.resolve('dist/share')});
const routes=['','territorio/','demografia/','epidemiologia/','determinantes/','servicios/','prioridades/','biblioteca/'];
fs.writeFileSync('dist/robots.txt',`User-agent: *\nAllow: /\nSitemap: ${site.origin}/sitemap.xml\n`);
fs.writeFileSync('dist/sitemap.xml',`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${routes.map(r=>`<url><loc>${site.origin}/${r}</loc></url>`).join('')}</urlset>\n`);
run(path.resolve('scripts/validate-pages.mjs'));
console.log('Build estático para Cloudflare Pages preparado con destino: '+site.origin);
