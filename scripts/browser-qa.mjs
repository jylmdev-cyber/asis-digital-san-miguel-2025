import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base=process.env.QA_URL||'http://127.0.0.1:4322/';
fs.mkdirSync('qa',{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1050}});
const page=await context.newPage();
const errors=[];page.on('pageerror',e=>errors.push(e.message));
const results=[];
for(const route of ['','territorio/','demografia/','epidemiologia/','determinantes/','servicios/','prioridades/','biblioteca/']){
 await page.goto(base+route);await page.waitForLoadState('networkidle');assert.equal(await page.locator('h1').count(),1);
 assert.ok(await page.locator('main').isVisible());
 const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
 results.push({route:route||'inicio',violations:axe.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary})).slice(0,12)}))});
 if(route==='')await page.screenshot({path:'qa/dashboard-desktop.png',fullPage:true});
 if(route==='territorio/')await page.screenshot({path:'qa/territorio-desktop.png',fullPage:true});
}
await page.goto(base);await page.waitForLoadState('networkidle');const pngReady=page.waitForEvent('download');await page.getByRole('button',{name:'Descargar gráfico de Principales causas de atención'}).click();const png=await pngReady;await png.saveAs('qa/morbilidad.png');assert.equal(fs.readFileSync('qa/morbilidad.png').subarray(1,4).toString(),'PNG');await page.getByRole('button',{name:'Ver tabla de Principales causas de atención'}).click();assert.ok(await page.locator('.chart-panel table').isVisible());
await page.goto(base+'territorio/');await page.waitForLoadState('networkidle');await page.locator('.map-selector select').selectOption('agua');assert.ok((await page.locator('.map-panel .panel-head').innerText()).includes('2017'));await page.locator('.leaflet-interactive').first().click();await page.waitForTimeout(350);assert.equal(await page.locator('.leaflet-popup').count(),1);assert.ok(await page.locator('.leaflet-popup').isVisible());assert.ok(page.url().includes('distrito='));
await page.goto(base+'demografia/');await page.waitForLoadState('networkidle');await page.locator('.filter-bar select').nth(0).selectOption('Llapa');assert.ok((await page.locator('.kpi').first().innerText()).includes('3,950')||(await page.locator('.kpi').first().innerText()).includes('3950'));assert.ok(page.url().includes('distrito=Llapa'));await page.locator('.filter-bar select').nth(2).selectOption('2023');assert.ok((await page.locator('.kpi').first().innerText()).includes('4,323'));
const dl=page.waitForEvent('download');await page.getByRole('button',{name:'CSV',exact:true}).first().click();const download=await dl;await download.saveAs('qa/poblacion-filtered.csv');const csv=fs.readFileSync('qa/poblacion-filtered.csv','utf8');assert.ok(csv.includes('Llapa'));assert.ok(csv.includes('2023'));assert.ok(csv.includes('source_page'));assert.ok(!csv.includes('Bolívar'));
await page.goto(base+'determinantes/');await page.waitForLoadState('networkidle');await page.locator('.filter-bar select').last().selectOption('emigracion');assert.equal(await page.locator('.chart-panel').count(),0);assert.ok((await page.locator('.data-panel').innerText()).includes('150.4'));
await page.goto(base);await page.waitForLoadState('networkidle');await page.getByRole('button',{name:'Buscar en el ASIS',exact:true}).click();await page.getByRole('textbox',{name:'Buscar en contenidos y documento'}).fill('tuberculosis');await page.waitForTimeout(300);assert.ok(await page.locator('.search-results a').count()>0);await page.keyboard.press('Escape');assert.ok(!await page.locator('dialog').isVisible());
await page.getByRole('button',{name:'Activar modo oscuro'}).click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');await page.screenshot({path:'qa/dashboard-dark.png',fullPage:true});
const darkAxe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag22aa']).analyze();results.push({route:'inicio-dark',violations:darkAxe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
await page.setViewportSize({width:390,height:844});await page.getByRole('button',{name:'Activar modo claro'}).click();await page.waitForTimeout(300);await page.screenshot({path:'qa/dashboard-mobile.png',fullPage:true});const mobileAxe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag22aa']).analyze();results.push({route:'inicio-mobile',violations:mobileAxe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));await page.getByRole('button',{name:'Abrir navegación'}).click();assert.ok(await page.locator('.sidebar.open').isVisible());await page.getByRole('button',{name:'Cerrar navegación',exact:true}).click();
for(const route of ['territorio/','demografia/','epidemiologia/','determinantes/','servicios/','prioridades/','biblioteca/']){await page.goto(base+route);await page.waitForLoadState('networkidle');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),route);}
await page.goto(base);await page.setViewportSize({width:768,height:1024});await page.waitForLoadState('networkidle');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
fs.writeFileSync('qa/results.json',JSON.stringify({testedAt:new Date().toISOString(),base,results,errors},null,2));await browser.close();console.log(JSON.stringify({routes:8,accessibility:results.map(r=>({route:r.route,violations:r.violations.length})),errors}));assert.equal(errors.length,0,'Browser runtime errors');assert.ok(results.every(r=>r.violations.length===0),'Accessibility violations; inspect qa/results.json');
